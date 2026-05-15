from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

import pandas as pd

DEFAULT_ENCODINGS = ("utf-8-sig", "utf-8", "cp932", "shift_jis")

EMAIL_HINTS = ("mail", "e-mail", "email", "メール")
PHONE_HINTS = ("tel", "phone", "電話", "携帯", "mobile")
FAX_HINTS = ("fax", "ＦＡＸ", "ファックス")
COMPANY_HINTS = ("会社", "company", "organization", "勤務先")
NAME_HINTS = ("氏名", "姓名", "name", "姓", "名")


def read_csv_auto(path: str | Path, encodings: Iterable[str] = DEFAULT_ENCODINGS) -> pd.DataFrame:
    """Read a CSV file by trying common Japanese encodings."""
    csv_path = Path(path)
    last_error: Exception | None = None

    for encoding in encodings:
        try:
            return pd.read_csv(csv_path, encoding=encoding, dtype=str).fillna("")
        except UnicodeDecodeError as exc:
            last_error = exc

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        f"Could not decode {csv_path} with: {', '.join(encodings)}",
    ) from last_error


def clean_text(value: object) -> str:
    """Normalize whitespace while preserving user-visible text."""
    if pd.isna(value):
        return ""
    text = str(value).replace("\u3000", " ").strip()
    text = re.sub(r"[ \t]+", " ", text)
    return text


def clean_email(value: object) -> str:
    text = clean_text(value).lower()
    return text if "@" in text else ""


def clean_phone(value: object) -> str:
    text = clean_text(value)
    if not text:
        return ""
    # Keep digits, leading plus, and common separators for readability.
    text = re.sub(r"[^0-9+()\- ]", "", text)
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text


def _matching_columns(columns: Iterable[str], hints: Iterable[str]) -> list[str]:
    lowered = {column: column.lower() for column in columns}
    return [
        column
        for column in columns
        if any(hint.lower() in lowered[column] or hint in column for hint in hints)
    ]


def normalize_dataframe(df: pd.DataFrame, dedupe: bool = True) -> pd.DataFrame:
    """Clean and optionally deduplicate a DataFrame exported from Eight."""
    cleaned = df.copy()
    cleaned.columns = [clean_text(column) for column in cleaned.columns]

    for column in cleaned.columns:
        cleaned[column] = cleaned[column].map(clean_text)

    for column in _matching_columns(cleaned.columns, EMAIL_HINTS):
        cleaned[column] = cleaned[column].map(clean_email)

    for column in _matching_columns(cleaned.columns, PHONE_HINTS + FAX_HINTS):
        cleaned[column] = cleaned[column].map(clean_phone)

    cleaned = cleaned.replace("", pd.NA).dropna(how="all").fillna("")

    if dedupe:
        cleaned = deduplicate(cleaned)

    return cleaned.reset_index(drop=True)


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate rows using email first, then company/name-like columns."""
    email_columns = _matching_columns(df.columns, EMAIL_HINTS)
    for column in email_columns:
        non_empty = df[column].astype(str).str.len() > 0
        with_email = df[non_empty].drop_duplicates(subset=[column], keep="first")
        without_email = df[~non_empty]
        df = pd.concat([with_email, without_email], ignore_index=True)
        break

    key_candidates = _matching_columns(df.columns, COMPANY_HINTS + NAME_HINTS)
    if key_candidates:
        subset = key_candidates[:4]
        df = df.drop_duplicates(subset=subset, keep="first")

    return df


def clean_file(input_path: str | Path, csv_path: str | Path, xlsx_path: str | Path | None = None, dedupe: bool = True) -> pd.DataFrame:
    df = read_csv_auto(input_path)
    cleaned = normalize_dataframe(df, dedupe=dedupe)

    csv_output = Path(csv_path)
    csv_output.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(csv_output, index=False, encoding="utf-8-sig")

    if xlsx_path is not None:
        xlsx_output = Path(xlsx_path)
        xlsx_output.parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_excel(xlsx_output, index=False)

    return cleaned


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean Eight exported business card CSV files.")
    parser.add_argument("input", type=Path, help="Path to Eight exported CSV file")
    parser.add_argument("--csv", type=Path, default=Path("eight_cards_clean.csv"), help="CSV output path")
    parser.add_argument("--xlsx", type=Path, default=Path("eight_cards_clean.xlsx"), help="XLSX output path")
    parser.add_argument("--no-xlsx", action="store_true", help="Do not write XLSX output")
    parser.add_argument("--no-dedupe", action="store_true", help="Do not deduplicate rows")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    xlsx_path = None if args.no_xlsx else args.xlsx
    cleaned = clean_file(args.input, args.csv, xlsx_path, dedupe=not args.no_dedupe)
    print(f"Cleaned {len(cleaned)} rows")
    print(f"CSV: {args.csv}")
    if xlsx_path is not None:
        print(f"XLSX: {xlsx_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
