#!/usr/bin/env python3
"""
간단한 에브리타임 로그인 테스트
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

def test_evertime_login():
    """에브리타임 로그인 테스트"""
    print("🚀 에브리타임 로그인 테스트 시작")
    
    # 환경변수 확인
    username = os.getenv('EVERYTIME_ID')
    password = os.getenv('EVERYTIME_PASSWORD')
    
    if not username or not password:
        print("❌ 환경변수 EVERYTIME_ID 또는 EVERYTIME_PASSWORD가 설정되지 않았습니다.")
        return False
    
    print(f"✅ 계정 정보 확인됨: {username}")
    
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
        
        print(f"🔧 ChromeDriver 경로: {driver_path}")
        print(f"🔧 Chrome 실행 파일: {chrome_options.binary_location}")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome 브라우저가 시작되었습니다.")
        
        # 에브리타임 로그인 페이지로 이동
        print("🌐 에브리타임 로그인 페이지로 이동 중...")
        driver.get("https://everytime.kr/login")
        time.sleep(5)  # 더 긴 대기 시간
        
        print(f"📍 현재 URL: {driver.current_url}")
        
        # 페이지 소스 확인
        print("📄 페이지 소스 확인 중...")
        page_source = driver.page_source
        print(f"페이지 길이: {len(page_source)} 문자")
        
        # 로그인 폼 요소 찾기
        wait = WebDriverWait(driver, 15)  # 더 긴 대기 시간
        
        # ID 입력 필드 찾기 (여러 가능한 선택자 시도)
        username_input = None
        selectors = [
            'input[name="userid"]', 
            'input[name="id"]', 
            'input[type="text"]', 
            '#userid', 
            '#id',
            'input[placeholder*="아이디"]',
            'input[placeholder*="ID"]'
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
            print("페이지 소스 일부:")
            print(page_source[:1000])
            return False
        
        # 비밀번호 입력 필드 찾기
        password_input = None
        pwd_selectors = [
            'input[name="password"]', 
            'input[type="password"]', 
            '#password',
            'input[placeholder*="비밀번호"]'
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
            '#login-btn',
            'button',
            'input[value*="로그인"]'
        ]
        
        for selector in button_selectors:
            try:
                if selector == 'button':
                    # 모든 버튼에서 로그인 텍스트 찾기
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        if "로그인" in btn.text or "login" in btn.text.lower():
                            login_button = btn
                            print(f"✅ 로그인 버튼 발견 (텍스트): {btn.text}")
                            break
                else:
                    login_button = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ 로그인 버튼 발견: {selector}")
                
                if login_button:
                    break
            except:
                continue
        
        if not login_button:
            print("❌ 로그인 버튼을 찾을 수 없습니다.")
            return False
        
        # 로그인 버튼 클릭
        print("🖱️ 로그인 버튼 클릭...")
        login_button.click()
        time.sleep(3)  # 짧은 대기 후 Alert 확인
        
        # Alert 처리
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"⚠️ Alert 발생: {alert_text}")
            alert.accept()  # Alert 닫기
            print("❌ 로그인 실패 - 에브리타임에서 오류 메시지 표시")
            return False
        except:
            # Alert가 없으면 정상적으로 진행
            pass
        
        time.sleep(5)  # 추가 대기
        
        # 로그인 결과 확인
        current_url = driver.current_url
        print(f"📍 로그인 후 URL: {current_url}")
        
        # 페이지 소스에서 로그인 성공 여부 확인
        page_source = driver.page_source.lower()
        
        if "login" not in current_url.lower() and "everytime.kr" in current_url:
            print("✅ 로그인 성공! 메인 페이지로 이동되었습니다.")
            return True
        elif "로그아웃" in page_source or "프로필" in page_source or "게시판" in page_source:
            print("✅ 로그인 성공! 사용자 메뉴가 표시됩니다.")
            return True
        else:
            print("❌ 로그인 실패 또는 확인 불가")
            print("페이지 소스 일부:")
            print(driver.page_source[:1000])
            return False
            
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
    print("에브리타임 로그인 자동화 테스트")
    print("=" * 60)
    
    success = test_evertime_login()
    
    print("=" * 60)
    if success:
        print("🎯 최종 결과: 로그인 성공!")
    else:
        print("💥 최종 결과: 로그인 실패!")
    print("=" * 60)
