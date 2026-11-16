"""
バルクモード：複数月まとめてイベント作成する画面
"""
import calendar
import datetime
import threading
from tkinter import messagebox
from typing import Callable

import customtkinter as ctk

from src.config.constants import DEFAULT_EVENT_TITLE_TEMPLATE, DEFAULT_TIME_END, DEFAULT_TIME_SPAN, DEFAULT_TIME_START
from src.exceptions.exceptions import AppError
from src.gui.components.weekday_selector import WeekdaySelector
from src.models.schedule import DateInfo, EventResult, ScheduleConfig, TimeSettings
from src.services.date_generation import DateGenerationService
from src.services.event_creation import EventCreationService
from src.utils.date_utils import get_month_sequence, validate_date
from src.utils.logger import get_logger

logger = get_logger(__name__)

_MONTHS = [str(i) for i in range(1, 13)]
_HOURS = [str(i) for i in range(0, 24)]
_SPANS = [str(i) for i in range(1, 13)]


class BulkFrame(ctk.CTkScrollableFrame):
    """複数月一括イベント作成画面"""

    def __init__(
        self,
        master,
        event_service: EventCreationService,
        date_service: DateGenerationService,
        on_result: Callable[[list[EventResult]], None],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self._event_service = event_service
        self._date_service = date_service
        self._on_result = on_result
        self._ex_times: list[int] = []
        self._ex_dates: list[DateInfo] = []
        self._build()

    def _build(self) -> None:
        pad = {"padx": 12, "pady": 6}

        ctk.CTkLabel(
            self,
            text="バルクモード / 一括作成",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(8, 16))

        # 年
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", **pad)
        ctk.CTkLabel(row, text="年:", width=100, anchor="w").pack(side="left")
        self._year_var = ctk.StringVar(value=str(datetime.date.today().year))
        ctk.CTkEntry(row, textvariable=self._year_var, width=100).pack(side="left")

        # 月範囲
        month_frame = ctk.CTkFrame(self)
        month_frame.pack(fill="x", **pad)
        ctk.CTkLabel(month_frame, text="月範囲", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", padx=8, pady=(8, 4)
        )
        ctk.CTkLabel(month_frame, text="開始月:").grid(row=1, column=0, padx=8, sticky="w")
        self._start_month = ctk.CTkComboBox(month_frame, values=_MONTHS, width=70)
        self._start_month.grid(row=1, column=1, padx=4, pady=4)
        ctk.CTkLabel(month_frame, text="終了月:").grid(row=1, column=2, padx=8, sticky="w")
        self._end_month = ctk.CTkComboBox(month_frame, values=_MONTHS, width=70)
        self._end_month.grid(row=1, column=3, padx=4)

        # 曜日
        wd_frame = ctk.CTkFrame(self)
        wd_frame.pack(fill="x", **pad)
        ctk.CTkLabel(wd_frame, text="曜日", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=8, pady=(8, 4)
        )
        self._weekday_selector = WeekdaySelector(wd_frame)
        self._weekday_selector.pack(padx=8, pady=4)

        # 時間設定
        time_frame = ctk.CTkFrame(self)
        time_frame.pack(fill="x", **pad)
        ctk.CTkLabel(time_frame, text="時間設定", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", padx=8, pady=(8, 4)
        )
        ctk.CTkLabel(time_frame, text="開始:").grid(row=1, column=0, padx=8, sticky="w")
        self._time_start = ctk.CTkComboBox(time_frame, values=_HOURS, width=70)
        self._time_start.grid(row=1, column=1, padx=4, pady=4)
        ctk.CTkLabel(time_frame, text="終了:").grid(row=1, column=2, padx=8, sticky="w")
        self._time_end = ctk.CTkComboBox(time_frame, values=_HOURS, width=70)
        self._time_end.grid(row=1, column=3, padx=4)
        ctk.CTkLabel(time_frame, text="間隔(h):").grid(row=2, column=0, padx=8, sticky="w")
        self._time_span = ctk.CTkComboBox(time_frame, values=_SPANS, width=70)
        self._time_span.grid(row=2, column=1, padx=4, pady=4)

        # 除外時間
        ex_time_frame = ctk.CTkFrame(self)
        ex_time_frame.pack(fill="x", **pad)
        ctk.CTkLabel(ex_time_frame, text="除外時間", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", padx=8, pady=(8, 4)
        )
        self._ex_time_entry = ctk.CTkComboBox(ex_time_frame, values=_HOURS, width=70)
        self._ex_time_entry.grid(row=1, column=0, padx=8, pady=4)
        ctk.CTkButton(ex_time_frame, text="追加", width=60, command=self._add_ex_time).grid(row=1, column=1, padx=4)
        ctk.CTkButton(ex_time_frame, text="削除", width=60, command=self._del_ex_time).grid(row=1, column=2, padx=4)
        self._ex_time_list = ctk.CTkTextbox(ex_time_frame, height=40, width=200, state="disabled")
        self._ex_time_list.grid(row=2, column=0, columnspan=3, padx=8, pady=4)

        # 除外日（毎月共通：日のみ指定）
        ex_date_frame = ctk.CTkFrame(self)
        ex_date_frame.pack(fill="x", **pad)
        ctk.CTkLabel(
            ex_date_frame,
            text="除外日（毎月共通：日のみ）",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=8, pady=(8, 4))
        ctk.CTkLabel(ex_date_frame, text="日:").grid(row=1, column=0, padx=8, sticky="w")
        self._ex_day_entry = ctk.CTkEntry(ex_date_frame, width=70)
        self._ex_day_entry.grid(row=1, column=1, padx=4, pady=4)
        ctk.CTkButton(ex_date_frame, text="追加", width=60, command=self._add_ex_day).grid(row=1, column=2, padx=4)
        ctk.CTkButton(ex_date_frame, text="削除", width=60, command=self._del_ex_day).grid(row=1, column=3, padx=4)
        self._ex_day_list = ctk.CTkTextbox(ex_date_frame, height=40, width=200, state="disabled")
        self._ex_day_list.grid(row=2, column=0, columnspan=4, padx=8, pady=4)
        self._ex_days: list[int] = []

        # イベントタイトルテンプレート
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", **pad)
        ctk.CTkLabel(title_frame, text="タイトルテンプレート:", width=150, anchor="w").pack(side="left")
        self._title_template = ctk.CTkEntry(title_frame, width=250)
        self._title_template.pack(side="left")

        # ログ
        ctk.CTkLabel(self, text="ログ:").pack(anchor="w", padx=12)
        self._log_box = ctk.CTkTextbox(self, height=120, state="disabled")
        self._log_box.pack(fill="x", padx=12, pady=4)

        # ボタン
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=16)
        self._run_btn = ctk.CTkButton(btn_frame, text="一括作成", width=160, command=self._on_run)
        self._run_btn.pack(side="right", padx=12)

        # デフォルト値
        self._set_defaults()

    def _set_defaults(self) -> None:
        today = datetime.date.today()
        self._start_month.set(str(today.month))
        self._end_month.set(str(min(today.month + 2, 12)))
        self._weekday_selector.set(
            {"Saturday": True, "Sunday": True,
             "Monday": False, "Tuesday": False,
             "Wednesday": False, "Thursday": False, "Friday": False}
        )
        self._time_start.set(str(DEFAULT_TIME_START))
        self._time_end.set(str(DEFAULT_TIME_END))
        self._time_span.set(str(DEFAULT_TIME_SPAN))
        self._title_template.insert(0, DEFAULT_EVENT_TITLE_TEMPLATE)

    # ------------------------------------------------------------------
    # 除外時間
    # ------------------------------------------------------------------

    def _add_ex_time(self) -> None:
        try:
            t = int(self._ex_time_entry.get())
        except ValueError:
            return
        if 0 <= t <= 23 and t not in self._ex_times:
            self._ex_times.append(t)
            self._ex_times.sort()
            self._refresh_ex_time_list()

    def _del_ex_time(self) -> None:
        try:
            t = int(self._ex_time_entry.get())
        except ValueError:
            return
        if t in self._ex_times:
            self._ex_times.remove(t)
            self._refresh_ex_time_list()

    def _refresh_ex_time_list(self) -> None:
        self._ex_time_list.configure(state="normal")
        self._ex_time_list.delete("1.0", "end")
        self._ex_time_list.insert("end", ", ".join(f"{t:02d}:00" for t in self._ex_times))
        self._ex_time_list.configure(state="disabled")

    # ------------------------------------------------------------------
    # 除外日（日のみ）
    # ------------------------------------------------------------------

    def _add_ex_day(self) -> None:
        try:
            d = int(self._ex_day_entry.get())
        except ValueError:
            return
        if 1 <= d <= 31 and d not in self._ex_days:
            self._ex_days.append(d)
            self._ex_days.sort()
            self._refresh_ex_day_list()

    def _del_ex_day(self) -> None:
        try:
            d = int(self._ex_day_entry.get())
        except ValueError:
            return
        if d in self._ex_days:
            self._ex_days.remove(d)
            self._refresh_ex_day_list()

    def _refresh_ex_day_list(self) -> None:
        self._ex_day_list.configure(state="normal")
        self._ex_day_list.delete("1.0", "end")
        self._ex_day_list.insert("end", ", ".join(f"{d}日" for d in self._ex_days))
        self._ex_day_list.configure(state="disabled")

    # ------------------------------------------------------------------
    # 実行
    # ------------------------------------------------------------------

    def _append_log(self, msg: str) -> None:
        self._log_box.configure(state="normal")
        self._log_box.insert("end", msg + "\n")
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _on_run(self) -> None:
        try:
            year = int(self._year_var.get())
            start_month = int(self._start_month.get())
            end_month = int(self._end_month.get())
        except ValueError:
            messagebox.showwarning("入力エラー", "年・月を正しく入力してください")
            return
        try:
            months = get_month_sequence(year, start_month, end_month)
        except AppError as e:
            messagebox.showwarning("入力エラー", str(e))
            return

        self._run_btn.configure(state="disabled")
        self._append_log("一括作成を開始します...")

        def run() -> None:
            results: list[EventResult] = []
            for year, month in months:
                last_day = calendar.monthrange(year, month)[1]
                # 除外日：月ごとに dateinfo に変換（無効な日は除外）
                ex_dates = [
                    DateInfo(month=month, day=d)
                    for d in self._ex_days
                    if validate_date(year, month, d)
                ]
                config = ScheduleConfig(
                    year=year,
                    start_date=DateInfo(month=month, day=1),
                    end_date=DateInfo(month=month, day=last_day),
                    weekdays=self._weekday_selector.get(),
                    time=TimeSettings(
                        start=int(self._time_start.get()),
                        end=int(self._time_end.get()),
                        span=int(self._time_span.get()),
                        excluded=list(self._ex_times),
                    ),
                    excluded_dates=ex_dates,
                    additional_dates=[],
                    event_title_template=self._title_template.get(),
                )
                event_name = config.get_event_title(month)
                self.after(0, lambda m=event_name: self._append_log(f"作成中: {m}"))
                try:
                    slots = self._date_service.generate(config)
                    result = self._event_service.create_event(event_name, slots)
                    results.append(result)
                    self.after(0, lambda r=result: self._append_log(
                        f"  → {'成功' if r.success else '失敗'}: {r.url}"
                    ))
                except AppError as e:
                    results.append(
                        EventResult(event_name=event_name, url="", success=False, error_message=str(e))
                    )
                    self.after(0, lambda msg=str(e): self._append_log(f"  → エラー: {msg}"))

            self.after(0, lambda: self._on_done(results))

        threading.Thread(target=run, daemon=True).start()

    def _on_done(self, results: list[EventResult]) -> None:
        self._run_btn.configure(state="normal")
        self._append_log("完了しました")
        self._on_result(results)
