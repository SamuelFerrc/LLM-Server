from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

from cortex.domain.models import SearchResult


class DDGSWebSearchService:
    def fetch_page_content(self, url: str, max_chars: int = 2000) -> str | None:
        try:
            response = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )

            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
                tag.decompose()

            text = soup.get_text(separator=" ", strip=True)
            if len(text) < 300:
                return None

            return text[:max_chars]

        except Exception:
            return None

    def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        results: list[SearchResult] = []

        with DDGS() as ddgs:
            hits = ddgs.text(query, max_results=limit)

            for hit in hits:
                url = hit["href"]
                content = self.fetch_page_content(url)

                if content:
                    results.append(
                        SearchResult(
                            title=hit["title"],
                            url=url,
                            content=content,
                        )
                    )

        return results

    def search_as_text(self, query: str, limit: int = 3) -> str:
        results = self.search(query, limit=limit)

        if not results:
            return "Nada encontrado."

        return "\n\n".join(result.content for result in results)

