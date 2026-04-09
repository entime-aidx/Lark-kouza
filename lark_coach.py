#!/usr/bin/env python3
"""
Lark講座 AIコーチングツール
=============================
3つの機能を統合:
  1. qa       - 受講生の質問にナレッジベースで自動回答
  2. roadmap  - 個別学習ロードマップ生成
  3. review   - 提出物の添削・フィードバック

Usage:
  python3 lark_coach.py qa
  python3 lark_coach.py roadmap
  python3 lark_coach.py review <file_path>
  python3 lark_coach.py server  # Webサーバーモード（受講生向け）
"""

import argparse
import json
import os
import sys
from pathlib import Path

import anthropic

# ============================================================
# 設定
# ============================================================
KNOWLEDGE_BASE_DIR = Path(__file__).parent / "knowledge"
KNOWLEDGE_SOURCE_DIR = Path.home() / "Downloads" / "Cursor" / "Lark講座ナレッジ"
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 8192
TODAY = __import__("datetime").date.today().isoformat()

# ============================================================
# ナレッジ読み込み
# ============================================================

def load_knowledge_index() -> str:
    """統合インデックスを読み込む"""
    index_path = KNOWLEDGE_BASE_DIR / "knowledge_index.md"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return ""


def load_source_files(categories: list[str] | None = None) -> str:
    """ソースナレッジから関連カテゴリのファイルを読み込む"""
    if not KNOWLEDGE_SOURCE_DIR.exists():
        return ""

    target_dirs = categories or [
        "03_講座運営（デリバリー）",
        "05_コンテンツライブラリ",
    ]

    contents = []
    for target in target_dirs:
        target_path = KNOWLEDGE_SOURCE_DIR / target
        if not target_path.exists():
            continue
        for md_file in sorted(target_path.rglob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            if len(text) > 100:  # 空に近いファイルはスキップ
                rel = md_file.relative_to(KNOWLEDGE_SOURCE_DIR)
                contents.append(f"--- {rel} ---\n{text[:2000]}")  # トークン節約

    # 合計で最大50,000文字に制限（API コスト最適化）
    result = []
    total = 0
    for c in contents:
        if total + len(c) > 50000:
            break
        result.append(c)
        total += len(c)
    return "\n\n".join(result)


def load_content_library() -> str:
    """動画リンク・学習パス付きコンテンツライブラリを読み込む"""
    lib_path = KNOWLEDGE_BASE_DIR / "content_library.json"
    if not lib_path.exists():
        return ""
    return lib_path.read_text(encoding="utf-8")


# ============================================================
# システムプロンプト
# ============================================================

SYSTEM_BASE = """あなたは「Lark講座AIコーチ」です。
寺山大夢（Lark研究所）が運営するLark講座の知見を元に、受講生をサポートします。

## あなたの性格・話し方
- フレンドリーだが専門的。敬語ベースだがカジュアルさも混ぜる
- 「〜ですね！」「〜してみましょう」など前向きなトーン
- 具体的な手順を示す（ステップ1, 2, 3...）
- Larkの機能名は正確に使う（Base, ドキュメント, メッセンジャー等）
- 背景や「なぜそうするのか」も説明する

## 重要ルール
- Larkの公式機能に基づいて回答する
- わからないことは正直に伝え、寺山に確認するよう促す
- 受講生のプランやマイルストーンに合わせた回答をする
"""


def get_qa_system(knowledge: str) -> str:
    return f"""{SYSTEM_BASE}

## あなたの役割: Q&A対応
受講生からの質問に、以下のナレッジベースを元に回答してください。

### 回答の方針
1. まず質問の背景を理解し、何を解決したいのか把握する
2. ナレッジベースから最適な情報を引き出す
3. 具体的な手順（Larkの操作方法含む）を示す
4. 関連する「つまずきポイント」があれば併せて伝える
5. 不明な場合は「寺山に直接確認しましょう」と案内

### ナレッジベース
{knowledge}
"""


def get_roadmap_system(knowledge: str, content_library: str) -> str:
    return f"""{SYSTEM_BASE}

## あなたの役割: 個別ロードマップ生成
受講生の情報を元に、**日付ベース・1日単位**のパーソナライズされたLark学習ロードマップを作成してください。

### 今日の日付
{TODAY}

### ヒアリング（最初のメッセージで一括して聞く）
以下を1つのメッセージでまとめて質問してください:
1. お名前
2. 業種・業態
3. 従業員数（何名でLarkを使うか）
4. 現在使っているツール
5. 一番解決したい課題（TOP3）
6. Lark経験レベル（初めて / 少し触った / ある程度使える）
7. 開始日（今日から？ or 特定の日？）
8. ゴール日 or 目標期間

### ロードマップの出力ルール（厳守）

1. **必ず実際の日付**（例: 2026-04-09(水)）を書く。「Week 1」のような抽象表現は禁止
2. **1日ごとにアクション**を記載する（土日は軽めor休みでもOK）
3. **各日に必ず動画リンクを1本以上つける**（コンテンツライブラリから選ぶ）
4. 受講生の**業種に合った動画**を優先的に配置する
5. アクションは「〜を見る」だけでなく「見た後に〜を実際にやる」まで含める
6. **マイルストーンチェックポイント**を週末ごとに入れる

### 出力フォーマット（これに厳密に従う）

```
# 🗓 {{名前}}さんの Lark学習ロードマップ
**期間**: {{開始日}} 〜 {{ゴール日}}（{{N}}日間）
**ゴール**: {{具体的な到達状態}}

---

## Phase 1: 基本操作マスター（{{開始日}} 〜 {{日付}}）

### 📅 {{YYYY-MM-DD}}(曜日) - {{その日のテーマ}}
**やること:**
- [ ] {{具体的なアクション1}}
- [ ] {{具体的なアクション2}}
- [ ] {{具体的なアクション3}}

**📺 今日の動画:**
- [{{動画タイトル}}]({{URL}})（{{時間}}）

**⏱ 目安時間:** {{N}}分

---

### 📅 {{次の日付}} - {{テーマ}}
...

---

## 🏁 Week 1 チェックポイント（{{日付}}）
- [ ] {{チェック項目1}}
- [ ] {{チェック項目2}}
→ 全てクリアしたら Phase 2 へ！

---

## Phase 2: ツール移行（{{日付}} 〜 {{日付}}）
...

---

## 📊 成功指標
| 指標 | 現在 | 目標 |
|---|---|---|
| {{指標名}} | {{現状}} | {{目標値}} |

## ⚠️ つまずきやすいポイント
- {{つまずき}} → **対策**: {{具体策}}

## 🎯 {{名前}}さんの業種に特におすすめの動画
- [{{タイトル}}]({{URL}})
```

### コンテンツライブラリ（動画リンク・学習パス）
{content_library}

### ナレッジベース
{knowledge}
"""


def get_review_system(knowledge: str) -> str:
    return f"""{SYSTEM_BASE}

## あなたの役割: 提出物の添削・フィードバック
受講生が作ったLarkの設定・構築物をレビューし、寺山大夢の視点でフィードバックします。

### 評価軸（5段階: ★1〜★5）

1. **課題適合性**: 自社の課題に対して適切なLark機能を選んでいるか
2. **設計の完成度**: Base/ドキュメント/ワークフローの構造が実用的か
3. **運用の持続性**: 日々の運用で継続できる設計になっているか
4. **拡張性**: 将来的にスケールできる構造か
5. **プレゼン力**: 発表資料として説得力があるか

### フィードバックのフォーマット
```
# 添削フィードバック

## 総合評価: {{★の数}} / 5

## 良い点 (Keep)
- {{具体的に良い点を3つ}}

## 改善点 (Improve)
- {{具体的な改善提案を3つ、手順付き}}

## 次のステップ
- {{次に取り組むべきこと}}

## 寺山からのコメント
（寺山の視点での一言アドバイス）
```

### レビューの姿勢
- まず良い点を認める（受講生のモチベーション維持）
- 改善点は「なぜそうした方がいいか」の理由付き
- 具体的な操作手順まで示す
- 他の受講生の成功事例を匿名で参考に出す

### ナレッジベース
{knowledge}
"""


# ============================================================
# 対話エンジン
# ============================================================

class LarkCoach:
    def __init__(self, mode: str):
        self.client = anthropic.Anthropic()
        self.mode = mode
        self.messages: list[dict] = []

        # ナレッジ読み込み
        knowledge = load_knowledge_index()
        if mode == "qa":
            extra = load_source_files(["03_講座運営（デリバリー）", "05_コンテンツライブラリ"])
            self.system = get_qa_system(knowledge + "\n\n" + extra)
        elif mode == "roadmap":
            extra = load_source_files(["03_講座運営（デリバリー）"])
            content_library = load_content_library()
            self.system = get_roadmap_system(knowledge + "\n\n" + extra, content_library)
        elif mode == "review":
            extra = load_source_files(["03_講座運営（デリバリー）", "05_コンテンツライブラリ"])
            self.system = get_review_system(knowledge + "\n\n" + extra)
        else:
            self.system = SYSTEM_BASE

    def chat(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=self.system,
            messages=self.messages,
        )

        assistant_text = response.content[0].text
        self.messages.append({"role": "assistant", "content": assistant_text})
        return assistant_text


def run_interactive(mode: str):
    """対話モードで実行"""
    coach = LarkCoach(mode)

    mode_labels = {
        "qa": "Q&A（質問回答）",
        "roadmap": "ロードマップ生成",
        "review": "添削・フィードバック",
    }

    print(f"\n{'='*50}")
    print(f"  Lark講座 AIコーチ - {mode_labels.get(mode, mode)}")
    print(f"{'='*50}")

    if mode == "qa":
        print("  Larkに関する質問をどうぞ。「quit」で終了。\n")
    elif mode == "roadmap":
        print("  受講生の情報をお聞きします。「quit」で終了。\n")
        # ロードマップは最初にヒアリングを開始
        greeting = coach.chat(
            "新しい受講生のロードマップを作成します。ヒアリングを始めてください。"
        )
        print(f"コーチ: {greeting}\n")
    elif mode == "review":
        print("  レビュー対象を貼り付けてください。「quit」で終了。\n")

    while True:
        try:
            user_input = input("あなた: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n終了します。")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("お疲れ様でした！")
            break

        response = coach.chat(user_input)
        print(f"\nコーチ: {response}\n")


def run_review_file(file_path: str):
    """ファイルを読み込んでレビュー"""
    path = Path(file_path)
    if not path.exists():
        print(f"エラー: ファイルが見つかりません: {file_path}")
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    coach = LarkCoach("review")

    print(f"\n{'='*50}")
    print(f"  Lark講座 AIコーチ - 添削モード")
    print(f"  対象: {path.name}")
    print(f"{'='*50}\n")

    prompt = f"""以下の受講生の提出物をレビューしてください。

ファイル名: {path.name}

---
{content[:8000]}
---

上記の内容を添削フィードバックのフォーマットに従ってレビューしてください。"""

    response = coach.chat(prompt)
    print(response)

    # 結果を保存
    output_dir = Path(__file__).parent / "reviews"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"review_{path.stem}.md"
    output_path.write_text(response, encoding="utf-8")
    print(f"\n📄 レビュー結果を保存しました: {output_path}")


# ============================================================
# Web サーバーモード（受講生が直接使えるシンプルUI）
# ============================================================

def run_server(port: int = 8080):
    """受講生向けWebチャットUI"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse

    sessions: dict[str, LarkCoach] = {}

    html_template = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lark講座 AIコーチ</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f5f5; }
.container { max-width: 900px; margin: 0 auto; padding: 20px; }
h1 { text-align: center; color: #1a73e8; margin-bottom: 10px; font-size: 1.5em; }
.subtitle { text-align: center; color: #666; margin-bottom: 20px; font-size: 0.9em; }
.mode-select { display: flex; gap: 10px; justify-content: center; margin-bottom: 20px; flex-wrap: wrap; }
.mode-btn { padding: 10px 20px; border: 2px solid #1a73e8; border-radius: 8px; background: white; color: #1a73e8; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.2s; }
.mode-btn:hover, .mode-btn.active { background: #1a73e8; color: white; }
.chat-box { background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 20px; min-height: 400px; max-height: 70vh; overflow-y: auto; margin-bottom: 15px; }
.msg { margin-bottom: 20px; }
.msg.user { text-align: right; }
.msg .bubble { display: inline-block; padding: 12px 18px; border-radius: 12px; max-width: 90%; text-align: left; line-height: 1.7; font-size: 14px; }
.msg.user .bubble { background: #1a73e8; color: white; white-space: pre-wrap; }
.msg.assistant .bubble { background: #f8f9fa; color: #333; border: 1px solid #e0e0e0; }
.msg.assistant .bubble h1, .msg.assistant .bubble h2, .msg.assistant .bubble h3 { margin-top: 16px; margin-bottom: 8px; color: #1a73e8; }
.msg.assistant .bubble h1 { font-size: 1.3em; }
.msg.assistant .bubble h2 { font-size: 1.15em; }
.msg.assistant .bubble h3 { font-size: 1.05em; }
.msg.assistant .bubble ul, .msg.assistant .bubble ol { padding-left: 20px; margin: 8px 0; }
.msg.assistant .bubble li { margin-bottom: 4px; }
.msg.assistant .bubble a { color: #1a73e8; text-decoration: underline; }
.msg.assistant .bubble table { border-collapse: collapse; width: 100%; margin: 10px 0; }
.msg.assistant .bubble th, .msg.assistant .bubble td { border: 1px solid #ddd; padding: 6px 10px; font-size: 13px; }
.msg.assistant .bubble th { background: #f0f4ff; }
.msg.assistant .bubble hr { margin: 16px 0; border: none; border-top: 1px solid #e0e0e0; }
.msg.assistant .bubble code { background: #f0f0f0; padding: 1px 4px; border-radius: 3px; font-size: 13px; }
.msg.assistant .bubble input[type="checkbox"] { margin-right: 6px; }
.msg .label { font-size: 11px; color: #999; margin-bottom: 3px; }
.input-area { display: flex; gap: 10px; }
.input-area textarea { flex: 1; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; resize: vertical; min-height: 50px; font-family: inherit; }
.input-area textarea:focus { border-color: #1a73e8; outline: none; }
.input-area button { padding: 12px 24px; background: #1a73e8; color: white; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 600; }
.input-area button:hover { background: #1557b0; }
.input-area button:disabled { background: #ccc; cursor: not-allowed; }
.loading { color: #999; font-style: italic; }
.export-btn { display: none; margin: 10px auto; padding: 8px 16px; background: #34a853; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; }
.export-btn:hover { background: #2d8f47; }
</style>
</head>
<body>
<div class="container">
  <h1>Lark講座 AIコーチ</h1>
  <p class="subtitle">寺山大夢（Lark研究所）のナレッジを元にサポートします</p>
  <div class="mode-select">
    <button class="mode-btn active" onclick="setMode('qa')">質問する</button>
    <button class="mode-btn" onclick="setMode('roadmap')">ロードマップ作成</button>
    <button class="mode-btn" onclick="setMode('review')">提出物レビュー</button>
  </div>
  <div id="chat" class="chat-box"></div>
  <button class="export-btn" id="exportBtn" onclick="exportMarkdown()">Markdownでダウンロード</button>
  <div class="input-area">
    <textarea id="input" placeholder="質問を入力してください..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"></textarea>
    <button id="sendBtn" onclick="send()">送信</button>
  </div>
</div>
<script>
let mode = 'qa';
let sessionId = Math.random().toString(36).slice(2);
let lastResponse = '';

marked.setOptions({ breaks: true, gfm: true });

function setMode(m) {
  mode = m;
  sessionId = Math.random().toString(36).slice(2);
  lastResponse = '';
  document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('chat').innerHTML = '';
  document.getElementById('exportBtn').style.display = 'none';
  const placeholders = {
    qa: '質問を入力してください...',
    roadmap: '上の質問に回答してください...',
    review: '提出物の内容を貼り付けてください...'
  };
  document.getElementById('input').placeholder = placeholders[m] || '';
  if (m === 'roadmap') {
    addMsg('assistant', 'ロードマップを作成します！以下を教えてください:\\n\\n1. お名前\\n2. 業種・業態\\n3. 従業員数\\n4. 現在使っているツール\\n5. 一番解決したい課題（TOP3）\\n6. Lark経験レベル（初めて / 少し触った / ある程度使える）\\n7. 開始日（今日から？ or 特定の日？）\\n8. ゴール日 or 目標期間');
  }
}

function addMsg(role, text) {
  const chat = document.getElementById('chat');
  const label = role === 'user' ? 'あなた' : 'AIコーチ';
  const content = role === 'assistant' ? marked.parse(text) : escHtml(text);
  chat.innerHTML += '<div class="msg ' + role + '"><div class="label">' + label + '</div><div class="bubble">' + content + '</div></div>';
  chat.scrollTop = chat.scrollHeight;
  if (role === 'assistant') {
    lastResponse = text;
    if (mode === 'roadmap' && text.length > 500) {
      document.getElementById('exportBtn').style.display = 'block';
    }
  }
}

function escHtml(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function exportMarkdown() {
  if (!lastResponse) return;
  const blob = new Blob([lastResponse], { type: 'text/markdown' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'roadmap_' + new Date().toISOString().slice(0,10) + '.md';
  a.click();
}

async function send() {
  const input = document.getElementById('input');
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  addMsg('user', text);
  document.getElementById('sendBtn').disabled = true;

  const chat = document.getElementById('chat');
  chat.innerHTML += '<div class="msg assistant loading" id="loading"><div class="bubble">考え中...</div></div>';
  chat.scrollTop = chat.scrollHeight;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode, session_id: sessionId, message: text })
    });
    const data = await res.json();
    document.getElementById('loading')?.remove();
    addMsg('assistant', data.response || 'エラーが発生しました');
  } catch (e) {
    document.getElementById('loading')?.remove();
    addMsg('assistant', '通信エラーが発生しました。再度お試しください。');
  }
  document.getElementById('sendBtn').disabled = false;
}
</script>
</body>
</html>"""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_template.encode("utf-8"))

        def do_POST(self):
            if self.path != "/api/chat":
                self.send_response(404)
                self.end_headers()
                return

            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))

            sid = body.get("session_id", "default")
            mode = body.get("mode", "qa")
            message = body.get("message", "")

            key = f"{sid}_{mode}"
            if key not in sessions:
                sessions[key] = LarkCoach(mode)

            try:
                response = sessions[key].chat(message)
                result = {"response": response}
            except Exception as e:
                result = {"response": f"エラーが発生しました: {str(e)}"}

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

        def log_message(self, format, *args):
            pass  # ログ抑制

    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"\n{'='*50}")
    print(f"  Lark講座 AIコーチ - Web版")
    print(f"  http://localhost:{port}")
    print(f"{'='*50}")
    print("Ctrl+C で停止\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nサーバーを停止しました。")
        server.server_close()


# ============================================================
# エントリーポイント
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Lark講座 AIコーチングツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python3 lark_coach.py qa              # Q&Aモード（対話）
  python3 lark_coach.py roadmap         # ロードマップ生成（対話）
  python3 lark_coach.py review          # 添削モード（対話）
  python3 lark_coach.py review file.md  # ファイルを添削
  python3 lark_coach.py server          # Web UIを起動
  python3 lark_coach.py server -p 3000  # ポート指定
        """,
    )
    parser.add_argument(
        "mode",
        choices=["qa", "roadmap", "review", "server"],
        help="動作モード",
    )
    parser.add_argument("file", nargs="?", help="レビュー対象ファイル（reviewモード時）")
    parser.add_argument("-p", "--port", type=int, default=8080, help="サーバーポート")

    args = parser.parse_args()

    # APIキー確認
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("エラー: ANTHROPIC_API_KEY が設定されていません。")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    if args.mode == "server":
        run_server(args.port)
    elif args.mode == "review" and args.file:
        run_review_file(args.file)
    else:
        run_interactive(args.mode)


if __name__ == "__main__":
    main()
