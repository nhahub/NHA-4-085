from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import time

# ===========================
# Search Keywords
# ===========================
search_terms = [
    "AI",
    "Data",
    "Software",
    "IT"
]

PAGES_TO_SCRAPE = 5
list_jobs = []

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)


def safe_find_text(parent, by, selector, default="N/A"):
    try:
        return parent.find_element(by, selector).text.strip()
    except NoSuchElementException:
        return default


for job_search in search_terms:

    print(f"\n========== Searching: {job_search} ==========\n")

    driver.get("https://wuzzuf.net/jobs/egypt")

    try:
        search_box = wait.until(
            EC.presence_of_element_located((By.NAME, "q"))
        )

        search_box.clear()
        search_box.send_keys(job_search)

        search_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//form//button[@type="submit"]')
            )
        )

        search_btn.click()

    except TimeoutException:
        print("Search failed")
        continue

    for page_num in range(1, PAGES_TO_SCRAPE + 1):

        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "css-pkv5jc")
                )
            )

            time.sleep(2)

        except TimeoutException:
            break

        jobs = driver.find_elements(By.CLASS_NAME, "css-pkv5jc")

        print(
            f"Keyword: {job_search} | Page: {page_num} | Jobs: {len(jobs)}"
        )

        for job in jobs:

            try:

                job_title = safe_find_text(
                    job,
                    By.CSS_SELECTOR,
                    "h2 a, .css-193uk2c"
                )

                company_name = safe_find_text(
                    job,
                    By.CSS_SELECTOR,
                    ".css-ipsyv7 a, .css-ipsyv7"
                )

                location = safe_find_text(
                    job,
                    By.CLASS_NAME,
                    "css-16x61xq"
                )

                try:
                    tags_elements = job.find_elements(
                        By.CSS_SELECTOR,
                        ".css-5jhz9n span, .css-5jhz9n"
                    )

                    tags = ", ".join(
                        [
                            t.text.strip()
                            for t in tags_elements
                            if t.text.strip()
                        ]
                    )

                    if not tags:
                        tags = "N/A"

                except:
                    tags = "N/A"

                experience = safe_find_text(
                    job,
                    By.CSS_SELECTOR,
                    ".css-1rhj4yg span, .css-1rhj4yg div:nth-child(2) span"
                )

                publish_date = safe_find_text(
                    job,
                    By.CLASS_NAME,
                    "css-eg55jf"
                )

                try:
                    job_link = job.find_element(
                        By.CSS_SELECTOR,
                        "h2 a"
                    ).get_attribute("href")

                except:
                    job_link = "N/A"

                list_jobs.append({

                    "search_term": job_search,

                    "job_title": job_title,

                    "company_name": company_name,

                    "location": location,

                    "tags": tags,

                    "experience": experience,

                    "publish_date": publish_date,

                    "job_link": job_link,

                    "page": page_num

                })

            except Exception as e:
                print(e)
                continue
        # ===========================
        # Go To Next Page
        # ===========================
        if page_num < PAGES_TO_SCRAPE:

            try:

                next_button = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            'a[href*="start="]'
                        )
                    )
                )

                next_url = next_button.get_attribute("href")

                print(f"Next Page: {next_url}")

                driver.get(next_url)

                wait.until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "css-pkv5jc")
                    )
                )

                time.sleep(2)

            except Exception:
                print("No next page")
                break


driver.quit()

# ===========================
# Create DataFrame
# ===========================

df = pd.DataFrame(list_jobs)

print(f"\nTotal scraped rows: {len(df)}")

# ===========================
# Remove Duplicate Jobs
# ===========================

if not df.empty:

    df.drop_duplicates(
        subset=["job_link"],
        inplace=True
    )

    print(f"After removing duplicates: {len(df)}")

    df.reset_index(drop=True, inplace=True)

    output_path = r"C:\Users\Public\TechJobs_Wuzzuf.csv"

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(df.head())

    print(f"\nSaved Successfully -> {output_path}")

else:

    print("No jobs found.")