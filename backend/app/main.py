from fastapi import FastAPI, Query, HTTPException, Body, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
from io import BytesIO
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from . import data_loader as dl
from . import repository as repo
from .api import saved_periods

app = FastAPI(title="鱼价数据平台 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册保存时间段功能路由
app.include_router(saved_periods.router, prefix="/api", tags=["保存时间段"])

@app.get("/api/fishes")
def get_fishes(q: str | None = Query(default=None)):
    return dl.fishes(q)

@app.get("/api/markets")
def get_markets(region_code: str | None = Query(default=None)):
    return dl.markets(region_code)

@app.get("/api/prices")
def get_prices(
    fish_id: int, 
    market_id: int, 
    start: str | None = None, 
    end: str | None = None, 
    granularity: str = Query(default="day"),
    lunar_mode: bool = Query(default=False)
):
    """
    查询价格数据
    
    Args:
        fish_id: 鱼种ID
        market_id: 市场ID
        start: 开始日期 (公历格式 YYYY-MM-DD)
        end: 结束日期 (公历格式 YYYY-MM-DD)
        granularity: 粒度 (day/week/month)
        lunar_mode: 是否启用农历模式，返回数据包含农历信息
    """
    now = datetime.now().date().isoformat()
    if not start: 
        start = now
    if not end:
        end = now
    if granularity not in ("day","week","month"):
        granularity = "day"
    res = dl.prices(fish_id, market_id, start, end, granularity, lunar_mode)
    return JSONResponse(res)

@app.get("/api/forecast")
def get_forecast(fish_id: int, market_id: int, horizon: int = Query(default=14)):
    res = dl.forecast(fish_id, market_id, horizon)
    return JSONResponse(res)

class PriceInput(BaseModel):
    fish_id: int
    market_id: int
    price: float
    ts: str
    currency: str = "CNY"
    unit: str = "kg"
    price_type: str = "pond"
    source_url: Optional[str] = None
    source_text: Optional[str] = None

class BatchPriceInput(BaseModel):
    prices: List[PriceInput]

@app.post("/api/prices")
def add_price(data: PriceInput):
    try:
        datetime.fromisoformat(data.ts.replace('Z', '+00:00'))
    except:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format like 2024-01-15 or 2024-01-15T00:00:00")
    point = {
        "price": data.price,
        "ts": data.ts if 'T' in data.ts else data.ts + "T00:00:00+08:00",
        "currency": data.currency,
        "unit": data.unit
    }
    success = repo.insert_prices(data.fish_id, data.market_id, [point], data.price_type, data.source_url)
    if success:
        return {"success": True, "message": "Price added successfully"}
    raise HTTPException(status_code=500, detail="Failed to add price")

@app.post("/api/prices/batch")
def add_prices_batch(data: BatchPriceInput):
    added = 0
    failed = 0
    for p in data.prices:
        try:
            point = {
                "price": p.price,
                "ts": p.ts if 'T' in p.ts else p.ts + "T00:00:00+08:00",
                "currency": p.currency,
                "unit": p.unit
            }
            if repo.insert_prices(p.fish_id, p.market_id, [point], p.price_type, p.source_url):
                added += 1
            else:
                failed += 1
        except:
            failed += 1
    return {"success": True, "added": added, "failed": failed}

@app.get("/api/fishes/list")
def list_fishes():
    from .db import get_conn
    conn = get_conn()
    if not conn:
        return []
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, alias, species_code FROM fishes ORDER BY id")
        rows = cur.fetchall()
    return [{"id": r[0], "name": r[1], "alias": r[2], "species_code": r[3]} for r in rows]

@app.get("/api/markets/list")
def list_markets():
    from .db import get_conn
    conn = get_conn()
    if not conn:
        return []
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, region_code, source_code FROM markets ORDER BY id")
        rows = cur.fetchall()
    return [{"id": r[0], "name": r[1], "region_code": r[2], "source_code": r[3]} for r in rows]

@app.get("/api/templates/prices.xlsx")
def download_excel_template():
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "价格数据"
    
    headers = ["鱼种名称", "市场名称", "价格", "日期", "货币", "单位", "价格类型", "来源URL"]
    ws.append(headers)
    
    example_data = [
        ["鲈鱼", "上海农产品中心", 15.80, "2024-01-15", "CNY", "kg", "pond", ""],
        ["泥鳅", "民众渔业", 12.50, "2024-01-16", "CNY", "kg", "pond", ""],
        ["草鱼", "上海农产品中心", 8.20, "2024-01-17", "CNY", "kg", "wholesale", ""]
    ]
    for row in example_data:
        ws.append(row)
    
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        ws.column_dimensions[column].width = max_length + 4
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=prices_template.xlsx"}
    )

@app.get("/api/templates/prices.csv")
def download_csv_template():
    csv_content = "鱼种名称,市场名称,价格,日期,货币,单位,价格类型,来源URL\n鲈鱼,上海农产品中心,15.80,2024-01-15,CNY,kg,pond,\n泥鳅,民众渔业,12.50,2024-01-16,CNY,kg,pond,\n草鱼,上海农产品中心,8.20,2024-01-17,CNY,kg,wholesale,"
    
    return StreamingResponse(
        BytesIO(csv_content.encode('utf-8-sig')),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=prices_template.csv"}
    )

@app.post("/api/import/excel")
async def import_excel(file: UploadFile = File(...)):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="请上传Excel文件 (.xlsx 或 .xls)")
    
    try:
        from openpyxl import load_workbook
        
        contents = await file.read()
        wb = load_workbook(BytesIO(contents))
        ws = wb.active
        
        fishes = {f["name"]: f["id"] for f in list_fishes()}
        markets = {m["name"]: m["id"] for m in list_markets()}
        
        added = 0
        failed = 0
        errors = []
        
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not row or not row[0]:
                continue
            
            try:
                fish_name = str(row[0]).strip() if row[0] else None
                market_name = str(row[1]).strip() if row[1] else None
                price = float(row[2]) if row[2] else None
                ts = str(row[3]).strip() if row[3] else None
                
                if not all([fish_name, market_name, price, ts]):
                    errors.append(f"第{row_idx}行: 缺少必填字段")
                    failed += 1
                    continue
                
                fish_id = fishes.get(fish_name)
                market_id = markets.get(market_name)
                
                if not fish_id:
                    errors.append(f"第{row_idx}行: 找不到鱼种 '{fish_name}'")
                    failed += 1
                    continue
                if not market_id:
                    errors.append(f"第{row_idx}行: 找不到市场 '{market_name}'")
                    failed += 1
                    continue
                
                price_type = str(row[6]).strip() if row[6] else "pond"
                source_url = str(row[7]).strip() if row[7] else None
                
                point = {
                    "price": price,
                    "ts": ts if 'T' in ts else ts + "T00:00:00+08:00",
                    "currency": str(row[4]).strip() if row[4] else "CNY",
                    "unit": str(row[5]).strip() if row[5] else "kg"
                }
                
                if repo.insert_prices(fish_id, market_id, [point], price_type, source_url):
                    added += 1
                else:
                    failed += 1
            except Exception as e:
                errors.append(f"第{row_idx}行: {str(e)}")
                failed += 1
        
        return {
            "success": True,
            "added": added,
            "failed": failed,
            "errors": errors[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")
