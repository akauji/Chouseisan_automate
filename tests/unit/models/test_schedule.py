"""
schedule.py のユニットテスト
"""
import datetime
import pytest

from src.models.schedule import DateInfo, DateSlot, EventResult, ScheduleConfig, TimeSettings


class TestDateSlotFormat:
    def test_format_single_digit_time(self):
        slot = DateSlot(
            date=datetime.date(2025, 7, 6),
            time=9,
            weekday_jp="日",
            is_additional=False,
        )
        assert slot.format_for_chouseisan() == "7/6(日) 09:00~"

    def test_format_double_digit_time(self):
        slot = DateSlot(
            date=datetime.date(2025, 7, 6),
            time=17,
            weekday_jp="日",
            is_additional=False,
        )
        assert slot.format_for_chouseisan() == "7/6(日) 17:00~"


class TestScheduleConfigGetEventTitle:
    def test_title_with_month_placeholder(self):
        config = ScheduleConfig(
            year=2025,
            start_date=DateInfo(7, 1),
            end_date=DateInfo(7, 31),
            weekdays={},
            time=TimeSettings(9, 17, 1, []),
            excluded_dates=[],
            additional_dates=[],
            event_title_template="{month}月度練習日程",
        )
        assert config.get_event_title(7) == "7月度練習日程"

    def test_title_without_placeholder(self):
        config = ScheduleConfig(
            year=2025,
            start_date=DateInfo(7, 1),
            end_date=DateInfo(7, 31),
            weekdays={},
            time=TimeSettings(9, 17, 1, []),
            excluded_dates=[],
            additional_dates=[],
            event_title_template="固定タイトル",
        )
        assert config.get_event_title(7) == "固定タイトル"


class TestEventResult:
    def test_success(self):
        result = EventResult(event_name="test", url="http://example.com", success=True)
        assert result.success is True
        assert result.error_message == ""

    def test_failure(self):
        result = EventResult(
            event_name="test", url="", success=False, error_message="エラー"
        )
        assert result.success is False
        assert result.error_message == "エラー"
