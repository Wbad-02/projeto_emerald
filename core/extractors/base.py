from __future__ import annotations

import csv
import io
import re
import unicodedata
from abc import ABC, abstractmethod

import pandas as pd


class BaseExtractor(ABC):
    def __init__(self, uploaded_file):
        self.file = uploaded_file

    @abstractmethod
    def execute(self):
        raise NotImplementedError

    @staticmethod
    def normalize(text: str) -> str:
        if not text:
            return ""
        nfkd = unicodedata.normalize("NFKD", str(text))
        return "".join(c for c in nfkd if not unicodedata.combining(c)).upper().strip()

    @staticmethod
    def extract_year(text: str):
        if not text:
            return None
        match = re.search(r"\b(20\d{2})\b", str(text))
        return match.group(1) if match else None

    @staticmethod
    def parse_decimal(value):
        if value is None:
            return 0.0

        raw = str(value).strip()
        if not raw or raw in {"-", "0", "0.0", "0,0", "0,00", "0.00"}:
            return 0.0

        negative = "(" in raw or ")" in raw or raw.startswith("-")
        cleaned = re.sub(r"[^\d,\.-]", "", raw)

        has_dot = "." in cleaned
        has_comma = "," in cleaned

        if has_dot and has_comma:
            if cleaned.rfind(",") > cleaned.rfind("."):
                cleaned = cleaned.replace(".", "").replace(",", ".")
            else:
                cleaned = cleaned.replace(",", "")
        elif has_comma and not has_dot:
            cleaned = cleaned.replace(".", "").replace(",", ".")

        cleaned = cleaned.replace("--", "-")

        try:
            number = float(cleaned)
        except ValueError:
            return 0.0

        return -abs(number) if negative else number

    def _read_raw_bytes(self):
        self.file.seek(0)
        raw_bytes = self.file.read()
        self.file.seek(0)
        return raw_bytes

    def read_csv_rows(self):
        raw = self._read_raw_bytes()
        text = ""
        for enc in ("utf-8", "latin-1", "cp1252", "utf-16"):
            try:
                text = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        if not text:
            return []

        return list(csv.reader(io.StringIO(text)))

    def read_excel_rows(self, engine=None):
        raw = self._read_raw_bytes()
        try:
            df = pd.read_excel(io.BytesIO(raw), header=None, dtype=str, engine=engine)
        except Exception:
            return []

        return (
            df.fillna("")
            .astype(str)
            .apply(lambda row: row.tolist(), axis=1)
            .tolist()
        )

    def read_pdf_lines(self):
        try:
            from pypdf import PdfReader
        except Exception:
            return []

        raw = self._read_raw_bytes()
        try:
            reader = PdfReader(io.BytesIO(raw))
        except Exception:
            return []

        lines = []
        for page in reader.pages:
            content = page.extract_text() or ""
            lines.extend(content.splitlines())
        return lines
