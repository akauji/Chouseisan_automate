"""
プラグイン基底クラスと PluginManager
"""
from abc import ABC, abstractmethod

from src.exceptions.exceptions import PluginError
from src.models.schedule import DateSlot, EventResult
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Plugin(ABC):
    """全プラグインの基底クラス"""

    @abstractmethod
    def get_name(self) -> str:
        """プラグイン名を返す。"""


class EventCreatorPlugin(Plugin):
    """イベント作成プラグインの基底クラス"""

    @abstractmethod
    def create_event(self, event_name: str, slots: list[DateSlot]) -> EventResult:
        """イベントを作成する。

        Args:
            event_name: イベント名
            slots: 候補日時のリスト

        Returns:
            作成結果
        """


class PluginManager:
    """プラグインの登録・取得を管理するクラス"""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        """プラグインを登録する。

        Args:
            plugin: 登録するプラグイン
        """
        name = plugin.get_name()
        self._plugins[name] = plugin
        logger.info(f"プラグインを登録しました: {name}")

    def get(self, name: str) -> Plugin | None:
        """プラグインを名前で取得する。

        Args:
            name: プラグイン名

        Returns:
            見つかった Plugin、存在しない場合は None
        """
        return self._plugins.get(name)

    def get_or_raise(self, name: str) -> Plugin:
        """プラグインを名前で取得する（存在しない場合は例外）。

        Args:
            name: プラグイン名

        Returns:
            Plugin オブジェクト

        Raises:
            PluginError: プラグインが登録されていない場合
        """
        plugin = self.get(name)
        if plugin is None:
            raise PluginError(f"プラグインが見つかりません: {name}", plugin_name=name)
        return plugin

    def list_names(self) -> list[str]:
        """登録済みプラグイン名の一覧を返す。"""
        return list(self._plugins.keys())
