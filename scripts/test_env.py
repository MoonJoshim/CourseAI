#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

print("=== 환경변수 테스트 ===")
print(f"EVERYTIME_ID: {repr(os.getenv('EVERYTIME_ID'))}")
print(f"EVERYTIME_PASSWORD: {repr(os.getenv('EVERYTIME_PASSWORD'))}")
print(f"Password length: {len(os.getenv('EVERYTIME_PASSWORD', ''))}")
print(f"Contains @: {'@' in os.getenv('EVERYTIME_PASSWORD', '')}")

# 실제 크롤링 함수 테스트
print("\n=== 크롤링 함수 테스트 ===")
try:
    from backend.api.lecture_api import login_to_everytime, setup_driver
    
    print("드라이버 설정 중...")
    driver = setup_driver()
    
    if driver:
        print("드라이버 설정 성공!")
        print("로그인 테스트 중...")
        result = login_to_everytime(driver)
        print(f"로그인 결과: {result}")
        
        if driver:
            driver.quit()
    else:
        print("드라이버 설정 실패!")
        
except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()
