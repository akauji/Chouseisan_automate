"""
メインウィンドウ（画面遷移管理）
"""
import threading
from typing import Optional

import customtkinter as ctk

from src.exceptions.exceptions import AppError
from src.models.schedule import DateSlot, EventResult, ScheduleConfig
from src.plugins.base import PluginManager
from src.plugins.chouseisan.plugin import ChouseisanPlugin
from src.services.date_generation import DateGenerationService
from src.services.event_creation import EventCreationService
from src.utils.logger import get_logger

logger = get_logger(__name__)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """アプリケーションのメインウィンドウ"""

    def __init__(self, bulk_mode: bool = False) -> None:
        super().__init__()
        self.title("調整さん自動作成ツール V2")
        self.geometry("700x600")
        self.resizable(True, True)

        self._bulk_mode = bulk_mode

        # サービス初期化
        plugin_manager = PluginManager()
        plugin_manager.register(ChouseisanPlugin())
        self._event_service = EventCreationService(plugin_manager)
        self._date_service = DateGenerationService()

        # 画面遷移用コンテナ
        self._container = ctk.CTkFrame(self, fg_color="transparent")
        self._container.pack(fill="both", expand=True, padx=10, pady=10)

        # 遅延インポート（循環参照回避）
        self._show_initial_screen()

    # ------------------------------------------------------------------
    # 画面遷移
    # ------------------------------------------------------------------

    def _clear(self) -> None:
        """コンテナ内の全ウィジェットを削除する"""
        for w in self._container.winfo_children():
            w.destroy()

    def _show_initial_screen(self) -> None:
        if self._bulk_mode:
            self.show_bulk()
        else:
            self.show_schedule()

    def show_schedule(self) -> None:
        """Step1: 設定入力画面を表示する"""
        from src.gui.frames.schedule_frame import ScheduleFrame

        self._clear()
        frame = ScheduleFrame(self._container, on_next=self._on_schedule_done)
        frame.pack(fill="both", expand=True)

    def _on_schedule_done(self, config: ScheduleConfig) -> None:
        """設定入力完了コールバック"""
        try:
            if self._date_service.is_period_too_long(config) and not self._confirm_long_period(config):
                return
            slots = self._date_service.generate(config)
            self.show_preview(config, slots)
        except AppError as e:
            self._show_error(str(e))

    def _confirm_long_period(self, config: ScheduleConfig) -> bool:
        """期間が長すぎる場合に続行してよいかユーザーに確認する。

        Args:
            config: スケジュール設定

        Returns:
            続行する場合 True
        """
        from tkinter import messagebox

        days = self._date_service.get_period_days(config)
        return messagebox.askyesno(
            "期間の確認",
            f"期間が {days} 日間（約{days // 30}か月）あります。\n"
            "開始日・終了日の入力ミスではありませんか？\n\n"
            "このまま候補日時を生成しますか？",
            icon="warning",
        )

    def show_preview(self, config: ScheduleConfig, slots: list[DateSlot]) -> None:
        """Step2: 日時確認・編集画面を表示する"""
        from src.gui.frames.preview_frame import PreviewFrame

        self._clear()
        frame = PreviewFrame(
            self._container,
            config=config,
            slots=slots,
            on_back=self.show_schedule,
            on_next=self._on_preview_done,
        )
        frame.pack(fill="both", expand=True)

    def _on_preview_done(self, config: ScheduleConfig, slots: list[DateSlot]) -> None:
        """日時確認完了コールバック"""
        self.show_progress(config, slots)

    def show_progress(self, config: ScheduleConfig, slots: list[DateSlot]) -> None:
        """Step3: 処理中画面を表示する"""
        from src.gui.frames.progress_frame import ProgressFrame

        self._clear()
        frame = ProgressFrame(self._container)
        frame.pack(fill="both", expand=True)

        event_name = config.get_event_title(config.start_date.month)

        def run() -> None:
            try:
                result = self._event_service.create_event(event_name, slots)
                self.after(0, lambda: self.show_result([result]))
            except AppError as e:
                result = EventResult(
                    event_name=event_name, url="", success=False, error_message=str(e)
                )
                self.after(0, lambda: self.show_result([result]))

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def show_result(self, results: list[EventResult]) -> None:
        """Step4: 結果表示画面を表示する"""
        from src.gui.frames.result_frame import ResultFrame

        self._clear()
        frame = ResultFrame(
            self._container,
            results=results,
            on_restart=self.show_schedule,
        )
        frame.pack(fill="both", expand=True)

    def show_bulk(self) -> None:
        """バルクモード画面を表示する"""
        from src.gui.frames.bulk_frame import BulkFrame

        self._clear()
        frame = BulkFrame(
            self._container,
            event_service=self._event_service,
            date_service=self._date_service,
            on_result=self.show_result,
        )
        frame.pack(fill="both", expand=True)

    def show_profile(self, on_close: Optional[callable] = None) -> None:
        """プロファイル管理画面をダイアログで表示する"""
        from src.gui.frames.profile_frame import ProfileDialog

        dialog = ProfileDialog(self, on_close=on_close)
        dialog.grab_set()

    def _show_error(self, message: str) -> None:
        from tkinter import messagebox

        messagebox.showerror("エラー", message, parent=self)
