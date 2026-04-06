"""
date_generation.py のユニットテスト
"""
import datetime
import pytest

from src.exceptions.exceptions import ValidationError
from src.models.schedule import DateInfo, ScheduleConfig, TimeSettings
from src.services.date_generation import DateGenerationService


@pytest.fixture
def service() -> DateGenerationService:
    return DateGenerationService()


@pytest.fixture
def config(basic_config) -> ScheduleConfig:
    return basic_config


class TestDateGenerationService:
    def test_generates_slots_for_selected_weekdays(self, service, config):
        """水・土・日のみ選択した場合"""
        slots = service.generate(config)
        for slot in slots:
            assert slot.weekday_jp in ("水", "土", "日")

    def test_excludes_excluded_date(self, service, config):
        """除外日（7/15）が含まれないこと"""
        slots = service.generate(config)
        excluded_date = datetime.date(2025, 7, 15)
        assert all(slot.date != excluded_date for slot in slots)

    def test_excludes_excluded_times(self, service, config):
        """除外時間（13時）が含まれないこと"""
        slots = service.generate(config)
        assert all(slot.time != 13 for slot in slots)

    def test_time_span_applied(self, service, config):
        """span=2 なので 9, 11, 15, 17 になること（13は除外）"""
        slots = service.generate(config)
        times = {slot.time for slot in slots}
        assert 9 in times
        assert 11 in times
        assert 13 not in times
        assert 15 in times
        assert 17 in times

    def test_additional_date_out_of_range(self, service):
        """追加日が範囲外でも含まれること"""
        config = ScheduleConfig(
            year=2025,
            start_date=DateInfo(month=7, day=1),
            end_date=DateInfo(month=7, day=5),
            weekdays={d: False for d in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]},
            time=TimeSettings(start=10, end=10, span=1, excluded=[]),
            excluded_dates=[],
            additional_dates=[DateInfo(month=8, day=1)],
            event_title_template="{month}月度練習日程",
        )
        slots = service.generate(config)
        assert any(slot.date == datetime.date(2025, 8, 1) for slot in slots)

    def test_invalid_time_raises(self, service):
        config = ScheduleConfig(
            year=2025,
            start_date=DateInfo(month=7, day=1),
            end_date=DateInfo(month=7, day=31),
            weekdays={},
            time=TimeSettings(start=25, end=17, span=1, excluded=[]),
            excluded_dates=[],
            additional_dates=[],
            event_title_template="{month}月度",
        )
        with pytest.raises(ValidationError):
            service.generate(config)

    def test_start_after_end_raises(self, service):
        config = ScheduleConfig(
            year=2025,
            start_date=DateInfo(month=7, day=31),
            end_date=DateInfo(month=7, day=1),
            weekdays={},
            time=TimeSettings(start=9, end=17, span=1, excluded=[]),
            excluded_dates=[],
            additional_dates=[],
            event_title_template="{month}月度",
        )
        with pytest.raises(ValidationError):
            service.generate(config)

    def test_slots_sorted(self, service, config):
        """結果が日付・時間順になっていること"""
        slots = service.generate(config)
        for i in range(len(slots) - 1):
            a, b = slots[i], slots[i + 1]
            assert (a.date, a.time) <= (b.date, b.time)
