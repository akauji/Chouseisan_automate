"""
プロファイルのデータモデル
"""
from dataclasses import dataclass
from src.models.schedule import ScheduleConfig


@dataclass
class Profile:
    """プロファイルを表すデータクラス"""

    name: str
    config: ScheduleConfig
    created_at: str   # ISO形式
    updated_at: str   # ISO形式
