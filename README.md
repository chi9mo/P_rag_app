# 医薬品添付文書 RAG チャットアプリ

医薬品の添付文書（PDF）を知識源として、自然言語で質問・回答できるローカル動作の RAG チャットアプリです。

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![LangChain](https://img.shields.io/badge/LangChain-lightgrey)
![Ollama](https://img.shields.io/badge/Ollama-local_LLM-orange)
![Qdrant](https://img.shields.io/badge/Qdrant-vector_DB-red)

---

## 作った背景

元薬剤師として、医療現場で「添付文書を素早く調べる」場面の多さを実感してきました。
AI・LLM の学習として RAG（Retrieval-Augmented Generation）を実装する際、自分がよく知るドメインである医薬品情報を題材として選びました。

現時点は**学習・プロトタイプ段階**ですが、将来的には複数の添付文書を横断検索できるアプリへの発展を想定しています。

---

## 主な機能

- 添付文書 PDF を自動でインデックス化（初回起動時のみ）
- 質問に対してストリーミングで回答を表示
- 回答の根拠となったページ番号と引用テキストを出典として表示
- 多ターン会話（文脈を保持した連続質問）
- リセットボタンで会話履歴をクリア

---

## 技術スタック

| 役割 | 技術 | コメント |
|---|---|---|
| LLM | Ollama (`qwen3:14b`) — ローカル実行・API キー不要 | M5 ユニファイドメモリ32Gでスワップが1Gほど発生した。 |
| Embedding | Ollama (`qwen3-embedding:0.6b`) | まずは小さいもので実装。精度Up Phaseで調整予定 |
| ベクトル DB | Qdrant（ローカルストレージモード） | Docker不要でも実行可能 |
| RAG フレームワーク | LangChain |  |
| PDF 解析 | pdfplumber |  |
| UI | Gradio |  |
| パッケージ管理 | uv |  |

すべてローカルで完結しており、外部 API やクラウドサービスへの依存はありません。

---

## セットアップ

### 前提

- [Ollama](https://ollama.com) がインストール済みであること
- uv がインストール済みであること

### 手順

```bash
# 1. モデルを取得
ollama pull qwen3:14b
ollama pull qwen3-embedding:0.6b

# 2. 依存関係をインストール
uv sync

# 3. アプリを起動（初回はインデックスを自動構築）
uv run python -m rag_app.app
```

ブラウザで `http://127.0.0.1:7860` を開く。

---

## プロジェクト構成

```
P_rag_app/
├── medicine-package-insert.pdf   # 知識源 PDF
├── src/
│   └── rag_app/
│       ├── indexer.py            # PDF → チャンク → Qdrant 投入
│       ├── chain.py              # RAG チェーン（検索 + LLM）
│       └── app.py                # Gradio UI
├── SPEC.md                       # 仕様書
├── PLAN.md                       # 実装プラン
├── TEST.md                       # テスト手順・結果
└── Claude Code を用いた個人用アプリ開発手順_v1.md
```

---

## 開発プロセスについて

本プロジェクトは Claude Code を活用して開発しました。
仕様策定 → 設計 → 実装 → テストの流れを自分なりに整理した手順書を [`Claude Code を用いた個人用アプリ開発手順_v1.md`](./Claude%20Code%20を用いた個人用アプリ開発手順_v1.md) にまとめています。

---

## 今後の拡張予定

- [ ] 複数 PDF の管理・切り替え
- [ ] Hybrid 検索（ベクトル検索 + BM25）による精度向上
- [ ] インデックス再構築ボタンの追加
- [ ] 大規模な医療ガイドライン（420 ページ）への対応
