"""
MongoDB 데이터베이스 연결 및 컬렉션 관리
"""

import os
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from config.config import Config
from loguru import logger


class DatabaseManager:
    """MongoDB 데이터베이스 관리자"""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self._connect()
    
    def _connect(self):
        """MongoDB 연결"""
        try:
            uri = Config.MONGO_URI
            self.client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            self.db = self.client[Config.MONGO_DB_NAME]
            
            # 연결 테스트
            self.client.admin.command('ping')
            logger.success("MongoDB 연결 성공")
            
        except Exception as e:
            logger.error(f"MongoDB 연결 실패: {str(e)}")
            raise
    
    def get_collection(self, collection_name: str) -> Collection:
        """컬렉션 가져오기"""
        if not self.db:
            raise Exception("데이터베이스가 연결되지 않았습니다")
        return self.db[collection_name]
    
    def create_indexes(self):
        """인덱스 생성"""
        try:
            # 강의 컬렉션 인덱스
            courses_collection = self.get_collection("courses")
            courses_collection.create_index("course_id", unique=True)
            courses_collection.create_index("course_name")
            courses_collection.create_index("professor")
            courses_collection.create_index("department")
            courses_collection.create_index("semester")
            courses_collection.create_index("average_rating")
            courses_collection.create_index("created_at")
            courses_collection.create_index([("course_name", "text"), ("professor", "text")])
            
            # 대화 컬렉션 인덱스
            conversations_collection = self.get_collection("conversations")
            conversations_collection.create_index("session_id", unique=True)
            conversations_collection.create_index("user_id")
            conversations_collection.create_index("created_at")
            conversations_collection.create_index("is_active")
            
            # 사용자 컬렉션 인덱스
            users_collection = self.get_collection("users")
            users_collection.create_index("user_id", unique=True)
            users_collection.create_index("student_id")
            users_collection.create_index("created_at")
            
            # 활동 로그 컬렉션 인덱스
            activities_collection = self.get_collection("user_activities")
            activities_collection.create_index("user_id")
            activities_collection.create_index("activity_type")
            activities_collection.create_index("timestamp")
            activities_collection.create_index([("user_id", 1), ("timestamp", -1)])
            
            # 분석 컬렉션 인덱스
            search_analytics_collection = self.get_collection("search_analytics")
            search_analytics_collection.create_index("date")
            
            course_analytics_collection = self.get_collection("course_analytics")
            course_analytics_collection.create_index([("course_id", 1), ("date", 1)])
            
            chat_analytics_collection = self.get_collection("chat_analytics")
            chat_analytics_collection.create_index("date")
            
            system_metrics_collection = self.get_collection("system_metrics")
            system_metrics_collection.create_index("timestamp")
            
            logger.success("MongoDB 인덱스 생성 완료")
            
        except Exception as e:
            logger.error(f"인덱스 생성 실패: {str(e)}")
            raise
    
    def close(self):
        """연결 종료"""
        if self.client:
            self.client.close()
            logger.info("MongoDB 연결 종료")


# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager()


def get_database() -> Database:
    """데이터베이스 인스턴스 가져오기"""
    return db_manager.db


def get_collection(collection_name: str) -> Collection:
    """컬렉션 가져오기"""
    return db_manager.get_collection(collection_name)


# 컬렉션 이름 상수
class Collections:
    """컬렉션 이름 상수"""
    COURSES = "courses"
    CONVERSATIONS = "conversations"
    USERS = "users"
    USER_ACTIVITIES = "user_activities"
    SEARCH_ANALYTICS = "search_analytics"
    COURSE_ANALYTICS = "course_analytics"
    CHAT_ANALYTICS = "chat_analytics"
    SYSTEM_METRICS = "system_metrics"
