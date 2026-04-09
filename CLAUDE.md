# Lark講座 AIコーチングツール

## 概要
寺山大夢（Lark研究所）のLark講座を支援する3つのAIツール。

## ツール一覧

### 1. Q&Aボット (`qa`)
受講生の質問にナレッジベースを元に自動回答。
```
python3 lark_coach.py qa
```

### 2. ロードマップ生成 (`roadmap`)
受講生の業種・課題・目標を聞き出し、個別学習計画を作成。
```
python3 lark_coach.py roadmap
```

### 3. 添削・フィードバック (`review`)
受講生の提出物（Larkの設計・構築物）を5軸で評価しフィードバック。
```
python3 lark_coach.py review           # 対話モード
python3 lark_coach.py review file.md   # ファイル指定
```

### 4. Webサーバー (`server`)
受講生がブラウザから直接使えるチャットUI。
```
python3 lark_coach.py server           # http://localhost:8080
python3 lark_coach.py server -p 3000   # ポート指定
```

## ナレッジ構成
- `knowledge/knowledge_index.md` - 統合インデックス（カリキュラム・機能マップ・つまずき対策）
- ソース: `~/Downloads/Cursor/Lark講座ナレッジ/` から動的に読み込み

## 技術スタック
- Python 3.11 + Anthropic SDK
- Claude Sonnet（コスト最適化）
- 標準ライブラリのみ（追加パッケージ不要）

## 拡張予定
- Lark MCP連携（受講生データの自動取得）
- 発表採点システム
- 受講生ごとの専用ページ生成
