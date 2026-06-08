# 環境構築手順

## 手順表

| ツール | 状態 |
|---|---|
| `uv` |  |
| `python3` |  |
| `ollama` |  |
| `pyproject.toml` |  |

---

## Step 1: Python バージョンの固定

Python 3.14 は最新すぎてライブラリの wheel が揃っていないケースがあるため、
安定性の高い **3.12** を uv で管理する（グローバル環境の Homebrew Python は変更しない）。

```bash
# プロジェクトルートで実行
# 使う Python バージョンを固定
uv python pin 3.12
```

`.python-version` ファイルが生成され、このプロジェクト内では 3.12 が使われる。

---

## Step 2: Ollama のインストール

### 推奨: curl

現在（2026/6/9）、
ollama v0.30.0 以降、Homebrew 版は `llama-server` バイナリが含まれておらず動作しない問題がある（2026年6月時点で未修正）。公式インストーラーを使うこと。

以下のコマンドを実行する。

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

インストール後はメニューバーに ollama アイコンが表示され、自動起動する。

動作確認:

```bash
ollama --version
```

---

### 参考: Homebrew でのインストール（現在は非推奨）

> **注意:** v0.30.0 以降は `llama-server binary not found` エラーが発生する。詳細は `SETUP_QA.md` を参照。

```bash
brew install ollama
brew services start ollama
```

---

## Step 3: LLM・Embedding モデルの取得

モデルのダウンロードは時間がかかるため、先に実行しておく。


```bash
# LLM（約9GB）
ollama pull qwen3:14b

# Embedding（約600MB）
ollama pull qwen3-embedding:0.6b
```

取得済みモデルの確認:

```bash
ollama list
```

---
## Step 4: uv プロジェクトの初期化

```bash
uv init --no-readme
```

`pyproject.toml` が生成される。生成後、`pyproject.toml` の `requires-python` が
`3.12` になっていることを確認する（`uv init` は `.python-version` を参照する）。

> `uv init` が生成するサンプルファイル（`hello.py` など）は削除してよい。
> src レイアウトのディレクトリ構成は実装フェーズで作成する。

---

## Step 5: 依存パッケージのインストール

```bash
uv add pdfplumber langchain langchain-ollama langchain-qdrant qdrant-client gradio
```

`.venv/` がプロジェクトルートに作成され、グローバル環境は汚染されない。


インストール確認:

```bash
uv run python -c "import pdfplumber, langchain, gradio, qdrant_client; print('OK')"
```

---

## Step 6: 動作確認

Ollama が起動していることを確認:

```bash
ollama list
```

Embedding モデルの疎通確認:

```bash
uv run python -c "
from langchain_ollama import OllamaEmbeddings
emb = OllamaEmbeddings(model='qwen3-embedding:0.6b')
print(len(emb.embed_query('テスト')))  # 1024 が出れば OK
"
```

---

## セットアップ完了後のディレクトリ構成

```
P_rag_app/
├── .python-version     # 3.12 固定
├── .venv/              # uv が管理（.gitignore 対象）
├── pyproject.toml
├── uv.lock
├── guideline.pdf       # .gitignore 対象
├── SPEC.md
├── CLAUDE.md
├── SETUP.md
└── .gitignore
```

---

## トラブルシューティング

| 症状 | 対処 |
|---|---|
| `ollama: command not found` | 公式インストーラーで再インストール |
| `llama-server binary not found` | Homebrew 版の既知バグ。公式インストーラーへ切り替える（`SETUP_QA.md` 参照） |
| Embedding の疎通確認で接続エラー | メニューバーの ollama アイコンから起動を確認 |
| `uv run python` で `ModuleNotFoundError` | `uv sync` を実行して `.venv` を再構築 |
| モデルのダウンロードが途中で止まる | `ollama pull <model>` を再実行（レジューム対応） |
