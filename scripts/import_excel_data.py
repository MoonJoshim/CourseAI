#!/usr/bin/env python3
"""
Excel 파일에서 강의 데이터를 읽어서 MongoDB에 저장하는 스크립트
"""

import pandas as pd
import sys
import os
from datetime import datetime
from pathlib import Path

# 프로젝트 루트 경로 추가
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from backend.api import get_mongo_db

COURSE_FILE = PROJECT_ROOT / "course" / "2025-2.xlsx"

def clean_excel_data():
    """Excel 파일에서 강의 데이터를 정리"""
    print("📊 Excel 파일 읽는 중...")
    
    if not COURSE_FILE.exists():
        raise FileNotFoundError(f"강의 데이터 파일을 찾을 수 없습니다: {COURSE_FILE}")

    # Excel 파일 읽기
    df = pd.read_excel(COURSE_FILE)
    
    # 첫 번째 행은 제목이므로 제거하고, 두 번째 행을 컬럼명으로 사용
    df_clean = df.iloc[2:].copy()  # 3번째 행부터 데이터
    df_clean.columns = df.iloc[1].tolist()  # 2번째 행을 컬럼명으로 설정
    
    # 컬럼명 정리 (줄바꿈 문자 제거)
    df_clean.columns = [col.replace('\n', '') for col in df_clean.columns]
    
    # NaN 값이 있는 행 제거
    df_clean = df_clean.dropna(subset=['과목명', '담당교수'])
    
    print(f"✅ 총 {len(df_clean)}개의 강의 데이터를 찾았습니다.")
    
    return df_clean

def transform_to_course_schema(df):
    """데이터를 MongoDB 스키마에 맞게 변환"""
    print("🔄 데이터 변환 중...")
    
    courses = []
    
    for idx, row in df.iterrows():
        try:
            # 기본 강의 정보
            course_data = {
                'course_id': f"2025-2-{int(row['순번']):04d}",
                'course_name': str(row['과목명']).strip(),
                'professor': str(row['담당교수']).strip(),
                'department': str(row['개설학부']).strip(),
                'major': str(row['개설전공']).strip(),
                'semester': '2025-2',
                'credits': int(row['학점']) if pd.notna(row['학점']) else 3,
                'hours': int(row['시간']) if pd.notna(row['시간']) else 3,
                'course_code': str(row['교과목코드']).strip() if pd.notna(row['교과목코드']) else '',
                'subject_id': str(row['과목ID']).strip() if pd.notna(row['과목ID']) else '',
                'course_type': str(row['학수구분']).strip() if pd.notna(row['학수구분']) else '',
                'subject_type': str(row['교과구분']).strip() if pd.notna(row['교과구분']) else '',
                'english_lecture': str(row['영어강의']).strip() if pd.notna(row['영어강의']) else 'N',
                'english_grade': str(row['영어강의등급']).strip() if pd.notna(row['영어강의등급']) else '',
                'international_only': str(row['유학생전용']).strip() if pd.notna(row['유학생전용']) else 'N',
                'intensive_course': str(row['윤강여부']).strip() if pd.notna(row['윤강여부']) else 'N',
                'affiliation': str(row['소속']).strip() if pd.notna(row['소속']) else '',
                'lecture_time': str(row['강의시간명']).strip() if pd.notna(row['강의시간명']) else '',
                'lecture_method': str(row['수업방식']).strip() if pd.notna(row['수업방식']) else '',
                'course_characteristics': str(row['과목특성']).strip() if pd.notna(row['과목특성']) else '',
                'course_english_name': str(row['과목영문명']).strip() if pd.notna(row['과목영문명']) else '',
                'target_grade': str(row['수강대상학년']).strip() if pd.notna(row['수강대상학년']) else '',
                'class_method': str(row['분반별수업방식']).strip() if pd.notna(row['분반별수업방식']) else '',
                'class_type': str(row['분반별수업방법']).strip() if pd.notna(row['분반별수업방법']) else '',
                
                # 기본값 설정
                'rating': 0.0,
                'average_rating': 0.0,
                'total_reviews': 0,
                'reviews': [],
                'details': {
                    'attendance': '정보 없음',
                    'exam': '정보 없음',
                    'assignment': '정보 없음',
                    'team_project': '정보 없음',
                    'credits': int(row['학점']) if pd.notna(row['학점']) else 3,
                    'time_slot': str(row['강의시간명']).strip() if pd.notna(row['강의시간명']) else '',
                    'room': '정보 없음',
                    'lecture_method': str(row['수업방식']).strip() if pd.notna(row['수업방식']) else ''
                },
                'ai_summary': f"{str(row['과목명']).strip()} 강의입니다. {str(row['담당교수']).strip()} 교수님이 담당하시며, {int(row['학점']) if pd.notna(row['학점']) else 3}학점 과목입니다.",
                'keywords': [str(row['과목명']).strip(), str(row['담당교수']).strip()],
                'tags': ['2025-2학기', str(row['개설학부']).strip()],
                'popularity_score': 50.0,
                'trend_direction': 'stable',
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'last_crawled_at': datetime.now(),
                'source': 'excel_2025_2'
            }
            
            courses.append(course_data)
            
        except Exception as e:
            print(f"⚠️ 행 {idx} 처리 중 오류: {e}")
            continue
    
    print(f"✅ {len(courses)}개 강의 데이터 변환 완료")
    return courses

def save_to_mongodb(courses):
    """MongoDB에 강의 데이터 저장"""
    print("💾 MongoDB에 데이터 저장 중...")
    
    try:
        # MongoDB 연결
        db = get_mongo_db()
        collection = db.courses
        
        # 기존 2025-2학기 데이터 삭제
        result = collection.delete_many({'semester': '2025-2', 'source': 'excel_2025_2'})
        print(f"🗑️ 기존 2025-2학기 데이터 {result.deleted_count}개 삭제")
        
        # 새 데이터 삽입
        if courses:
            result = collection.insert_many(courses)
            print(f"✅ {len(result.inserted_ids)}개 강의 데이터 저장 완료")
            
            # 인덱스 생성
            collection.create_index("course_id", unique=True)
            collection.create_index("course_name")
            collection.create_index("professor")
            collection.create_index("department")
            collection.create_index("semester")
            collection.create_index("average_rating")
            collection.create_index([("course_name", "text"), ("professor", "text")])
            
            print("📊 인덱스 생성 완료")
            
        else:
            print("❌ 저장할 데이터가 없습니다.")
            
    except Exception as e:
        print(f"❌ MongoDB 저장 오류: {e}")
        return False
    
    return True

def main():
    """메인 실행 함수"""
    print("🚀 Excel 데이터 MongoDB 저장 시작")
    print("=" * 50)
    
    try:
        # 1. Excel 데이터 정리
        df = clean_excel_data()
        
        # 2. 데이터 변환
        courses = transform_to_course_schema(df)
        
        # 3. MongoDB 저장
        success = save_to_mongodb(courses)
        
        if success:
            print("=" * 50)
            print("🎉 Excel 데이터 MongoDB 저장 완료!")
            print(f"📊 총 {len(courses)}개 강의 데이터가 저장되었습니다.")
        else:
            print("❌ 데이터 저장에 실패했습니다.")
            
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
