# BLS Labor Statistics Scraper — CPI, Jobs, Wages & Unemployment Data

Scrape the **Bureau of Labor Statistics (BLS)** public API to extract time-series economic data including CPI, employment, wages, and unemployment rates. Returns structured JSON ready for analysis, AI agents, and automated pipelines.

## Who This Is For

- **Economists & analysts** tracking macroeconomic trends
- **HR & compensation teams** benchmarking wages and salary bands
- **Financial researchers** building inflation models
- **AI agents (Claude, ChatGPT, MCP)** needing real-time US economic data
- **Data engineers** building economic dashboards and alerts
- **Journalists** covering economic policy and labor markets

## What Data You Get

| Field | Description |
|-------|-------------|
| `seriesId` | BLS series ID (e.g. CUUR0000SA0) |
| `seriesTitle` | Human-readable series name |
| `year` | Year of data point |
| `period` | Period code (M01-M13, Q01-Q05, S01-S02) |
| `periodName` | Month or quarter name |
| `value` | The numeric value |
| `latest` | Whether this is the most recent data point |
| `footnotes` | Any data caveats or notes |
| `scrapedAt` | ISO timestamp of scrape |

## Popular Series IDs

| Series ID | Description |
|-----------|-------------|
| `CUUR0000SA0` | Consumer Price Index (CPI-U) — All Urban |
| `LNS14000000` | Unemployment Rate (seasonally adjusted) |
| `CES0000000001` | Total Nonfarm Payroll Employment |
| `CES0500000003` | Average Hourly Earnings — Private Sector |
| `WPUFD4` | Producer Price Index — Final Demand |
| `LNS12000000` | Employed Civilians |
| `LNS11000000` | Civilian Labor Force Level |

Browse all series at: https://www.bls.gov/data/

## Example Input

```json
{
  "seriesIds": ["CUUR0000SA0", "LNS14000000", "CES0000000001"],
  "startYear": 2020,
  "endYear": 2024,
  "maxResults": 50
}
```

## Example Output

```json
[
  {
    "seriesId": "CUUR0000SA0",
    "seriesTitle": "Consumer Price Index - All Urban Consumers (CPI-U)",
    "year": "2024",
    "period": "M12",
    "periodName": "December",
    "value": "315.605",
    "latest": false,
    "footnotes": null,
    "scrapedAt": "2024-12-01T12:00:00+00:00"
  },
  {
    "seriesId": "LNS14000000",
    "seriesTitle": "Unemployment Rate (Seasonally Adjusted)",
    "year": "2024",
    "period": "M12",
    "periodName": "December",
    "value": "4.1",
    "latest": false,
    "footnotes": null,
    "scrapedAt": "2024-12-01T12:00:00+00:00"
  }
]
```

## AI Agent Queries This Actor Handles

1. "What is the current US inflation rate (CPI)?"
2. "Show me US unemployment rate for the last 5 years"
3. "What are average hourly earnings for US workers?"
4. "Get me BLS nonfarm payroll employment data"
5. "What is the current producer price index?"
6. "Show me monthly CPI data from 2020 to 2024"
7. "What are the latest BLS economic indicators?"
8. "Fetch Bureau of Labor Statistics time series data"
9. "Get US labor market statistics for economic analysis"
10. "What is the US jobs report data for 2024?"

## Works with AI Agents

- ✅ **Claude** via Apify MCP integration
- ✅ **ChatGPT** via Apify plugin / MCP
- ✅ **Any LLM agent** using Apify's Actor API
- ✅ **n8n, Make, Zapier** workflow automations

## Tags

`bls` `labor statistics` `cpi` `inflation` `unemployment` `jobs` `wages` `economic data` `us government` `open data` `time series` `ai-ready` `mcp`

## Notes

- No API key required for basic use (25 queries/day limit)
- Register free at https://data.bls.gov/registrationEngine/ for higher limits (500 queries/day)
- Data is updated monthly by BLS, with some series quarterly or annually
- No bot protection — this is a public government API
