#!/usr/bin/env python3
"""
에브리타임 특정 강의 정보 가져오기
메인 → 강의실 → 검색 → 실전코딩 1
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def login_to_everytime(driver):
    """에브리타임 로그인"""
    print("🔐 에브리타임 로그인 중...")
    
    # 로그인 페이지로 이동
    driver.get("https://everytime.kr/login")
    time.sleep(5)  # 더 긴 대기 시간
    
    print(f"📍 현재 URL: {driver.current_url}")
    
    # 환경변수에서 계정 정보 가져오기
    username = os.getenv('EVERYTIME_ID')
    password = os.getenv('EVERYTIME_PASSWORD')
    
    if not username or not password:
        raise ValueError("EVERYTIME_ID와 EVERYTIME_PASSWORD 환경변수를 설정해주세요.")
    
    print(f"✅ 계정 정보 확인됨: {username}")
    
    # 로그인 폼 요소 찾기
    wait = WebDriverWait(driver, 15)
    
    # ID 입력 필드 찾기 (여러 선택자 시도)
    username_input = None
    selectors = [
        'input[name="id"]',
        'input[name="userid"]', 
        'input[type="text"]', 
        '#userid', 
        '#id'
    ]
    
    for selector in selectors:
        try:
            username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            print(f"✅ ID 입력 필드 발견: {selector}")
            break
        except:
            print(f"❌ 선택자 {selector} 실패")
            continue
    
    if not username_input:
        print("❌ ID 입력 필드를 찾을 수 없습니다.")
        return False
    
    # 비밀번호 입력 필드 찾기
    password_input = None
    pwd_selectors = [
        'input[name="password"]', 
        'input[type="password"]', 
        '#password'
    ]
    
    for selector in pwd_selectors:
        try:
            password_input = driver.find_element(By.CSS_SELECTOR, selector)
            print(f"✅ 비밀번호 입력 필드 발견: {selector}")
            break
        except:
            print(f"❌ 비밀번호 선택자 {selector} 실패")
            continue
    
    if not password_input:
        print("❌ 비밀번호 입력 필드를 찾을 수 없습니다.")
        return False
    
    # 로그인 정보 입력
    print("📝 로그인 정보 입력 중...")
    username_input.clear()
    username_input.send_keys(username)
    time.sleep(2)
    
    password_input.clear()
    password_input.send_keys(password)
    time.sleep(2)
    
    # 로그인 버튼 찾기 및 클릭
    login_button = None
    button_selectors = [
        'input[type="submit"]', 
        'button[type="submit"]', 
        '.login-btn', 
        '#login-btn'
    ]
    
    for selector in button_selectors:
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, selector)
            print(f"✅ 로그인 버튼 발견: {selector}")
            break
        except:
            continue
    
    if not login_button:
        print("❌ 로그인 버튼을 찾을 수 없습니다.")
        return False
    
    # 로그인 버튼 클릭
    print("🖱️ 로그인 버튼 클릭...")
    login_button.click()
    time.sleep(3)
    
    # Alert 처리
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        print(f"⚠️ Alert 발생: {alert_text}")
        alert.accept()
        print("❌ 로그인 실패 - 에브리타임에서 오류 메시지 표시")
        return False
    except:
        # Alert가 없으면 정상적으로 진행
        pass
    
    time.sleep(5)  # 추가 대기
    
    # 로그인 성공 확인
    current_url = driver.current_url
    print(f"📍 로그인 후 URL: {current_url}")
    
    if "login" not in current_url.lower() and "everytime.kr" in current_url:
        print("✅ 로그인 성공!")
        return True
    else:
        print("❌ 로그인 실패!")
        return False

def navigate_to_lecture_room(driver):
    """강의실로 이동"""
    print("🏛️ 강의실 페이지로 이동 중...")
    
    wait = WebDriverWait(driver, 15)
    
    try:
        # 메인 네비게이션에서 "강의실" 찾기
        # 여러 가능한 선택자 시도
        lecture_selectors = [
            'a[href="/lecture"]',
            'a:contains("강의실")',
            '.nav a[href*="lecture"]',
            'nav a[href="/lecture"]'
        ]
        
        lecture_link = None
        for selector in lecture_selectors:
            try:
                if 'contains' in selector:
                    # 텍스트로 링크 찾기
                    links = driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        if "강의실" in link.text:
                            lecture_link = link
                            print(f"✅ 강의실 링크 발견 (텍스트): {link.text}")
                            break
                else:
                    lecture_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"✅ 강의실 링크 발견: {selector}")
                
                if lecture_link:
                    break
            except:
                continue
        
        if not lecture_link:
            print("❌ 강의실 링크를 찾을 수 없습니다.")
            return False
        
        # 강의실 클릭
        lecture_link.click()
        time.sleep(3)
        
        print(f"📍 현재 URL: {driver.current_url}")
        return True
        
    except Exception as e:
        print(f"❌ 강의실 이동 중 오류: {str(e)}")
        return False

def search_lecture(driver, search_term="실전코딩 1"):
    """강의 검색"""
    print(f"🔍 '{search_term}' 검색 중...")
    
    wait = WebDriverWait(driver, 15)
    
    try:
        # 검색창 찾기
        search_selectors = [
            'input[placeholder*="과목"]',
            'input[placeholder*="교수"]',
            'input[placeholder*="검색"]',
            'input[type="text"]',
            '.search input',
            '#search'
        ]
        
        search_input = None
        for selector in search_selectors:
            try:
                search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                print(f"✅ 검색창 발견: {selector}")
                break
            except:
                continue
        
        if not search_input:
            print("❌ 검색창을 찾을 수 없습니다.")
            return False
        
        # 검색어 입력
        search_input.clear()
        search_input.send_keys(search_term)
        time.sleep(1)
        
        # Enter 키 또는 검색 버튼 클릭
        search_input.send_keys(Keys.ENTER)
        time.sleep(3)
        
        print("✅ 검색 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 검색 중 오류: {str(e)}")
        return False

def click_lecture_result(driver, lecture_name="실전코딩"):
    """검색 결과에서 강의 클릭"""
    print(f"🎯 '{lecture_name}' 강의 클릭 중...")
    
    wait = WebDriverWait(driver, 15)
    
    try:
        # 검색 결과에서 강의 찾기
        time.sleep(2)  # 검색 결과 로딩 대기
        
        # 여러 방법으로 강의 링크 찾기
        lecture_elements = []
        
        # 방법 1: 텍스트로 찾기
        try:
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for link in all_links:
                if lecture_name in link.text:
                    lecture_elements.append(link)
                    print(f"✅ 강의 링크 발견 (텍스트): {link.text}")
        except:
            pass
        
        # 방법 2: div나 다른 요소에서 찾기
        try:
            all_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{lecture_name}')]")
            for elem in all_elements:
                if elem.tag_name in ['a', 'div', 'span', 'li']:
                    lecture_elements.append(elem)
                    print(f"✅ 강의 요소 발견: {elem.tag_name} - {elem.text[:50]}")
        except:
            pass
        
        if not lecture_elements:
            print("❌ 강의를 찾을 수 없습니다.")
            print("현재 페이지 소스 일부:")
            print(driver.page_source[:1000])
            return False
        
        # 첫 번째 결과 클릭
        first_result = lecture_elements[0]
        first_result.click()
        time.sleep(3)
        
        print("✅ 강의 클릭 완료!")
        print(f"📍 현재 URL: {driver.current_url}")
        return True
        
    except Exception as e:
        print(f"❌ 강의 클릭 중 오류: {str(e)}")
        return False

def get_lecture_detailed_info(driver):
    """강의 상세 정보 수집"""
    print("📋 강의 상세 정보 수집 중...")
    
    try:
        # 페이지 로딩 대기
        time.sleep(3)
        
        # 페이지 HTML 수집
        page_html = driver.page_source
        current_url = driver.current_url
        
        print(f"✅ 정보 수집 완료!")
        print(f"📍 현재 URL: {current_url}")
        print(f"📄 HTML 크기: {len(page_html):,}자")
        
        # 파일로 저장
        os.makedirs('data', exist_ok=True)
        
        # 강의 상세 HTML 저장
        detail_file_path = 'data/lecture_detail.html'
        with open(detail_file_path, 'w', encoding='utf-8') as f:
            f.write(page_html)
        
        print(f"💾 HTML 파일 저장: {detail_file_path}")
        
        # HTML 미리보기
        print("\n" + "="*60)
        print("📖 강의 상세 페이지 HTML 미리보기 (처음 1000자)")
        print("="*60)
        print(page_html[:1000])
        print("="*60)
        print(f"... (총 {len(page_html):,}자 중 처음 1000자만 표시)")
        
        return True
        
    except Exception as e:
        print(f"❌ 정보 수집 중 오류: {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    print("🚀 에브리타임 실전코딩 1 강의 정보 수집 시작")
    
    driver = None
    try:
        # Chrome 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1200,800")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--disable-extensions")
        
        # macOS에서 Chrome 실행 파일 경로 명시
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        # ChromeDriver 설정
        driver_path = ChromeDriverManager().install()
        if "THIRD_PARTY_NOTICES.chromedriver" in driver_path:
            driver_path = driver_path.replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome 브라우저가 시작되었습니다.")
        
        # 단계별 실행
        if not login_to_everytime(driver):
            return False
        
        if not navigate_to_lecture_room(driver):
            return False
        
        if not search_lecture(driver, "실전코딩 1"):
            return False
        
        if not click_lecture_result(driver, "실전코딩"):
            return False
        
        if not get_lecture_detailed_info(driver):
            return False
        
        # 브라우저를 잠시 열어둠 (확인용)
        print("\n⏰ 10초 후 브라우저가 종료됩니다. (페이지 확인 시간)")
        time.sleep(10)
        
        return True
        
    except Exception as e:
        print(f"❌ 전체 프로세스 중 오류 발생: {str(e)}")
        return False
        
    finally:
        if driver:
            print("🔒 브라우저 종료 중...")
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    print("=" * 60)
    print("에브리타임 실전코딩 1 강의 정보 수집기")
    print("=" * 60)
    
    success = main()
    
    print("=" * 60)
    if success:
        print("🎯 결과: 강의 정보 수집 성공!")
        print("📁 저장된 파일: data/lecture_detail.html")
    else:
        print("💥 결과: 강의 정보 수집 실패!")
    print("=" * 60)
