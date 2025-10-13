"""
MongoDB 스키마 정의 및 검증
"""

from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, Field, validator
from bson import ObjectId


class DatabaseSchema:
    """데이터베이스 스키마 정의"""
    
    # 컬렉션별 스키마 정의
    COURSES_SCHEMA = {
        "bsonType": "object",
        "required": ["course_id", "course_name", "professor", "department", "semester"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "course_id": {"bsonType": "string", "minLength": 1},
            "course_name": {"bsonType": "string", "minLength": 1},
            "professor": {"bsonType": "string", "minLength": 1},
            "department": {"bsonType": "string"},
            "semester": {"bsonType": "string"},
            "details": {
                "bsonType": "object",
                "properties": {
                    "attendance": {"bsonType": "string"},
                    "exam": {"bsonType": "string"},
                    "assignment": {"bsonType": "string"},
                    "team_project": {"bsonType": "string"},
                    "time_slot": {"bsonType": ["string", "null"]},
                    "room": {"bsonType": ["string", "null"]},
                    "credits": {"bsonType": "int", "minimum": 1, "maximum": 6}
                }
            },
            "reviews": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["review_id", "rating", "comment", "semester"],
                    "properties": {
                        "review_id": {"bsonType": "string"},
                        "rating": {"bsonType": "double", "minimum": 0.0, "maximum": 5.0},
                        "comment": {"bsonType": "string"},
                        "semester": {"bsonType": "string"},
                        "created_at": {"bsonType": "date"},
                        "source": {"bsonType": "string"},
                        "sentiment_score": {"bsonType": ["double", "null"]},
                        "has_team_project": {"bsonType": ["bool", "null"]},
                        "difficulty_level": {"bsonType": ["int", "null"], "minimum": 1, "maximum": 5},
                        "workload_level": {"bsonType": ["int", "null"], "minimum": 1, "maximum": 5}
                    }
                }
            },
            "total_reviews": {"bsonType": "int", "minimum": 0},
            "average_rating": {"bsonType": "double", "minimum": 0.0, "maximum": 5.0},
            "ai_summary": {"bsonType": ["string", "null"]},
            "sentiment_analysis": {"bsonType": ["object", "null"]},
            "keywords": {"bsonType": "array", "items": {"bsonType": "string"}},
            "tags": {"bsonType": "array", "items": {"bsonType": "string"}},
            "popularity_score": {"bsonType": "double", "minimum": 0.0},
            "trend_direction": {"bsonType": "string", "enum": ["up", "down", "stable"]},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
            "last_crawled_at": {"bsonType": ["date", "null"]},
            "source": {"bsonType": "string"}
        }
    }
    
    CONVERSATIONS_SCHEMA = {
        "bsonType": "object",
        "required": ["session_id", "messages"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "session_id": {"bsonType": "string", "minLength": 1},
            "user_id": {"bsonType": ["string", "null"]},
            "messages": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["role", "content"],
                    "properties": {
                        "role": {"bsonType": "string", "enum": ["user", "assistant", "system", "function"]},
                        "content": {"bsonType": "string"},
                        "timestamp": {"bsonType": "date"},
                        "function_name": {"bsonType": ["string", "null"]},
                        "function_args": {"bsonType": ["object", "null"]},
                        "function_result": {"bsonType": ["object", "null"]},
                        "tokens_used": {"bsonType": ["int", "null"]},
                        "model_used": {"bsonType": ["string", "null"]}
                    }
                }
            },
            "total_messages": {"bsonType": "int", "minimum": 0},
            "title": {"bsonType": ["string", "null"]},
            "tags": {"bsonType": "array", "items": {"bsonType": "string"}},
            "category": {"bsonType": ["string", "null"]},
            "total_tokens_used": {"bsonType": "int", "minimum": 0},
            "function_calls_count": {"bsonType": "int", "minimum": 0},
            "is_active": {"bsonType": "bool"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
            "last_activity": {"bsonType": "date"}
        }
    }
    
    USERS_SCHEMA = {
        "bsonType": "object",
        "required": ["user_id"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "user_id": {"bsonType": "string", "minLength": 1},
            "name": {"bsonType": ["string", "null"]},
            "major": {"bsonType": ["string", "null"]},
            "semester": {"bsonType": ["int", "null"], "minimum": 1, "maximum": 16},
            "student_id": {"bsonType": ["string", "null"]},
            "gpa": {"bsonType": ["double", "null"], "minimum": 0.0, "maximum": 4.5},
            "total_credits": {"bsonType": "int", "minimum": 0},
            "required_credits": {"bsonType": "int", "minimum": 0},
            "preferences": {
                "bsonType": "object",
                "properties": {
                    "interests": {"bsonType": "array", "items": {"bsonType": "string"}},
                    "preferred_difficulty": {"bsonType": ["string", "null"], "enum": ["easy", "medium", "hard", None]},
                    "avoid_team_projects": {"bsonType": "bool"},
                    "preferred_professors": {"bsonType": "array", "items": {"bsonType": "string"}},
                    "time_preferences": {"bsonType": "array", "items": {"bsonType": "string"}}
                }
            },
            "bookmarked_courses": {"bsonType": "array", "items": {"bsonType": "string"}},
            "search_history": {"bsonType": "array", "items": {"bsonType": "string"}},
            "chat_sessions": {"bsonType": "array", "items": {"bsonType": "string"}},
            "total_searches": {"bsonType": "int", "minimum": 0},
            "total_chat_messages": {"bsonType": "int", "minimum": 0},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
            "last_login": {"bsonType": ["date", "null"]},
            "is_active": {"bsonType": "bool"}
        }
    }
    
    USER_ACTIVITIES_SCHEMA = {
        "bsonType": "object",
        "required": ["user_id", "activity_type", "activity_data"],
        "properties": {
            "_id": {"bsonType": "objectId"},
            "user_id": {"bsonType": "string", "minLength": 1},
            "activity_type": {"bsonType": "string", "enum": ["search", "chat", "bookmark", "view"]},
            "activity_data": {"bsonType": "object"},
            "ip_address": {"bsonType": ["string", "null"]},
            "user_agent": {"bsonType": ["string", "null"]},
            "timestamp": {"bsonType": "date"},
            "session_id": {"bsonType": ["string", "null"]}
        }
    }


class SchemaValidator:
    """스키마 검증기"""
    
    @staticmethod
    def validate_course(data: Dict[str, Any]) -> bool:
        """강의 데이터 스키마 검증"""
        try:
            # 필수 필드 검증
            required_fields = ["course_id", "course_name", "professor", "department", "semester"]
            for field in required_fields:
                if field not in data or not data[field]:
                    return False
            
            # 평점 범위 검증
            if "average_rating" in data:
                rating = data["average_rating"]
                if not isinstance(rating, (int, float)) or rating < 0.0 or rating > 5.0:
                    return False
            
            # 리뷰 데이터 검증
            if "reviews" in data and isinstance(data["reviews"], list):
                for review in data["reviews"]:
                    if not isinstance(review, dict):
                        return False
                    if "rating" in review:
                        rating = review["rating"]
                        if not isinstance(rating, (int, float)) or rating < 0.0 or rating > 5.0:
                            return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def validate_conversation(data: Dict[str, Any]) -> bool:
        """대화 데이터 스키마 검증"""
        try:
            # 필수 필드 검증
            if "session_id" not in data or not data["session_id"]:
                return False
            
            # 메시지 검증
            if "messages" in data and isinstance(data["messages"], list):
                valid_roles = ["user", "assistant", "system", "function"]
                for message in data["messages"]:
                    if not isinstance(message, dict):
                        return False
                    if "role" not in message or message["role"] not in valid_roles:
                        return False
                    if "content" not in message or not message["content"]:
                        return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def validate_user(data: Dict[str, Any]) -> bool:
        """사용자 데이터 스키마 검증"""
        try:
            # 필수 필드 검증
            if "user_id" not in data or not data["user_id"]:
                return False
            
            # GPA 검증
            if "gpa" in data and data["gpa"] is not None:
                gpa = data["gpa"]
                if not isinstance(gpa, (int, float)) or gpa < 0.0 or gpa > 4.5:
                    return False
            
            # 학기 검증
            if "semester" in data and data["semester"] is not None:
                semester = data["semester"]
                if not isinstance(semester, int) or semester < 1 or semester > 16:
                    return False
            
            return True
            
        except Exception:
            return False
