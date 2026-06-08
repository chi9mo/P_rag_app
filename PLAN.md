# 実装プラン

## 前提

- 環境構築（SETUP.md）は完了済み
- 仕様は SPEC.md、実装方針は CLAUDE.md に準拠
- 実行コマンド: `uv run python -m rag_app.app`

---

## フェーズ一覧

| フェーズ | 内容 | 成果物 |
|---|---|---|
| 1 | プロジェクト構造の作成 | `src/rag_app/` ディレクトリ、`__init__.py` |
| 2 | インデックス構築 | `indexer.py` |
| 3 | RAG チェーン | `chain.py` |
| 4 | Gradio UI | `app.py` |
| 5 | 統合テスト | 動作確認 |

---

## Phase 1: プロジェクト構造の作成

### タスク

- [ ] `src/rag_app/` ディレクトリを作成する
- [ ] `src/rag_app/__init__.py` を作成する（空ファイル）
- [ ] `src/rag_app/indexer.py` を作成する（空ファイル）
- [ ] `src/rag_app/chain.py` を作成する（空ファイル）
- [ ] `src/rag_app/app.py` を作成する（空ファイル）
- [ ] `.gitignore` に `qdrant_storage/`, `.venv/`, `__pycache__/`, `*.pyc`, `guideline.pdf` が含まれていることを確認する
- [ ] `pyproject.toml` に `[tool.uv] package = true` または src レイアウト用の設定が必要か確認する

---

## Phase 2: indexer.py — インデックス構築

### 役割

`guideline.pdf` を読み込み、チャンクに分割して Qdrant に投入する。
アプリ起動時に呼び出され、`qdrant_storage/` が存在する場合はスキップする。

### タスク

- [ ] pdfplumber で PDF を読み込み、ページ単位でテキストを抽出する
  - `page.page_number` を `metadata["page"]` として Document に格納
- [ ] `RecursiveCharacterTextSplitter` でチャンク分割する
  - `chunk_size=500`, `chunk_overlap=50`
- [ ] `OllamaEmbeddings(model="qwen3-embedding:0.6b")` を初期化する
- [ ] `QdrantClient(path="./qdrant_storage")` を初期化する
- [ ] Qdrant コレクション `"guideline"` を作成する
  - ベクトル次元数: `size=1024`
- [ ] `QdrantVectorStore` にチャンクを投入する
- [ ] 起動時判定ロジックを実装する
  - `qdrant_storage/` が存在し、コレクションが存在すればスキップ
  - 存在しなければ構築を実行
- [ ] `build_index()` と `load_vectorstore()` を関数として整理する

---

## Phase 3: chain.py — RAG チェーン

### 役割

Retriever と LLM を繋ぎ、ストリーミングで回答を返す。
`(answer_stream, source_documents)` の形で呼び出し元に返す。

### タスク

- [ ] `ChatOllama(model="qwen3:14b", streaming=True)` を初期化する
- [ ] Retriever を設定する
  - `vectorstore.as_retriever(search_kwargs={"k": 4})`
- [ ] システムプロンプトを実装する
  - 日本語で回答するよう指示
  - 提供されたコンテキストのみを根拠に回答させる
  - コンテキストに情報がない場合は「資料に記載がありません」と答えさせる
- [ ] 会話履歴（messages リスト）を受け取り、RAG 検索 + LLM 呼び出しを行う関数を実装する
- [ ] ストリーミングトークンを `yield` で返す実装にする
- [ ] `source_documents` から `metadata["page"]` と `page_content` を取り出して返す

---

## Phase 4: app.py — Gradio UI

### 役割

チャット画面を提供するエントリポイント。

### タスク

- [ ] `gr.Blocks` でレイアウトを構築する
- [ ] `gr.Chatbot` でチャット表示エリアを配置する
- [ ] テキスト入力欄と送信ボタンを配置する
- [ ] ストリーミング表示を実装する（`yield` でトークンを逐次更新）
- [ ] 出典エリアを配置する
  - 回答の下に `gr.Accordion` または `gr.Markdown` でページ番号と引用テキストを表示
- [ ] リセットボタンを配置する（会話履歴リストをクリア）
- [ ] 会話履歴を Python リストで管理する（セッション内のみ保持）
- [ ] アプリ起動時に `indexer.py` の判定ロジックを呼び出す

---

## Phase 5: 統合テスト・動作確認

### タスク

- [ ] アプリを起動する: `uv run python -m rag_app.app`
- [ ] 初回起動でインデックスが自動構築されることを確認する
- [ ] `qdrant_storage/` が生成されていることを確認する
- [ ] 2回目の起動でインデックス構築がスキップされることを確認する
- [ ] 質問を入力してストリーミングで回答が返ることを確認する
- [ ] 出典（ページ番号・引用テキスト）が表示されることを確認する
- [ ] リセットボタンで会話履歴がクリアされることを確認する
- [ ] `guideline.pdf` に記載のない質問に対して「資料に記載がありません」と返ることを確認する

---

## 実装順序の注意点

- Phase 2 → Phase 3 → Phase 4 の順に実装する（依存関係あり）
- Phase 2 完了後、単体で `build_index()` を実行してインデックスが構築できることを確認してから Phase 3 に進む
- Phase 3 完了後、Gradio なしで chain を呼び出してレスポンスが返ることを確認してから Phase 4 に進む
