# セットアップ Q&A

## Q. `ollama serve` と `brew services start ollama` の違いは？

| | `ollama serve` | `brew services start ollama` |
|---|---|---|
| 起動方法 | 手動（フォアグラウンド） | 自動（バックグラウンド） |
| ターミナル | 占有される | 占有されない |
| Mac再起動後 | 自動起動しない | 自動起動する |
| ログ確認 | ターミナルにそのまま出る | ログファイルに記録される |
| 停止方法 | `Ctrl+C` | `brew services stop ollama` |

**このプロジェクトでは `brew services start ollama` の方が便利。**

理由：
- ターミナルを1つ消費しない
- Mac再起動後も自動で立ち上がるので、毎回コマンドを打たなくて済む

`ollama serve` はサーバーのログをリアルタイムで見たいデバッグ時に使う程度。

---

## Q. Embedding 疎通確認で `llama-server binary not found` エラーが出た

### エラーの核心

```
ollama._types.ResponseError: error starting llama-server: llama-server binary not found
(status code: 500)
```

### 原因

ollama **v0.30.0** からアーキテクチャが変更され、モデルを動かすエンジンとして `llama-server` という別バイナリが必要になった。しかし **Homebrew の formula がこの変更に未対応**のため、`brew install ollama` で入るパッケージに `llama-server` が含まれていない。

- 関連 Issue: [ollama/ollama #16535](https://github.com/ollama/ollama/issues/16535)
- Homebrew 修正 PR: [homebrew-core #285963](https://github.com/Homebrew/homebrew-core/pull/285963)（2026年6月時点で未マージ）

### エラーメッセージの `cmake ...` では解決しないのか

エラーメッセージには以下の案内がある：

> Run `cmake -S llama/server --preset cpu && cmake --build --preset cpu` first

これは「ソースコードから自分でビルドしてください」という開発者向けの手順。cmake のインストール・Xcode ツール・数十分のビルド時間が必要で、一般ユーザーが取るべき対処ではない。

### ステータスコード 500 について

HTTP 500 = サーバー内部エラー。「ollama サーバー自体は起動しているが、内部処理（今回は `llama-server` の起動）が失敗した」ときに返るコード。

### 対応: 公式インストーラーへ切り替える

公式インストーラー（`.dmg`）は `llama-server` を含むすべてのバイナリが同梱されている。Homebrew の修正が未マージである以上、これが唯一の確実な解決策。

```bash
# 1. Homebrew 版を停止・削除
brew services stop ollama
brew uninstall ollama  # ちなみに、アンインストールしてもモデルデータは消えない。

# 2. ollama.com から macOS 用インストーラーをダウンロードしてインストール
```

インストール後はメニューバーに ollama アイコンが表示され、自動起動する（`brew services` は不要）。
