import sys
import requests
from bs4 import BeautifulSoup
from ddgs import DDGS


def get_page_content(url, max_chars=2000):

    try:
        headers = {
            "User-Agent":"Mozilla/5.0"
        }

        r = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        soup = BeautifulSoup(
            r.text,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "nav",
            "header",
            "footer",
            "aside"
        ]):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        if len(text) < 300:
            return None

        return text[:max_chars]

    except Exception:
        return None


def web_search(query, n=3):

    results = []

    with DDGS() as ddgs:
        hits = ddgs.text(
            query,
            max_results=n
        )

        for hit in hits:

            url = hit["href"]

            #print(f"\nLendo {url}\n")

            content = get_page_content(url)

            if content:
                results.append(
                    {
                        "title": hit["title"],
                        "url": url,
                        "content": content
                    }
                )

    return results


def main():

    if len(sys.argv) < 2:
        print(
            'Uso: python GoogleSearch.py "pesquisa"'
        )
        return

    query = " ".join(
        sys.argv[1:]
    )

    results = web_search(query)

    if not results:
        print("Nada encontrado.")
        return
    merged_content = "\n\n".join(
        r["content"] for r in results
    )

    print(merged_content)


if __name__ == "__main__":
    main()