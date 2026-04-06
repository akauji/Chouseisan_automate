"""
調整さん（chouseisan.com）連携プラグイン
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from src.config.constants import LOGIN_URL
from src.exceptions.exceptions import WebDriverError
from src.models.schedule import DateSlot, EventResult
from src.plugins.base import EventCreatorPlugin
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ChouseisanPlugin(EventCreatorPlugin):
    """調整さんサイトでイベントを作成するプラグイン"""

    def get_name(self) -> str:
        """プラグイン名を返す。"""
        return "chouseisan"

    def create_event(self, event_name: str, slots: list[DateSlot]) -> EventResult:
        """調整さんサイトでイベントを作成する。

        Args:
            event_name: イベント名
            slots: 候補日時のリスト

        Returns:
            作成結果（EventResult）
        """
        date_text = self._format_slots(slots)
        driver = None
        try:
            driver = self._create_driver()
            driver.get(LOGIN_URL)

            driver.find_element(By.ID, "name").send_keys(event_name)
            driver.find_element(By.ID, "kouho").send_keys(date_text)
            driver.find_element(By.ID, "createBtn").click()

            element = driver.find_element(By.ID, "listUrl")
            url = element.get_attribute("value") or ""

            logger.info(f"イベントを作成しました: {event_name} -> {url}")
            return EventResult(event_name=event_name, url=url, success=True)

        except NoSuchElementException as e:
            msg = f"ページの要素が見つかりません: {e}"
            logger.error(msg)
            raise WebDriverError(msg) from e
        except WebDriverException as e:
            msg = f"WebDriverエラー: {e}"
            logger.error(msg)
            raise WebDriverError(msg) from e
        finally:
            if driver:
                driver.quit()

    def _create_driver(self) -> webdriver.Chrome:
        """Chromeドライバーを生成する。"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

    def _format_slots(self, slots: list[DateSlot]) -> str:
        """DateSlot リストを調整さん入力用テキストに変換する。

        Args:
            slots: 候補日時のリスト

        Returns:
            改行区切りのテキスト
        """
        return "\n".join(slot.format_for_chouseisan() for slot in slots)
