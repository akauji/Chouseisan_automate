# CLAUDE.md

## プロジェクト概要

「調整さん」（chouseisan.com）のイベント日程調整ページを自動作成するPythonデスクトップアプリ。
GUIで設定を入力し、候補日時を生成、Seleniumでブラウザを操作してイベントを作成する。

- **設計書**: `docs/architecture.md`
- **実装計画**: `docs/implementation_plan.md`
- **リファクタリング元**: `../Chouseisan_Refactoring/`

## コーディング規約

- Python 3.9+、型ヒント必須（`list[X]` 記法を使用、`List[X]` は使わない）
- 1関数・1クラスに1つの責務（Single Responsibility）
- docstringはGoogle形式で記述
- ファイル・クラス・関数名はスネークケース / PascalCase（PEP8準拠）
- マジックナンバーは `src/config/constants.py` に定数として定義する
- ログは `src/utils/logger.py` の `get_logger(__name__)` を使用する
- 例外は `src/exceptions/exceptions.py` のアプリ例外クラスを使用する（組み込み例外を直接raiseしない）

## 禁止事項

- ファイル経由のデータ連携禁止（`setting.csv` / `output.txt` 等）。サービス間はオブジェクトで受け渡す
- `except Exception` の素のキャッチ禁止。必ずアプリ例外に変換してraise
- ビジネスロジックをGUIレイヤー（`src/gui/`）に書かない
- グローバル変数・シングルトン禁止。依存はコンストラクタ注入で渡す
- `.bak` ファイルや `backup/` ディレクトリをコミットしない

## ファイル構成

```
Chouseisan_V2/
├── main.py
├── requirements.txt
├── profiles/               # プロファイルJSON保存先（gitignore対象）
├── docs/
│   ├── architecture.md
│   └── implementation_plan.md
└── src/
    ├── config/constants.py     # 定数（URL・エンコーディング等）
    ├── models/
    │   ├── schedule.py         # スケジュール設定・DateSlot・EventResult
    │   └── profile.py          # プロファイル
    ├── services/
    │   ├── date_generation.py  # 日時生成（ScheduleConfig → list[DateSlot]）
    │   ├── event_creation.py   # イベント作成（Selenium）
    │   └── profile_service.py  # プロファイルCRUD
    ├── plugins/
    │   ├── base.py             # Plugin基底 + PluginManager
    │   └── chouseisan/plugin.py
    ├── gui/
    │   ├── app.py              # メインウィンドウ・画面遷移
    │   ├── frames/             # 各画面（schedule/preview/progress/result/bulk/profile）
    │   └── components/         # 再利用ウィジェット
    ├── exceptions/exceptions.py
    └── utils/
        ├── date_utils.py
        └── logger.py
```

## よく使うコマンド

```bash
# アプリ起動（通常モード）
python main.py

# アプリ起動（バルクモード）
python main.py --bulk

# テスト実行
pytest tests/

# カバレッジ付きテスト
pytest tests/ --cov=src --cov-report=term-missing

# 型チェック
mypy src/

# コードフォーマット
black src/ tests/
```
