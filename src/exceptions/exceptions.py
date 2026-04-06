"""
アプリケーション例外クラス（フラット・統合設計）
"""


class AppError(Exception):
    """全例外の基底クラス"""


class ConfigError(AppError):
    """設定読み込み・解析エラー"""


class ValidationError(AppError):
    """入力値の検証エラー"""

    def __init__(self, message: str, field: str = "") -> None:
        super().__init__(message)
        self.field = field


class DateError(AppError):
    """日付処理エラー"""


class FileError(AppError):
    """ファイルI/Oエラー"""

    def __init__(self, message: str, file_path: str = "") -> None:
        super().__init__(message)
        self.file_path = file_path


class WebDriverError(AppError):
    """Seleniumエラー"""


class PluginError(AppError):
    """プラグインエラー"""

    def __init__(self, message: str, plugin_name: str = "") -> None:
        super().__init__(message)
        self.plugin_name = plugin_name
