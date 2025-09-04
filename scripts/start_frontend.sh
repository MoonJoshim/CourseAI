#!/bin/bash
"""
프론트엔드 서버 시작 스크립트
"""

echo "🌐 프론트엔드 서버 시작"
echo "📍 http://localhost:8000/src/frontend/lecture_search.html"

cd "$(dirname "$0")/.."
python3 -m http.server 8000
