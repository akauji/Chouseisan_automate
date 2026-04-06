# 実装計画

設計の詳細は `architecture.md` を参照。

## Phase 1: 基盤・コアロジック

| # | タスク | 対象ファイル | 状態 |
|---|---|---|---|
| 1-1 | プロジェクト初期設定 | `requirements.txt`, `main.py`, `src/__init__.py` 等 | ⬜ 未着手 |
| 1-2 | 例外クラス実装 | `src/exceptions/exceptions.py` | ⬜ 未着手 |
| 1-3 | データモデル実装 | `src/models/schedule.py`, `src/models/profile.py` | ⬜ 未着手 |
| 1-4 | ユーティリティ実装 | `src/utils/date_utils.py`, `src/utils/logger.py` | ⬜ 未着手 |
| 1-5 | 日時生成サービス実装 | `src/services/date_generation.py` | ⬜ 未着手 |
| 1-6 | プロファイルサービス実装 | `src/services/profile_service.py` | ⬜ 未着手 |
| 1-7 | プラグインシステム実装 | `src/plugins/base.py`, `src/plugins/chouseisan/plugin.py` | ⬜ 未着手 |
| 1-8 | イベント作成サービス実装 | `src/services/event_creation.py` | ⬜ 未着手 |
| 1-9 | Phase 1 テスト実装 | `tests/unit/` 以下 | ⬜ 未着手 |

## Phase 2: GUI実装

| # | タスク | 対象ファイル | 状態 |
|---|---|---|---|
| 2-1 | メインウィンドウ | `src/gui/app.py` | ⬜ 未着手 |
| 2-2 | 再利用コンポーネント | `src/gui/components/` | ⬜ 未着手 |
| 2-3 | Step1: 設定入力画面 | `src/gui/frames/schedule_frame.py` | ⬜ 未着手 |
| 2-4 | Step2: 日時確認・編集画面 | `src/gui/frames/preview_frame.py` | ⬜ 未着手 |
| 2-5 | Step3: 処理中画面 | `src/gui/frames/progress_frame.py` | ⬜ 未着手 |
| 2-6 | Step4: 結果表示画面 | `src/gui/frames/result_frame.py` | ⬜ 未着手 |
| 2-7 | バルクモード画面 | `src/gui/frames/bulk_frame.py` | ⬜ 未着手 |
| 2-8 | プロファイル管理画面 | `src/gui/frames/profile_frame.py` | ⬜ 未着手 |

## 凡例

| 記号 | 意味 |
|---|---|
| ⬜ | 未着手 |
| 🔄 | 進行中 |
| ✅ | 完了 |
