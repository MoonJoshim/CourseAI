"""
사용자 정보 MongoDB 모델
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class UserPreferences(BaseModel):
    """사용자 선호도 모델"""
    interests: List[str] = Field(default_factory=list, description="관심 분야")
    preferred_difficulty: Optional[str] = Field(None, description="선호 난이도 (easy/medium/hard)")
    avoid_team_projects: bool = Field(default=False, description="팀프로젝트 회피 여부")
    preferred_professors: List[str] = Field(default_factory=list, description="선호 교수")
    time_preferences: List[str] = Field(default_factory=list, description="시간대 선호도")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }


class UserProfile(BaseModel):
    """사용자 프로필 모델"""
    _id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: str = Field(..., description="사용자 고유 ID")
    
    # 기본 정보
    name: Optional[str] = Field(None, description="이름")
    major: Optional[str] = Field(None, description="전공")
    semester: Optional[int] = Field(None, description="학기")
    student_id: Optional[str] = Field(None, description="학번")
    
    # 학업 정보
    gpa: Optional[float] = Field(None, ge=0.0, le=4.5, description="GPA")
    total_credits: int = Field(default=0, description="총 이수 학점")
    required_credits: int = Field(default=130, description="졸업 필요 학점")
    
    # 선호도 및 설정
    preferences: UserPreferences = Field(default_factory=UserPreferences, description="사용자 선호도")
    
    # 활동 기록
    bookmarked_courses: List[str] = Field(default_factory=list, description="북마크한 강의 ID 목록")
    search_history: List[str] = Field(default_factory=list, description="검색 기록")
    chat_sessions: List[str] = Field(default_factory=list, description="챗봇 세션 ID 목록")
    
    # 통계
    total_searches: int = Field(default=0, description="총 검색 횟수")
    total_chat_messages: int = Field(default=0, description="총 챗봇 메시지 수")
    
    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.now, description="계정 생성일")
    updated_at: datetime = Field(default_factory=datetime.now, description="마지막 수정일")
    last_login: Optional[datetime] = Field(None, description="마지막 로그인")
    is_active: bool = Field(default=True, description="계정 활성 상태")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        allow_population_by_field_name = True


class UserActivity(BaseModel):
    """사용자 활동 로그 모델"""
    _id: Optional[ObjectId] = Field(None, alias="_id")
    user_id: str = Field(..., description="사용자 ID")
    activity_type: str = Field(..., description="활동 유형 (search/chat/bookmark/view)")
    
    # 활동 상세
    activity_data: Dict[str, Any] = Field(..., description="활동 데이터")
    ip_address: Optional[str] = Field(None, description="IP 주소")
    user_agent: Optional[str] = Field(None, description="사용자 에이전트")
    
    # 메타데이터
    timestamp: datetime = Field(default_factory=datetime.now, description="활동 시간")
    session_id: Optional[str] = Field(None, description="세션 ID")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        allow_population_by_field_name = True
