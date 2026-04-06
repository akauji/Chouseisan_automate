"""
Step4: 結果表示画面
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable

import customtkinter as ctk

from src.models.schedule import EventResult
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ResultFrame(ctk.CTkFrame):
    """イベント作成結果を表示する画面"""

    def __init__(
        self,
        master,
        results: list[EventResult],
        on_restart: Callable[[], None],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self._on_restart = on_restart
        self._build(results)

    def _build(self, results: list[EventResult]) -> None:
        ctk.CTkLabel(
            self,
            text="Step 4 / 作成結果",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(8, 4))

        success_count = sum(1 for r in results if r.success)
        ctk.CTkLabel(
            self,
            text=f"完了: {success_count}/{len(results)} 件成功",
        ).pack(pady=(0, 8))

        # 結果テーブル（ttk.Treeview）
        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(fill="both", expand=True, padx=12, pady=4)

        columns = ("name", "url", "status")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        tree.heading("name", text="イベント名")
        tree.heading("url", text="URL")
        tree.heading("status", text="状態")
        tree.column("name", width=180)
        tree.column("url", width=320)
        tree.column("status", width=70)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        for r in results:
            status = "成功" if r.success else "失敗"
            tree.insert("", "end", values=(r.event_name, r.url, status))

        # URL コピーボタン（成功した1件目のURLを対象）
        first_success = next((r for r in results if r.success), None)
        if first_success:
            url_frame = ctk.CTkFrame(self, fg_color="transparent")
            url_frame.pack(fill="x", padx=12, pady=4)
            url_entry = ctk.CTkEntry(url_frame, width=400)
            url_entry.insert(0, first_success.url)
            url_entry.configure(state="readonly")
            url_entry.pack(side="left", padx=4)
            ctk.CTkButton(
                url_frame,
                text="URLをコピー",
                width=100,
                command=lambda: self._copy_url(first_success.url),
            ).pack(side="left", padx=4)

        # エラーメッセージ表示
        errors = [r for r in results if not r.success]
        if errors:
            err_box = ctk.CTkTextbox(self, height=80, state="disabled")
            err_box.pack(fill="x", padx=12, pady=4)
            err_box.configure(state="normal")
            for r in errors:
                err_box.insert("end", f"[{r.event_name}] {r.error_message}\n")
            err_box.configure(state="disabled")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=12)
        ctk.CTkButton(
            btn_frame,
            text="最初に戻る",
            width=140,
            command=self._on_restart,
        ).pack(side="right", padx=12)

    def _copy_url(self, url: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(url)
