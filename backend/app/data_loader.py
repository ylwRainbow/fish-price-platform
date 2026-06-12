import yaml
import os
from datetime import datetime, timedelta, date
from dateutil import tz
from . import repository as repo
from . import connectors as conn
from .lunar_utils import solar_to_lunar, get_lunar_festivals, get_solar_terms

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

CFG = load_config()

def fishes(q=None):
    items = CFG["fishes"]
    if q:
        ql = q.lower()
        items = [i for i in items if ql in i["name"].lower() or ql in i.get("alias","").lower() or ql in i["code"].lower()]
    return items

def markets(region_code=None):
    items = CFG["markets"]
    if region_code:
        items = [i for i in items if str(i.get("region_code","")) == str(region_code)]
    return items

def find_fish_market(fish_id, market_id):
    fish = next((i for i in CFG["fishes"] if i["id"] == fish_id), None)
    market = next((i for i in CFG["markets"] if i["id"] == market_id), None)
    if not fish or not market:
        return None, None, None
    src = next((s for s in CFG["sources"] if s["fish_code"] == fish["code"] and s["market_code"] == market["code"]), None)
    return fish, market, src

def daterange(start, end):
    s = datetime.fromisoformat(start)
    e = datetime.fromisoformat(end)
    d = []
    cur = s
    while cur <= e:
        d.append(cur.date().isoformat())
        cur += timedelta(days=1)
    return d

def gen_mock_series(base, start, end):
    dates = daterange(start, end)
    arr = []
    for i, iso in enumerate(dates):
        v = base + (i * 0.02) + (abs((i % 30) - 15) * 0.03)
        arr.append({"ts": iso + "T00:00:00+08:00", "price": round(v,2), "currency": "CNY", "unit": "kg"})
    return arr

def aggregate(points, granularity):
    if granularity == "day":
        return points
    buckets = {}
    for p in points:
        dt = datetime.fromisoformat(p["ts"].replace("Z","+00:00"))
        if granularity == "week":
            key = dt.strftime("%G-W%V")
        else:
            key = dt.strftime("%Y-%m")
        b = buckets.get(key, [])
        b.append(p["price"])
        buckets[key] = b
    out = []
    for k in sorted(buckets.keys()):
        avg = sum(buckets[k]) / len(buckets[k])
        if granularity == "week":
            dt = datetime.strptime(k + "-1", "%G-W%V-%u")
        else:
            dt = datetime.strptime(k + "-01", "%Y-%m-%d")
        out.append({"ts": dt.date().isoformat() + "T00:00:00+08:00", "price": round(avg,2), "currency": "CNY", "unit": "kg"})
    return out

def prices(fish_id, market_id, start, end, granularity="day", lunar_mode=False):
    """
    查询价格数据
    
    Args:
        fish_id: 鱼种ID
        market_id: 市场ID
        start: 开始日期
        end: 结束日期
        granularity: 粒度
        lunar_mode: 是否返回农历信息
    """
    fish, market, src = find_fish_market(fish_id, market_id)
    if not fish or not market:
        return {"fish": fish, "market": market, "points": []}
    price_type = "pond"
    # 先查询数据库，无论是否有 source 配置
    try:
        pts_db = repo.query_prices(fish_id, market_id, start, end, granularity, price_type)
    except Exception:
        pts_db = []
    if pts_db:
        # 如果启用农历模式，为每个数据点添加农历信息
        if lunar_mode:
            pts_db = add_lunar_info(pts_db)
        return {"fish": fish, "market": market, "points": pts_db}
    # 如果数据库没有数据，且有 source 配置，尝试从 source 获取
    if not src:
        return {"fish": fish, "market": market, "points": []}
    src_type = src.get("type", "mock")
    try:
        c = conn.connector_from_source(src)
        pts = c.fetch(fish, market, start, end)
    except Exception:
        pts = []
    if not pts:
        base = float(src.get("params", {}).get("base", 20.0))
        pts = gen_mock_series(base, start, end)
    pts = aggregate(pts, granularity)
    # 如果启用农历模式，为每个数据点添加农历信息
    if lunar_mode:
        pts = add_lunar_info(pts)
    return {"fish": fish, "market": market, "points": pts}


def add_lunar_info(points):
    """
    为价格数据点添加农历信息
    
    Args:
        points: 价格数据点列表
        
    Returns:
        添加了农历信息的数据点列表
    """
    result = []
    for p in points:
        # 解析日期
        ts_str = p.get("ts", "")
        if "T" in ts_str:
            solar_date = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).date()
        else:
            solar_date = datetime.fromisoformat(ts_str).date()
        
        # 获取农历信息
        lunar_info = solar_to_lunar(solar_date)
        
        # 获取节日和节气
        festivals = get_lunar_festivals(lunar_info["lunar_month"], lunar_info["lunar_day"])
        solar_terms = get_solar_terms(solar_date)
        
        # 创建新的数据点
        new_point = {
            **p,
            "solar_date": solar_date.isoformat(),
            "lunar_year": lunar_info["lunar_year"],
            "lunar_month": lunar_info["lunar_month"],
            "lunar_day": lunar_info["lunar_day"],
            "lunar_date_str": lunar_info["lunar_date_str"],
            "lunar_month_str": lunar_info["lunar_month_str"],
            "lunar_day_str": lunar_info["lunar_day_str"],
            "is_leap_month": lunar_info["is_leap"],
            "festivals": festivals,
            "solar_terms": solar_terms
        }
        result.append(new_point)
    return result

def forecast(fish_id, market_id, horizon=14):
    fish, market, src = find_fish_market(fish_id, market_id)
    if not fish or not market or not src:
        return {"fish": fish, "market": market, "horizon": horizon, "model": "ES", "points": []}
    base = float(src.get("params", {}).get("base", 20.0))
    today = datetime.now(tz.gettz("Asia/Shanghai")).date()
    out = []
    last = base
    for i in range(1, horizon+1):
        d = today + timedelta(days=i)
        v = last + 0.03 * i
        out.append({"date": d.isoformat(), "price": round(v,2), "lower": round(v-0.6,2), "upper": round(v+0.6,2)})
    return {"fish": fish, "market": market, "horizon": horizon, "model": "ES", "points": out}
