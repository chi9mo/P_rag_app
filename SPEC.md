# RAG チャットアプリ 仕様書

## 概要

`guideline.pdf` の内容を知識源として、ユーザーの質問に日本語で回答する RAG ベースの GUI チャットアプリ。

---

## 機能要件

### RAG パイプライン

| 項目 | 仕様 |
|---|---|
| データソース | `guideline.pdf`（日本語、リポジトリルートに配置） |
| インデックス構築 | アプリ起動時に1回のみ実行。`qdrant_storage/` が存在する場合はスキップ |
| 検索戦略 | ベクトル類似検索（シンプル実装。将来的に Hybrid 検索へ拡張余地あり） |
| 検索件数（top-k） | 4件（デフォルト） |
| 回答言語 | 日本語固定（システムプロンプトで指定） |

### チャット UI

| 項目 | 仕様 |
|---|---|
| フレームワーク | Gradio |
| 会話履歴 | セッション内のみ保持（アプリ再起動でリセット） |
| ストリーミング | あり（LLM の応答をリアルタイム表示） |
| 出典表示 | 回答の下に参照チャンクのページ番号と引用テキストを表示 |
| リセットボタン | セッション内の会話履歴をクリアするボタンを配置 |

---

## 非機能要件

- 動作環境: ローカル Mac（インターネット接続不要）
- LLM・Embedding はすべて Ollama 経由でローカル実行
- Qdrant はサーバー不要のローカルストレージモードを使用（Docker 不要）
- 外部 API キー・クラウドサービスは一切使用しない

---

## 技術スタック

| 役割 | ライブラリ / ツール | 備考 |
|---|---|---|
| パッケージ管理 | `uv` | |
| PDF 解析 | `pdfplumber` | ページ番号をメタデータとして保持 |
| チャンク分割 | LangChain `RecursiveCharacterTextSplitter` | |
| Embedding モデル | `qwen3-embedding:0.6b` | Ollama 経由 |
| ベクトル DB | Qdrant（ローカルストレージモード） | `./qdrant_storage/` に永続化 |
| LLM | `qwen3:14b` | Ollama 経由、ストリーミング有効 |
| GUI | Gradio | |
| パイプライン統合 | LangChain | |

---

## プロジェクト構成

```
P_rag_app/
├── guideline.pdf           # 知識源 PDF
├── pyproject.toml
├── .gitignore
├── SPEC.md                 # 本ファイル
├── CLAUDE.md               # 実装ガイド
├── src/
│   └── rag_app/
│       ├── __init__.py
│       ├── indexer.py      # PDF解析 → チャンク → Qdrant 投入
│       ├── chain.py        # RAG チェーン（検索 + プロンプト + LLM）
│       └── app.py          # Gradio UI（エントリポイント）
└── qdrant_storage/         # Qdrant 永続データ（.gitignore 対象）
```

---

## セットアップ手順

1. Ollama をインストール（https://ollama.com）
2. モデルを取得:
   ```bash
   ollama pull qwen3:14b
   ollama pull qwen3-embedding:0.6b
   ```
3. 依存関係をインストール:
   ```bash
   uv sync
   ```
4. アプリを起動（初回はインデックスを自動構築）:
   ```bash
   uv run python -m rag_app.app
   ```

---

## 将来の拡張候補（現スコープ外）

- Hybrid 検索（ベクトル + BM25）への切り替え
- 複数 PDF の管理・切り替え
- インデックス再構築ボタンの追加
