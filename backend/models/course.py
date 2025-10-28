"""
강의 정보 MongoDB 모델
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class Review(BaseModel):
    """강의평 모델"""
    review_id: str = Field(..., description="리뷰 고유 ID")
    rating: float = Field(..., ge=0.0, le=5.0, description="평점 (0.0-5.0)")
    comment: str = Field(..., description="리뷰 내용")
    semester: str = Field(..., description="학기 (예: 2024-1)")
    created_at: datetime = Field(default_factory=datetime.now, description="리뷰 작성일")
    source: str = Field(default="evertime", description="리뷰 출처")
    
    # AI 분석 결과
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0, description="감정 분석 점수")
    has_team_project: Optional[bool] = Field(None, description="팀프로젝트 여부")
    difficulty_level: Optional[int] = Field(None, ge=1, le=5, description="난이도 (1-5)")
    workload_level: Optional[int] = Field(None, ge=1, le=5, description="과제량 (1-5)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        validate_by_name = True
        populate_by_name = True


class CourseDetails(BaseModel):
    """강의 상세 정보"""
    attendance: str = Field(default="정보 없음", description="출석 관련 정보")
    exam: str = Field(default="정보 없음", description="시험 관련 정보")
    assignment: str = Field(default="정보 없음", description="과제 관련 정보")
    team_project: str = Field(default="정보 없음", description="팀프로젝트 관련 정보")
    time_slot: Optional[str] = Field(None, description="수업 시간")
    room: Optional[str] = Field(None, description="강의실")
    credits: int = Field(default=3, description="학점")


class Course(BaseModel):
    """강의 모델"""
    id: Optional[ObjectId] = Field(None, alias="_id")
    course_id: str = Field(..., description="강의 고유 ID (예: SW101)")
    course_name: str = Field(..., description="강의명")
    professor: str = Field(..., description="교수명")
    department: str = Field(..., description="학과")
    semester: str = Field(..., description="학기")
    
    # 기본 정보
    details: CourseDetails = Field(default_factory=CourseDetails, description="강의 상세 정보")
    
    # 리뷰 관련
    reviews: List[Review] = Field(default_factory=list, description="강의평 목록")
    total_reviews: int = Field(default=0, description="총 리뷰 수")
    average_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="평균 평점")
    
    # AI 분석 결과
    ai_summary: Optional[str] = Field(None, description="AI 요약")
    sentiment_analysis: Optional[Dict[str, Any]] = Field(None, description="감정 분석 결과")
    keywords: List[str] = Field(default_factory=list, description="키워드")
    tags: List[str] = Field(default_factory=list, description="태그")
    
    # 통계
    popularity_score: float = Field(default=0.0, description="인기도 점수")
    trend_direction: str = Field(default="stable", description="트렌드 방향 (up/down/stable)")
    
    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.now, description="생성일")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정일")
    last_crawled_at: Optional[datetime] = Field(None, description="마지막 크롤링일")
    source: str = Field(default="evertime", description="데이터 출처")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        validate_by_name = True
        populate_by_name = True


class CourseSearchResult(BaseModel):
    """강의 검색 결과 모델"""
    keyword: str = Field(..., description="검색 키워드")
    results: List[Course] = Field(..., description="검색 결과")
    total_count: int = Field(..., description="총 결과 수")
    search_time: datetime = Field(default_factory=datetime.now, description="검색 시간")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        validate_by_name = True
        populate_by_name = True
