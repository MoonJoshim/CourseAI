"""
에브리타임 크롤링 프로젝트 설정
"""

import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class Config:
    """프로젝트 설정 클래스"""
    
    # 에브리타임 설정
    EVERYTIME_BASE_URL = "https://everytime.kr"
    EVERYTIME_LOGIN_URL = f"{EVERYTIME_BASE_URL}/login"
    EVERYTIME_LECTURE_URL = f"{EVERYTIME_BASE_URL}/lecture"
    
    # 로그인 정보
    EVERYTIME_ID = os.getenv('EVERYTIME_ID')
    EVERYTIME_PASSWORD = os.getenv('EVERYTIME_PASSWORD')
    
    # 크롤링 설정
    HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'
    DELAY_BETWEEN_REQUESTS = float(os.getenv('DELAY_BETWEEN_REQUESTS', '2.0'))
    
    # 로그 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join('logs', 'crawler.log')
    
    # 데이터 저장 경로
    DATA_DIR = 'data'
    COURSES_FILE = 'courses.csv'
    REVIEWS_FILE = 'reviews.csv'
    
    # 웹드라이버 설정
    CHROME_OPTIONS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--window-size=1920,1080',
        '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    ]
    
    # 대기 시간 설정
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 10
    
    @classmethod
    def validate(cls):
        """설정 유효성 검사"""
        if not cls.EVERYTIME_ID or not cls.EVERYTIME_PASSWORD:
            raise ValueError("EVERYTIME_ID와 EVERYTIME_PASSWORD 환경변수를 설정해주세요.")
        
        # 필요한 디렉토리 생성
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        return True
