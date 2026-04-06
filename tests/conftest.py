"""
pytest 共通フィクスチャ
"""
import datetime
import pytest

from src.models.schedule import DateInfo, DateSlot, EventResult, ScheduleConfig, TimeSettings


@pytest.fixture
def basic_config() -> ScheduleConfig:
    """基本的な ScheduleConfig フィクスチャ"""
    return ScheduleConfig(
        year=2025,
        start_date=DateInfo(month=7, day=1),
        end_date=DateInfo(month=7, day=31),
        weekdays={
            "Monday": False,
            "Tuesday": False,
            "Wednesday": True,
            "Thursday": False,
            "Friday": False,
            "Saturday": True,
            "Sunday": True,
        },
        time=TimeSettings(start=9, end=17, span=2, excluded=[13]),
        excluded_dates=[DateInfo(month=7, day=15)],
        additional_dates=[],
        event_title_template="{month}月度練習日程",
    )


@pytest.fixture
def sample_slots() -> list[DateSlot]:
    """サンプル DateSlot リスト"""
    return [
        DateSlot(date=datetime.date(2025, 7, 6), time=9, weekday_jp="日", is_additional=False),
        DateSlot(date=datetime.date(2025, 7, 6), time=11, weekday_jp="日", is_additional=False),
        DateSlot(date=datetime.date(2025, 7, 13), time=9, weekday_jp="日", is_additional=False),
    ]
