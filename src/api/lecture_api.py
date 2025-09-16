#!/usr/bin/env python3
"""
에브리타임 크롤링 API 서버 - 수정된 버전
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import urllib.parse
import time
import os
from dotenv import load_dotenv
import sys
import os
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

def setup_driver():
    """Chrome 웹드라이버 설정"""
    chrome_options = Options()
    
    # 안정성을 위한 Chrome 옵션
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # macOS에서 Chrome 실행 파일 경로 명시
    chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    try:
        driver_path = ChromeDriverManager().install()
        if "THIRD_PARTY_NOTICES.chromedriver" in driver_path:
            driver_path = driver_path.replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver")
    
        # ChromeDriver 권한 확인
        import stat
        import os
        if not os.access(driver_path, os.X_OK):
            os.chmod(driver_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            print(f"✅ ChromeDriver 권한 설정: {driver_path}")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 타임아웃 설정
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        
        print(f"✅ Chrome 드라이버 설정 완료: {driver.session_id}")
        return driver
        
    except Exception as e:
        print(f"❌ ChromeDriver 설정 오류: {e}")
        raise

def get_or_create_driver():
    """전역 드라이버 가져오기 또는 생성"""
    global global_driver, login_time
    
    if global_driver is None:
        print("🔄 새 드라이버 세션 생성 중...")
        global_driver = setup_driver()
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
    """에브리타임 로그인"""
    try:
        print("🔐 에브리타임 로그인 중...")
        
        user_id = os.getenv("EVERYTIME_ID")
        user_password = os.getenv("EVERYTIME_PASSWORD")
        print(f"🔑 사용할 ID: {user_id}")
        
        driver.get("https://everytime.kr/login")
        time.sleep(3)
        
        # ID 입력
        try:
            id_input = driver.find_element(By.NAME, "userid")
        except:
            id_input = driver.find_element(By.NAME, "id")
        id_input.send_keys(user_id)
        
        # 비밀번호 입력
        pw_input = driver.find_element(By.NAME, "password")
        pw_input.send_keys(user_password)
        
        # 로그인 버튼 클릭
        login_btn = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        login_btn.click()
        
        print("🤖 reCAPTCHA가 있을 수 있습니다. 수동으로 해결해주세요...")
        print("⏰ 60초 대기 중... (reCAPTCHA 해결 후 자동 진행)")
        
        # reCAPTCHA 해결을 위해 더 긴 대기 시간
        for i in range(60):
            time.sleep(1)
            
            try:
                current_url = driver.current_url
                
                if "everytime.kr" in current_url and "login" not in current_url.lower():
                    print("✅ 로그인 성공!")
                    return True
                
                try:
                    alert = driver.switch_to.alert
                    alert_text = alert.text
                    alert.accept()
                    print(f"❌ 로그인 실패 - Alert: {alert_text}")
                    return False
                except:
                    pass
        
            except Exception as e:
                print(f"⚠️ URL 체크 오류: {e}")
                continue
        
        print("⏰ 시간 초과 - 로그인 확인 불가")
        return False
            
    except Exception as e:
        print(f"❌ 로그인 오류: {str(e)}")
        return False

def search_lecture(driver, keyword):
    """강의 검색"""
    try:
        print(f"🔍 '{keyword}' 검색 중...")
        
        current_url = driver.current_url
        if "lecture" not in current_url:
            print("📍 강의실 페이지로 이동...")
            driver.get("https://everytime.kr/lecture")
            time.sleep(3)
        else:
            print("📍 이미 강의실 페이지에 있음")
            time.sleep(1)
        
        # 검색창 찾기
        search_input = None
        selectors = [
            'input[placeholder*="과목"]',
            'input[name="keyword"]',
            'input[type="text"]',
            '#keyword'
        ]
        
        for selector in selectors:
            try:
                search_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                print(f"✅ 검색창 발견: {selector}")
                break
            except:
                continue
                
        if not search_input:
            print("❌ 검색창을 찾을 수 없음")
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
            
            page_source = driver.page_source
            print(f"📄 페이지 길이: {len(page_source)} 문자")
            
            # 여러 선택자로 강의 목록 찾기 시도
            selectors = [
                '.item',
                '.lecture',
                'tr',
                '.list tr',
                '[class*="item"]',
                '.course',
                'li'
            ]
            
            lecture_items = []
            for selector in selectors:
                try:
                    items = driver.find_elements(By.CSS_SELECTOR, selector)
                    if items and len(items) > 1:
                        print(f"✅ 선택자 '{selector}'로 {len(items)}개 요소 발견")
                        lecture_items = items[:10]
                        break
                except:
                    continue
            
            if not lecture_items:
                print("❌ 강의 목록 요소를 찾을 수 없음")
                return []
            
            print(f"📋 {len(lecture_items)}개 요소에서 강의 정보 추출 시도")
            
            for i, item in enumerate(lecture_items):
                try:
                    print(f"📝 요소 {i+1} 분석 중...")
                    
                    # 강의명 추출
                    subject = ""
                    subject_selectors = ['.name', '.subject', '.title', 'td:first-child', '.course-name']
                    for sel in subject_selectors:
                        try:
                            subject_elem = item.find_element(By.CSS_SELECTOR, sel)
                            subject = subject_elem.text.strip()
                            if subject and len(subject) > 1:
                                print(f"   ✅ 강의명: '{subject}' (선택자: {sel})")
                                break
                        except:
                            continue
                    
                    if not subject:
                        print(f"   ❌ 강의명을 찾을 수 없음 - 요소 텍스트: '{item.text[:50]}...'")
                        continue
                    
                    # 교수명 추출
                    professor = "정보 없음"
                    professor_selectors = ['.professor', '.teacher', '.instructor', 'td:nth-child(2)', '.prof']
                    for sel in professor_selectors:
                        try:
                            professor_elem = item.find_element(By.CSS_SELECTOR, sel)
                            professor = professor_elem.text.strip()
                            if professor:
                                print(f"   ✅ 교수명: '{professor}' (선택자: {sel})")
                                break
                        except:
                            continue
                    
                    # 평점 추출
                    rating = 0.0
                    rating_selectors = ['.rating', '.score', '.rate', '.grade']
                    for sel in rating_selectors:
                        try:
                            rating_elem = item.find_element(By.CSS_SELECTOR, sel)
                            rating_text = rating_elem.text.strip()
                            if rating_text:
                                rating = float(rating_text)
                                print(f"   ✅ 평점: {rating} (선택자: {sel})")
                                break
                        except:
                            continue
                    
                    # 기본 정보만 수집
                    lectures.append({
                        'subject': subject,
                        'professor': professor,
                        'rating': 0.0,
                        'reviewCount': 0,
                        'reviews': [],
                        'details': {
                            'attendance': '정보 없음',
                            'exam': '정보 없음',
                            'assignment': '정보 없음',
                            'teamProject': '정보 없음'
                        }
                    })
                    
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
        return jsonify({'error': '검색어를 입력해주세요'}), 400
    
    # 실제 에브리타임 크롤링
    print(f"🔍 실제 크롤링 시작: {keyword}")
    
    results = []
    
    try:
        if ensure_logged_in():
            driver = get_or_create_driver()
            results = search_lecture(driver, keyword)
            print(f"✅ 실제 크롤링 완료: {len(results)}개 강의 발견")
            
            if results:
                cached_search_results[keyword] = results
                print(f"💾 검색 결과 캐시 저장: {keyword}")
            
            if len(results) == 0:
                print("⚠️ 크롤링 결과 없음 - 테스트 데이터 추가")
                results = [{
                    'subject': f'{keyword} (검색 결과 없음)',
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
                for lecture in results:
                    if not lecture.get('reviews') or len(lecture['reviews']) == 0:
                        lecture['reviews'] = [
                            {
                                'rating': 0.0,
                                'comment': f'{lecture["subject"]} 강의에 대한 리뷰가 아직 없습니다.',
                                'semester': '리뷰 없음'
                            }
                        ]
                    
                    if lecture['reviews'] and lecture['reviews'][0]['rating'] > 0:
                        total_rating = sum(review['rating'] for review in lecture['reviews'])
                        lecture['rating'] = round(total_rating / len(lecture['reviews']), 1)
                    else:
                        lecture['rating'] = 0.0
        else:
            print("❌ 로그인 실패")
            return jsonify({'error': '에브리타임 로그인에 실패했습니다'}), 500
            
    except Exception as e:
        print(f"❌ 실제 크롤링 오류: {str(e)}")
        return jsonify({'error': f'크롤링 중 오류 발생: {str(e)}'}), 500
    
    return jsonify({
        'keyword': keyword,
        'results': results,
        'count': len(results)
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
    print("📍 http://localhost:5002")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5002)
    finally:
        cleanup_driver()
