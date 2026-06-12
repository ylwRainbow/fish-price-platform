"""
时间段保存功能数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import re


class SavedPeriodBase(BaseModel):
    """基础时间段模型"""
    name: str = Field(..., min_length=1, max_length=50, description="时间段名称")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")


class SavedPeriodCreate(SavedPeriodBase):
    """创建时间段请求模型"""
    type: str = Field(..., description="时间段类型：lunar 或 solar")


class SavedPeriodUpdate(BaseModel):
    """更新时间段请求模型"""
    name: str = Field(..., min_length=1, max_length=50, description="时间段名称")


class SavedPeriodResponse(SavedPeriodBase):
    """时间段响应模型"""
    id: int
    type: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SavedPeriodListResponse(BaseModel):
    """时间段列表响应模型"""
    success: bool = True
    data: list[SavedPeriodResponse]
    message: Optional[str] = None


class SavedPeriodSingleResponse(BaseModel):
    """单个时间段响应模型"""
    success: bool = True
    data: SavedPeriodResponse
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    error: str
    message: str
