# Doctors

- This scraper is from the first page only of the website (as a sample).
- Date of scraper 2025-02-20

# Usage

1. Clone repository

```bash
git clone https://github.com/MuhammadTarek10/vezeeta-scraper.git
cd vezeeta-scraper
```

2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install requirements

```bash
pip install -r requirements.txt
```

4. Run scraper

```
cd scraper
scrapy crawl doctors -o doctors.csv
```
