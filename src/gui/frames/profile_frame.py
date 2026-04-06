"""
プロファイル管理ダイアログ
"""
from tkinter import messagebox
from typing import Callable, Optional

import customtkinter as ctk

from src.exceptions.exceptions import AppError
from src.services.profile_service import ProfileService
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProfileDialog(ctk.CTkToplevel):
    """プロファイルの一覧・削除ができるダイアログ"""

    def __init__(
        self,
        master,
        on_close: Optional[Callable[[], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self.title("プロファイル管理")
        self.geometry("400x320")
        self.resizable(False, False)
        self._profile_service = ProfileService()
        self._on_close = on_close
        self.protocol("WM_DELETE_WINDOW", self._on_destroy)
        self._build()
        self._refresh()

    def _build(self) -> None:
        ctk.CTkLabel(
            self,
            text="プロファイル管理",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(12, 8))

        # リストボックス相当（CTkScrollableFrame + ラベル）
        list_frame = ctk.CTkScrollableFrame(self, height=180)
        list_frame.pack(fill="both", expand=True, padx=16, pady=4)
        self._list_frame = list_frame
        self._selected_name: Optional[str] = None

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=8)
        ctk.CTkButton(btn_frame, text="削除", width=80, command=self._delete_selected).pack(
            side="left", padx=4
        )
        ctk.CTkButton(btn_frame, text="閉じる", width=80, command=self._on_destroy).pack(
            side="right", padx=4
        )

    def _refresh(self) -> None:
        for w in self._list_frame.winfo_children():
            w.destroy()
        names = self._profile_service.list_names()
        if not names:
            ctk.CTkLabel(self._list_frame, text="（プロファイルなし）").pack()
            return
        for name in names:
            row = ctk.CTkFrame(self._list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            btn = ctk.CTkButton(
                row,
                text=name,
                fg_color="transparent",
                text_color=("black", "white"),
                hover_color=("gray80", "gray30"),
                anchor="w",
                command=lambda n=name: self._select(n),
            )
            btn.pack(fill="x")
            if name == self._selected_name:
                btn.configure(fg_color=("gray70", "gray40"))

    def _select(self, name: str) -> None:
        self._selected_name = name
        self._refresh()

    def _delete_selected(self) -> None:
        if not self._selected_name:
            messagebox.showinfo("情報", "削除するプロファイルを選択してください", parent=self)
            return
        if not messagebox.askyesno(
            "確認",
            f"「{self._selected_name}」を削除しますか？",
            parent=self,
        ):
            return
        try:
            self._profile_service.delete(self._selected_name)
            self._selected_name = None
            self._refresh()
        except AppError as e:
            messagebox.showerror("エラー", str(e), parent=self)

    def _on_destroy(self) -> None:
        if self._on_close:
            self._on_close()
        self.destroy()
