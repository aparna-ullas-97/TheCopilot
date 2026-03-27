import httpx
from bs4 import BeautifulSoup

from packages.utils.logger import get_logger

logger = get_logger(__name__)


class UrlExtractor:
    def fetch_and_extract(self, url: str) -> tuple[str, str]:
        logger.info("Fetching URL: %s", url)

        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; RubixAI/1.0)"
        }

        response = httpx.get(url, headers=headers, timeout=20.0, follow_redirects=True)
        response.raise_for_status()

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
            tag.decompose()

        title = None
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        main = soup.find("main")
        article = soup.find("article")

        if article:
            content_root = article
        elif main:
            content_root = main
        else:
            content_root = soup.body or soup

        text = content_root.get_text(separator="\n", strip=True)

        cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n".join(cleaned_lines)

        return (title or url, cleaned_text)