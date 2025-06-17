# 🎓 University Course Scraper

A Python-based scraper to collect **postgraduate course data** — including course names, URLs, eligibility criteria, and tuition fees — from university websites.  
This tool handles both **HTML pages** and **JavaScript-rendered content** using `requests` and `Selenium`.

---

## 🚀 Features

- ✅ Scrapes course names and links  
- 🔍 Extracts eligibility and fee details from each course page  
- 🌐 Supports both static and JS-rendered university websites  
- 📦 Outputs clean JSON data  
- 🧩 Easily extendable for more universities  

---

## 🛠 Project Structure
unit_data/
│
├── scraper.py # Main scraping script
├── chromedriver.exe # Required for JS-rendered sites
├── requirements.txt # Required Python libraries
├── glasgow_courses.json # Scraped course names/links (Glasgow)
├── glasgow_courses_detailed.json # Includes eligibility & fee
├── roehampton_courses.json # Example: Roehampton University
└── README.md 


---

## Installation

```bash
git clone https://github.com/Suhani-09/universityscrapper.git
cd universityscrapper
pip install -r requirements.txt

## Add ChromeDriver
Download the correct version of chromedriver from:
https://chromedriver.chromium.org/downloads

Make sure it’s named chromedriver.exe and placed in the root directory of the project.

## Run

python scraper.py
