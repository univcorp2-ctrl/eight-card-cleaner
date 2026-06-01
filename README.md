<!-- AI_README_SETUP_GUIDE_START -->
## 🧭 画像付き初期設定ガイド

![README 画像付き初期設定ガイド](docs/assets/readme-setup-guide.svg)

このリポジトリ **eight-card-cleaner** を初めて開いた人は、まずここだけ見れば初期設定から実行、成果物確認まで進められます。

### 最初にやること

1. 必要なSecretや外部サービス設定を確認します。
2. GitHub Actions または README の実行手順に沿って動かします。
3. 実行ログと成果物を確認します。
4. エラー時は Actions の失敗ステップと Secret名を確認します。

### 詳しい画像付きガイド

- [docs/setup-visual-guide.md](docs/setup-visual-guide.md)
- [docs/image-generation-prompts.md](docs/image-generation-prompts.md)

> SecretやAPIキーの実値は、README、Issue、ログ、画像に絶対に貼らないでください。例では `********` または `YOUR_SECRET_HERE` を使います。

<!-- AI_README_SETUP_GUIDE_END -->


# eight-card-cleaner

Eightの公式エクスポートCSVを読み込み、名刺情報をきれいに整形してCSV/XLSXで出力するPython CLIです。

> 注意: このツールはログイン後ページをスクレイピングしません。Eightの公式ダウンロード機能で取得したCSVを対象にします。

## 主な機能

- UTF-8 BOM / UTF-8 / CP932 / Shift_JIS の自動読み込み
- 全セルの前後空白、全角スペース、連続空白の整理
- メールアドレスの小文字化
- 電話番号、FAX番号の表記ゆれ整理
- メールアドレス優先の重複削除
- CSVとExcelの両方に出力

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Excel出力も使う場合:

```bash
pip install -e '.[excel]'
```

開発・テスト用:

```bash
pip install -e '.[dev,excel]'
pytest
```

## 使い方

```bash
eight-card-cleaner input.csv --csv output.csv --xlsx output.xlsx
```

CSVだけ出す場合:

```bash
eight-card-cleaner input.csv --csv output.csv --no-xlsx
```

重複削除をしない場合:

```bash
eight-card-cleaner input.csv --csv output.csv --no-dedupe
```

## 推奨フロー

1. Eightの公式機能から名刺データをCSVでダウンロードする
2. このツールで整形する
3. CRM、Google Contacts、Excelなどに取り込む

## 例

```bash
eight-card-cleaner eight_export.csv --csv eight_cards_clean.csv --xlsx eight_cards_clean.xlsx
```

## ライセンス

MIT
