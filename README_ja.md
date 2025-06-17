# LLMCommit

LLMを使用してgitコミットメッセージを自動生成する高速CLIツール。
git add、commit、pushまでを一つのコマンドで実行可能。

🚀 **NEW**: ファイルキャッシュ機能で同じdiffは瞬時に処理！

## 解決する悩み

### 😩 よくある開発者の悩み

- **「コミットメッセージを考えるのが面倒...」**
  - 変更内容は覚えているけど、適切な言葉にするのに時間がかかる
  - 毎回 `git commit -m "update"` で済ませてしまう
  - 後から見返した時に何をしたか分からない

- **「毎回同じような作業の繰り返し...」**
  - `git add .` → `git commit -m "..."` → `git push` の3ステップが面倒
  - コミットメッセージを考える→タイプする→間違える→やり直す
  - 小さな変更でも手間がかかりすぎる

- **「英語でのコミットメッセージが苦手...」**
  - 適切な英語表現が思い浮かばない
  - 文法やスペルが心配
  - チーム内で統一感のないメッセージになってしまう

- **「開発の流れが中断される...」**
  - コーディングに集中していたのにコミット作業で思考が途切れる
  - メッセージを考えている間に次に何をするか忘れる
  - 作業効率が下がってしまう

### ✅ llmcommitでの解決

- **🤖 AIが自動でメッセージ生成**
  - 変更内容を解析して適切なメッセージを自動生成
  - 一貫性のある品質の高いメッセージ
  - 英語・日本語両対応

- **⚡ ワンコマンドで完結**
  - `llmcommit -a -p` だけでadd→commit→pushまで完了
  - 思考の中断を最小限に
  - 2-3秒で処理完了

- **🎯 実用的な品質**
  - ファイルタイプに応じた適切なメッセージ
  - 「Update configuration」「Fix bug in auth」など文脈を理解
  - チーム開発でも使える品質

- **💾 学習機能付き**
  - 同じような変更は瞬時にキャッシュから返却
  - 使うほど速くなる
  - プロジェクト固有のパターンも学習

### 🎯 こんな人におすすめ

- **個人開発者**: 一人で開発していてコミットメッセージに時間をかけたくない
- **チーム開発**: メッセージの品質を統一したい
- **非英語ネイティブ**: 英語でのコミットメッセージに自信がない
- **効率重視**: 開発の流れを中断したくない
- **初心者**: 良いコミットメッセージの書き方を学びたい

### 📈 導入効果

| Before | After |
|--------|-------|
| 毎回3-5分かけてメッセージを考える | **2.5秒**で自動生成 ⚡ |
| `git add` → `git commit` → `git push` | `llmcommit -a -p` |
| 「update」「fix」など適当なメッセージ | 「Update user authentication logic」など具体的 |
| 英語表現で悩む | AI が適切な英語で生成 |
| 作業の流れが中断される | シームレスな開発体験 |
| 初回設定が面倒 | **自動で最適化設定を作成** ✨ |

## 特徴

- 🤖 **LLMベース**: Hugging Face Transformersを使用
- 🐳 **Docker対応**: 環境差異を防ぐDockerベース実行
- ⚡ **軽量**: コンパクトなモデルに最適化
- 💾 **キャッシュ**: ファイルベースキャッシュで高速化
- 📈 **進行状況表示**: 各ステップを可視化
- 🎛️ **設定可能**: モデルやプロンプトを簡単に切り替え
- 🇯🇵 **日本語対応**: 日本製PLamoモデルも対応

## インストール

### ワンライナーインストール
```bash
curl -sSL https://raw.githubusercontent.com/0xkaz/llmcommit/main/install.sh | bash
```

### ローカルインストール
```bash
pip install llmcommit
```

### Docker使用
```bash
git clone https://github.com/0xkaz/llmcommit.git
cd llmcommit
make setup
```

## 使い方

### 基本コマンド
```bash
# 自動でadd + commit + push
llmcommit -a -p

# 最速モード（フックスキップ）
llmcommit -a -p --no-verify

# ドライラン（確認のみ）
llmcommit --dry-run

# キャッシュ管理
llmcommit-cache stats    # 統計表示
llmcommit-cache clear    # 古いキャッシュを削除
```

### オプション一覧
- `-a, --add-all`: 全ファイルを自動でgit add
- `-p, --push`: コミット後に自動でpush
- `--no-verify`: gitフックをスキップ（高速化）
- `--force-push`: 強制push（注意して使用）
- `--dry-run`: コミットせずメッセージのみ表示
- `--preset PRESET`: 設定プリセットを使用
- `--no-cache`: キャッシュを無効化
- `--cache-dir PATH`: カスタムキャッシュディレクトリ

### プリセット一覧
```bash
# 超高速モード（2.5秒）
llmcommit --preset ultra-fast -a -p

# 軽量LLMモード（3-5秒）
llmcommit --preset ultra-light -a -p

# 高性能軽量モード（5-8秒）
llmcommit --preset light -a -p

# バランス型（8-12秒）
llmcommit --preset balanced -a -p

# 標準モード（10-15秒）
llmcommit --preset standard -a -p
```

## 高速化のポイント

1. **⚡ 高速モード（デフォルト）**: ルールベースエンジンで2.5秒実行
2. **🎯 自動設定作成**: 初回実行時に最適化設定を自動生成
3. **💾 キャッシュ機構**: 同じdiffは瞬時に返却（<0.1秒）
4. **🚫 遅延インポート**: 高速モード時はLLMライブラリを読み込まない
5. **🔧 フックスキップ**: `--no-verify`でさらに高速

## パフォーマンス

### 実行時間の比較

| 状況 | 時間 | 説明 |
|------|------|------|
| **高速モード（デフォルト）** | **2.5秒** | ⚡ ルールベースエンジン |
| 初回実行（LLMモード） | 30-60秒 | モデルダウンロード含む |
| 2回目以降（LLMモード） | 10-30秒 | モデルロードのみ |
| キャッシュヒット | <0.1秒 | 同じdiffの場合 |

### 対応モデル

| モデル | サイズ | 速度 | 用途 |
|--------|--------|------|------|
| **SmolLM-135M** | 135M | ⚡⚡ 超高速 | 🏆 2024年最軽量 |
| **TinyLlama-1.1B** | 1.1B | ⚡ 最速LLM | 🎯 高性能軽量 |
| distilgpt2 | 82M | 🚀 高速 | 基本用途 |
| DialoGPT-small | 117M | 🌟 中速 | 対話特化 |
| gpt2 | 124M | 🌠 中速 | 標準品質 |

## 設定

`.llmcommit.json` ファイルで設定をカスタマイズ：

```json
{
  "preset": "ultra-fast",
  "cache_dir": "~/.cache/llmcommit",
  "auto_add": true,
  "auto_push": false
}
```

## よくある使用例

```bash
# 開発中の高速コミット
llmcommit -a -p --no-verify

# 慎重なコミット（確認後に実行）
llmcommit --dry-run
llmcommit -a

# キャッシュ統計確認
llmcommit-cache stats

# 古いキャッシュをクリア（7日以上）
llmcommit-cache clear --days 7
```

## トラブルシューティング

### モデルダウンロードが遅い
初回はモデルダウンロードが必要です。一度ダウンロードすれば永続化されます。

### キャッシュが効かない
```bash
# キャッシュ統計を確認
llmcommit-cache stats

# キャッシュディレクトリを確認
llmcommit-cache show
```

### メモリ不足
より小さいモデル（ultra-fast）を使用するか、Docker環境で実行してください。

## ライセンス

MIT License