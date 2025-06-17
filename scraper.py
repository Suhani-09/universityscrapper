import os, re, json, time, requests
from bs4 import BeautifulSoup

# ---------- Selenium setup ----------
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# -------------------------------------

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def fetch_static(url: str, timeout=12) -> str | None:
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        if r.ok and "text/html" in r.headers.get("Content-Type", ""):
            print("✅  Fetched with requests")
            return r.text
    except Exception as err:
        print("⚠️  Static fetch error:", err)
    return None


def fetch_dynamic(url: str, wait_selector: str) -> str | None:
    print("🌐  Falling back to Selenium…")
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=opts)

    try:
        driver.get(url)
        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
        )
        html = driver.page_source
        print("✅  Page rendered by Selenium")
        return html
    except Exception as err:
        print("❌  Selenium failed:", err)
        return None
    finally:
        driver.quit()


###############################################################################
# Extract detailed info from each course page
###############################################################################
def get_course_details(course_url: str) -> dict:
    try:
        response = requests.get(course_url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        eligibility = None
        fees = None

        # Try locating eligibility/entry requirement
        entry_section = soup.find("section", id=re.compile("entry|requirement", re.I))
        if entry_section:
            eligibility = entry_section.get_text(" ", strip=True)

        # Try locating fees section
        fees_section = soup.find("section", id=re.compile("fee", re.I))
        if fees_section:
            fees = fees_section.get_text(" ", strip=True)

        return {
            "eligibility": eligibility,
            "fees": fees
        }
    except Exception as e:
        print(f"❌ Failed to fetch details for {course_url}: {e}")
        return {"eligibility": None, "fees": None}


###############################################################################
# Extract course list
###############################################################################
def extract_courses(html: str, base_url: str, link_keyword: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    anchors = soup.select(f'a[href*="{link_keyword}"]')
    print(f"🔍  Found {len(anchors)} raw links")

    seen = set()
    courses = []
    for a in anchors:
        href = a.get("href") or ""
        if href.startswith("/"):
            href = base_url.rstrip("/") + href
        if link_keyword not in href or href in seen:
            continue
        title = re.sub(r"\s+", " ", a.text.strip())
        if not title:
            continue
        seen.add(href)
        details = get_course_details(href)
        courses.append({
            "course_name": title,
            "course_link": href,
            **details
        })
        time.sleep(1)  # be polite

    print(f"✅  Parsed {len(courses)} unique courses")
    return courses


###############################################################################
# Main orchestrator
###############################################################################
def scrape_courses(
    target_url: str,
    base_url: str,
    link_keyword: str,
    output_name: str,
):
    print(f"\n🚀  Scraping: {target_url}")

    html = fetch_static(target_url)
    if not html or link_keyword not in html:
        html = fetch_dynamic(target_url, f'a[href*="{link_keyword}"]')
        if not html:
            print("❌  Could not fetch page at all.")
            return

    courses = extract_courses(html, base_url, link_keyword)
    if not courses:
        print("❌  Selector matched zero courses. Tweaking link_keyword usually fixes this.")
        return

    out_file = os.path.join(DATA_DIR, output_name)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(courses, f, indent=2, ensure_ascii=False)
    print(f"💾  Saved to {out_file}")


###############################################################################
# Run config
###############################################################################
if __name__ == "__main__":
    scrape_courses(
        target_url="https://www.gla.ac.uk/postgraduate/taught/",
        base_url="https://www.gla.ac.uk",
        link_keyword="/postgraduate/taught/",
        output_name="glasgow_courses_detailed.json",
    )
