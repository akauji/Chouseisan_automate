# Chouseisan V2 アーキテクチャ設計書

## 1. プロジェクト概要

「調整さん」イベント自動作成ツールのV2。
保守性・テスト容易性・ユーザー体験を重視したゼロからの書き直し。

## 2. 技術スタック

| 要素 | 採用技術 |
|---|---|
| 言語 | Python 3.9+ |
| GUI | customtkinter |
| ブラウザ操作 | Selenium + webdriver-manager |
| テスト | pytest |
| 設定保存 | JSON (profiles/) |

## 3. ディレクトリ構成

```
Chouseisan_V2/
├── main.py                        # エントリポイント
├── requirements.txt
├── profiles/                      # プロファイルJSON保存先
├── docs/
│   └── architecture.md
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── constants.py           # URL・エンコーディング等の定数
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schedule.py            # スケジュール設定モデル（統合）
│   │   └── profile.py             # プロファイルモデル
│   ├── services/
│   │   ├── __init__.py
│   │   ├── date_generation.py     # 日時生成サービス
│   │   ├── event_creation.py      # イベント作成サービス
│   │   └── profile_service.py     # プロファイル管理サービス
│   ├── plugins/
│   │   ├── __init__.py
│   │   ├── base.py                # Plugin基底クラス + PluginManager
│   │   └── chouseisan/
│   │       ├── __init__.py
│   │       └── plugin.py          # 調整さんプラグイン
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── app.py                 # メインウィンドウ（画面遷移管理）
│   │   ├── frames/
│   │   │   ├── __init__.py
│   │   │   ├── schedule_frame.py  # Step1: 設定入力
│   │   │   ├── preview_frame.py   # Step2: 日時確認・編集
│   │   │   ├── progress_frame.py  # Step3: 処理中表示
│   │   │   ├── result_frame.py    # Step4: 結果表示
│   │   │   ├── bulk_frame.py      # バルクモード設定入力
│   │   │   └── profile_frame.py   # プロファイル管理
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── date_list.py       # 日時リストウィジェット（編集対応）
│   │       └── weekday_selector.py # 曜日選択ウィジェット
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── exceptions.py          # 例外クラス（統合・フラット設計）
│   └── utils/
│       ├── __init__.py
│       ├── date_utils.py
│       └── logger.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── unit/
    │   ├── models/
    │   ├── services/
    │   └── utils/
    └── integration/
```

## 4. データモデル

### 4.1 schedule.py

```python
@dataclass
class DateInfo:
    month: int
    day: int

@dataclass
class TimeSettings:
    start: int          # 開始時間 (0-23)
    end: int            # 終了時間 (0-23)
    span: int           # 時間間隔（時間単位）
    excluded: list[int] # 除外時間リスト

@dataclass
class ScheduleConfig:
    year: int
    start_date: DateInfo
    end_date: DateInfo
    weekdays: dict[str, bool]        # {"Monday": True, ...}
    time: TimeSettings
    excluded_dates: list[DateInfo]
    additional_dates: list[DateInfo]
    event_title_template: str        # "{month}月度練習日程"

@dataclass
class DateSlot:
    """生成された1つの候補日時"""
    date: datetime.date
    time: int
    weekday_jp: str     # "月", "火", ...
    is_additional: bool # 追加日かどうか

@dataclass
class EventResult:
    """イベント作成結果"""
    event_name: str
    url: str
    success: bool
    error_message: str = ""
```

### 4.2 profile.py

```python
@dataclass
class Profile:
    name: str
    config: ScheduleConfig
    created_at: str     # ISO形式
    updated_at: str     # ISO形式
```

## 5. 実行フロー

### 5.1 通常モード（ステップ実行）

```
Step 1: 設定入力 (schedule_frame)
  └─ プロファイル読み込み（任意）
  └─ 「日時を生成」ボタン
        ↓  ScheduleConfig をメモリで受け渡し
Step 2: 日時確認・編集 (preview_frame)
  └─ 生成された DateSlot リストを表示
  └─ 個別削除・手動追加が可能
  └─ 「イベントを作成」ボタン
        ↓  編集済み DateSlot リストをメモリで受け渡し
Step 3: 処理中 (progress_frame)
  └─ Selenium実行中をプログレスバーで表示
  └─ ログをリアルタイム表示
        ↓
Step 4: 結果表示 (result_frame)
  └─ 作成されたURL・成否を表示
  └─ 「最初に戻る」ボタン
```

### 5.2 バルクモード

```
バルク設定入力 (bulk_frame)
  └─ 年・開始月〜終了月・曜日・時間・除外設定
  └─ イベント名テンプレート
  └─ 「一括作成」ボタン
        ↓
月ごとにループ:
  1. DateSlot 生成
  2. Selenium でイベント作成
  3. 結果を記録
        ↓
結果一覧表示 (result_frame)
  └─ 月ごとの成否・URLを表示
```

## 6. 例外クラス設計

```python
# exceptions/exceptions.py（フラット・統合）

class AppError(Exception):
    """全例外の基底"""

class ConfigError(AppError):
    """設定読み込み・解析エラー"""

class ValidationError(AppError):
    """入力値の検証エラー"""
    def __init__(self, message: str, field: str = "")

class DateError(AppError):
    """日付処理エラー"""

class FileError(AppError):
    """ファイルI/Oエラー"""
    def __init__(self, message: str, file_path: str = "")

class WebDriverError(AppError):
    """Seleniumエラー"""

class PluginError(AppError):
    """プラグインエラー"""
    def __init__(self, message: str, plugin_name: str = "")
```

エラーコード番号体系は廃止。エラーメッセージの明確化で対応。

## 7. サービス層設計

### date_generation.py
- 入力: `ScheduleConfig`
- 出力: `list[DateSlot]`
- ファイルI/O なし（メモリ内完結）

### event_creation.py
- 入力: `list[DateSlot]`, `event_title: str`, `plugin_name: str`
- 出力: `EventResult`
- 依存: Plugin（注入）

### profile_service.py
- プロファイルのCRUD（`profiles/*.json`）
- 入力・出力: `Profile`

## 8. プラグイン設計

```python
# plugins/base.py に Plugin + PluginManager を統合

class Plugin(ABC):
    @abstractmethod
    def get_name(self) -> str: ...

class EventCreatorPlugin(Plugin):
    @abstractmethod
    def create_event(self, event_name: str, slots: list[DateSlot]) -> EventResult: ...

class PluginManager:
    def register(self, plugin: Plugin) -> None: ...
    def get(self, name: str) -> Plugin | None: ...
```

## 9. 参照

- 実装計画: `docs/implementation_plan.md`
