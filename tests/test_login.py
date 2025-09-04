#!/usr/bin/env python3
"""
에브리타임 로그인 테스트 스크립트
"""

import os
import sys
import time
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent / "src"))

from evertime_crawler import EverytimeCrawler
from loguru import logger

def test_login():
    """로그인 테스트 함수"""
    print("🚀 에브리타임 로그인 테스트를 시작합니다...")
    
    try:
        # 크롤러 초기화 (헤드리스 모드 비활성화)
        with EverytimeCrawler(headless=False) as crawler:
            print("✅ 크롤러가 초기화되었습니다.")
            
            # 로그인 시도
            print("🔐 로그인을 시도합니다...")
            if crawler.login():
                print("🎉 로그인 성공!")
                
                # 로그인 후 페이지 확인
                current_url = crawler.driver.current_url
                print(f"📍 현재 페이지: {current_url}")
                
                # 메인 페이지 요소 확인
                try:
                    # 프로필이나 메뉴 요소가 있는지 확인
                    page_source = crawler.driver.page_source
                    if "로그아웃" in page_source or "프로필" in page_source or "게시판" in page_source:
                        print("✅ 메인 페이지에 성공적으로 접속했습니다.")
                        return True
                    else:
                        print("⚠️ 로그인은 되었지만 메인 페이지 확인이 어렵습니다.")
                        return True
                except Exception as e:
                    print(f"⚠️ 페이지 확인 중 오류: {e}")
                    return True
                    
            else:
                print("❌ 로그인 실패!")
                return False
                
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("에브리타임 로그인 자동화 테스트")
    print("=" * 50)
    
    # 환경변수 확인
    if not os.path.exists('.env'):
        print("❌ .env 파일이 없습니다!")
        sys.exit(1)
    
    # 로그인 테스트 실행
    success = test_login()
    
    print("=" * 50)
    if success:
        print("🎯 테스트 결과: 성공!")
    else:
        print("💥 테스트 결과: 실패!")
    print("=" * 50)
