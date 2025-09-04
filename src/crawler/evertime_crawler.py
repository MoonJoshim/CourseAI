"""
에브리타임 크롤링 모듈
로그인 및 강의평 데이터 수집 기능
"""

import os
import time
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
from loguru import logger
import pandas as pd

# 환경변수 로드
load_dotenv()

class EverytimeCrawler:
    """에브리타임 크롤링 클래스"""
    
    def __init__(self, headless: bool = False):
        """
        크롤러 초기화
        
        Args:
            headless (bool): 헤드리스 모드 여부
        """
        self.base_url = "https://everytime.kr"
        self.login_url = f"{self.base_url}/login"
        self.driver = None
        self.session = requests.Session()
        self.headless = headless
        
        # 환경변수에서 로그인 정보 가져오기
        self.username = os.getenv('EVERYTIME_ID')
        self.password = os.getenv('EVERYTIME_PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError("EVERYTIME_ID와 EVERYTIME_PASSWORD 환경변수를 설정해주세요.")
        
        logger.info("에브리타임 크롤러가 초기화되었습니다.")
    
    def setup_driver(self):
        """Chrome 웹드라이버 설정"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # 웹드라이버 자동 설치 및 설정
        driver_path = ChromeDriverManager().install()
        # macOS에서 올바른 chromedriver 파일 찾기
        if "THIRD_PARTY_NOTICES.chromedriver" in driver_path:
            driver_path = driver_path.replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver")
        
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info("Chrome 웹드라이버가 설정되었습니다.")
    
    def login(self) -> bool:
        """
        에브리타임 로그인 수행
        
        Returns:
            bool: 로그인 성공 여부
        """
        try:
            if not self.driver:
                self.setup_driver()
            
            logger.info("에브리타임 로그인 페이지로 이동 중...")
            
            self.driver.get(self.login_url)
            
            # 로그인 폼 대기
            wait = WebDriverWait(self.driver, 10)
            username_input = wait.until(
                EC.presence_of_element_located((By.NAME, "userid"))
            )
            password_input = self.driver.find_element(By.NAME, "password")
            
            # 로그인 정보 입력
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            
            # 로그인 버튼 클릭
            login_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            login_button.click()
            
            # 로그인 성공 확인 (메인 페이지로 리다이렉트)
            time.sleep(3)
            
            if "everytime.kr" in self.driver.current_url and "login" not in self.driver.current_url:
                logger.success("에브리타임 로그인에 성공했습니다!")
                return True
            else:
                logger.error("로그인에 실패했습니다.")
                return False
                
        except Exception as e:
            logger.error(f"로그인 중 오류 발생: {str(e)}")
            return False
    
    def get_course_list(self) -> List[Dict]:
        """
        강의 목록 수집
        
        Returns:
            List[Dict]: 강의 정보 리스트
        """
        try:
            # 강의평 페이지로 이동
            course_url = f"{self.base_url}/lecture"
            self.driver.get(course_url)
            time.sleep(2)
            
            # 강의 목록 파싱
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            courses = []
            
            # 강의 항목들 찾기 (실제 HTML 구조에 맞게 수정 필요)
            course_elements = soup.find_all('div', class_='lecture-item')
            
            for element in course_elements:
                course_info = {
                    'name': element.find('h3').text.strip() if element.find('h3') else '',
                    'professor': element.find('span', class_='professor').text.strip() if element.find('span', class_='professor') else '',
                    'rating': element.find('span', class_='rating').text.strip() if element.find('span', class_='rating') else '',
                    'url': element.find('a')['href'] if element.find('a') else ''
                }
                courses.append(course_info)
            
            logger.info(f"총 {len(courses)}개의 강의를 찾았습니다.")
            return courses
            
        except Exception as e:
            logger.error(f"강의 목록 수집 중 오류 발생: {str(e)}")
            return []
    
    def get_course_reviews(self, course_url: str) -> List[Dict]:
        """
        특정 강의의 강의평 수집
        
        Args:
            course_url (str): 강의 상세 페이지 URL
            
        Returns:
            List[Dict]: 강의평 리스트
        """
        try:
            self.driver.get(course_url)
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            reviews = []
            
            # 강의평 항목들 찾기 (실제 HTML 구조에 맞게 수정 필요)
            review_elements = soup.find_all('div', class_='review-item')
            
            for element in review_elements:
                review_info = {
                    'content': element.find('p', class_='content').text.strip() if element.find('p', class_='content') else '',
                    'rating': element.find('span', class_='rating').text.strip() if element.find('span', class_='rating') else '',
                    'date': element.find('span', class_='date').text.strip() if element.find('span', class_='date') else '',
                    'semester': element.find('span', class_='semester').text.strip() if element.find('span', class_='semester') else ''
                }
                reviews.append(review_info)
            
            logger.info(f"총 {len(reviews)}개의 강의평을 수집했습니다.")
            return reviews
            
        except Exception as e:
            logger.error(f"강의평 수집 중 오류 발생: {str(e)}")
            return []
    
    def save_to_csv(self, data: List[Dict], filename: str):
        """
        데이터를 CSV 파일로 저장
        
        Args:
            data (List[Dict]): 저장할 데이터
            filename (str): 파일명
        """
        try:
            df = pd.DataFrame(data)
            filepath = os.path.join('data', filename)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.success(f"데이터가 {filepath}에 저장되었습니다.")
        except Exception as e:
            logger.error(f"CSV 저장 중 오류 발생: {str(e)}")
    
    def close(self):
        """웹드라이버 종료"""
        if self.driver:
            self.driver.quit()
            logger.info("웹드라이버가 종료되었습니다.")
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()
