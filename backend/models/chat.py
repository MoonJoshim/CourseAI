"""
챗봇 대화 MongoDB 모델
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from enum import Enum


class MessageRole(str, Enum):
    """메시지 역할"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"


class Message(BaseModel):
    """대화 메시지 모델"""
    role: MessageRole = Field(..., description="메시지 역할")
    content: str = Field(..., description="메시지 내용")
    timestamp: datetime = Field(default_factory=datetime.now, description="메시지 시간")
    
    # Function Call 관련
    function_name: Optional[str] = Field(None, description="호출된 함수명")
    function_args: Optional[Dict[str, Any]] = Field(None, description="함수 인자")
    function_result: Optional[Dict[str, Any]] = Field(None, description="함수 결과")
    
    # 메타데이터
    tokens_used: Optional[int] = Field(None, description="사용된 토큰 수")
    model_used: Optional[str] = Field(None, description="사용된 모델")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        validate_by_name = True


class Conversation(BaseModel):
    """대화 세션 모델"""
    _id: Optional[ObjectId] = Field(None, alias="_id")
    session_id: str = Field(..., description="세션 고유 ID")
    user_id: Optional[str] = Field(None, description="사용자 ID (익명 사용자용)")
    
    # 대화 내용
    messages: List[Message] = Field(default_factory=list, description="메시지 목록")
    total_messages: int = Field(default=0, description="총 메시지 수")
    
    # 대화 메타데이터
    title: Optional[str] = Field(None, description="대화 제목")
    tags: List[str] = Field(default_factory=list, description="대화 태그")
    category: Optional[str] = Field(None, description="대화 카테고리")
    
    # 통계
    total_tokens_used: int = Field(default=0, description="총 사용 토큰 수")
    function_calls_count: int = Field(default=0, description="함수 호출 횟수")
    
    # 상태
    is_active: bool = Field(default=True, description="활성 세션 여부")
    created_at: datetime = Field(default_factory=datetime.now, description="생성일")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정일")
    last_activity: datetime = Field(default_factory=datetime.now, description="마지막 활동일")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        validate_by_name = True
        allow_population_by_field_name = True


class ChatRequest(BaseModel):
    """챗봇 요청 모델"""
    message: str = Field(..., description="사용자 메시지")
    session_id: Optional[str] = Field(None, description="세션 ID")
    history: List[Dict[str, str]] = Field(default_factory=list, description="대화 히스토리")
    
    # 요청 옵션
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="응답 창의성")
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000, description="최대 토큰 수")
    use_functions: bool = Field(default=True, description="함수 호출 사용 여부")


class ChatResponse(BaseModel):
    """챗봇 응답 모델"""
    response: str = Field(..., description="AI 응답")
    session_id: str = Field(..., description="세션 ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시간")
    
    # Function Call 관련
    function_called: Optional[str] = Field(None, description="호출된 함수명")
    function_result: Optional[Dict[str, Any]] = Field(None, description="함수 결과")
    
    # 메타데이터
    tokens_used: Optional[int] = Field(None, description="사용된 토큰 수")
    model_used: Optional[str] = Field(None, description="사용된 모델")
    response_time_ms: Optional[int] = Field(None, description="응답 시간 (밀리초)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        validate_by_name = True
