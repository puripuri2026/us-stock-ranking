from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd
import yfinance as yf


def read_stocks(path: Path) -> list[dict]:
    """stocks.txt の「ティッカー 会社名」を読み込む。"""
    if not path.exists():
        raise FileNotFoundError(f"銘柄リストが見つかりません: {path}")

    stocks = []
    seen = set()
    for line_no, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue

        parts = line.split(maxsplit=1)
        ticker = parts[0].strip().upper()
        name = parts[1].strip() if len(parts) > 1 else ticker

        # Yahoo Finance の米国株シンボルに対応。例: NVDA, AAPL, BRK-B
        if not re.fullmatch(r"[A-Z0-9][A-Z0-9.-]{0,14}", ticker):
            print(f"警告: {line_no}行目を読み飛ばします: {raw}", file=sys.stderr)
            continue
        if ticker in seen:
            print(f"警告: 重複ティッカーをスキップします: {ticker}", file=sys.stderr)
            continue

        seen.add(ticker)
        stocks.append({"code": ticker, "name": name, "ticker": ticker})

    if not stocks:
        raise ValueError(
            "stocks.txt に有効な米国株ティッカーがありません。例: NVDA NVIDIA"
        )
    return stocks


def download_one(stock: dict) -> dict:
    ticker = stock["ticker"]
    print(f"株価取得中: {ticker} ({stock['name']})")
    frame = yf.download(
        ticker,
        period="10y",
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    if frame is None or frame.empty:
        print(f"警告: データを取得できませんでした: {ticker}", file=sys.stderr)
        return {**stock, "data": [], "error": "株価データを取得できませんでした"}

    # yfinance のバージョンによって MultiIndex になる場合に対応
    if isinstance(frame.columns, pd.MultiIndex):
        level0 = set(map(str, frame.columns.get_level_values(0)))
        if {"Open", "High", "Low", "Close"}.issubset(level0):
            frame.columns = frame.columns.get_level_values(0)
        else:
            frame.columns = frame.columns.get_level_values(-1)

    required = ["Open", "High", "Low", "Close"]
    if not all(column in frame.columns for column in required):
        return {**stock, "data": [], "error": "OHLC列がありません"}

    frame = frame[required].dropna(subset=required)
    rows = []
    for timestamp, row in frame.iterrows():
        try:
            rows.append({
                "time": pd.Timestamp(timestamp).date().isoformat(),
                "open": round(float(row["Open"]), 4),
                "high": round(float(row["High"]), 4),
                "low": round(float(row["Low"]), 4),
                "close": round(float(row["Close"]), 4),
            })
        except (TypeError, ValueError):
            continue

    return {
        **stock,
        "data": rows,
        "error": None if rows else "株価データがありません",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="米国株の株価履歴を取得します")
    parser.add_argument("--input", default="stocks.txt")
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stocks = read_stocks(Path(args.input))

    results = []
    for stock in stocks:
        try:
            results.append(download_one(stock))
        except Exception as exc:
            print(f"警告: {stock['ticker']} の処理中にエラー: {exc}", file=sys.stderr)
            results.append({**stock, "data": [], "error": str(exc)})

    successful = sum(bool(stock["data"]) for stock in results)
    payload = {
        "generatedAt": pd.Timestamp.now(tz="Asia/Tokyo").isoformat(),
        "source": "Yahoo Finance via yfinance (US stocks)",
        "market": "US",
        "historyYears": 10,
        "stocks": results,
    }
    output_file = output_dir / "stock_data.json"
    output_file.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"出力: {output_file}（{successful}/{len(results)}銘柄で取得）")
    if successful == 0:
        raise RuntimeError("全銘柄の株価データを取得できませんでした。")


if __name__ == "__main__":
    main()
