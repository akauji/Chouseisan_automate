"""
Step3: 処理中画面
"""
import customtkinter as ctk
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProgressFrame(ctk.CTkFrame):
    """Selenium実行中をプログレスバーで表示する画面"""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(
            self,
            text="Step 3 / 処理中",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(40, 20))

        ctk.CTkLabel(self, text="イベントを作成しています。しばらくお待ちください...").pack(pady=8)

        self._progress = ctk.CTkProgressBar(self, mode="indeterminate", width=400)
        self._progress.pack(pady=16)
        self._progress.start()

        self._log_box = ctk.CTkTextbox(self, height=200, width=500, state="disabled")
        self._log_box.pack(padx=20, pady=8, fill="both", expand=True)

    def append_log(self, message: str) -> None:
        """ログメッセージを追記する。

        Args:
            message: 表示するメッセージ
        """
        self._log_box.configure(state="normal")
        self._log_box.insert("end", message + "\n")
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def stop(self) -> None:
        """プログレスバーを停止する。"""
        self._progress.stop()
