# Assignment 2 — Movie Data Collection & Analysis Pipeline

**Author:** Zhixian Wang  
**Course:** STAT 418 — Tools in Data Science  
**Due:** Before Week 5 class at 6:00 PM

---

## Overview

A four-stage pipeline that collects data on 50 popular movies by combining the TMDB REST API with OMDb API (IMDb ratings), then cleans, merges, and analyses the data to surface trends in ratings, genres, finances, and release timings.

---

## Data Sources

| Source | What we collect | Method |
|--------|----------------|--------|
| [TMDB API](https://developers.themoviedb.org/3) | Title, release date, runtime, genres, budget, revenue, TMDB rating, cast/crew, production companies | REST API |
| [OMDb API](http://www.omdbapi.com/) | IMDb rating, IMDb vote count, Metascore | REST API (fallback from direct IMDb scraping — see Ethical Considerations) |

---

## Setup

### 1. Prerequisites

- Python 3.9+
- [`uv`](https://github.com/astral-sh/uv) (or pip)

### 2. Install dependencies

```bash
uv pip install -r requirements.txt
# or
pip install -r requirements.txt
```

### 3. API keys

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```
TMDB_API_KEY=your_tmdb_api_key_here
TMDB_READ_ACCESS_TOKEN=your_tmdb_read_access_token_here
OMDB_API_KEY=your_omdb_api_key_here
```

- **TMDB key:** free at <https://www.themoviedb.org/settings/api>  
- **OMDb key:** free (1,000 req/day) at <http://www.omdbapi.com/apikey.aspx>

**Never commit your `.env` file.**

---

## How to Run

### Full pipeline (collect → scrape → process → analyse)

```bash
python run_pipeline.py
```

### Skip collection (reuse existing raw data)

```bash
python run_pipeline.py --skip-collect
```

### Run individual stages

```bash
python api_collector.py    # Stage 1: fetch TMDB data
python web_scraper.py      # Stage 2: fetch IMDb/OMDb ratings
python data_processor.py   # Stage 3: merge & clean
python analyze_data.py     # Stage 4: analysis & plots
```

---

## Directory Structure

```
submissions/ZhixianWang/
├── README.md
├── REPORT.md
├── requirements.txt
├── .env.example
├── api_collector.py
├── web_scraper.py
├── data_processor.py
├── analyze_data.py
├── run_pipeline.py
├── data/
│   ├── raw/
│   │   ├── tmdb/movies.json
│   │   └── imdb/ratings.json
│   ├── processed/
│   │   ├── movies.csv        ← submitted sample data
│   │   └── movies.json
│   └── analysis/
│       ├── 1_rating_analysis.png
│       ├── 2_genre_analysis.png
│       ├── 3_financial_analysis.png
│       ├── 4_temporal_analysis.png
│       └── summary.txt
└── logs/
    └── pipeline.log
```

---

## Ethical Considerations

### Rate limiting
- TMDB API: 1 request per 0.25 s (well within the 40 req/10 s limit).
- OMDb API: 1 request per 2 s (well within the 1,000 req/day free tier).

### robots.txt
The scraper checks `https://www.imdb.com/robots.txt` before making any requests. `/title/` paths are permitted for general user-agents.

### IMDb direct scraping
During development, IMDb title pages returned HTTP 202 responses with an AWS WAF JavaScript challenge — a bot-protection mechanism that prevents HTML parsing with `requests` + `BeautifulSoup` alone. Rather than attempt to circumvent this protection, the pipeline uses the OMDb API as a compliant alternative that provides the same fields (IMDb rating, vote count, Metascore) via an official API.

### User-Agent
All requests identify themselves as:  
`UCLA STAT418 Student - zachwang2015@gmail.com`

### Data use
- Data collected for academic and educational purposes only.
- Raw data is not committed to the repository (excluded via `.gitignore`).
- Data is not shared or used commercially.

---

## Known Limitations

- 11/50 movies have no IMDb rating — these are very recent or unreleased titles with few votes on IMDb.
- Budget and revenue are unknown for 21/50 movies (TMDB stores 0 for undisclosed figures).
- The dataset is limited to TMDB's "popular movies" list, which skews toward recent blockbusters.
- OMDb free tier caps at 1,000 requests/day; running the pipeline repeatedly may hit this limit.
