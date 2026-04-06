"""
date_utils.py のユニットテスト
"""
import datetime
import pytest

from src.exceptions.exceptions import DateError
from src.utils.date_utils import get_date_range, get_japanese_weekday, validate_date


class TestGetJapaneseWeekday:
    @pytest.mark.parametrize(
        "date, expected",
        [
            (datetime.date(2025, 7, 6), "日"),   # Sunday
            (datetime.date(2025, 7, 7), "月"),   # Monday
            (datetime.date(2025, 7, 8), "火"),   # Tuesday
            (datetime.date(2025, 7, 9), "水"),   # Wednesday
            (datetime.date(2025, 7, 10), "木"),  # Thursday
            (datetime.date(2025, 7, 11), "金"),  # Friday
            (datetime.date(2025, 7, 12), "土"),  # Saturday
        ],
    )
    def test_all_weekdays(self, date, expected):
        assert get_japanese_weekday(date) == expected


class TestGetDateRange:
    def test_single_day(self):
        d = datetime.date(2025, 7, 1)
        result = get_date_range(d, d)
        assert result == [d]

    def test_range(self):
        start = datetime.date(2025, 7, 1)
        end = datetime.date(2025, 7, 3)
        result = get_date_range(start, end)
        assert result == [
            datetime.date(2025, 7, 1),
            datetime.date(2025, 7, 2),
            datetime.date(2025, 7, 3),
        ]

    def test_invalid_range_raises(self):
        start = datetime.date(2025, 7, 5)
        end = datetime.date(2025, 7, 1)
        with pytest.raises(DateError):
            get_date_range(start, end)


class TestValidateDate:
    def test_valid_date(self):
        assert validate_date(2025, 7, 1) is True

    def test_invalid_date(self):
        assert validate_date(2025, 2, 30) is False
