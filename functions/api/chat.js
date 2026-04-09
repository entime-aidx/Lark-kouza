// Cloudflare Pages Function: /api/chat
// POST { mode, messages, message }
// env.ANTHROPIC_API_KEY が必要

const KNOWLEDGE_INDEX = `# Lark講座 ナレッジインデックス

> このファイルはAIツールが参照するための統合インデックス。

---

## カリキュラム体系

### ライトプラン（全4回 / 1ヶ月）
| 回 | テーマ | ゴール |
|---|---|---|
| 1 | Lark基礎 & 初期設定 | アカウント作成〜基本操作 |
| 2 | チャット & カレンダー設計 | コミュニケーション基盤 |
| 3 | ドキュメント & タスク管理 | 情報の一元管理 |
| 4 | 運用ルール策定 & まとめ | 自走できる状態 |

### スタンダードプラン（全8回 / 3ヶ月）
| 回 | テーマ | ゴール |
|---|---|---|
| 1 | 現状分析 & ゴール設定 | 課題と理想の明確化 |
| 2 | Lark基礎 & 初期設定 | 基本操作 |
| 3 | チャット & グループ設計 | コミュニケーション設計 |
| 4 | カレンダー & 会議設計 | スケジュール一元化 |
| 5 | ドキュメント & Wiki構築 | ナレッジベース構築 |
| 6 | Base（DB）で売上・データ管理 | 数値管理の仕組み化 |
| 7 | タスク管理 & プロジェクト | 業務フローの可視化 |
| 8 | 運用定着 & 振り返り | 自走体制の確立 |

### プレミアムプラン（全12回 / 6ヶ月）
1-8はスタンダードと同様 + 以下を追加:
| 9 | 自動化ワークフロー① | 日報・申請の自動化 |
| 10 | 自動化ワークフロー② | 通知・集計の自動化 |
| 11 | スタッフ研修 & 定着支援 | メンバー全員が使える状態 |
| 12 | KPIダッシュボード & 総仕上げ | 経営判断が即時にできる |

---

## マイルストーン定義

| MS | 達成基準 | 目安 |
|---|---|---|
| M1 | チャット・カレンダー・ドキュメントを1人で使える | 1〜2週 |
| M2 | 既存ツール→Larkチャットへの移行完了 | 2〜3週 |
| M3 | 売上 or タスク管理のBase構築完了 | 1〜2ヶ月 |
| M4 | 毎日Larkを開いて業務が回る状態 | 2〜3ヶ月 |
| M5 | サポートなしで運用・改善ができる | 3ヶ月〜 |

---

## Lark機能マップ（課題→解決策）

| 課題カテゴリ | 具体例 | Lark機能 |
|---|---|---|
| チャット分散 | Chatwork/Slack/LINE併用 | Larkメッセンジャーに集約 |
| ビデオ会議 | Zoom課金 | Larkミーティング（無料） |
| ドキュメント管理 | Notion/Google Docs散在 | Larkドキュメント＋Wiki |
| データ管理 | スプレッドシート地獄 | Lark Base（DB） |
| タスク管理 | Trello/Asana別管理 | Larkタスク |
| スケジュール | Googleカレンダー別管理 | Larkカレンダー |
| ファイル共有 | Google Drive/Dropbox | Larkドライブ |
| 勤怠管理 | 紙・Excel | Lark承認＋Base |
| 売上管理 | 手書き→月末Excel | Base→自動集計 |
| 日報管理 | メール・紙 | Larkドキュメント＋自動化 |
| 顧客管理 | バラバラ | Lark Base CRM |

---

## 業界別導入パターン

| 業界 | 主な課題 | 活用ポイント |
|---|---|---|
| 飲食業 | シフト・売上・連絡 | カレンダー + Base + チャット |
| 美容・サロン | 予約・顧客・教育 | Base + Wiki + チャット |
| EC・物販 | 在庫・発注・分析 | Base + 自動化 + ダッシュボード |
| コンサル・士業 | 顧客・資料・タスク | Base + ドキュメント + プロジェクト |
| コンテンツ販売 | 受講生・コンテンツ・コミュニティ | チャット + ドキュメント + Base |
| 建設・不動産 | 現場・日報・写真 | チャット + ドキュメント + ドライブ |

---

## よくあるつまずきと対応

| つまずき | 原因 | 対応策 |
|---|---|---|
| Larkを開く習慣がない | 既存ツールに慣れている | 毎朝チェックイン習慣 / ホーム画面配置 |
| スタッフが使わない | 導入目的が未共有 | 「なぜ変えるか」説明会 |
| Baseの設計がわからない | DB概念が未経験 | テンプレートからカスタマイズ |
| モチベ低下 | 効果実感まで時間がかかる | 小さな成功体験を作る |
| データ移行が面倒 | 量が多い/形式バラバラ | 優先度高→段階移行 / CSV一括 |

---

## Q&A対応ガイドライン

- 24時間以内に初回返信（営業日）
- 質問の背景を確認してから回答
- スクショ・画面録画を活用
- 表面的な回答を避け、なぜそうするかを説明`;

const CONTENT_LIBRARY_SUMMARY = `## 主要学習動画ライブラリ

### M1: 基本操作（1週間）
- Day1 導入: [この動画1本でOK！Larkの導入方法完全解説](https://www.youtube.com/watch?v=yJ5rNopFrt8)（15:30）
- Day2 チャット: [社内連絡はLark一択！チャット機能の最終形態完全解説](https://www.youtube.com/watch?v=C-7ej6O1bZs)（22:49）
- Day3 カレンダー: [Larkのカレンダー機能を徹底解説](https://www.youtube.com/watch?v=bftVrIB-Az4)（14:33）
- Day4 ドキュメント: [Docsで使えるボード・マインドノート完全解説](https://www.youtube.com/watch?v=ZtME9SlZgAs)（15:55）
- Day5 ビデオ会議: [Larkで議事録をとる方法が便利すぎてやばい！](https://www.youtube.com/watch?v=ztpmp-5p4Iw)（14:25）
- Day6 タスク: [Larkの使い方徹底解説 タスク管理やプロジェクト管理もこれで完結](https://www.youtube.com/watch?v=_fBpJ9wUu-0)（1:08:35）
- Day7 振り返り: [社内管理はLark一択！全てが1つになった最強ツール](https://www.youtube.com/watch?v=BYIgSVlDVww)（32:12）

### M2: ツール移行（2週間目）
- 移行計画: [人気ITツールとLarkを比較した結果が衝撃だった](https://www.youtube.com/watch?v=fWAozep1WpY)（42:01）
- チャット移行: [Larkチャットが便利すぎる！他のチャットツールと徹底比較](https://www.youtube.com/watch?v=iK6kZIsStH4)（23:57）
- データ移行: [スプレッドシート、ExcelからBaseに移行する方法](https://www.youtube.com/watch?v=kr2e0F63o7s)（24:43）
- Googleフォーム代替: [GoogleフォームをBaseに置き換える方法](https://www.youtube.com/watch?v=EyZXEaJKLSE)（18:43）

### M3: データ管理構築（1〜2ヶ月）
- Base入門: [Excel・スプレッドシートを超えた、LarkのBase機能完全解説](https://www.youtube.com/watch?v=pTgSX0YDnmc)（12:59）
- Base深掘り: [Base完全解説！スプレッドシートより最強な理由と実務活用術](https://www.youtube.com/watch?v=uDDMEb2DcFs)（1:06:55）
- 売上管理: [脱・Excel！売上管理を超スムーズに行う最新アプリの使い方](https://www.youtube.com/watch?v=54hlw4elOns)（35:47）
- 顧客管理: [Baseを使った顧客管理シートの作り方完全解説](https://www.youtube.com/watch?v=0yviqWRAU8c)（28:41）
- ダッシュボード: [Larkダッシュボードの使い方徹底解説](https://www.youtube.com/watch?v=NImhfO7o6U8)（21:18）

### M4: 自動化・運用定着（2〜3ヶ月）
- 自動化基本: [Larkの自動化機能であなたの"ムダな時間"をゼロにする方法](https://www.youtube.com/watch?v=-diZUj3lZjg)（36:40）
- 自動化実践: [Excel関数卒業！Larkで誰でも自動化機能が作れる時代へ](https://www.youtube.com/watch?v=BlvCsDIlTq4)（30:59）
- 勤怠管理: [脱・Excel！誰でも簡単にできる勤怠管理システムの作り方](https://www.youtube.com/watch?v=M_OBZuNvE-o)（27:29）
- 日報システム: [日報を自動で管理する最強のツールを紹介します](https://www.youtube.com/watch?v=r1r1zXz_hfc)（28:34）

### 業種別おすすめ動画
- コンテンツ販売: [受講生管理を最適化する方法](https://www.youtube.com/watch?v=HcCHvdhY4CM)（40:43）
- クライアントワーク: [クライアントワーカー向けLarkの活用方法完全解説](https://www.youtube.com/watch?v=IFm5QK-_2ns)（21:50）
- 店舗ビジネス: [店舗経営者が取り入れて良かったデジタルツールを徹底解説](https://www.youtube.com/watch?v=MXy9zceCFPo)（16:47）
- 企業DX: [企業のITツール費用を大幅に削減する方法](https://www.youtube.com/watch?v=ZbuYj6cERqM)（18:36）`;

const SYSTEM_BASE = `あなたは「Lark講座AIコーチ」です。
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
- 受講生のプランやマイルストーンに合わせた回答をする`;

function getSystemPrompt(mode, today) {
  const knowledge = KNOWLEDGE_INDEX + '\n\n' + CONTENT_LIBRARY_SUMMARY;

  if (mode === 'qa') {
    return `${SYSTEM_BASE}

## あなたの役割: Q&A対応
受講生からの質問に、以下のナレッジベースを元に回答してください。

### 回答の方針
1. まず質問の背景を理解し、何を解決したいのか把握する
2. ナレッジベースから最適な情報を引き出す
3. 具体的な手順（Larkの操作方法含む）を示す
4. 関連する「つまずきポイント」があれば併せて伝える
5. 不明な場合は「寺山に直接確認しましょう」と案内

### ナレッジベース
${knowledge}`;
  }

  if (mode === 'roadmap') {
    return `${SYSTEM_BASE}

## あなたの役割: 個別ロードマップ生成
受講生の情報を元に、**日付ベース・1日単位**のパーソナライズされたLark学習ロードマップを作成してください。

### 今日の日付
${today}

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
1. **必ず実際の日付**（例: ${today}(水)）を書く。「Week 1」のような抽象表現は禁止
2. **1日ごとにアクション**を記載する（土日は軽めor休みでもOK）
3. **各日に必ず動画リンクを1本以上つける**（コンテンツライブラリから選ぶ）
4. 受講生の**業種に合った動画**を優先的に配置する
5. アクションは「〜を見る」だけでなく「見た後に〜を実際にやる」まで含める
6. **マイルストーンチェックポイント**を週末ごとに入れる

### コンテンツライブラリ（動画リンク・学習パス）
${CONTENT_LIBRARY_SUMMARY}

### ナレッジベース
${KNOWLEDGE_INDEX}`;
  }

  if (mode === 'review') {
    return `${SYSTEM_BASE}

## あなたの役割: 提出物の添削・フィードバック
受講生が作ったLarkの設定・構築物をレビューし、寺山大夢の視点でフィードバックします。

### 評価軸（5段階: ★1〜★5）
1. **課題適合性**: 自社の課題に対して適切なLark機能を選んでいるか
2. **設計の完成度**: Base/ドキュメント/ワークフローの構造が実用的か
3. **運用の持続性**: 日々の運用で継続できる設計になっているか
4. **拡張性**: 将来的にスケールできる構造か
5. **プレゼン力**: 発表資料として説得力があるか

### フィードバックのフォーマット
\`\`\`
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
\`\`\`

### レビューの姿勢
- まず良い点を認める（受講生のモチベーション維持）
- 改善点は「なぜそうした方がいいか」の理由付き
- 具体的な操作手順まで示す

### ナレッジベース
${knowledge}`;
  }

  return SYSTEM_BASE;
}

export async function onRequestPost(context) {
  const { request, env } = context;

  const apiKey = env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return Response.json({ error: 'ANTHROPIC_API_KEY が設定されていません' }, { status: 500 });
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: 'リクエストの形式が不正です' }, { status: 400 });
  }

  const { mode = 'qa', messages = [], message } = body;
  if (!message || typeof message !== 'string') {
    return Response.json({ error: 'message が必要です' }, { status: 400 });
  }

  const today = new Date().toLocaleDateString('ja-JP', {
    year: 'numeric', month: '2-digit', day: '2-digit', timeZone: 'Asia/Tokyo'
  }).replace(/\//g, '-');

  const systemPrompt = getSystemPrompt(mode, today);

  // 会話履歴 + 今回のメッセージを組み立てる
  const allMessages = [
    ...messages,
    { role: 'user', content: message },
  ];

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-6',
        max_tokens: 8192,
        system: systemPrompt,
        messages: allMessages,
      }),
    });

    if (!response.ok) {
      const err = await response.text();
      console.error('Anthropic API error:', err);
      return Response.json({ error: 'AIサービスとの通信に失敗しました' }, { status: 502 });
    }

    const data = await response.json();
    const assistantText = data.content?.[0]?.text ?? '';

    return Response.json({ response: assistantText });
  } catch (e) {
    console.error('Fetch error:', e);
    return Response.json({ error: '通信エラーが発生しました' }, { status: 500 });
  }
}
