"""
분석 및 통계 MongoDB 모델
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class SearchAnalytics(BaseModel):
    """검색 분석 모델"""
    _id: Optional[ObjectId] = Field(None, alias="_id")
    date: datetime = Field(..., description="분석 날짜")
    
    # 검색 통계
    total_searches: int = Field(default=0, description="총 검색 수")
    unique_keywords: int = Field(default=0, description="고유 키워드 수")
    popular_keywords: List[Dict[str, Any]] = Field(default_factory=list, description="인기 키워드")
    
    # 검색 결과 통계
    avg_results_per_search: float = Field(default=0.0, description="검색당 평균 결과 수")
    no_result_searches: int = Field(default=0, description="결과 없는 검색 수")
    
    # 시간대별 통계
    hourly_searches: Dict[str, int] = Field(default_factory=dict, description="시간대별 검색 수")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        validate_by_name = True
        allow_population_by_field_name = True


class CourseAnalytics(BaseModel):
    """강의 분석 모델"""
    _id: Optional[ObjectId] = Field(None, alias="_id")
    course_id: str = Field(..., description="강의 ID")
    date: datetime = Field(..., description="분석 날짜")
    
    # 조회 통계
    total_views: int = Field(default=0, description="총 조회 수")
    unique_viewers: int = Field(default=0, description="고유 조회자 수")
    
    # 검색 통계
    search_appearances: int = Field(default=0, description="검색 결과 노출 수")
    search_clicks: int = Field(default=0, description="검색 결과 클릭 수")
    click_through_rate: float = Field(default=0.0, description="클릭률")
    
    # 북마크 통계
    bookmarks: int = Field(default=0, description="북마크 수")
    
    # 리뷰 통계
    new_reviews: int = Field(default=0, description="신규 리뷰 수")
    avg_rating: float = Field(default=0.0, description="평균 평점")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        validate_by_name = True
        allow_population_by_field_name = True


class ChatAnalytics(BaseModel):
    """챗봇 분석 모델"""
    _id: Optional[ObjectId] = Field(None, alias="_id")
    date: datetime = Field(..., description="분석 날짜")
    
    # 대화 통계
    total_conversations: int = Field(default=0, description="총 대화 수")
    total_messages: int = Field(default=0, description="총 메시지 수")
    avg_messages_per_conversation: float = Field(default=0.0, description="대화당 평균 메시지 수")
    
    # 사용자 통계
    unique_users: int = Field(default=0, description="고유 사용자 수")
    returning_users: int = Field(default=0, description="재방문 사용자 수")
    
    # Function Call 통계
    function_calls: int = Field(default=0, description="함수 호출 수")
    function_success_rate: float = Field(default=0.0, description="함수 성공률")
    popular_functions: List[Dict[str, Any]] = Field(default_factory=list, description="인기 함수")
    
    # 응답 시간 통계
    avg_response_time_ms: float = Field(default=0.0, description="평균 응답 시간")
    max_response_time_ms: int = Field(default=0, description="최대 응답 시간")
    
    # 토큰 사용량
    total_tokens_used: int = Field(default=0, description="총 사용 토큰 수")
    avg_tokens_per_message: float = Field(default=0.0, description="메시지당 평균 토큰 수")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        validate_by_name = True
        allow_population_by_field_name = True


class SystemMetrics(BaseModel):
    """시스템 메트릭 모델"""
    _id: Optional[ObjectId] = Field(None, alias="_id")
    timestamp: datetime = Field(default_factory=datetime.now, description="측정 시간")
    
    # 크롤링 통계
    crawling_status: str = Field(..., description="크롤링 상태 (active/error/idle)")
    last_crawl_time: Optional[datetime] = Field(None, description="마지막 크롤링 시간")
    crawl_success_rate: float = Field(default=0.0, description="크롤링 성공률")
    total_crawled_courses: int = Field(default=0, description="총 크롤링된 강의 수")
    
    # API 통계
    api_requests_per_minute: int = Field(default=0, description="분당 API 요청 수")
    api_error_rate: float = Field(default=0.0, description="API 에러율")
    avg_api_response_time_ms: float = Field(default=0.0, description="평균 API 응답 시간")
    
    # 데이터베이스 통계
    db_connection_count: int = Field(default=0, description="DB 연결 수")
    db_query_time_ms: float = Field(default=0.0, description="DB 쿼리 시간")
    
    # 리소스 사용량
    memory_usage_mb: float = Field(default=0.0, description="메모리 사용량 (MB)")
    cpu_usage_percent: float = Field(default=0.0, description="CPU 사용률 (%)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        validate_by_name = True
        allow_population_by_field_name = True
