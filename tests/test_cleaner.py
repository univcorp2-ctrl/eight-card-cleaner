from pathlib import Path

import pandas as pd

from eight_card_cleaner.cleaner import clean_email, clean_phone, clean_text, normalize_dataframe, clean_file


def test_clean_text_normalizes_spaces():
    assert clean_text("  山田　太郎  ") == "山田 太郎"


def test_clean_email_lowercases_and_validates():
    assert clean_email("  TARO@example.COM ") == "taro@example.com"
    assert clean_email("not-an-email") == ""


def test_clean_phone_keeps_readable_separators():
    assert clean_phone("TEL: 03-1234-5678") == "03-1234-5678"


def test_normalize_dataframe_cleans_and_deduplicates():
    df = pd.DataFrame(
        [
            {"会社名": " 株式会社サンプル ", "氏名": "山田　太郎", "メール": "TARO@EXAMPLE.COM", "電話": "TEL: 03-1234-5678"},
            {"会社名": "株式会社サンプル", "氏名": "山田 太郎", "メール": "taro@example.com", "電話": "03-1234-5678"},
            {"会社名": "別会社", "氏名": "佐藤 花子", "メール": "hanako@example.com", "電話": "090 1111 2222"},
        ]
    )

    cleaned = normalize_dataframe(df)

    assert len(cleaned) == 2
    assert cleaned.loc[0, "会社名"] == "株式会社サンプル"
    assert cleaned.loc[0, "氏名"] == "山田 太郎"
    assert cleaned.loc[0, "メール"] == "taro@example.com"


def test_clean_file_writes_csv(tmp_path: Path):
    input_csv = tmp_path / "input.csv"
    output_csv = tmp_path / "output.csv"

    pd.DataFrame([{"会社名": " テスト株式会社 ", "メール": "INFO@EXAMPLE.COM"}]).to_csv(input_csv, index=False, encoding="utf-8-sig")

    cleaned = clean_file(input_csv, output_csv, xlsx_path=None)

    assert output_csv.exists()
    assert len(cleaned) == 1
    assert cleaned.loc[0, "メール"] == "info@example.com"
