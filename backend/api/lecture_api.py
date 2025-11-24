#!/usr/bin/env python3
"""
에브리타임 크롤링 API 서버 - 개선된 버전
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import urllib.parse
import time
import os
from dotenv import load_dotenv
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd
try:
    from config.config import Config
except ImportError:
    class Config:
        EVERYTIME_ID = os.getenv('EVERYTIME_ID')
        EVERYTIME_PASSWORD = os.getenv('EVERYTIME_PASSWORD')
        HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'

from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_requests
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
import re
from backend.api import get_mongo_db
# from backend.models.course import Course, Review, CourseDetails

# 환경변수 로드
load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 한글 JSON 응답을 위해
CORS(app)  # CORS 허용

# 전역 드라이버 세션 관리
global_driver = None
login_time = None
SESSION_TIMEOUT = 30 * 60  # 30분 (초 단위)
cached_search_results = {}  # 검색 결과 캐시

SOFTWARE_COURSES_CACHE = None
SOFTWARE_COURSES_CACHE_TS = 0
SOFTWARE_COURSES_SOURCE = Path(__file__).resolve().parents[2] / 'course' / '2025-2.xlsx'

GOOGLE_AUTH_REQUEST = google_auth_requests.Request()


def verify_google_credential(credential: Optional[str]) -> Dict[str, Any]:
    """Google ID 토큰 검증"""
    if not credential:
        raise ValueError("Google credential is missing.")
    
    if not Config.GOOGLE_CLIENT_ID:
        raise ValueError("GOOGLE_CLIENT_ID 환경 변수가 설정되지 않았습니다.")
    
    try:
        id_info = id_token.verify_oauth2_token(
            credential,
            GOOGLE_AUTH_REQUEST,
            Config.GOOGLE_CLIENT_ID
        )
        if id_info.get('aud') != Config.GOOGLE_CLIENT_ID:
            raise ValueError("토큰의 클라이언트 ID가 일치하지 않습니다.")
        return id_info
    except ValueError as exc:
        raise ValueError(f"유효하지 않은 Google 토큰입니다: {exc}") from exc


def get_users_collection():
    """사용자 컬렉션 가져오기"""
    db = get_mongo_db()
    return db['users']


def serialize_user(user_doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """MongoDB 사용자 문서 직렬화"""
    if not user_doc:
        return None
    
    def _fmt_dt(value):
        if isinstance(value, datetime):
            return value.isoformat()
        return None
    
    return {
        "user_id": user_doc.get("user_id"),
        "email": user_doc.get("email"),
        "email_verified": user_doc.get("email_verified"),
        "name": user_doc.get("name"),
        "given_name": user_doc.get("given_name"),
        "family_name": user_doc.get("family_name"),
        "picture": user_doc.get("picture"),
        "locale": user_doc.get("locale"),
        "major": user_doc.get("major"),
        "semester": user_doc.get("semester"),
        "phone": user_doc.get("phone"),
        "goal": user_doc.get("goal"),
        "bio": user_doc.get("bio"),
        "interests": user_doc.get("interests", []),
        "preferences": user_doc.get("preferences", {}),
        "provider": user_doc.get("provider", "google"),
        "last_login": _fmt_dt(user_doc.get("last_login")),
        "created_at": _fmt_dt(user_doc.get("created_at")),
        "updated_at": _fmt_dt(user_doc.get("updated_at")),
    }


def upsert_google_user(id_info: Dict[str, Any]) -> Dict[str, Any]:
    """Google 로그인 사용자를 upsert"""
    users_collection = get_users_collection()
    user_id = id_info.get("sub")
    now = datetime.utcnow()
    
    if not user_id:
        raise ValueError("Google 사용자 ID를 확인할 수 없습니다.")
    
    base_updates = {
        "user_id": user_id,
        "email": id_info.get("email"),
        "email_verified": id_info.get("email_verified"),
        "name": id_info.get("name"),
        "given_name": id_info.get("given_name"),
        "family_name": id_info.get("family_name"),
        "picture": id_info.get("picture"),
        "locale": id_info.get("locale"),
        "provider": "google",
        "updated_at": now,
        "last_login": now,
    }
    
    existing = users_collection.find_one({"user_id": user_id})
    if existing:
        users_collection.update_one(
            {"_id": existing["_id"]},
            {"$set": base_updates}
        )
        updated = users_collection.find_one({"_id": existing["_id"]})
    else:
        new_doc = {
            **base_updates,
            "created_at": now,
            "major": None,
            "semester": None,
            "phone": "",
            "goal": "",
            "bio": "",
            "interests": [],
            "preferences": {},
        }
        users_collection.insert_one(new_doc)
        updated = new_doc
    
    return updated


def get_bearer_token() -> Optional[str]:
    """Authorization 헤더에서 Bearer 토큰 추출"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        return None
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return None


@app.route("/api/auth/google", methods=["POST"])
def authenticate_with_google():
    """Google OAuth ID 토큰을 검증해 사용자 정보 반환"""
    payload = request.get_json(silent=True) or {}
    credential = payload.get("credential") or payload.get("id_token")
    
    if not credential:
        return jsonify({"error": "credential 필드가 필요합니다."}), 400
    
    try:
        id_info = verify_google_credential(credential)
        user_doc = upsert_google_user(id_info)
        return jsonify({
            "token": credential,
            "user": serialize_user(user_doc)
        })
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 401
    except Exception as exc:  # pylint: disable=broad-except
        return jsonify({"error": "Google 인증 처리 중 오류가 발생했습니다.", "detail": str(exc)}), 500


@app.route("/api/auth/me", methods=["GET"])
def get_authenticated_user():
    """현재 로그인한 사용자 정보 조회"""
    token = get_bearer_token()
    if not token:
        return jsonify({"error": "Authorization 헤더가 필요합니다."}), 401
    
    try:
        id_info = verify_google_credential(token)
        user_id = id_info.get("sub")
        if not user_id:
            raise ValueError("Google 사용자 ID를 확인할 수 없습니다.")
        
        users_collection = get_users_collection()
        user_doc = users_collection.find_one({"user_id": user_id})
        if not user_doc:
            user_doc = upsert_google_user(id_info)
        else:
            users_collection.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {"last_login": datetime.utcnow(), "updated_at": datetime.utcnow()}}
            )
            user_doc = users_collection.find_one({"_id": user_doc["_id"]})
        
        return jsonify({"user": serialize_user(user_doc)})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 401
    except Exception as exc:  # pylint: disable=broad-except
        return jsonify({"error": "사용자 정보를 가져오는 중 오류가 발생했습니다.", "detail": str(exc)}), 500


@app.route("/api/users/me", methods=["PUT"])
def update_authenticated_user():
    """현재 사용자 프로필 업데이트"""
    token = get_bearer_token()
    if not token:
        return jsonify({"error": "Authorization 헤더가 필요합니다."}), 401
    
    try:
        id_info = verify_google_credential(token)
        user_id = id_info.get("sub")
        if not user_id:
            raise ValueError("Google 사용자 ID를 확인할 수 없습니다.")
        
        payload = request.get_json(silent=True) or {}
        users_collection = get_users_collection()
        user_doc = users_collection.find_one({"user_id": user_id})
        if not user_doc:
            user_doc = upsert_google_user(id_info)
        
        updates: Dict[str, Any] = {}
        if "name" in payload:
            updates["name"] = payload["name"]
        if "major" in payload:
            updates["major"] = payload["major"]
        if "goal" in payload:
            updates["goal"] = payload["goal"]
        if "bio" in payload:
            updates["bio"] = payload["bio"]
        if "phone" in payload:
            updates["phone"] = payload["phone"]
        if "semester" in payload:
            semester_value = payload["semester"]
            try:
                updates["semester"] = int(semester_value) if semester_value not in (None, "") else None
            except (TypeError, ValueError):
                raise ValueError("semester 값은 정수이어야 합니다.")
        if "interests" in payload:
            interests_value = payload["interests"]
            if isinstance(interests_value, str):
                interests_value = [
                    item.strip() for item in interests_value.split(",") if item.strip()
                ]
            if not isinstance(interests_value, list):
                raise ValueError("interests 값은 리스트여야 합니다.")
            updates["interests"] = interests_value
        if "preferences" in payload:
            preferences_value = payload["preferences"]
            if not isinstance(preferences_value, dict):
                raise ValueError("preferences 값은 객체여야 합니다.")
            updates["preferences"] = preferences_value
        
        updates["updated_at"] = datetime.utcnow()
        
        users_collection.update_one({"user_id": user_id}, {"$set": updates})
        refreshed = users_collection.find_one({"user_id": user_id})
        return jsonify({"user": serialize_user(refreshed)})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # pylint: disable=broad-except
        return jsonify({"error": "사용자 정보를 업데이트하는 중 오류가 발생했습니다.", "detail": str(exc)}), 500


@app.route("/api/auth/logout", methods=["POST"])
def logout_user():
    """클라이언트 측 로그아웃 처리를 위한 엔드포인트 (서버 상태 없음)"""
    return jsonify({"success": True})


def _clean_string(value):
    if pd.isna(value):
        return ''
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value).strip()
    return str(value).strip()


def _clean_number(value, fallback=0):
    if pd.isna(value):
        return fallback
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            return fallback


def load_software_courses_from_excel(force_reload: bool = False):
    """엑셀 파일에서 소프트웨어학과 과목 데이터를 로드"""
    global SOFTWARE_COURSES_CACHE, SOFTWARE_COURSES_CACHE_TS

    if not force_reload and SOFTWARE_COURSES_CACHE is not None:
        return SOFTWARE_COURSES_CACHE

    if not SOFTWARE_COURSES_SOURCE.exists():
        raise FileNotFoundError(f"엑셀 파일을 찾을 수 없습니다: {SOFTWARE_COURSES_SOURCE}")

    df = pd.read_excel(SOFTWARE_COURSES_SOURCE, header=1)
    if '과목명' not in df.columns:
        raise ValueError('엑셀 파일 형식이 예상과 다릅니다. (과목명 열이 없음)')

    df = df[df['과목명'].notna()].copy()

    if '소속' in df.columns:
        df = df[df['소속'] == '소프트웨어학과']
    elif '개설\n전공' in df.columns:
        df = df[df['개설\n전공'].fillna('').str.contains('소프트웨어', na=False)]

    df.fillna('', inplace=True)

    courses = []
    for _, row in df.iterrows():
        course = {
            'course_id': _clean_string(row.get('과목\nID') or row.get('수강\n번호')),
            'course_name': _clean_string(row.get('과목명')),
            'course_code': _clean_string(row.get('교과목\n코드')),
            'professor': _clean_string(row.get('담당\n교수')),
            'department': _clean_string(row.get('소속') or row.get('개설\n전공')),
            'major': _clean_string(row.get('개설\n전공')),
            'semester': '2025-2',
            'credits': _clean_number(row.get('학점'), 0),
            'hours': _clean_number(row.get('시간'), 0),
            'course_type': _clean_string(row.get('학수\n구분')),
            'subject_type': _clean_string(row.get('교과\n구분')),
            'lecture_time': _clean_string(row.get('강의\n시간명')),
            'lecture_method': _clean_string(row.get('분반별\n수업\n방식') or row.get('수업\n방식')),
            'class_method': _clean_string(row.get('수업\n방식')),
            'class_type': _clean_string(row.get('분반별\n수업\n방법') or row.get('과목\n특성')),
            'course_characteristics': _clean_string(row.get('과목\n특성')),
            'course_english_name': _clean_string(row.get('과목\n영문명')),
            'target_grade': _clean_string(row.get('수강\n대상\n학년')),
            'average_rating': 0.0,
            'rating': 0.0,
            'total_reviews': 0,
            'reviews': [],
            'details': {
                'lecture_method': _clean_string(row.get('분반별\n수업\n방식') or row.get('수업\n방식')),
                'room': '',
                'time_slot': _clean_string(row.get('강의\n시간명')),
                'assignment': '정보 없음',
                'attendance': '정보 없음',
                'exam': '정보 없음',
                'team_project': '정보 없음',
                'credits': _clean_number(row.get('학점'), 0),
            },
            'ai_summary': '',
            'keywords': list({
                _clean_string(row.get('과목명')),
                _clean_string(row.get('담당\n교수')),
                _clean_string(row.get('교과목\n코드'))
            } - {''}),
            'tags': ['2025-2학기', '소프트웨어학과'],
            'popularity_score': 50.0,
            'trend_direction': 'stable',
            'source': 'excel_2025_2'
        }

        # course_id가 비어 있는 경우 course_code로 대체
        if not course['course_id']:
            course['course_id'] = course['course_code'] or course['course_name']

        courses.append(course)

    SOFTWARE_COURSES_CACHE = courses
    SOFTWARE_COURSES_CACHE_TS = time.time()
    print(f"✅ 소프트웨어학과 과목 {len(courses)}개 로드 (엑셀)")
    return SOFTWARE_COURSES_CACHE

# 샘플 데이터 (실제 크롤링 실패 시 사용)
SAMPLE_COURSES = [
    {
        "course_id": "CS301",
        "course_name": "데이터베이스",
        "professor": "김데이터",
        "department": "컴퓨터공학과",
        "semester": "2024-1",
        "details": {
            "attendance": "중요",
            "exam": "중간/기말",
            "assignment": "많음",
            "team_project": "있음",
            "credits": 3
        },
        "reviews": [
            {
                "review_id": "r001",
                "rating": 4.2,
                "comment": "개념 설명이 자세하고 실습이 많아서 좋았습니다. 팀프로젝트도 실무에 도움이 됩니다.",
                "semester": "2024-1",
                "has_team_project": True,
                "difficulty_level": 3,
                "workload_level": 4
            },
            {
                "review_id": "r002",
                "rating": 3.8,
                "comment": "SQL 실습이 많아서 기초를 잘 배울 수 있었어요. 과제가 좀 많았지만 도움이 많이 됨.",
                "semester": "2024-1",
                "has_team_project": False,
                "difficulty_level": 3,
                "workload_level": 3
            }
        ],
        "ai_summary": "데이터베이스 설계와 SQL 활용에 중점. 실무 중심 교육으로 취업에 도움됨.",
        "keywords": ["데이터베이스", "SQL", "NoSQL", "설계"],
        "tags": ["실무중심", "과제많음", "팀플있음"],
        "average_rating": 4.0,
        "total_reviews": 2,
        "popularity_score": 85.5,
        "trend_direction": "up"
    },
    {
        "course_id": "CS302",
        "course_name": "웹프로그래밍",
        "professor": "박웹",
        "department": "소프트웨어학과",
        "semester": "2024-1",
        "details": {
            "attendance": "보통",
            "exam": "프로젝트",
            "assignment": "보통",
            "team_project": "개인",
            "credits": 3
        },
        "reviews": [
            {
                "review_id": "r003",
                "rating": 4.5,
                "comment": "React와 Node.js를 배울 수 있어서 좋았어요. 포트폴리오 만들기 좋음.",
                "semester": "2024-1",
                "has_team_project": False,
                "difficulty_level": 3,
                "workload_level": 3
            },
            {
                "review_id": "r004",
                "rating": 4.0,
                "comment": "프론트엔드와 백엔드 모두 배워서 실무에 바로 적용할 수 있었어요.",
                "semester": "2024-1",
                "has_team_project": False,
                "difficulty_level": 3,
                "workload_level": 3
            }
        ],
        "ai_summary": "현업에서 사용하는 웹 기술 스택 교육. 개인 프로젝트 중심.",
        "keywords": ["React", "Node.js", "프론트엔드", "백엔드"],
        "tags": ["실용적", "프로젝트중심", "포트폴리오"],
        "average_rating": 4.25,
        "total_reviews": 2,
        "popularity_score": 92.0,
        "trend_direction": "up"
    },
    {
        "course_id": "CS303",
        "course_name": "알고리즘",
        "professor": "이알고",
        "department": "컴퓨터공학과",
        "semester": "2024-1",
        "details": {
            "attendance": "중요",
            "exam": "시험위주",
            "assignment": "많음",
            "team_project": "없음",
            "credits": 3
        },
        "reviews": [
            {
                "review_id": "r005",
                "rating": 3.5,
                "comment": "개념이 어렵지만 설명이 자세해서 이해하기 좋았어요. 과제가 많아서 부담스럽긴 했음.",
                "semester": "2024-1",
                "has_team_project": False,
                "difficulty_level": 4,
                "workload_level": 4
            }
        ],
        "ai_summary": "기초 알고리즘부터 고급 알고리즘까지 체계적으로 교육. 코딩 테스트 준비에 적합.",
        "keywords": ["알고리즘", "자료구조", "시간복잡도", "정렬"],
        "tags": ["개념중심", "코딩테스트", "과제많음"],
        "average_rating": 3.5,
        "total_reviews": 1,
        "popularity_score": 78.0,
        "trend_direction": "stable"
    }
]

def search_courses_by_keyword(keyword):
    """키워드로 강의 검색 (샘플 데이터 기반)"""
    results = []
    keyword_lower = keyword.lower()

    for course in SAMPLE_COURSES:
        # 강의명이나 교수명에 키워드가 포함되어 있는지 확인
        if (keyword_lower in course["course_name"].lower() or
            keyword_lower in course["professor"].lower() or
            any(keyword_lower in tag.lower() for tag in course["tags"]) or
            any(keyword_lower in kw.lower() for kw in course["keywords"])):

            # 실제 데이터 구조로 변환
            course_data = {
                "course_id": course["course_id"],
                "course_name": course["course_name"],
                "professor": course["professor"],
                "department": course["department"],
                "semester": course["semester"],
                "details": course["details"],
                "reviews": course["reviews"],
                "ai_summary": course["ai_summary"],
                "keywords": course["keywords"],
                "tags": course["tags"],
                "average_rating": course["average_rating"],
                "total_reviews": course["total_reviews"],
                "popularity_score": course["popularity_score"],
                "trend_direction": course["trend_direction"]
            }
            results.append(course_data)

    return results

def search_courses_from_db(keyword, limit=50, offset=0):
    """MongoDB에서 강의 검색"""
    try:
        db = get_mongo_db()
        collection = db.courses
        
        # 텍스트 검색 쿼리 (강의명, 교수명, 학과명에서 검색)
        if keyword:
            query = {
                "$or": [
                    {"course_name": {"$regex": keyword, "$options": "i"}},
                    {"professor": {"$regex": keyword, "$options": "i"}},
                    {"department": {"$regex": keyword, "$options": "i"}},
                    {"major": {"$regex": keyword, "$options": "i"}},
                    {"course_english_name": {"$regex": keyword, "$options": "i"}}
                ]
            }
        else:
            # 빈 키워드인 경우 모든 강의
            query = {}
        
        # 검색 실행 (페이지네이션 적용)
        cursor = collection.find(query).skip(offset).limit(limit)
        results = []
        
        for doc in cursor:
            # MongoDB 문서를 API 응답 형식으로 변환
            course_data = {
                "course_id": doc.get("course_id", ""),
                "course_name": doc.get("course_name", ""),
                "professor": doc.get("professor", ""),
                "department": doc.get("department", ""),
                "major": doc.get("major", ""),
                "semester": doc.get("semester", ""),
                "credits": doc.get("credits", 3),
                "hours": doc.get("hours", 3),
                "course_code": doc.get("course_code", ""),
                "subject_id": doc.get("subject_id", ""),
                "course_type": doc.get("course_type", ""),
                "subject_type": doc.get("subject_type", ""),
                "lecture_time": doc.get("lecture_time", ""),
                "lecture_method": doc.get("lecture_method", ""),
                "course_characteristics": doc.get("course_characteristics", ""),
                "course_english_name": doc.get("course_english_name", ""),
                "target_grade": doc.get("target_grade", ""),
                "class_method": doc.get("class_method", ""),
                "class_type": doc.get("class_type", ""),
                "rating": doc.get("rating", 0.0),
                "average_rating": doc.get("average_rating", 0.0),
                "total_reviews": doc.get("total_reviews", 0),
                "reviews": doc.get("reviews", []),
                "details": doc.get("details", {}),
                "ai_summary": doc.get("ai_summary", ""),
                "keywords": doc.get("keywords", []),
                "tags": doc.get("tags", []),
                "popularity_score": doc.get("popularity_score", 50.0),
                "trend_direction": doc.get("trend_direction", "stable"),
                "source": doc.get("source", "database")
            }
            results.append(course_data)
        
        print(f"✅ DB에서 {len(results)}개 강의 발견")
        return results
        
    except Exception as e:
        print(f"❌ DB 검색 오류: {str(e)}")
        return []

def get_all_courses_from_db(limit=50, offset=0):
    """MongoDB에서 모든 강의 가져오기"""
    try:
        db = get_mongo_db()
        collection = db.courses
        
        # 모든 강의 조회 (페이지네이션 적용)
        cursor = collection.find({}).skip(offset).limit(limit)
        results = []
        
        for doc in cursor:
            # MongoDB 문서를 API 응답 형식으로 변환
            course_data = {
                "course_id": doc.get("course_id", ""),
                "course_name": doc.get("course_name", ""),
                "professor": doc.get("professor", ""),
                "department": doc.get("department", ""),
                "major": doc.get("major", ""),
                "semester": doc.get("semester", ""),
                "credits": doc.get("credits", 3),
                "hours": doc.get("hours", 3),
                "course_code": doc.get("course_code", ""),
                "subject_id": doc.get("subject_id", ""),
                "course_type": doc.get("course_type", ""),
                "subject_type": doc.get("subject_type", ""),
                "lecture_time": doc.get("lecture_time", ""),
                "lecture_method": doc.get("lecture_method", ""),
                "course_characteristics": doc.get("course_characteristics", ""),
                "course_english_name": doc.get("course_english_name", ""),
                "target_grade": doc.get("target_grade", ""),
                "class_method": doc.get("class_method", ""),
                "class_type": doc.get("class_type", ""),
                "rating": doc.get("rating", 0.0),
                "average_rating": doc.get("average_rating", 0.0),
                "total_reviews": doc.get("total_reviews", 0),
                "reviews": doc.get("reviews", []),
                "details": doc.get("details", {}),
                "ai_summary": doc.get("ai_summary", ""),
                "keywords": doc.get("keywords", []),
                "tags": doc.get("tags", []),
                "popularity_score": doc.get("popularity_score", 50.0),
                "trend_direction": doc.get("trend_direction", "stable"),
                "source": doc.get("source", "database")
            }
            results.append(course_data)
        
        print(f"✅ DB에서 전체 {len(results)}개 강의 조회")
        return results
        
    except Exception as e:
        print(f"❌ 전체 강의 조회 오류: {str(e)}")
        return []

def setup_driver():
    """Chrome 웹드라이버 설정 (강력한 봇 감지 우회)"""
    chrome_options = Options()

    # 기본 안정성 옵션
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    
    # 강력한 봇 감지 우회 설정
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-automation")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions-file-access-check")
    chrome_options.add_argument("--disable-extensions-http-throttling")
    chrome_options.add_argument("--disable-extensions-except")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--disable-preconnect")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-hang-monitor")
    chrome_options.add_argument("--disable-prompt-on-repost")
    chrome_options.add_argument("--disable-domain-reliability")
    chrome_options.add_argument("--disable-component-extensions-with-background-pages")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    
    # 실제 사용자처럼 보이게 하는 User-Agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # 헤드리스 모드 비활성화 (봇 감지 방지)
    # chrome_options.add_argument("--headless")

    # macOS에서 Chrome 실행 파일 경로 명시
    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    try:
        # ChromeDriver 자동 설치 및 설정
        driver_path = ChromeDriverManager().install()
        print(f"📁 ChromeDriver 경로: {driver_path}")

        # ChromeDriver 권한 확인 및 설정
        import stat
        import os
        if not os.access(driver_path, os.X_OK):
            os.chmod(driver_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            print(f"✅ ChromeDriver 권한 설정 완료")

        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # 강력한 봇 감지 우회 JavaScript 실행
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        driver.execute_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """)
        
        driver.execute_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ko-KR', 'ko', 'en-US', 'en'],
            });
        """)
        
        driver.execute_script("""
            window.chrome = {
                runtime: {},
            };
        """)
        
        driver.execute_script("""
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({ state: 'granted' }),
                }),
            });
        """)

        # CDP 명령으로 추가 설정
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """
        })

        # 타임아웃 설정
        driver.implicitly_wait(5)
        driver.set_page_load_timeout(15)

        print(f"✅ Chrome 드라이버 설정 완료 (강력한 봇 감지 우회)")
        return driver

    except Exception as e:
        print(f"❌ ChromeDriver 설정 오류: {e}")
        print("⚠️ 크롤링 대신 샘플 데이터를 사용합니다.")
        return None

def get_or_create_driver():
    """전역 드라이버 가져오기 또는 생성"""
    global global_driver, login_time

    if global_driver is None:
        print("🔄 새 드라이버 세션 생성 중...")
        global_driver = setup_driver()
        if global_driver is None:
            print("⚠️ 드라이버 생성 실패 - 샘플 데이터 모드로 전환")
        else:
            print("✅ 새 드라이버 생성 완료")
    else:
        print("🔄 기존 드라이버 재사용")

    return global_driver

def ensure_logged_in():
    """로그인 상태 확인 및 유지"""
    global global_driver, login_time

    current_time = time.time()

    # 드라이버가 없거나 창이 닫혔는지 확인
    driver_needs_restart = False
    try:
        if global_driver is not None:
            test_url = global_driver.current_url
            print(f"🔍 드라이버 상태 확인: {test_url}")
        else:
            driver_needs_restart = True
    except Exception as e:
        print(f"⚠️ 드라이버 연결 끊어짐: {e}")
        driver_needs_restart = True

    if driver_needs_restart:
        print("🔄 드라이버 재시작...")
        cleanup_driver()
        global_driver = None
        login_time = None

    # 드라이버 가져오기
    driver = get_or_create_driver()

    # 로그인 상태 확인
    if login_time is None:
        print("🔐 첫 로그인 필요 - 로그인 시도 중...")
        if login_to_everytime(driver):
            login_time = current_time
            print("✅ 첫 로그인 성공 - 세션 저장됨")
            return True
        else:
            print("❌ 첫 로그인 실패")
            return False
    elif (current_time - login_time) > SESSION_TIMEOUT:
        print("⏰ 세션 만료 - 재로그인 필요")
        if login_to_everytime(driver):
            login_time = current_time
            print("✅ 재로그인 성공 - 세션 갱신됨")
            return True
        else:
            print("❌ 재로그인 실패")
            return False
    else:
        try:
            current_url = driver.current_url

            if "login" in current_url.lower():
                print("⚠️ 세션 만료 감지 - 재로그인 필요")
                if login_to_everytime(driver):
                    login_time = current_time
                    print("✅ 재로그인 성공")
                    return True
                else:
                    print("❌ 재로그인 실패")
                    return False
            else:
                remaining_time = int(SESSION_TIMEOUT - (current_time - login_time))
                print(f"✅ 기존 세션 유효함 (남은 시간: {remaining_time}초)")
                return True

        except Exception as e:
            print(f"⚠️ 세션 확인 중 오류: {e}")
            if login_to_everytime(driver):
                login_time = current_time
                print("✅ 세션 복구 성공")
                return True
            else:
                print("❌ 세션 복구 실패")
                return False

def cleanup_driver():
    """드라이버 정리"""
    global global_driver, login_time

    if global_driver:
        try:
            global_driver.quit()
            print("🗑️ 드라이버 정리 완료")
        except:
            pass
        finally:
            global_driver = None
            login_time = None

def login_to_everytime(driver):
    """에브리타임 로그인 (개선된 버전)"""
    try:
        print("🔐 에브리타임 로그인 중...")

        user_id = os.getenv("EVERYTIME_ID")
        user_password = os.getenv("EVERYTIME_PASSWORD")

        if not user_id or not user_password:
            print("❌ 환경변수 EVERYTIME_ID 또는 EVERYTIME_PASSWORD가 설정되지 않았습니다.")
            return False

        print(f"🔑 사용할 ID: {user_id}")
        print(f"🔑 사용할 비밀번호: {user_password}")
        print(f"🔍 환경변수 확인:")
        print(f"   EVERYTIME_ID: {os.getenv('EVERYTIME_ID')}")
        print(f"   EVERYTIME_PASSWORD: {os.getenv('EVERYTIME_PASSWORD')}")

        # 에브리타임 로그인 페이지로 직접 이동 (간단하게)
        print("🔗 로그인 페이지로 이동...")
        driver.get("https://everytime.kr/login")
        time.sleep(5)  # 페이지 로딩 대기

        # 페이지 소스 확인
        page_source = driver.page_source
        print(f"📄 로그인 페이지 로드됨 (길이: {len(page_source)})")

        # ID 입력 필드 찾기
        id_input = None
        id_selectors = [
            "input[name='userid']",
            "input[name='id']", 
            "#userid",
            "#id",
            "input[placeholder*='아이디']",
            "input[placeholder*='ID']"
        ]
        
        for selector in id_selectors:
            try:
                id_input = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"✅ ID 입력 필드 발견: {selector}")
                break
            except:
                continue

        if not id_input:
            print("❌ ID 입력 필드를 찾을 수 없습니다.")
            return False

        # ID 입력 (간단하게)
        id_input.clear()
        time.sleep(0.5)
        id_input.click()
        time.sleep(0.5)
        id_input.send_keys(user_id)
        print("✅ ID 입력 완료")

        # 비밀번호 입력 필드 찾기
        pw_input = None
        pw_selectors = [
            "input[name='password']",
            "#password",
            "input[type='password']",
            "input[placeholder*='비밀번호']"
        ]
        
        for selector in pw_selectors:
            try:
                pw_input = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ 비밀번호 입력 필드 발견: {selector}")
                break
            except:
                continue

        if not pw_input:
            print("❌ 비밀번호 입력 필드를 찾을 수 없습니다.")
            return False

        # 비밀번호 입력 (간단하게)
        pw_input.clear()
        time.sleep(0.5)
        pw_input.click()
        time.sleep(0.5)
        pw_input.send_keys(user_password)
        print("✅ 비밀번호 입력 완료")
        
        # 입력된 비밀번호 확인 (디버깅용)
        time.sleep(1)
        actual_password = pw_input.get_attribute('value')
        print(f"🔍 실제 입력된 비밀번호: '{actual_password}' (길이: {len(actual_password) if actual_password else 0})")
        
        if actual_password != user_password:
            print(f"⚠️ 비밀번호 불일치!")
            print(f"   예상: '{user_password}'")
            print(f"   실제: '{actual_password}'")
            
            # 재시도: 클리어 후 다시 입력
            pw_input.clear()
            time.sleep(0.5)
            pw_input.send_keys(user_password)
            time.sleep(0.5)
            final_password = pw_input.get_attribute('value')
            print(f"🔄 재입력 후: '{final_password}'")
        else:
            print("✅ 비밀번호 입력 검증 성공!")

        # 로그인 버튼 찾기 및 클릭
        login_btn = None
        login_selectors = [
            'input[type="submit"]',
            'button[type="submit"]',
            'button[class*="login"]',
            'input[value*="로그인"]',
            'button[class*="btn"]'
        ]
        
        for selector in login_selectors:
            try:
                login_btn = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ 로그인 버튼 발견: {selector}")
                break
            except:
                continue

        if not login_btn:
            print("❌ 로그인 버튼을 찾을 수 없습니다.")
            return False

        # 로그인 버튼 클릭 (더 자연스럽게)
        time.sleep(1)
        login_btn.click()
        print("✅ 로그인 버튼 클릭 완료")

        # 로그인 결과 대기 및 확인
        time.sleep(5)
        
        # Alert 처리 (Alert가 있어도 로그인 성공할 수 있음)
        alert_occurred = False
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"⚠️ Alert 발생: {alert_text}")
            alert.accept()
            alert_occurred = True
            
            if "올바른 정보" in alert_text:
                print("❌ 로그인 실패 - 잘못된 계정 정보")
                return False
            else:
                print("⚠️ Alert 발생했지만 로그인 성공 가능성 있음")
        except:
            pass

        # URL 확인으로 로그인 성공 여부 판단
        current_url = driver.current_url
        print(f"현재 URL: {current_url}")

        # 로그인 성공 확인 (더 정확한 판단)
        if "everytime.kr" in current_url and "login" not in current_url.lower():
            print("✅ 로그인 성공! (메인 페이지로 이동)")
            return True
        elif "account.everytime.kr" in current_url and "login" not in current_url.lower():
            print("✅ 로그인 성공! (계정 페이지로 이동)")
            return True
        elif current_url == "https://everytime.kr/" or current_url == "https://everytime.kr":
            print("✅ 로그인 성공! (메인 페이지)")
            return True
        else:
            print("❌ 로그인 실패 - 로그인 페이지에 머물러 있음")
            print(f"   현재 URL: {current_url}")
            return False

    except Exception as e:
        print(f"❌ 로그인 오류: {str(e)}")
        return False

def search_lecture(driver, keyword):
    """강의 검색 (실제 크롤링)"""
    try:
        print(f"🔍 '{keyword}' 검색 중...")

        # 에브리타임 강의실 페이지로 이동
        print("📍 강의실 페이지로 이동...")
        driver.get("https://everytime.kr/lecture")
        time.sleep(5)  # 페이지 로딩 대기 시간 증가

        # 페이지 소스 확인
        page_source = driver.page_source
        print(f"📄 강의실 페이지 로드됨 (길이: {len(page_source)})")
        
        # 페이지 제목 확인
        page_title = driver.title
        print(f"📋 페이지 제목: {page_title}")
        
        # 현재 URL 확인
        current_url = driver.current_url
        print(f"🌐 현재 URL: {current_url}")

        # 검색창 찾기 (더 많은 선택자 시도)
        search_input = None
        selectors = [
            'input[placeholder*="과목"]',
            'input[placeholder*="강의"]',
            'input[name="keyword"]',
            'input[name="search"]',
            'input[type="text"]',
            '#keyword',
            '#search',
            '.search input',
            'form input[type="text"]',
            'input[class*="search"]'
        ]

        print("🔍 검색창 찾는 중...")
        for i, selector in enumerate(selectors):
            try:
                print(f"   시도 {i+1}/{len(selectors)}: {selector}")
                search_input = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"✅ 검색창 발견: {selector}")
                break
            except Exception as e:
                print(f"   ❌ 실패: {str(e)[:50]}...")
                continue

        if not search_input:
            print("❌ 검색창을 찾을 수 없음")
            print("🔍 페이지에서 사용 가능한 input 요소들:")
            try:
                all_inputs = driver.find_elements(By.TAG_NAME, "input")
                for i, inp in enumerate(all_inputs[:10]):  # 처음 10개만
                    try:
                        input_type = inp.get_attribute("type") or "text"
                        input_name = inp.get_attribute("name") or "no-name"
                        input_placeholder = inp.get_attribute("placeholder") or "no-placeholder"
                        print(f"   Input {i+1}: type='{input_type}', name='{input_name}', placeholder='{input_placeholder}'")
                    except:
                        print(f"   Input {i+1}: 정보 추출 실패")
            except Exception as e:
                print(f"   Input 요소 조회 실패: {e}")
            return []

        # 검색어 입력
        search_input.clear()
        search_input.send_keys(keyword)

        # 검색 실행
        try:
            search_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"], button[type="submit"]')
            search_button.click()
        except:
            search_input.submit()

        time.sleep(5)

        # 검색 결과 수집
        lectures = []
        try:
            print("🔍 검색 결과 페이지 분석 중...")

            # 현재 URL 확인
            current_url = driver.current_url
            print(f"🌐 검색 후 URL: {current_url}")
            
            page_source = driver.page_source
            print(f"📄 페이지 길이: {len(page_source)} 문자")

            # 페이지 제목 확인
            page_title = driver.title
            print(f"📋 페이지 제목: {page_title}")

            # 여러 선택자로 강의 목록 찾기 시도 (에브리타임 특화)
            selectors = [
                'tr[onclick]',  # 에브리타임 강의 목록의 일반적인 형태
                'table tbody tr',  # 테이블 본문의 행들
                '.lecture tr',
                'table tr',
                '.list tr',
                'tr[class*="item"]',
                'tr[class*="lecture"]',
                'tr[class*="course"]',
                '.item',
                '.lecture',
                'tr',
                '.course',
                'li'
            ]

            lecture_items = []
            for selector in selectors:
                try:
                    items = driver.find_elements(By.CSS_SELECTOR, selector)
                    if items and len(items) > 1:
                        print(f"✅ 선택자 '{selector}'로 {len(items)}개 요소 발견")
                        lecture_items = items[:15]  # 더 많은 결과 수집
                        break
                except Exception as e:
                    print(f"   ❌ 선택자 '{selector}' 실패: {str(e)[:30]}...")
                    continue

            if not lecture_items:
                print("❌ 강의 목록 요소를 찾을 수 없음")
                print("🔍 페이지에서 사용 가능한 테이블 요소들:")
                try:
                    all_tables = driver.find_elements(By.TAG_NAME, "table")
                    print(f"   테이블 개수: {len(all_tables)}")
                    for i, table in enumerate(all_tables[:3]):
                        try:
                            rows = table.find_elements(By.TAG_NAME, "tr")
                            print(f"   테이블 {i+1}: {len(rows)}개 행")
                        except:
                            print(f"   테이블 {i+1}: 행 조회 실패")
                except Exception as e:
                    print(f"   테이블 요소 조회 실패: {e}")
                return []

            print(f"📋 {len(lecture_items)}개 요소에서 강의 정보 추출 시도")

            for i, item in enumerate(lecture_items):
                try:
                    print(f"📝 요소 {i+1} 분석 중...")

                    # 강의명 추출 (에브리타임 특화)
                    subject = ""
                    subject_selectors = [
                        'td:first-child',  # 에브리타임의 일반적인 구조
                        'td:nth-child(1)',
                        '.name', 
                        '.subject', 
                        '.title', 
                        '.course-name',
                        'a',
                        'span'
                    ]
                    for sel in subject_selectors:
                        try:
                            subject_elem = item.find_element(By.CSS_SELECTOR, sel)
                            subject = subject_elem.text.strip()
                            if subject and len(subject) > 1 and len(subject) < 50:  # 너무 긴 텍스트 제외
                                print(f"   ✅ 강의명: '{subject}' (선택자: {sel})")
                                break
                        except:
                            continue

                    if not subject:
                        # 첫 번째 td 요소에서 직접 추출 시도
                        try:
                            tds = item.find_elements(By.TAG_NAME, "td")
                            if tds and len(tds) > 0:
                                subject = tds[0].text.strip()
                                if subject and len(subject) > 1:
                                    print(f"   ✅ 강의명 (첫 번째 td): '{subject}'")
                        except:
                            pass
                    
                    if not subject:
                        print(f"   ❌ 강의명을 찾을 수 없음 - 요소 텍스트: '{item.text[:50]}...'")
                        continue

                    # 교수명 추출 (에브리타임 특화)
                    professor = "정보 없음"
                    professor_selectors = [
                        'td:nth-child(2)',  # 에브리타임의 일반적인 구조
                        'td:nth-child(3)',
                        '.professor', 
                        '.teacher', 
                        '.instructor', 
                        '.prof'
                    ]
                    for sel in professor_selectors:
                        try:
                            professor_elem = item.find_element(By.CSS_SELECTOR, sel)
                            professor = professor_elem.text.strip()
                            if professor and len(professor) > 1 and len(professor) < 20:
                                print(f"   ✅ 교수명: '{professor}' (선택자: {sel})")
                                break
                        except:
                            continue
                    
                    if professor == "정보 없음":
                        # 두 번째 td 요소에서 직접 추출 시도
                        try:
                            tds = item.find_elements(By.TAG_NAME, "td")
                            if tds and len(tds) > 1:
                                professor = tds[1].text.strip()
                                if professor and len(professor) > 1:
                                    print(f"   ✅ 교수명 (두 번째 td): '{professor}'")
                        except:
                            pass

                    # 평점 추출 (에브리타임 특화)
                    rating = 0.0
                    rating_selectors = [
                        'td:nth-child(4)',  # 에브리타임의 일반적인 구조
                        'td:nth-child(5)',
                        '.rating', 
                        '.score', 
                        '.rate', 
                        '.grade'
                    ]
                    for sel in rating_selectors:
                        try:
                            rating_elem = item.find_element(By.CSS_SELECTOR, sel)
                            rating_text = rating_elem.text.strip()
                            if rating_text:
                                # 숫자만 추출
                                import re
                                numbers = re.findall(r'\d+\.?\d*', rating_text)
                                if numbers:
                                    rating = float(numbers[0])
                                    if rating <= 5.0:  # 평점은 보통 5점 만점
                                        print(f"   ✅ 평점: {rating} (선택자: {sel})")
                                        break
                        except:
                            continue
                    
                    # 평점이 없으면 기본값 설정
                    if rating == 0.0:
                        rating = 3.0  # 기본 평점
                        print(f"   ⚠️ 평점 정보 없음 - 기본값 {rating} 설정")

                    # 강의 데이터 생성 (API 응답 형식에 맞춤)
                    lecture_data = {
                        'course_id': f"ET{len(lectures)+1:03d}",  # 에브리타임 강의 ID
                        'course_name': subject,
                        'professor': professor,
                        'department': '정보없음',  # 기본값
                        'semester': '2024-2',  # 기본값
                        'rating': rating,
                        'average_rating': rating,
                        'total_reviews': 0,
                        'reviews': [],
                        'details': {
                            'attendance': '정보 없음',
                            'exam': '정보 없음',
                            'assignment': '정보 없음',
                            'team_project': '정보 없음',
                            'credits': 3
                        },
                        'ai_summary': f"{subject} 강의입니다. {professor} 교수님이 담당하시며, 평점은 {rating}점입니다.",
                        'keywords': [subject, professor],
                        'tags': ['에브리타임', '강의평'],
                        'popularity_score': rating * 20,  # 평점 기반 인기도
                        'trend_direction': 'stable',
                        'source': 'evertime'
                    }

                    lectures.append(lecture_data)
                    print(f"   ✅ 강의 정보 수집 완료: {subject} - {professor} (평점: {rating})")

                except Exception as e:
                    print(f"강의 정보 추출 오류: {e}")
                    continue

        except Exception as e:
            print(f"검색 결과 처리 오류: {e}")

        print(f"✅ {len(lectures)}개 강의 발견")
        return lectures

    except Exception as e:
        print(f"❌ 검색 오류: {str(e)}")
        return []

@app.route('/api/search', methods=['GET'])
def api_search():
    """강의 검색 API"""
    keyword = request.args.get('keyword', '').strip()
    limit = int(request.args.get('limit', 50))  # 기본 50개
    offset = int(request.args.get('offset', 0))  # 기본 0부터 시작

    # 한글 인코딩 문제 해결
    original_keyword = keyword
    try:
        if '%' in keyword:
            keyword = urllib.parse.unquote(keyword)
            print(f"📝 URL 디코딩: '{original_keyword}' → '{keyword}'")

        if isinstance(keyword, bytes):
            keyword = keyword.decode('utf-8')
            print(f"📝 바이트 디코딩: bytes → '{keyword}'")

        if len(keyword.encode('utf-8')) != len(keyword):
            try:
                keyword = keyword.encode('latin-1').decode('utf-8')
                print(f"📝 UTF-8 재해석: '{original_keyword}' → '{keyword}'")
            except:
                pass

    except Exception as e:
        print(f"⚠️ 키워드 디코딩 오류: {e}")

    print(f"🔍 최종 검색 키워드: '{keyword}' (길이: {len(keyword)})")

    if not keyword:
        # 빈 검색어인 경우 모든 강의 반환 (개설과목 현황용)
        print(f"🔍 전체 강의 목록 요청 (limit={limit}, offset={offset})")
        results = get_all_courses_from_db(limit, offset)
        
        # 전체 개수 조회
        db = get_mongo_db()
        collection = db.courses
        total_count = collection.count_documents({})
        
        return jsonify({
            'keyword': '',
            'results': results,
            'count': len(results),
            'total_count': total_count,
            'has_more': (offset + limit) < total_count,
            'offset': offset,
            'limit': limit
        })

    # MongoDB에서 강의 검색 (우선순위)
    print(f"🔍 DB에서 강의 검색 시작: {keyword}")

    results = []

    try:
        # 먼저 MongoDB에서 검색
        print(f"🔍 DB 검색 시작: '{keyword}' (limit={limit}, offset={offset})")
        results = search_courses_from_db(keyword, limit, offset)
        print(f"🔍 DB 검색 결과: {len(results)}개")
        
        if results:
            print(f"✅ DB 검색 완료: {len(results)}개 강의 발견")
            # 전체 검색 결과 개수 조회
            db = get_mongo_db()
            collection = db.courses
            if keyword:
                query = {
                    "$or": [
                        {"course_name": {"$regex": keyword, "$options": "i"}},
                        {"professor": {"$regex": keyword, "$options": "i"}},
                        {"department": {"$regex": keyword, "$options": "i"}},
                        {"major": {"$regex": keyword, "$options": "i"}},
                        {"course_english_name": {"$regex": keyword, "$options": "i"}}
                    ]
                }
                total_count = collection.count_documents(query)
            else:
                total_count = collection.count_documents({})
            
            return jsonify({
                'keyword': keyword,
                'results': results,
                'count': len(results),
                'total_count': total_count,
                'has_more': (offset + limit) < total_count,
                'offset': offset,
                'limit': limit
            })
        else:
            # DB 검색 실패 시 샘플 데이터 사용
            print("⚠️ DB 검색 결과 없음 - 샘플 데이터로 대체")
            results = search_courses_by_keyword(keyword)
            print(f"✅ 샘플 데이터에서 {len(results)}개 강의 발견")

        if len(results) == 0:
            print("⚠️ 검색 결과 없음 - 기본 메시지 반환")
            results = [{
                'course_name': f'{keyword} (검색 결과 없음)',
                'professor': '해당 강의를 찾을 수 없습니다',
                'rating': 0.0,
                'reviews': [
                    {
                        'rating': 0.0,
                        'comment': f'"{keyword}"에 대한 검색 결과가 없습니다. 다른 키워드로 검색해보세요.',
                        'semester': '검색 결과 없음'
                    }
                ],
                'details': {
                    'attendance': '정보 없음',
                    'exam': '정보 없음',
                    'assignment': '정보 없음',
                    'teamProject': '정보 없음'
                }
            }]
        else:
            # 실제 데이터에 리뷰 정보 추가
            for lecture in results:
                if not lecture.get('reviews') or len(lecture['reviews']) == 0:
                    lecture['reviews'] = [
                        {
                            'rating': 0.0,
                            'comment': f'{lecture.get("course_name", "강의")} 강의에 대한 리뷰가 아직 없습니다.',
                            'semester': '리뷰 없음'
                        }
                    ]

                if lecture['reviews'] and lecture['reviews'][0]['rating'] > 0:
                    total_rating = sum(review['rating'] for review in lecture['reviews'])
                    lecture['rating'] = round(total_rating / len(lecture['reviews']), 1)
                else:
                    lecture['rating'] = 0.0

    except Exception as e:
        print(f"❌ 크롤링 오류: {str(e)}")
        # 오류 발생 시 샘플 데이터 반환
        results = search_courses_by_keyword(keyword)

    return jsonify({
        'keyword': keyword,
        'results': results,
        'count': len(results)
    })


@app.route('/api/software-courses', methods=['GET'])
def api_software_courses():
    """엑셀에서 소프트웨어학과 과목 목록 반환"""
    keyword = request.args.get('keyword', '').strip()
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    force_reload = request.args.get('refresh', 'false').lower() == 'true'

    try:
        courses = load_software_courses_from_excel(force_reload=force_reload)
    except FileNotFoundError as e:
        print(f"❌ 소프트웨어 과목 데이터 파일 없음: {e}")
        return jsonify({'error': 'course_file_not_found', 'message': str(e)}), 404
    except Exception as e:
        print(f"❌ 소프트웨어 과목 로드 오류: {e}")
        return jsonify({'error': 'course_load_failed', 'message': str(e)}), 500

    filtered = courses
    if keyword:
        keyword_lower = keyword.lower()
        filtered = [
            course for course in courses
            if any(
                keyword_lower in (course.get(field, '') or '').lower()
                for field in ('course_name', 'professor', 'course_code', 'course_english_name')
            )
        ]

    total_count = len(filtered)
    results = filtered[offset:offset + limit]
    has_more = (offset + len(results)) < total_count

    return jsonify({
        'keyword': keyword,
        'results': results,
        'count': len(results),
        'total_count': total_count,
        'has_more': has_more,
        'offset': offset,
        'limit': limit,
        'source': 'excel_2025_2'
    })


@app.route('/')
def index():
    """메인 페이지"""
    return '''
    <h1>에브리타임 강의평 크롤링 API</h1>
    <p>실제 에브리타임 사이트에서 강의 정보를 크롤링합니다.</p>

    <h2>사용법:</h2>
    <ul>
        <li><code>GET /api/search?keyword=강의명</code> - 강의 검색</li>
    </ul>
    '''

@app.route('/api/health/db', methods=['GET'])
def health_db():
    """MongoDB 연결 헬스체크"""
    try:
        db = get_mongo_db()
        result = db.command('ping')
        return jsonify({'ok': True, 'result': result}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

if __name__ == '__main__':
    import atexit
    import signal

    atexit.register(cleanup_driver)

    def signal_handler(sig, frame):
        print("\n🛑 서버 종료 신호 감지")
        cleanup_driver()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("🚀 에브리타임 강의평 크롤링 API 서버 시작")
    print("📍 http://34.58.143.2:5002")

    try:
        app.run(debug=True, host='0.0.0.0', port=5002)
    finally:
        cleanup_driver()
@app.route('/api/courses/from-pinecone', methods=['GET'])
def get_courses_from_pinecone():
    """Pinecone에서 강의 목록 가져오기 (강의평 기반으로 요약)"""
    try:
        from pinecone import Pinecone
        from collections import defaultdict
        
        PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
        PINECONE_INDEX = os.getenv('PINECONE_INDEX', 'courses-dev')
        
        if not PINECONE_API_KEY:
            return jsonify({'success': False, 'error': 'PINECONE_API_KEY not set'}), 500
        
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX)
        
        # 모든 강의평 벡터 가져오기
        results = index.query(
            vector=[0.0] * 768,
            top_k=10000,
            include_metadata=True
        )
        
        # 강의별로 그룹화
        courses_dict = defaultdict(lambda: {
            'reviews': [],
            'ratings': [],
            'semesters': set(),
            'professors': set()
        })
        
        for match in results.matches:
            meta = match.metadata
            if not meta:
                continue
                
            course_name = meta.get('course_name', 'Unknown')
            professor = meta.get('professor', 'Unknown')
            rating = meta.get('rating', 0)
            semester = meta.get('semester', '')
            text = meta.get('text', '')
            
            key = f"{course_name}_{professor}"
            courses_dict[key]['course_name'] = course_name
            courses_dict[key]['professor'] = professor
            courses_dict[key]['department'] = meta.get('department', '소프트웨어학과')
            courses_dict[key]['reviews'].append(text)
            courses_dict[key]['ratings'].append(float(rating))
            courses_dict[key]['semesters'].add(semester)
            courses_dict[key]['professors'].add(professor)
        
        # 강의 목록 생성
        courses = []
        for idx, (key, data) in enumerate(courses_dict.items(), 1):
            avg_rating = sum(data['ratings']) / len(data['ratings']) if data['ratings'] else 0
            review_count = len(data['reviews'])
            
            # 최근 강의평 3개로 AI 요약 생성
            recent_reviews = data['reviews'][:3]
            ai_summary = ' '.join(recent_reviews[:2])[:150] + '...' if recent_reviews else '강의평 정보 없음'
            
            # 태그 추출 (간단한 키워드 기반)
            tags = []
            all_text = ' '.join(data['reviews'])
            if '팀플' in all_text or '팀프로젝트' in all_text:
                if '없' in all_text or '노팀플' in all_text:
                    tags.append('노팀플')
                else:
                    tags.append('팀플있음')
            if '과제' in all_text:
                if '많' in all_text:
                    tags.append('과제많음')
                else:
                    tags.append('적당한과제')
            if '꿀강' in all_text or '쉬' in all_text:
                tags.append('쉬움')
            if '성적' in all_text and '잘' in all_text:
                tags.append('성적잘줌')
            
            courses.append({
                'id': idx,
                'courseCode': f'SCE{300 + idx}',
                'name': data['course_name'],
                'professor': data['professor'],
                'department': data['department'],
                'credits': 3,
                'rating': round(avg_rating, 1),
                'reviewCount': review_count,
                'popularity': min(100, review_count * 3),
                'tags': tags[:4] if tags else ['강의평있음'],
                'semester': max(data['semesters']) if data['semesters'] else '2024-2',
                'timeSlot': '-',
                'room': '-',
                'aiSummary': ai_summary,
                'sentiment': int(avg_rating * 20),
                'difficulty': 3,
                'workload': 3,
                'gradeGenerosity': int(avg_rating),
                'bookmarked': False,
                'trend': 'up' if avg_rating >= 4.0 else 'down',
                'keywords': []
            })
        
        # 평점 높은 순으로 정렬
        courses.sort(key=lambda x: x['rating'], reverse=True)
        
        return jsonify({
            'success': True,
            'courses': courses,
            'total': len(courses)
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500
