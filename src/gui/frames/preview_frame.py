"""
Step2: 日時確認・編集画面
"""
from typing import Callable

import customtkinter as ctk

from src.gui.components.date_list import DateListWidget
from src.models.schedule import DateSlot, ScheduleConfig
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PreviewFrame(ctk.CTkFrame):
    """生成された日時を確認・編集する画面"""

    def __init__(
        self,
        master,
        config: ScheduleConfig,
        slots: list[DateSlot],
        on_back: Callable[[], None],
        on_next: Callable[[ScheduleConfig, list[DateSlot]], None],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self._config = config
        self._on_back = on_back
        self._on_next = on_next
        self._build(slots)

    def _build(self, slots: list[DateSlot]) -> None:
        ctk.CTkLabel(
            self,
            text="Step 2 / 日時確認・編集",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(8, 4))

        event_name = self._config.get_event_title(self._config.start_date.month)
        ctk.CTkLabel(self, text=f"イベント名: {event_name}").pack(pady=(0, 8))

        self._date_list = DateListWidget(self, slots=slots)
        self._date_list.pack(fill="both", expand=True, padx=12, pady=4)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=12)
        ctk.CTkButton(btn_frame, text="← 戻る", width=120, command=self._on_back).pack(
            side="left", padx=12
        )
        ctk.CTkButton(
            btn_frame,
            text="イベントを作成 →",
            width=160,
            command=self._on_create,
        ).pack(side="right", padx=12)

    def _on_create(self) -> None:
        slots = self._date_list.get_slots()
        if not slots:
            from tkinter import messagebox
            messagebox.showwarning("確認", "候補日時が1件もありません")
            return
        self._on_next(self._config, slots)
