# CLAUDE.md — 実装ガイド

## プロジェクト概要

`guideline.pdf`（日本語）を知識源とした RAG チャットアプリ。
詳細仕様は `SPEC.md` を参照。

---

## パッケージ管理

- **`uv`** を使用。`pip install` は使わない。
- 依存追加: `uv add <package>`
- 実行: `uv run python -m rag_app.app`

---

## 主要コンポーネントの実装方針

### 1. indexer.py — インデックス構築

```python
# PDF 解析（ページ番号をメタデータに含める）
import pdfplumber
# page.page_number を metadata["page"] として Document に格納

# チャンク分割
from langchain.text_splitter import RecursiveCharacterTextSplitter
# chunk_size=500, chunk_overlap=50 をデフォルトとする

# Embedding（Ollama 経由）
from langchain_ollama import OllamaEmbeddings
embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b")

# Qdrant ローカルストレージモード（Docker 不要、サーバー不要）
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
client = QdrantClient(path="./qdrant_storage")
# コレクション名: "guideline"
```

**起動時の判定ロジック:**
- `./qdrant_storage/` ディレクトリが存在し、コレクションが存在すれば構築をスキップ
- 存在しなければ構築を実行

### 2. chain.py — RAG チェーン

```python
# LLM（Ollama 経由、ストリーミング有効）
from langchain_ollama import ChatOllama
llm = ChatOllama(model="qwen3:14b", streaming=True)

# 検索（top-k=4）
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
```

**システムプロンプト方針:**
- 日本語で回答するよう明示的に指示
- 提供されたコンテキストのみを根拠に回答させる
- コンテキストに情報がない場合は「資料に記載がありません」と答えさせる

**出典情報の返し方:**
- チェーンは `(answer_stream, source_documents)` を返す
- `source_documents` の各 Document から `metadata["page"]` と `page_content` を取り出して UI に渡す

### 3. app.py — Gradio UI

**UI 構成:**
- `gr.ChatInterface` または `gr.Blocks` でチャット画面を構築
- ストリーミング: `yield` でトークンを逐次返す
- 出典エリア: チャットの下に `gr.Markdown` または `gr.Accordion` で表示
- リセットボタン: 会話履歴リスト（`list`）をクリア

**会話履歴の扱い:**
- セッション内のみ保持（Python リストで管理）
- LangChain の `ConversationBufferMemory` または messages リストで多ターン対応

---

## 依存パッケージ一覧（想定）

```toml
# pyproject.toml の dependencies
dependencies = [
    "pdfplumber",
    "langchain",
    "langchain-ollama",
    "langchain-qdrant",
    "qdrant-client",
    "gradio",
]
```

---

## .gitignore に含めるもの

```
qdrant_storage/
__pycache__/
.venv/
*.pyc
```

---

## 注意事項

- Ollama は起動済みである前提（メニューバーの ollama アプリが起動していること）
- モデルが未取得の場合は `ollama pull qwen3:14b` と `ollama pull qwen3-embedding:0.6b` を先に実行
- `qwen3-embedding:0.6b` のベクトル次元数は **1024**。Qdrant コレクション作成時に `size=1024` を指定する
- `langchain-qdrant` は `langchain-community` の Qdrant 統合とは別パッケージなので注意
