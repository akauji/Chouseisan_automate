"""
日付・時間操作に関するユーティリティ関数
"""
import datetime

from src.config.constants import WEEKDAY_JP
from src.exceptions.exceptions import DateError
from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_japanese_weekday(dt: datetime.date) -> str:
    """日付から日本語の曜日を取得する。

    Args:
        dt: 日付オブジェクト

    Returns:
        日本語の曜日（月、火、水、木、金、土、日）

    Raises:
        DateError: 曜日の変換に失敗した場合
    """
    try:
        weekday_eng = dt.strftime("%A")
        result = WEEKDAY_JP.get(weekday_eng)
        if result is None:
            raise DateError(f"未知の曜日: {weekday_eng}")
        return result
    except DateError:
        raise
    except Exception as e:
        raise DateError(f"曜日の変換に失敗しました: {e}") from e


def get_date_range(
    start: datetime.date, end: datetime.date
) -> list[datetime.date]:
    """開始日から終了日までの日付リストを取得する。

    Args:
        start: 開始日
        end: 終了日

    Returns:
        日付のリスト

    Raises:
        DateError: 開始日が終了日より後の場合
    """
    if start > end:
        raise DateError(
            f"開始日 {start} が終了日 {end} より後です"
        )
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += datetime.timedelta(days=1)
    return dates


def validate_date(year: int, month: int, day: int) -> bool:
    """日付が有効かどうかを検証する。

    Args:
        year: 年
        month: 月
        day: 日

    Returns:
        有効な日付であれば True、そうでなければ False
    """
    try:
        datetime.date(year, month, day)
        return True
    except ValueError:
        return False


def get_month_sequence(
    year: int, start_month: int, end_month: int
) -> list[tuple[int, int]]:
    """開始月から終了月までの (年, 月) のリストを取得する。

    開始月が終了月より後の場合は年をまたぐものとみなし、
    12月の次は翌年1月として扱う（例: 2026年 11〜2月 → 2026/11, 2026/12, 2027/1, 2027/2）。

    Args:
        year: 開始月の年
        start_month: 開始月 (1-12)
        end_month: 終了月 (1-12)

    Returns:
        (年, 月) タプルのリスト

    Raises:
        DateError: 月が 1〜12 の範囲外の場合
    """
    for month in (start_month, end_month):
        if not 1 <= month <= 12:
            raise DateError(f"月が不正です: {month}")
    sequence: list[tuple[int, int]] = []
    current_year, current_month = year, start_month
    while True:
        sequence.append((current_year, current_month))
        if current_month == end_month:
            return sequence
        current_month += 1
        if current_month > 12:
            current_year, current_month = current_year + 1, 1
