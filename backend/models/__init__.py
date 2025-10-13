# MongoDB 모델 패키지

from .course import Course, Review, CourseDetails, CourseSearchResult
from .chat import Conversation, Message, MessageRole, ChatRequest, ChatResponse
from .user import UserProfile, UserPreferences, UserActivity
from .analytics import SearchAnalytics, CourseAnalytics, ChatAnalytics, SystemMetrics
from .database import DatabaseManager, get_database, get_collection, Collections
from .schema import DatabaseSchema, SchemaValidator

__all__ = [
    # Course models
    'Course', 'Review', 'CourseDetails', 'CourseSearchResult',
    
    # Chat models
    'Conversation', 'Message', 'MessageRole', 'ChatRequest', 'ChatResponse',
    
    # User models
    'UserProfile', 'UserPreferences', 'UserActivity',
    
    # Analytics models
    'SearchAnalytics', 'CourseAnalytics', 'ChatAnalytics', 'SystemMetrics',
    
    # Database utilities
    'DatabaseManager', 'get_database', 'get_collection', 'Collections',
    
    # Schema utilities
    'DatabaseSchema', 'SchemaValidator'
]