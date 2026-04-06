"""
ロガーユーティリティ
"""
import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """指定した名前のロガーを取得する。

    Args:
        name: ロガー名（通常は __name__）

    Returns:
        設定済みのロガーオブジェクト
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
