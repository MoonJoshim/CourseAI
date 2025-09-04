#!/usr/bin/env python3
"""
에브리타임 크롤링 메인 실행 파일
"""

import os
import sys
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent / "src"))

from evertime_crawler import EverytimeCrawler
from loguru import logger

def main():
    """메인 실행 함수"""
    try:
        # 환경변수 확인
        if not os.path.exists('.env'):
            logger.error(".env 파일이 없습니다. env.example을 복사하여 .env 파일을 생성하고 계정 정보를 입력해주세요.")
            return
        
        # 크롤러 실행
        with EverytimeCrawler(headless=False) as crawler:
            # 로그인
            if crawler.login():
                logger.info("로그인 성공! 크롤링을 시작합니다.")
                
                # 강의 목록 수집
                courses = crawler.get_course_list()
                if courses:
                    # 강의 목록 저장
                    crawler.save_to_csv(courses, 'courses.csv')
                    
                    # 첫 번째 강의의 강의평 수집 (예시)
                    if courses and courses[0].get('url'):
                        first_course_url = courses[0]['url']
                        if not first_course_url.startswith('http'):
                            first_course_url = f"https://everytime.kr{first_course_url}"
                        
                        reviews = crawler.get_course_reviews(first_course_url)
                        if reviews:
                            crawler.save_to_csv(reviews, 'reviews.csv')
                
                logger.success("크롤링이 완료되었습니다!")
            else:
                logger.error("로그인에 실패했습니다. 계정 정보를 확인해주세요.")
                
    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
