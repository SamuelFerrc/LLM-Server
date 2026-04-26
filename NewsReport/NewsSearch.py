import sys
import feedparser
from ExtractKeys import extract_keys

def get_news(query, keywords=None, mode="or"):

    url = f"https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

    feed = feedparser.parse(url)

    results = []

    for item in feed.entries:

        text = (
            item.title + " " +
            getattr(item, "summary", "")
        ).lower()

        if not keywords:
            results.append(item)
            continue

        keywords = [k.lower() for k in keywords]

        if mode == "and":
            if all(k in text for k in keywords):
                results.append(item)

        elif mode == "or":
            if any(k in text for k in keywords):
                results.append(item)
   # print(results[:5])
    return results



def main():

    if len(sys.argv) < 2:
        print('Uso: python3 NewsSearch.py "tema da notícia"')
        return


    # pega tudo após nome do script
    args = " ".join(sys.argv[1:])
    query, keywords = extract_keys(args)
    news = get_news(query, keywords)

    for item in news[:5]:
        print(item.title, ".")
        #print("Data de Publicação:", getattr(item, "published", "sem data"))
        #print("-")


if __name__ == "__main__":
    main()


#news = get_news(
 #   query="irã",
  #  keywords=["irã", "estados unidos", "israel"],
  #  mode="or"
#)

#for item in news[:10]:
 #   print("📰", item.title)
  #  print("🔗", item.link)
   # print("📅", getattr(item, "published", "sem data"))
   # print("-" * 60)