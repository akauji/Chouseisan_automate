"""
曜日選択ウィジェット
"""
import customtkinter as ctk

from src.config.constants import WEEKDAYS, WEEKDAY_JP


class WeekdaySelector(ctk.CTkFrame):
    """7曜日のチェックボックスをまとめたウィジェット"""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._vars: dict[str, ctk.BooleanVar] = {}

        for i, key in enumerate(WEEKDAYS):
            var = ctk.BooleanVar(value=False)
            self._vars[key] = var
            ctk.CTkCheckBox(self, text=WEEKDAY_JP[key], variable=var, width=50).grid(
                row=0, column=i, padx=4, pady=4
            )

    def get(self) -> dict[str, bool]:
        """選択状態を返す。

        Returns:
            {"Monday": True/False, ...} の辞書
        """
        return {key: var.get() for key, var in self._vars.items()}

    def set(self, values: dict[str, bool]) -> None:
        """選択状態をセットする。

        Args:
            values: {"Monday": True/False, ...} の辞書
        """
        for key, val in values.items():
            if key in self._vars:
                self._vars[key].set(val)
