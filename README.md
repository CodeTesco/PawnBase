# ♟️ FIDE Chess Results Scraper & Database

An automated web scraping pipeline built with Scrapy and PostgreSQL that extracts tournament results, player ratings, and match pairings from [Chess-Results.com](https://chess-results.com).

## 📊 Dataset Overview
* **Tournaments:** ~2,800
* **Players:** ~16,000 (with FIDE IDs, titles, and ratings)
* **Matches:** ~190,000 pairings and outcomes

## 🛠️ Tech Stack
* **Language:** Python
* **Scraper:** Scrapy
* **Database:** PostgreSQL (`psycopg2`)

---

## 🗄️ Database Schema

* **`tournaments`**: `tournament_id` (PK), `tourney_name`, `date`, `base_minutes`, `increment_seconds`, `location`
* **`players`**: `player_id` (PK / FIDE ID), `name`, `title`, `standard_rating`, `blitz_rating`, `rapid_rating`, `gender`
* **`matches`**: `match_id` (PK), `tournament_id`,, `white_id`, `black_id`, `result`, `white_rtg`, `black_rtg`

---

## 🚀 Quickstart

### 1. Install Dependencies
```bash
pip install scrapy psycopg2-binary
```

### 2. Configure Database
Set your PostgreSQL credentials in `pipelines.py` and run your schema creation script:
```bash
psql -U postgres -d chess_data -f schema.sql
```

### 3. Run the Spiders (In Order)
Run the spiders in this sequence to satisfy relational foreign key constraints:
```bash
scrapy crawl tourneySpider
scrapy crawl playerSpider
scrapy crawl matchSpider
```

---

## 📥 Export to CSV
To dump the dataset into CSV files for analysis:
```sql
\copy tournaments TO 'tournaments.csv' DELIMITER ',' CSV HEADER ENCODING 'UTF8';
\copy players TO 'players.csv' DELIMITER ',' CSV HEADER ENCODING 'UTF8';
\copy matches TO 'matches.csv' DELIMITER ',' CSV HEADER ENCODING 'UTF8';
```

---

## 📜 License
* **Code:** MIT
* **Dataset:** [CC0] Public Domain