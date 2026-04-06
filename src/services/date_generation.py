"""
日時生成サービス（ScheduleConfig → list[DateSlot]）
"""
import datetime

from src.exceptions.exceptions import DateError, ValidationError
from src.models.schedule import DateInfo, DateSlot, ScheduleConfig
from src.utils.date_utils import get_date_range, get_japanese_weekday
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DateGenerationService:
    """ScheduleConfig から DateSlot リストを生成するサービス"""

    def generate(self, config: ScheduleConfig) -> list[DateSlot]:
        """候補日時リストを生成する。

        Args:
            config: スケジュール設定

        Returns:
            生成された DateSlot のリスト（日付・時間順）

        Raises:
            ValidationError: 設定値が不正な場合
            DateError: 日付処理に失敗した場合
        """
        self._validate(config)

        start = datetime.date(config.year, config.start_date.month, config.start_date.day)
        end = datetime.date(config.year, config.end_date.month, config.end_date.day)

        if start > end:
            raise ValidationError("開始日が終了日より後です", field="start_date")

        date_range = get_date_range(start, end)

        # 除外日のセット
        excluded_set = {
            datetime.date(config.year, d.month, d.day)
            for d in config.excluded_dates
        }

        # 追加日のセット
        additional_set = {
            datetime.date(config.year, d.month, d.day)
            for d in config.additional_dates
        }

        slots: list[DateSlot] = []

        for date in date_range:
            if date in excluded_set:
                continue

            is_additional = date in additional_set
            weekday_name = date.strftime("%A")  # Monday, Tuesday, ...

            # 通常日：曜日チェック
            if not is_additional and not config.weekdays.get(weekday_name, False):
                continue

            weekday_jp = get_japanese_weekday(date)
            time_slots = self._generate_time_slots(config, weekday_jp, date, is_additional)
            slots.extend(time_slots)

        # 追加日が範囲外の場合も処理
        for additional_date_info in config.additional_dates:
            additional_date = datetime.date(
                config.year, additional_date_info.month, additional_date_info.day
            )
            if additional_date < start or additional_date > end:
                if additional_date not in excluded_set:
                    weekday_jp = get_japanese_weekday(additional_date)
                    time_slots = self._generate_time_slots(
                        config, weekday_jp, additional_date, is_additional=True
                    )
                    slots.extend(time_slots)

        slots.sort(key=lambda s: (s.date, s.time))
        logger.info(f"候補日時を {len(slots)} 件生成しました")
        return slots

    def _generate_time_slots(
        self,
        config: ScheduleConfig,
        weekday_jp: str,
        date: datetime.date,
        is_additional: bool,
    ) -> list[DateSlot]:
        """指定日の時間スロットを生成する。

        Args:
            config: スケジュール設定
            weekday_jp: 日本語曜日
            date: 対象日
            is_additional: 追加日フラグ

        Returns:
            DateSlot のリスト
        """
        slots: list[DateSlot] = []
        current_time = config.time.start
        while current_time <= config.time.end:
            if current_time not in config.time.excluded:
                slots.append(
                    DateSlot(
                        date=date,
                        time=current_time,
                        weekday_jp=weekday_jp,
                        is_additional=is_additional,
                    )
                )
            current_time += config.time.span
        return slots

    def _validate(self, config: ScheduleConfig) -> None:
        """設定値を検証する。

        Args:
            config: スケジュール設定

        Raises:
            ValidationError: 不正な値が含まれる場合
        """
        if not 0 <= config.time.start <= 23:
            raise ValidationError(
                f"開始時間が不正です: {config.time.start}", field="time.start"
            )
        if not 0 <= config.time.end <= 23:
            raise ValidationError(
                f"終了時間が不正です: {config.time.end}", field="time.end"
            )
        if config.time.start > config.time.end:
            raise ValidationError("開始時間が終了時間より後です", field="time.start")
        if config.time.span <= 0:
            raise ValidationError(
                f"時間間隔が不正です: {config.time.span}", field="time.span"
            )
        if not config.event_title_template:
            raise ValidationError("イベントタイトルテンプレートが空です", field="event_title_template")
