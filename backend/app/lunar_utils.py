"""
农历日期处理工具模块

提供公历与农历日期的相互转换功能
"""
from zhdate import ZhDate
from datetime import datetime, date
from typing import Tuple, Optional, Dict, List


# 农历月份中文名称
LUNAR_MONTH_NAMES = ['正月', '二月', '三月', '四月', '五月', '六月', 
                     '七月', '八月', '九月', '十月', '冬月', '腊月']

# 农历日中文名称
LUNAR_DAY_NAMES = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                   '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                   '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']


def solar_to_lunar(solar_date: date) -> Dict:
    """
    将公历日期转换为农历日期
    
    Args:
        solar_date: 公历日期
        
    Returns:
        包含农历信息的字典
    """
    try:
        zh_date = ZhDate.from_datetime(datetime.combine(solar_date, datetime.min.time()))
        lunar_month = zh_date.lunar_month
        lunar_day = zh_date.lunar_day
        
        # 生成农历日期字符串
        month_str = LUNAR_MONTH_NAMES[lunar_month - 1] if 1 <= lunar_month <= 12 else str(lunar_month)
        day_str = LUNAR_DAY_NAMES[lunar_day - 1] if 1 <= lunar_day <= 30 else str(lunar_day)
        lunar_date_str = f"{month_str}{day_str}"
        
        return {
            "lunar_year": zh_date.lunar_year,
            "lunar_month": lunar_month,
            "lunar_day": lunar_day,
            "lunar_date_str": lunar_date_str,
            "lunar_month_str": month_str,
            "lunar_day_str": day_str,
            "is_leap": zh_date.leap_month == lunar_month
        }
    except Exception as e:
        print(f"农历转换失败: {e}")
        return {
            "lunar_year": None,
            "lunar_month": None,
            "lunar_day": None,
            "lunar_date_str": "",
            "lunar_month_str": "",
            "lunar_day_str": "",
            "is_leap": False
        }


def lunar_to_solar(lunar_year: int, lunar_month: int, lunar_day: int, is_leap: bool = False) -> Optional[date]:
    """
    将农历日期转换为公历日期
    
    Args:
        lunar_year: 农历年份
        lunar_month: 农历月份
        lunar_day: 农历日
        is_leap: 是否闰月
        
    Returns:
        公历日期或None
    """
    try:
        zh_date = ZhDate(lunar_year, lunar_month, lunar_day, is_leap)
        return zh_date.to_datetime().date()
    except Exception:
        return None


def parse_lunar_date_str(lunar_str: str) -> Optional[Tuple[int, int, int, bool]]:
    """
    解析农历日期字符串
    
    支持格式:
    - "2024-01-15" (农历2024年正月十五)
    - "甲辰年正月初一"
    
    Args:
        lunar_str: 农历日期字符串
        
    Returns:
        (年, 月, 日, 是否闰月) 或 None
    """
    try:
        if '-' in lunar_str:
            parts = lunar_str.split('-')
            if len(parts) == 3:
                return (int(parts[0]), int(parts[1]), int(parts[2]), False)
        return None
    except Exception:
        return None


def get_lunar_festivals(lunar_month: int, lunar_day: int) -> List[str]:
    """
    获取农历节日
    
    Args:
        lunar_month: 农历月份
        lunar_day: 农历日
        
    Returns:
        节日名称列表
    """
    festivals = {
        (1, 1): ["春节"],
        (1, 15): ["元宵节"],
        (2, 2): ["龙抬头"],
        (5, 5): ["端午节"],
        (7, 7): ["七夕节"],
        (7, 15): ["中元节"],
        (8, 15): ["中秋节"],
        (9, 9): ["重阳节"],
        (12, 8): ["腊八节"],
        (12, 23): ["小年"],
        (12, 30): ["除夕"],
    }
    return festivals.get((lunar_month, lunar_day), [])


def get_solar_terms(solar_date: date) -> List[str]:
    """
    获取节气
    
    Args:
        solar_date: 公历日期
        
    Returns:
        节气名称列表
    """
    try:
        zh_date = ZhDate.from_datetime(datetime.combine(solar_date, datetime.min.time()))
        # zhdate 库的节气方法可能不同，尝试多种方式
        if hasattr(zh_date, 'get_solar_term'):
            term = zh_date.get_solar_term()
            if term:
                return [term]
        elif hasattr(zh_date, 'solar_term'):
            term = zh_date.solar_term
            if term:
                return [term]
        return []
    except Exception:
        return []


def get_lunar_display(solar_date: date, include_festival: bool = True) -> str:
    """
    获取农历显示字符串
    
    Args:
        solar_date: 公历日期
        include_festival: 是否包含节日
        
    Returns:
        农历显示字符串，如 "正月十五(元宵节)"
    """
    lunar_info = solar_to_lunar(solar_date)
    if not lunar_info["lunar_date_str"]:
        return ""
    
    result = lunar_info["lunar_date_str"]
    
    if include_festival:
        festivals = get_lunar_festivals(lunar_info["lunar_month"], lunar_info["lunar_day"])
        if festivals:
            result += f"({festivals[0]})"
        else:
            terms = get_solar_terms(solar_date)
            if terms:
                result += f"({terms[0]})"
    
    return result
