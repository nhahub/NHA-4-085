import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime        

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

all_jobs: list[dict] = []

def parse_date(value, is_unix: bool = False) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    if not value:
        return today
    try:
        if is_unix:
            try:
                return datetime.utcfromtimestamp(int(str(value))).strftime("%Y-%m-%d")
            except (ValueError, OSError):
                pass
        value_str = str(value).strip()
        if len(value_str) >= 10:
            return datetime.strptime(value_str[:10], "%Y-%m-%d").strftime("%Y-%m-%d")
    except Exception:
        pass
    return today


def scrape_remotive() -> None:
    url = "https://remotive.com/api/remote-jobs"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        jobs = response.json().get("jobs", [])
        for job in jobs:
            all_jobs.append({
                "Title":    job.get("title", "N/A"),
                "Company":  job.get("company_name", "N/A"),
                "Location": job.get("candidate_required_location", "Worldwide"),
                "URL":      job.get("url", "N/A"),
                "Date":     parse_date(job.get("publication_date", "")),  
                "Source":   "Remotive",
            })

        print(f" Remotive   → {len(jobs):>5} jobs collected")

    except requests.RequestException as e:
        print(f" Remotive error: {e}")


def scrape_remoteok() -> None:
    url = "https://remoteok.com/api"
    try:
        
        time.sleep(2)
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        count = 0
        for job in response.json():
            if not (isinstance(job, dict) and "position" in job):
                continue  

            job_id   = job.get("id", "")
            raw_date = job.get("date") or job.get("epoch", "")           
            all_jobs.append({
                "Title":    job.get("position", "N/A"),
                "Company":  job.get("company", "N/A"),
                "Location": job.get("location") or "Worldwide",
                "URL":      job.get("url") or f"https://remoteok.com/remote-jobs/{job_id}",
                "Date":     parse_date(raw_date, is_unix=True),            
                "Source":   "RemoteOK",
            })
            count += 1

        print(f"RemoteOK   → {count:>5} jobs collected")

    except requests.RequestException as e:
        print(f" RemoteOK error: {e}")


if __name__ == "__main__":
    print("=" * 45)
    print("  Smart CV Analyzer – Job Data Collection")
    print("=" * 45)

    scrape_remotive()
    scrape_remoteok()

    df = pd.DataFrame(all_jobs, columns=["Title", "Company", "Location", "URL", "Date", "Source"])  # ← إضافة Date

    df.drop_duplicates(subset=["Title", "Company", "URL"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    output_file = "jobs_dataset.csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig") 

    print("=" * 45)
    print(f" Saved → {output_file}")
    print(f"   Total unique jobs : {len(df)}")
    print(f"   Sources breakdown :\n{df['Source'].value_counts().to_string()}")
    print("=" * 45)
    print(df.head(10).to_string(index=False))