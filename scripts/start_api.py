#!/usr/bin/env python3
"""
API 서버 시작 스크립트
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# API 서버 실행
from src.api.lecture_crawler_api import app

if __name__ == '__main__':
    print("🚀 에브리타임 강의평 크롤링 API 서버 시작")
    print("📍 http://localhost:5002")
    print("🔧 실제 크롤링 기능 활성화됨")
    app.run(debug=True, host='0.0.0.0', port=5002)
