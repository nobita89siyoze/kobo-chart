name: Fetch 1min OHLCV

on:
  workflow_dispatch:
    inputs:
      year:
        description: '取得する年（例: 2022, 2023, 2024, 2025, all）'
        required: true
        default: '2025'

jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install requests pandas

      - name: Fetch 1min data
        env:
          JQUANTS_API_KEY: ${{ secrets.JQUANTS_API_KEY }}
        run: python fetch_1min.py "${{ github.event.inputs.year }}"

      - name: Upload CSV
        uses: actions/upload-artifact@v4
        with:
          name: 1min-ohlcv-${{ github.event.inputs.year }}
          path: output/*.csv
          retention-days: 30
