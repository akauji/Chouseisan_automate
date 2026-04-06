"""
Chouseisan V2 エントリポイント
"""
import argparse
import sys
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    """アプリケーションのエントリポイント"""
    parser = argparse.ArgumentParser(description="調整さん自動作成ツール V2")
    parser.add_argument(
        "--bulk",
        action="store_true",
        help="バルクモードで起動する",
    )
    args = parser.parse_args()

    try:
        import customtkinter as ctk
        from src.gui.app import App

        app = App(bulk_mode=args.bulk)
        app.mainloop()
    except ImportError as e:
        logger.error(f"依存ライブラリの読み込みに失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
