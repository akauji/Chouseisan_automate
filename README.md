# 調整さん自動作成ツール V2

[調整さん](https://chouseisan.com) のイベント日程調整ページを自動作成する Python デスクトップアプリです。  
GUI で設定を入力し、候補日時を生成し、Selenium でブラウザを操作してイベントを作成します。

## 機能

- **通常モード（ステップ実行）**
  1. 年・期間・曜日・時間帯などを GUI で設定
  2. 生成された候補日時を確認・編集（個別削除・手動追加）
  3. ブラウザ自動操作でイベントを作成
  4. 作成された URL を表示・クリップボードにコピー

- **バルクモード**  
  月範囲を指定して複数月分のイベントを一括作成

- **プロファイル保存・読み込み**  
  設定を名前を付けて保存し、次回以降に再利用

## 必要環境

| 項目 | バージョン |
|---|---|
| Python | 3.9 以上 |
| Google Chrome | 最新版推奨 |

> ChromeDriver は `webdriver-manager` が自動でダウンロードするため、別途インストール不要です。

## セットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd Chouseisan_V2

# 依存ライブラリをインストール
pip install -r requirements.txt
```

## 起動方法

```bash
# 通常モード
python main.py

# バルクモード
python main.py --bulk
```

## 使い方

### 通常モード

```
Step 1: 設定入力
  - 年・期間（開始月日〜終了月日）を指定
  - 対象曜日にチェック
  - 時間帯（開始・終了・間隔）を設定
  - 除外時間・除外日・追加日（曜日不問）を必要に応じて登録
  - イベントタイトルテンプレートを入力（例: {month}月度練習日程）
  - 「日時を生成」ボタンをクリック

Step 2: 日時確認・編集
  - 生成された候補日時を一覧表示
  - 不要な日時を選択して「削除」
  - 必要な日時を「追加」で手動入力
  - 「イベントを作成」ボタンをクリック

Step 3: 処理中
  - ブラウザが自動操作されイベントが作成されます
  - 完了まで待機

Step 4: 結果表示
  - 作成された URL を確認・コピー
  - 「最初に戻る」で Step 1 に戻る
```

### バルクモード

1. 年・開始月〜終了月を指定
2. 曜日・時間設定・除外設定を入力
3. イベントタイトルテンプレートを入力
4. 「一括作成」ボタンをクリック
5. 月ごとに順番に処理され、完了後に結果一覧を表示

### プロファイル

- **保存**: Step 1 画面でプロファイル名を入力し「保存」
- **読み込み**: 保存済みプロファイルをコンボボックスで選択し「読み込み」
- **管理（削除）**: 「管理」ボタンからプロファイル管理ダイアログを開く
- プロファイルは `profiles/` フォルダに JSON ファイルとして保存されます

## イベントタイトルテンプレート

`{month}` を含めると、対象月の数字に自動置換されます。

| テンプレート | 7月の場合 |
|---|---|
| `{month}月度練習日程` | `7月度練習日程` |
| `2025年{month}月 定例会` | `2025年7月 定例会` |

## プロジェクト構成

```
Chouseisan_V2/
├── main.py                        # エントリポイント
├── requirements.txt
├── profiles/                      # プロファイル保存先（自動生成）
├── docs/
│   ├── architecture.md            # アーキテクチャ設計書
│   └── implementation_plan.md     # 実装計画
└── src/
    ├── config/constants.py        # 定数
    ├── models/                    # データモデル（ScheduleConfig, DateSlot 等）
    ├── services/                  # ビジネスロジック
    │   ├── date_generation.py     # 候補日時生成
    │   ├── event_creation.py      # イベント作成（プラグイン呼び出し）
    │   └── profile_service.py     # プロファイル CRUD
    ├── plugins/
    │   ├── base.py                # Plugin 基底 + PluginManager
    │   └── chouseisan/plugin.py   # 調整さん Selenium プラグイン
    ├── gui/
    │   ├── app.py                 # メインウィンドウ・画面遷移
    │   ├── frames/                # 各画面
    │   └── components/            # 再利用ウィジェット
    ├── exceptions/exceptions.py   # 例外クラス
    └── utils/                     # ロガー・日付ユーティリティ
```

## 開発コマンド

```bash
# テスト実行
pytest tests/

# カバレッジ付きテスト
pytest tests/ --cov=src --cov-report=term-missing

# 型チェック
mypy src/

# コードフォーマット
black src/ tests/
```

## 技術スタック

| 要素 | 技術 |
|---|---|
| GUI | [customtkinter](https://github.com/TomSchimansky/CustomTkinter) |
| ブラウザ操作 | [Selenium](https://www.selenium.dev/) + [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager) |
| テスト | [pytest](https://pytest.org/) |
| 設定保存 | JSON |
