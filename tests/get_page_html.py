#!/usr/bin/env python3
"""
에브리타임 강의평 페이지 HTML 가져오기
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def login_to_everytime(driver):
    """에브리타임 로그인"""
    print("🔐 에브리타임 로그인 중...")
    
    # 로그인 페이지로 이동
    driver.get("https://everytime.kr/login")
    time.sleep(3)
    
    # 환경변수에서 계정 정보 가져오기
    username = os.getenv('EVERYTIME_ID')
    password = os.getenv('EVERYTIME_PASSWORD')
    
    if not username or not password:
        raise ValueError("EVERYTIME_ID와 EVERYTIME_PASSWORD 환경변수를 설정해주세요.")
    
    # 로그인 폼 요소 찾기
    wait = WebDriverWait(driver, 15)
    
    # ID 입력
    username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="id"]')))
    username_input.clear()
    username_input.send_keys(username)
    
    # 비밀번호 입력
    password_input = driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')
    password_input.clear()
    password_input.send_keys(password)
    
    # 로그인 버튼 클릭
    login_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
    login_button.click()
    time.sleep(3)
    
    # Alert 처리
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        print(f"⚠️ Alert 발생: {alert_text}")
        alert.accept()
        return False
    except:
        pass
    
    # 로그인 성공 확인
    current_url = driver.current_url
    if "login" not in current_url.lower() and "everytime.kr" in current_url:
        print("✅ 로그인 성공!")
        return True
    else:
        print("❌ 로그인 실패!")
        return False

def get_lecture_page_html():
    """강의평 페이지 HTML 가져오기"""
    print("🚀 에브리타임 강의평 페이지 HTML 가져오기 시작")
    
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
        
        # 로그인 수행
        if not login_to_everytime(driver):
            return False
        
        print("🌐 강의평 페이지로 이동 중...")
        
        # 강의평 메인 페이지로 이동
        driver.get("https://everytime.kr/lecture")
        time.sleep(5)
        
        current_url = driver.current_url
        print(f"📍 현재 URL: {current_url}")
        
        # 페이지 HTML 가져오기
        print("📄 페이지 HTML 수집 중...")
        page_html = driver.page_source
        
        print(f"✅ HTML 수집 완료! 총 {len(page_html):,}자")
        
        # data 디렉토리가 없으면 생성
        os.makedirs('data', exist_ok=True)
        
        # HTML을 파일로 저장
        html_file_path = 'data/raw_page.html'
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(page_html)
        
        print(f"💾 HTML 파일 저장 완료: {html_file_path}")
        
        # HTML 앞부분 출력 (1000자)
        print("\n" + "="*60)
        print("📖 HTML 미리보기 (처음 1000자)")
        print("="*60)
        print(page_html[:1000])
        print("="*60)
        print(f"... (총 {len(page_html):,}자 중 처음 1000자만 표시)")
        
        # 브라우저를 잠시 열어둠 (페이지 확인용)
        print("\n⏰ 5초 후 브라우저가 종료됩니다. (페이지 확인 시간)")
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
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
    print("에브리타임 강의평 페이지 HTML 수집기")
    print("=" * 60)
    
    success = get_lecture_page_html()
    
    print("=" * 60)
    if success:
        print("🎯 결과: HTML 수집 성공!")
        print("📁 저장된 파일: data/raw_page.html")
    else:
        print("💥 결과: HTML 수집 실패!")
    print("=" * 60)
