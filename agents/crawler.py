from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

COMMON_TLDS = ['.com', '.ai', '.in', '.org', '.net']
MAX_PAGES_TO_CRAWL = 50

def extract_links(url):
    links = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000)
            anchors = page.query_selector_all("a[href]")
            for a in anchors:
                href = a.get_attribute("href")
                if href:
                    full_url = urljoin(url, href)
                    links.append(full_url)
            browser.close()
    except Exception as e:
        print(f"Playwright error fetching {url}: {e}")
    return links

def filter_links(links, include_paths, exclude_paths):
    def include_filter(link):
        return not include_paths or any(link.startswith(path) for path in include_paths)
    def exclude_filter(link):
        return not any(link.startswith(path) for path in exclude_paths)
    return [link for link in links if include_filter(link) and exclude_filter(link)]

def crawl_site(start_url):
    parsed_start = urlparse(start_url)
    domain = parsed_start.netloc
    to_crawl = {start_url}
    visited = set()
    all_links_found = set()
    while to_crawl and len(visited) < MAX_PAGES_TO_CRAWL:
        current_url = to_crawl.pop()
        if current_url in visited:
            continue
        visited.add(current_url)
        links = extract_links(current_url)
        all_links_found.update(links)
        for link in links:
            parsed_link = urlparse(link)
            if parsed_link.netloc == domain and link not in visited and len(visited) + len(to_crawl) < MAX_PAGES_TO_CRAWL:
                to_crawl.add(link)
    return list(all_links_found), domain

def crawl_and_extract(state):
    url = state["input_url"]
    scan_type = state.get("scan_type", "full_crawl")
    include_paths = state.get("include_paths", [])
    exclude_paths = state.get("exclude_paths", [])
    notes = state.get("notes", "")
    if scan_type == "mock" or url == "test":
        all_links = [
            "https://example.com/page1",
            "https://example.com/page404",
            "https://example.com/page2",
            "https://example.com/page500"
        ]
        domain = "test"
    elif scan_type == "homepage_only":
        all_links = extract_links(url)
        all_links = filter_links(all_links, include_paths, exclude_paths)
        domain = urlparse(url).netloc.split('.')[0]
    else:
        all_links, domain = crawl_site(url)
        all_links = filter_links(all_links, include_paths, exclude_paths)
    return {"input_url": url, "all_links": all_links, "domain": domain}