"""
スケジュール関連のデータモデル
"""
import datetime
from dataclasses import dataclass, field


@dataclass
class DateInfo:
    """月日を表すデータクラス"""

    month: int
    day: int


@dataclass
class TimeSettings:
    """時間設定を表すデータクラス"""

    start: int           # 開始時間 (0-23)
    end: int             # 終了時間 (0-23)
    span: int            # 時間間隔（時間単位）
    excluded: list[int]  # 除外時間リスト


@dataclass
class ScheduleConfig:
    """スケジュール設定を表すデータクラス"""

    year: int
    start_date: DateInfo
    end_date: DateInfo
    weekdays: dict[str, bool]        # {"Monday": True, ...}
    time: TimeSettings
    excluded_dates: list[DateInfo]
    additional_dates: list[DateInfo]
    event_title_template: str        # "{month}月度練習日程"

    def get_event_title(self, month: int) -> str:
        """イベントタイトルを生成する。

        Args:
            month: 対象月

        Returns:
            フォーマット済みのイベントタイトル
        """
        return self.event_title_template.format(month=month)


@dataclass
class DateSlot:
    """生成された1つの候補日時を表すデータクラス"""

    date: datetime.date
    time: int            # 時間 (0-23)
    weekday_jp: str      # "月", "火", ...
    is_additional: bool  # 追加日かどうか

    def format_for_chouseisan(self) -> str:
        """調整さん入力用にフォーマットする。

        Returns:
            例: "7/6(日) 09:00~"
        """
        return f"{self.date.month}/{self.date.day}({self.weekday_jp}) {self.time:02d}:00~"


@dataclass
class EventResult:
    """イベント作成結果を表すデータクラス"""

    event_name: str
    url: str
    success: bool
    error_message: str = ""
