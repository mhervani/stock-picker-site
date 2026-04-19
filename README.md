# Stock Picker Site

Statisk nettside for et løpende stock-picking-eksperiment med månedlige porteføljer.

Nettsiden viser:
- aktiv måned
- månedens 3 picks
- benchmark mot S&P 500 og DNB Global Indeks
- graf for utvikling siden kjøp
- 2-ukers oppdatering
- historikk
- track record
- detaljside per måned

## Stack

- VS Code lokalt
- GitHub repo
- GitHub Pages for hosting
- GitHub Actions for automatiske prisoppdateringer
- HTML / CSS / JS frontend
- Python-scripts for dataflyt

---

## Mappestruktur

```text
data/
  raw/
    YYYY-MM-portfolio.txt
    YYYY-MM-midmonth.txt
    YYYY-MM-month-end.txt
  months/
    YYYY-MM.json
    index.json
  current_portfolio.json
  benchmarks.json
  updates.json
  performance.json
  monthly_history.json
  track_record.json
  chart_data.json

scripts/
  parse_llm_output.py
  parse_midmonth_output.py
  parse_month_end_output.py
  hydrate_month_benchmarks.py
  finalize_month_start.py
  apply_month_to_active.py
  rebuild_months_index.py
  rollover_month.py
  update_prices.py
  run_new_month_flow.py
  run_midmonth_flow.py
  run_month_end_flow.py