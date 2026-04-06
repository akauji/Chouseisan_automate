"""
アプリケーション全体で使用される定数
"""

# URL
LOGIN_URL = "https://chouseisan.com"

# エンコーディング
ENCODING = "utf-8"

# プロファイル保存ディレクトリ
PROFILES_DIR = "profiles"

# ファイル拡張子
PROFILE_EXTENSION = ".json"

# 曜日リスト（英語）
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# 曜日の日本語表記
WEEKDAY_JP = {
    "Monday": "月",
    "Tuesday": "火",
    "Wednesday": "水",
    "Thursday": "木",
    "Friday": "金",
    "Saturday": "土",
    "Sunday": "日",
}

# デフォルト値
DEFAULT_TIME_START = 9
DEFAULT_TIME_END = 17
DEFAULT_TIME_SPAN = 1
DEFAULT_EVENT_TITLE_TEMPLATE = "{month}月度練習日程"
