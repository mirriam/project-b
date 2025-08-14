import os
import requests
from bs4 import BeautifulSoup
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}

def scrape_job_details(job_url):
    try:
        resp = requests.get(job_url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "lxml")
        job_title = soup.select_one("h1").get_text(strip=True) if soup.select_one("h1") else ""
        company_name = soup.select_one("span > a").get_text(strip=True) if soup.select_one("span > a") else ""
        location = soup.select_one("div:nth-child(1) > span:nth-child(2)")
        location = location.get_text(strip=True) if location else ""
        job_type = soup.select_one("section.core-section-container.my-3.description > div > ul > li:nth-child(2) > span")
        job_type = job_type.get_text(strip=True) if job_type else ""
        application_anchor = soup.select_one("#teriary-cta-container > div > a")
        application_url = application_anchor['href'] if application_anchor and application_anchor.has_attr('href') else ""
        return {
            "title": job_title,
            "company": company_name,
            "location": location,
            "type": job_type,
            "apply_link": application_url,
            "source": job_url
        }
    except Exception as e:
        return {"error": f"Error scraping {job_url}: {e}"}

@app.route("/ping")
def ping():
    return "pong"

@app.route("/scrape", methods=["GET"])
def scrape():
    country = request.args.get("country", "United States")
    keywords = request.args.get("keywords", "")
    if not country:
        return jsonify({"error": "Country parameter is required"}), 400

    jobs = []
    try:
        for i in range(0, 2):
            url = f"https://www.linkedin.com/jobs/search?keywords={keywords}&location={country}&start={i * 25}"
            resp = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(resp.text, "lxml")
            job_links = [a["href"] for a in soup.select("#main-content > section > ul > li > div > a") if a.get("href")]
            for link in job_links:
                job_data = scrape_job_details(link)
                jobs.append(job_data)
                time.sleep(1)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(jobs)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
