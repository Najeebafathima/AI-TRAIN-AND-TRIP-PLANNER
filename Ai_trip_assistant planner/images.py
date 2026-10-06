import requests
import streamlit as st

API = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "AITripAssistant/1.0 (student project)"}
SKIP = ("flag", "map", "locator", "coat_of_arms", "logo", "seal")


def _query(params):
    base = {
        "action": "query", "format": "json", "prop": "pageimages",
        "piprop": "thumbnail", "pithumbsize": 800, "redirects": 1,
    }
    base.update(params)
    r = requests.get(API, params=base, headers=HEADERS, timeout=8)
    pages = r.json().get("query", {}).get("pages", {})
    return list(pages.values())


def _good(url):
    return not any(word in url.lower() for word in SKIP)


@st.cache_data(show_spinner=False)
def get_place_images(place, count=2):
    """Return up to `count` image URLs for any place name."""
    urls = []
    if not place:
        return urls
    try:
        # 1) the place's own Wikipedia page
        for p in _query({"titles": place.title()}):
            t = p.get("thumbnail")
            if t and _good(t["source"]):
                urls.append(t["source"])
        # 2) related tourist pages
        results = _query({
            "generator": "search",
            "gsrsearch": f"{place} tourist attraction",
            "gsrlimit": 8,
        })
        for p in sorted(results, key=lambda p: p.get("index", 99)):
            t = p.get("thumbnail")
            if t and _good(t["source"]) and t["source"] not in urls:
                urls.append(t["source"])
    except Exception:
        pass
    return urls[:count]