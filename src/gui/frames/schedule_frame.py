"""
Step1: 設定入力画面
"""
import datetime
from tkinter import messagebox
from typing import Callable, Optional

import customtkinter as ctk

from src.config.constants import DEFAULT_EVENT_TITLE_TEMPLATE, DEFAULT_TIME_END, DEFAULT_TIME_SPAN, DEFAULT_TIME_START
from src.exceptions.exceptions import AppError
from src.gui.components.weekday_selector import WeekdaySelector
from src.models.schedule import DateInfo, ScheduleConfig, TimeSettings
from src.services.profile_service import ProfileService
from src.utils.date_utils import validate_date
from src.utils.logger import get_logger

logger = get_logger(__name__)

_MONTHS = [str(i) for i in range(1, 13)]
_DAYS = [str(i) for i in range(1, 32)]
_HOURS = [str(i) for i in range(0, 24)]
_SPANS = [str(i) for i in range(1, 13)]


class ScheduleFrame(ctk.CTkScrollableFrame):
    """設定入力画面"""

    def __init__(
        self,
        master,
        on_next: Callable[[ScheduleConfig], None],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self._on_next = on_next
        self._profile_service = ProfileService()
        self._build()

    # ------------------------------------------------------------------
    # UI構築
    # ------------------------------------------------------------------

    def _build(self) -> None:
        pad = {"padx": 12, "pady": 6}

        # タイトル
        ctk.CTkLabel(self, text="Step 1 / 設定入力", font=ctk.CTkFont(size=18, weight="bold")).pack(
            pady=(8, 16)
        )

        # プロファイル行
        pf_frame = ctk.CTkFrame(self, fg_color="transparent")
        pf_frame.pack(fill="x", **pad)
        ctk.CTkLabel(pf_frame, text="プロファイル:").pack(side="left")
        self._profile_combo = ctk.CTkComboBox(pf_frame, values=self._load_profile_names(), width=180)
        self._profile_combo.pack(side="left", padx=8)
        ctk.CTkButton(pf_frame, text="読み込み", width=80, command=self._load_profile).pack(side="left", padx=4)
        ctk.CTkButton(pf_frame, text="保存", width=60, command=self._save_profile).pack(side="left", padx=4)
        ctk.CTkButton(pf_frame, text="管理", width=60, command=self._open_profile_manager).pack(side="left", padx=4)

        # 年
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", **pad)
        ctk.CTkLabel(row, text="年:", width=100, anchor="w").pack(side="left")
        self._year_var = ctk.StringVar(value=str(datetime.date.today().year))
        ctk.CTkEntry(row, textvariable=self._year_var, width=100).pack(side="left")

        # 期間（開始日・終了日）
        date_frame = ctk.CTkFrame(self)
        date_frame.pack(fill="x", **pad)
        ctk.CTkLabel(date_frame, text="期間", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=6, sticky="w", padx=8, pady=(8, 4)
        )
        ctk.CTkLabel(date_frame, text="開始月:").grid(row=1, column=0, padx=8, pady=4, sticky="w")
        self._start_month = ctk.CTkComboBox(date_frame, values=_MONTHS, width=70)
        self._start_month.grid(row=1, column=1, padx=4)
        ctk.CTkLabel(date_frame, text="日:").grid(row=1, column=2, padx=4)
        self._start_day = ctk.CTkComboBox(date_frame, values=_DAYS, width=70)
        self._start_day.grid(row=1, column=3, padx=4)

        ctk.CTkLabel(date_frame, text="終了月:").grid(row=2, column=0, padx=8, pady=4, sticky="w")
        self._end_month = ctk.CTkComboBox(date_frame, values=_MONTHS, width=70)
        self._end_month.grid(row=2, column=1, padx=4)
        ctk.CTkLabel(date_frame, text="日:").grid(row=2, column=2, padx=4)
        self._end_day = ctk.CTkComboBox(date_frame, values=_DAYS, width=70)
        self._end_day.grid(row=2, column=3, padx=4)

        # 曜日
        wd_frame = ctk.CTkFrame(self)
        wd_frame.pack(fill="x", **pad)
        ctk.CTkLabel(wd_frame, text="曜日", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=8, pady=(8, 4))
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
        self._ex_time_list = ctk.CTkTextbox(ex_time_frame, height=50, width=200, state="disabled")
        self._ex_time_list.grid(row=2, column=0, columnspan=3, padx=8, pady=4)
        self._ex_times: list[int] = []

        # 除外日
        ex_date_frame = ctk.CTkFrame(self)
        ex_date_frame.pack(fill="x", **pad)
        ctk.CTkLabel(ex_date_frame, text="除外日", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=6, sticky="w", padx=8, pady=(8, 4)
        )
        ctk.CTkLabel(ex_date_frame, text="月:").grid(row=1, column=0, padx=8, sticky="w")
        self._ex_date_month = ctk.CTkComboBox(ex_date_frame, values=_MONTHS, width=70)
        self._ex_date_month.grid(row=1, column=1, padx=4, pady=4)
        ctk.CTkLabel(ex_date_frame, text="日:").grid(row=1, column=2, padx=4)
        self._ex_date_day = ctk.CTkComboBox(ex_date_frame, values=_DAYS, width=70)
        self._ex_date_day.grid(row=1, column=3, padx=4)
        ctk.CTkButton(ex_date_frame, text="追加", width=60, command=self._add_ex_date).grid(row=1, column=4, padx=4)
        ctk.CTkButton(ex_date_frame, text="削除", width=60, command=self._del_ex_date).grid(row=1, column=5, padx=4)
        self._ex_date_list = ctk.CTkTextbox(ex_date_frame, height=50, width=200, state="disabled")
        self._ex_date_list.grid(row=2, column=0, columnspan=6, padx=8, pady=4)
        self._ex_dates: list[DateInfo] = []

        # 追加日
        add_date_frame = ctk.CTkFrame(self)
        add_date_frame.pack(fill="x", **pad)
        ctk.CTkLabel(add_date_frame, text="追加日（曜日不問）", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=6, sticky="w", padx=8, pady=(8, 4)
        )
        ctk.CTkLabel(add_date_frame, text="月:").grid(row=1, column=0, padx=8, sticky="w")
        self._add_date_month = ctk.CTkComboBox(add_date_frame, values=_MONTHS, width=70)
        self._add_date_month.grid(row=1, column=1, padx=4, pady=4)
        ctk.CTkLabel(add_date_frame, text="日:").grid(row=1, column=2, padx=4)
        self._add_date_day = ctk.CTkComboBox(add_date_frame, values=_DAYS, width=70)
        self._add_date_day.grid(row=1, column=3, padx=4)
        ctk.CTkButton(add_date_frame, text="追加", width=60, command=self._add_additional_date).grid(row=1, column=4, padx=4)
        ctk.CTkButton(add_date_frame, text="削除", width=60, command=self._del_additional_date).grid(row=1, column=5, padx=4)
        self._add_date_list = ctk.CTkTextbox(add_date_frame, height=50, width=200, state="disabled")
        self._add_date_list.grid(row=2, column=0, columnspan=6, padx=8, pady=4)
        self._additional_dates: list[DateInfo] = []

        # イベントタイトルテンプレート
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", **pad)
        ctk.CTkLabel(title_frame, text="タイトルテンプレート:", width=150, anchor="w").pack(side="left")
        self._title_template = ctk.CTkEntry(title_frame, width=250)
        self._title_template.pack(side="left")

        # ボタン行
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=16)
        ctk.CTkButton(btn_frame, text="日時を生成 →", width=160, command=self._on_generate).pack(side="right", padx=12)

        # デフォルト値
        self._set_defaults()

    # ------------------------------------------------------------------
    # デフォルト値設定
    # ------------------------------------------------------------------

    def _set_defaults(self) -> None:
        today = datetime.date.today()
        self._start_month.set(str(today.month))
        self._start_day.set("1")
        import calendar
        last_day = calendar.monthrange(today.year, today.month)[1]
        self._end_month.set(str(today.month))
        self._end_day.set(str(last_day))
        self._weekday_selector.set({"Saturday": True, "Sunday": True,
                                    "Monday": False, "Tuesday": False,
                                    "Wednesday": False, "Thursday": False,
                                    "Friday": False})
        self._time_start.set(str(DEFAULT_TIME_START))
        self._time_end.set(str(DEFAULT_TIME_END))
        self._time_span.set(str(DEFAULT_TIME_SPAN))
        self._title_template.insert(0, DEFAULT_EVENT_TITLE_TEMPLATE)

    # ------------------------------------------------------------------
    # 除外時間リスト操作
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
    # 除外日リスト操作
    # ------------------------------------------------------------------

    def _add_ex_date(self) -> None:
        try:
            m, d = int(self._ex_date_month.get()), int(self._ex_date_day.get())
        except ValueError:
            return
        year = int(self._year_var.get()) if self._year_var.get().isdigit() else datetime.date.today().year
        if validate_date(year, m, d):
            di = DateInfo(month=m, day=d)
            if di not in self._ex_dates:
                self._ex_dates.append(di)
                self._refresh_ex_date_list()

    def _del_ex_date(self) -> None:
        try:
            m, d = int(self._ex_date_month.get()), int(self._ex_date_day.get())
        except ValueError:
            return
        di = DateInfo(month=m, day=d)
        if di in self._ex_dates:
            self._ex_dates.remove(di)
            self._refresh_ex_date_list()

    def _refresh_ex_date_list(self) -> None:
        self._ex_date_list.configure(state="normal")
        self._ex_date_list.delete("1.0", "end")
        self._ex_date_list.insert("end", ", ".join(f"{d.month}/{d.day}" for d in self._ex_dates))
        self._ex_date_list.configure(state="disabled")

    # ------------------------------------------------------------------
    # 追加日リスト操作
    # ------------------------------------------------------------------

    def _add_additional_date(self) -> None:
        try:
            m, d = int(self._add_date_month.get()), int(self._add_date_day.get())
        except ValueError:
            return
        year = int(self._year_var.get()) if self._year_var.get().isdigit() else datetime.date.today().year
        if validate_date(year, m, d):
            di = DateInfo(month=m, day=d)
            if di not in self._additional_dates:
                self._additional_dates.append(di)
                self._refresh_add_date_list()

    def _del_additional_date(self) -> None:
        try:
            m, d = int(self._add_date_month.get()), int(self._add_date_day.get())
        except ValueError:
            return
        di = DateInfo(month=m, day=d)
        if di in self._additional_dates:
            self._additional_dates.remove(di)
            self._refresh_add_date_list()

    def _refresh_add_date_list(self) -> None:
        self._add_date_list.configure(state="normal")
        self._add_date_list.delete("1.0", "end")
        self._add_date_list.insert("end", ", ".join(f"{d.month}/{d.day}" for d in self._additional_dates))
        self._add_date_list.configure(state="disabled")

    # ------------------------------------------------------------------
    # プロファイル操作
    # ------------------------------------------------------------------

    def _load_profile_names(self) -> list[str]:
        try:
            return self._profile_service.list_names() or [""]
        except AppError:
            return [""]

    def _load_profile(self) -> None:
        name = self._profile_combo.get().strip()
        if not name:
            return
        try:
            profile = self._profile_service.load(name)
            self._apply_config(profile.config)
        except AppError as e:
            messagebox.showerror("エラー", str(e))

    def _save_profile(self) -> None:
        name = self._profile_combo.get().strip()
        if not name:
            messagebox.showwarning("警告", "プロファイル名を入力してください")
            return
        try:
            config = self._build_config()
            import datetime as dt
            from src.models.profile import Profile
            now = dt.datetime.now().isoformat()
            profile = Profile(name=name, config=config, created_at=now, updated_at=now)
            self._profile_service.save(profile)
            # コンボボックスを更新
            self._profile_combo.configure(values=self._load_profile_names())
            messagebox.showinfo("保存完了", f"プロファイル「{name}」を保存しました")
        except AppError as e:
            messagebox.showerror("エラー", str(e))

    def _open_profile_manager(self) -> None:
        # App への参照を辿る
        master = self.master
        while master is not None and not hasattr(master, "show_profile"):
            master = getattr(master, "master", None)
        if master and hasattr(master, "show_profile"):
            master.show_profile(on_close=lambda: self._profile_combo.configure(values=self._load_profile_names()))

    def _apply_config(self, config: ScheduleConfig) -> None:
        self._year_var.set(str(config.year))
        self._start_month.set(str(config.start_date.month))
        self._start_day.set(str(config.start_date.day))
        self._end_month.set(str(config.end_date.month))
        self._end_day.set(str(config.end_date.day))
        self._weekday_selector.set(config.weekdays)
        self._time_start.set(str(config.time.start))
        self._time_end.set(str(config.time.end))
        self._time_span.set(str(config.time.span))
        self._ex_times = list(config.time.excluded)
        self._refresh_ex_time_list()
        self._ex_dates = list(config.excluded_dates)
        self._refresh_ex_date_list()
        self._additional_dates = list(config.additional_dates)
        self._refresh_add_date_list()
        self._title_template.delete(0, "end")
        self._title_template.insert(0, config.event_title_template)

    # ------------------------------------------------------------------
    # 入力値収集・次画面へ
    # ------------------------------------------------------------------

    def _build_config(self) -> ScheduleConfig:
        year = int(self._year_var.get())
        return ScheduleConfig(
            year=year,
            start_date=DateInfo(
                month=int(self._start_month.get()),
                day=int(self._start_day.get()),
            ),
            end_date=DateInfo(
                month=int(self._end_month.get()),
                day=int(self._end_day.get()),
            ),
            weekdays=self._weekday_selector.get(),
            time=TimeSettings(
                start=int(self._time_start.get()),
                end=int(self._time_end.get()),
                span=int(self._time_span.get()),
                excluded=list(self._ex_times),
            ),
            excluded_dates=list(self._ex_dates),
            additional_dates=list(self._additional_dates),
            event_title_template=self._title_template.get(),
        )

    def _on_generate(self) -> None:
        try:
            config = self._build_config()
        except (ValueError, KeyError) as e:
            messagebox.showwarning("入力エラー", f"入力値を確認してください: {e}")
            return
        self._on_next(config)
