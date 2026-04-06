"""
日時リストウィジェット（削除・手動追加対応）
"""
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

import customtkinter as ctk

from src.models.schedule import DateSlot
from src.utils.date_utils import get_japanese_weekday, validate_date


class DateListWidget(ctk.CTkFrame):
    """DateSlot リストを表示・編集できるウィジェット"""

    def __init__(self, master, slots: list[DateSlot], **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._slots: list[DateSlot] = list(slots)
        self._build()

    def _build(self) -> None:
        # ツールバー
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(toolbar, text=f"候補日時: {len(self._slots)} 件").pack(side="left")
        ctk.CTkButton(toolbar, text="削除", width=60, command=self._delete_selected).pack(
            side="right", padx=4
        )
        ctk.CTkButton(toolbar, text="追加", width=60, command=self._show_add_dialog).pack(
            side="right", padx=4
        )

        # Treeview（customtkinter に Treeview がないため ttk を使用）
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True)

        columns = ("date", "time", "weekday", "type")
        self._tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self._tree.heading("date", text="日付")
        self._tree.heading("time", text="時間")
        self._tree.heading("weekday", text="曜日")
        self._tree.heading("type", text="種別")
        self._tree.column("date", width=100)
        self._tree.column("time", width=70)
        self._tree.column("weekday", width=50)
        self._tree.column("type", width=70)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._tree.pack(side="left", fill="both", expand=True)

        self._refresh_tree()

    def _refresh_tree(self) -> None:
        self._tree.delete(*self._tree.get_children())
        for slot in self._slots:
            self._tree.insert(
                "",
                "end",
                values=(
                    slot.date.strftime("%Y/%m/%d"),
                    f"{slot.time:02d}:00",
                    slot.weekday_jp,
                    "追加" if slot.is_additional else "通常",
                ),
            )

    def _delete_selected(self) -> None:
        sel = self._tree.selection()
        if not sel:
            return
        idx = self._tree.index(sel[0])
        del self._slots[idx]
        self._refresh_tree()
        self._update_count_label()

    def _update_count_label(self) -> None:
        # ツールバーのラベルを更新
        for child in self.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                for w in child.winfo_children():
                    if isinstance(w, ctk.CTkLabel):
                        w.configure(text=f"候補日時: {len(self._slots)} 件")
                        return

    def _show_add_dialog(self) -> None:
        """手動追加ダイアログ"""
        dialog = _AddDateDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self._slots.append(dialog.result)
            self._slots.sort(key=lambda s: (s.date, s.time))
            self._refresh_tree()
            self._update_count_label()

    def get_slots(self) -> list[DateSlot]:
        """現在のスロットリストを返す。"""
        return list(self._slots)


class _AddDateDialog(ctk.CTkToplevel):
    """手動で日時を追加するダイアログ"""

    def __init__(self, master) -> None:
        super().__init__(master)
        self.title("日時を追加")
        self.geometry("280x220")
        self.resizable(False, False)
        self.result: Optional[DateSlot] = None
        self._build()

    def _build(self) -> None:
        pad = {"padx": 12, "pady": 6}

        ctk.CTkLabel(self, text="月:").grid(row=0, column=0, sticky="w", **pad)
        self._month = ctk.CTkEntry(self, width=80)
        self._month.grid(row=0, column=1, **pad)

        ctk.CTkLabel(self, text="日:").grid(row=1, column=0, sticky="w", **pad)
        self._day = ctk.CTkEntry(self, width=80)
        self._day.grid(row=1, column=1, **pad)

        ctk.CTkLabel(self, text="年:").grid(row=2, column=0, sticky="w", **pad)
        self._year = ctk.CTkEntry(self, width=80)
        self._year.insert(0, str(datetime.date.today().year))
        self._year.grid(row=2, column=1, **pad)

        ctk.CTkLabel(self, text="時間 (0-23):").grid(row=3, column=0, sticky="w", **pad)
        self._time = ctk.CTkEntry(self, width=80)
        self._time.grid(row=3, column=1, **pad)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=8)
        ctk.CTkButton(btn_frame, text="追加", width=80, command=self._on_ok).pack(
            side="left", padx=6
        )
        ctk.CTkButton(btn_frame, text="キャンセル", width=80, command=self.destroy).pack(
            side="left", padx=6
        )

    def _on_ok(self) -> None:
        try:
            year = int(self._year.get())
            month = int(self._month.get())
            day = int(self._day.get())
            time = int(self._time.get())
        except ValueError:
            messagebox.showwarning("入力エラー", "数値を入力してください", parent=self)
            return

        if not validate_date(year, month, day):
            messagebox.showwarning("入力エラー", "無効な日付です", parent=self)
            return
        if not 0 <= time <= 23:
            messagebox.showwarning("入力エラー", "時間は 0〜23 で入力してください", parent=self)
            return

        date = datetime.date(year, month, day)
        self.result = DateSlot(
            date=date,
            time=time,
            weekday_jp=get_japanese_weekday(date),
            is_additional=True,
        )
        self.destroy()
