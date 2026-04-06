"""
プロファイル管理サービス（CRUD操作）
"""
import datetime
import json
import os
from pathlib import Path

from src.config.constants import ENCODING, PROFILES_DIR, PROFILE_EXTENSION
from src.exceptions.exceptions import FileError, ValidationError
from src.models.profile import Profile
from src.models.schedule import DateInfo, ScheduleConfig, TimeSettings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProfileService:
    """プロファイルのCRUD操作を提供するサービス"""

    def __init__(self, profiles_dir: str = PROFILES_DIR) -> None:
        """初期化。

        Args:
            profiles_dir: プロファイル保存ディレクトリのパス
        """
        self._dir = Path(profiles_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self._dir / (name + PROFILE_EXTENSION)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def save(self, profile: Profile) -> None:
        """プロファイルを保存する。

        Args:
            profile: 保存するプロファイル

        Raises:
            ValidationError: プロファイル名が空の場合
            FileError: ファイル書き込みに失敗した場合
        """
        if not profile.name:
            raise ValidationError("プロファイル名が空です", field="name")
        profile.updated_at = datetime.datetime.now().isoformat()
        path = self._path(profile.name)
        try:
            path.write_text(
                json.dumps(self._to_dict(profile), ensure_ascii=False, indent=2),
                encoding=ENCODING,
            )
            logger.info(f"プロファイルを保存しました: {path}")
        except OSError as e:
            raise FileError(f"プロファイルの保存に失敗しました: {e}", file_path=str(path)) from e

    def load(self, name: str) -> Profile:
        """プロファイルを読み込む。

        Args:
            name: プロファイル名

        Returns:
            読み込んだ Profile オブジェクト

        Raises:
            FileError: ファイルが存在しないか読み込みに失敗した場合
        """
        path = self._path(name)
        if not path.exists():
            raise FileError(f"プロファイルが見つかりません: {name}", file_path=str(path))
        try:
            data = json.loads(path.read_text(encoding=ENCODING))
            logger.info(f"プロファイルを読み込みました: {path}")
            return self._from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            raise FileError(f"プロファイルの解析に失敗しました: {e}", file_path=str(path)) from e
        except OSError as e:
            raise FileError(f"プロファイルの読み込みに失敗しました: {e}", file_path=str(path)) from e

    def delete(self, name: str) -> None:
        """プロファイルを削除する。

        Args:
            name: プロファイル名

        Raises:
            FileError: ファイルが存在しないか削除に失敗した場合
        """
        path = self._path(name)
        if not path.exists():
            raise FileError(f"プロファイルが見つかりません: {name}", file_path=str(path))
        try:
            path.unlink()
            logger.info(f"プロファイルを削除しました: {name}")
        except OSError as e:
            raise FileError(f"プロファイルの削除に失敗しました: {e}", file_path=str(path)) from e

    def list_names(self) -> list[str]:
        """保存済みプロファイル名の一覧を返す。

        Returns:
            プロファイル名のリスト（アルファベット順）
        """
        names = [
            p.stem
            for p in self._dir.glob(f"*{PROFILE_EXTENSION}")
        ]
        return sorted(names)

    # ------------------------------------------------------------------
    # シリアライズ / デシリアライズ
    # ------------------------------------------------------------------

    def _to_dict(self, profile: Profile) -> dict:
        cfg = profile.config
        return {
            "name": profile.name,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
            "config": {
                "year": cfg.year,
                "start_date": {"month": cfg.start_date.month, "day": cfg.start_date.day},
                "end_date": {"month": cfg.end_date.month, "day": cfg.end_date.day},
                "weekdays": cfg.weekdays,
                "time": {
                    "start": cfg.time.start,
                    "end": cfg.time.end,
                    "span": cfg.time.span,
                    "excluded": cfg.time.excluded,
                },
                "excluded_dates": [
                    {"month": d.month, "day": d.day} for d in cfg.excluded_dates
                ],
                "additional_dates": [
                    {"month": d.month, "day": d.day} for d in cfg.additional_dates
                ],
                "event_title_template": cfg.event_title_template,
            },
        }

    def _from_dict(self, data: dict) -> Profile:
        cfg_data = data["config"]
        config = ScheduleConfig(
            year=cfg_data["year"],
            start_date=DateInfo(**cfg_data["start_date"]),
            end_date=DateInfo(**cfg_data["end_date"]),
            weekdays=cfg_data["weekdays"],
            time=TimeSettings(**cfg_data["time"]),
            excluded_dates=[DateInfo(**d) for d in cfg_data["excluded_dates"]],
            additional_dates=[DateInfo(**d) for d in cfg_data["additional_dates"]],
            event_title_template=cfg_data["event_title_template"],
        )
        return Profile(
            name=data["name"],
            config=config,
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )
