# 米国株ランキング・チャート（GitHub Pages）

Yahoo Finance の日足データを取得し、ランキングとローソク足チャートを公開する米国株版です。日本株版とは別の新規リポジトリで使用してください。

## stocks.txt の書き方

1行に「Yahoo Finance のティッカー + 半角スペース + 表示名」を記入します。

```text
NVDA NVIDIA
AAPL Apple
MSFT Microsoft
AMZN Amazon
```

米国株は `NVDA`、`AAPL` のようにティッカーをそのまま指定します。通常、日本株の `.T` は付けません。クラス株などは Yahoo Finance 上の表記（例: `BRK-B`）を使用してください。表示名は省略でき、省略時はティッカーが表示名になります。

## 含まれる機能

- Yahoo Finance（yfinance）から最大10年分の日足OHLCデータを取得
- 指定期間内の最安値と最新終値から比率を計算し、比率の小さい順にランキング表示
- 日足・週足・月足のローソク足チャート
- チャート表示期間の変更
- 前の会社／次の会社ボタンで手動切り替え
- 1秒・3秒・5秒・10秒・15秒・30秒・60秒の自動切り替え
- GitHub Actions の Run workflow で株価データを更新
- スマートフォン対応

## GitHub への設定

1. 新しい **Public** リポジトリ（例: `us-stock-ranking`）を作成します。
2. このZIP内のファイルと `.github/workflows/update-stocks.yml` をリポジトリの同じ階層にアップロードします。
3. `stocks.txt` を自分の銘柄リストに編集します。
4. リポジトリの **Settings → Actions → General → Workflow permissions** で **Read and write permissions** を選び、保存します。
5. **Settings → Pages** で **Deploy from a branch** を選び、ブランチ `main`、フォルダー `/ (root)` を指定して保存します。
6. **Actions → Update US stock ranking → Run workflow** を実行します。
7. 実行が成功し `stock_data.json` が生成されたら、GitHub Pages のURLを開きます。

## 注意

- `stocks.txt`、ソースコード、取得した株価データはPublicリポジトリ上で公開されます。秘密情報は置かないでください。
- Yahoo Finance/yfinance のデータは必ずしもリアルタイムではなく、欠損・遅延・仕様変更が起こる場合があります。
- ランキングは投資判断のための参考情報であり、投資助言ではありません。
- Actions の実行に失敗した場合は、Actions タブでログを確認してください。
