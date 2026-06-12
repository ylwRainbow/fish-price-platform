"""
时间段保存功能 API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.saved_period import (
    SavedPeriodCreate,
    SavedPeriodUpdate,
    SavedPeriodResponse,
    SavedPeriodListResponse,
    SavedPeriodSingleResponse,
    ErrorResponse
)
from app.repository import (
    get_saved_periods,
    save_period,
    delete_saved_period,
    update_saved_period,
    count_saved_periods,
    get_saved_combinations,
    save_combination,
    delete_saved_combination
)
import json

router = APIRouter()


@router.get("/saved-periods", response_model=SavedPeriodListResponse)
async def list_saved_periods(
    type: str = Query(..., description="时间段类型：lunar 或 solar"),
    limit: int = Query(default=20, ge=1, le=50)
):
    """获取已保存的时间段列表"""
    if type not in ["lunar", "solar"]:
        raise HTTPException(status_code=400, detail="类型必须是 lunar 或 solar")
    
    periods = get_saved_periods(type, limit)
    # 添加 type 字段到每个时间段
    periods_with_type = [{**p, "type": type} for p in periods]
    
    return SavedPeriodListResponse(
        success=True,
        data=periods_with_type,
        message=f"获取成功，共 {len(periods)} 条"
    )


@router.post("/saved-periods", response_model=SavedPeriodSingleResponse)
async def create_saved_period(period: SavedPeriodCreate):
    """保存新的时间段"""
    if period.type not in ["lunar", "solar"]:
        raise HTTPException(status_code=400, detail="类型必须是 lunar 或 solar")
    
    # 检查是否超过限制
    count = count_saved_periods(period.type)
    if count >= 20:
        raise HTTPException(status_code=400, detail="已保存时间段数量已达上限（20 条）")
    
    saved = save_period(
        period_type=period.type,
        name=period.name,
        start_date=period.start_date,
        end_date=period.end_date
    )
    
    if not saved:
        raise HTTPException(status_code=500, detail="保存失败")
    
    # 添加 type 字段
    saved_with_type = {**saved, "type": period.type}
    
    return SavedPeriodSingleResponse(
        success=True,
        data=saved_with_type,
        message="保存成功"
    )


@router.delete("/saved-periods/{period_id}", response_model=ErrorResponse)
async def delete_saved(period_id: int, type: str = Query(...)):
    """删除已保存的时间段"""
    if type not in ["lunar", "solar"]:
        raise HTTPException(status_code=400, detail="类型必须是 lunar 或 solar")
    
    success = delete_saved_period(type, period_id)
    if not success:
        raise HTTPException(status_code=404, detail="时间段不存在或删除失败")
    
    return ErrorResponse(success=False, error="", message="删除成功")


@router.put("/saved-periods/{period_id}", response_model=SavedPeriodSingleResponse)
async def update_saved(period_id: int, period: SavedPeriodUpdate, type: str = Query(...)):
    """更新时间段名称"""
    if type not in ["lunar", "solar"]:
        raise HTTPException(status_code=400, detail="类型必须是 lunar 或 solar")
    
    updated = update_saved_period(type, period_id, period.name)
    if not updated:
        raise HTTPException(status_code=404, detail="时间段不存在或更新失败")
    
    # 添加 type 字段
    updated_with_type = {**updated, "type": type}
    
    return SavedPeriodSingleResponse(
        success=True,
        data=updated_with_type,
        message="更新成功"
    )


@router.get("/saved-period-combinations")
async def list_saved_combinations(
    type: str = Query(..., description="时间段类型：lunar 或 solar")
):
    """获取已保存的时间段组合列表"""
    if type not in ["lunar", "solar"]:
        raise HTTPException(status_code=400, detail="类型必须是 lunar 或 solar")
    
    combinations = get_saved_combinations(type)
    # 添加 type 字段到每个组合
    combinations_with_type = [{**c, "type": type} for c in combinations]
    
    return {
        "success": True,
        "data": combinations_with_type,
        "message": f"获取成功，共 {len(combinations)} 条"
    }


@router.post("/saved-period-combinations")
async def create_saved_combination(
    type: str = Query(..., description="时间段类型：lunar 或 solar"),
    name: str = Query(..., description="组合名称"),
    periods: str = Query(..., description="时间段列表（JSON 格式）")
):
    """保存新的时间段组合"""
    if type not in ["lunar", "solar"]:
        raise HTTPException(status_code=400, detail="类型必须是 lunar 或 solar")
    
    try:
        periods_data = json.loads(periods)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="时间段格式错误")
    
    saved = save_combination(
        period_type=type,
        name=name,
        periods=periods_data
    )
    
    if not saved:
        raise HTTPException(status_code=500, detail="保存失败")
    
    # 添加 type 字段
    saved_with_type = {**saved, "type": type}
    
    return {
        "success": True,
        "data": saved_with_type,
        "message": "保存成功"
    }


@router.delete("/saved-period-combinations/{combination_id}")
async def delete_saved_combination_endpoint(
    combination_id: int,
    type: str = Query(..., description="时间段类型：lunar 或 solar")
):
    """删除已保存的时间段组合"""
    if type not in ["lunar", "solar"]:
        raise HTTPException(status_code=400, detail="类型必须是 lunar 或 solar")
    
    success = delete_saved_combination(type, combination_id)
    if not success:
        raise HTTPException(status_code=404, detail="组合不存在或删除失败")
    
    return {
        "success": True,
        "message": "删除成功"
    }
