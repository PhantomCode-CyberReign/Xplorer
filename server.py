from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

# Site-specific simple scrapers (best-effort). Add or tune selectors as needed.
def scrape_pornhub(query, country="ALL"):
    q = urllib.parse.quote_plus(query)
    url = f"https://www.pornhub.com/video/search?search={q}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        cards = []
        for card in soup.select("div.phimage, div.pcVideoList"):  # try a couple selectors
            a = card.find("a", href=True)
            img = card.find("img")
            title = img.get("alt") if img and img.get("alt") else (a.get("title") if a and a.get("title") else None)
            thumb = img.get("data-thumb_url") or (img.get("src") if img else None)
            link = ("https://www.pornhub.com" + a['href']) if a else None
            if title and link:
                cards.append({"title": title.strip(), "thumb": thumb, "url": link})
            if len(cards) >= 12:
                break
        return cards
    except Exception as e:
        print("pornhub scrape err:", e)
        return []

def scrape_xvideos(query, country="ALL"):
    q = urllib.parse.quote_plus(query)
    url = f"https://www.xvideos.com/?k={q}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        cards = []
        for item in soup.select("div.thumb, div.video-thumb"):
            a = item.find("a", href=True)
            img = item.find("img")
            title = img.get("alt") if img and img.get("alt") else (a.get("title") if a and a.get("title") else None)
            thumb = img.get("data-src") or img.get("src") if img else None
            link = ("https://www.xvideos.com" + a['href']) if a else None
            if title and link:
                cards.append({"title": title.strip(), "thumb": thumb, "url": link})
            if len(cards) >= 12:
                break
        return cards
    except Exception as e:
        print("xvideos scrape err:", e)
        return []

# Add more scrapers for other sites similarly (xhamster, xnxx, redtube)...

SITE_SCRAPERS = {
    "PornHub": scrape_pornhub,
    "XVideos": scrape_xvideos,
    # "XNXX": scrape_xnxx,
    # "RedTube": scrape_redtube,
    # "XHamster": scrape_xhamster
}

@app.route("/")
def index():
    q = request.args.get("q", "")
    country = request.args.get("country", "ALL")
    results = {}
    if q:
        # for each site run scraper (sequential; you can parallelize later)
        for site_name, scraper in SITE_SCRAPERS.items():
            try:
                cards = scraper(q, country)
            except Exception as e:
                print("scraper error for", site_name, e)
                cards = []
            results[site_name] = cards
            time.sleep(0.5)  # polite delay
    return render_template("index.html", query=q, results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
