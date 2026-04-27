from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from cortex.bootstrap import create_search_service


_search_service = create_search_service()


def get_page_content(url, max_chars=2000):
    return _search_service.fetch_page_content(url, max_chars=max_chars)


def web_search(query, n=3):
    return [
        {
            "title": result.title,
            "url": result.url,
            "content": result.content,
        }
        for result in _search_service.search(query, limit=n)
    ]


def main():
    if len(sys.argv) < 2:
        print('Uso: python GoogleSearch.py "pesquisa"')
        return

    query = " ".join(sys.argv[1:])
    results = web_search(query)

    if not results:
        print("Nada encontrado.")
        return

    print("\n\n".join(result["content"] for result in results))


if __name__ == "__main__":
    main()
