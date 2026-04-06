"""
イベント作成サービス（プラグインへのファサード）
"""
from src.exceptions.exceptions import PluginError
from src.models.schedule import DateSlot, EventResult
from src.plugins.base import EventCreatorPlugin, PluginManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EventCreationService:
    """プラグインを使ってイベントを作成するサービス"""

    def __init__(self, plugin_manager: PluginManager) -> None:
        """初期化。

        Args:
            plugin_manager: 登録済み PluginManager
        """
        self._plugin_manager = plugin_manager

    def create_event(
        self,
        event_name: str,
        slots: list[DateSlot],
        plugin_name: str = "chouseisan",
    ) -> EventResult:
        """指定したプラグインでイベントを作成する。

        Args:
            event_name: イベント名
            slots: 候補日時のリスト
            plugin_name: 使用するプラグイン名

        Returns:
            EventResult

        Raises:
            PluginError: プラグインが見つからない場合
        """
        plugin = self._plugin_manager.get_or_raise(plugin_name)
        if not isinstance(plugin, EventCreatorPlugin):
            raise PluginError(
                f"プラグイン {plugin_name} はイベント作成をサポートしていません",
                plugin_name=plugin_name,
            )

        logger.info(f"イベント作成開始: {event_name} ({plugin_name})")
        return plugin.create_event(event_name, slots)
