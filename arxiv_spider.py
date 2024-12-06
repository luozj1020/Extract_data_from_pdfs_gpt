import arxiv
from tqdm import tqdm
import requests
import json
import time


def fetch_papers_paginated(keyword, max_results=10000):
    # Construct the default API client.
    client = arxiv.Client(
        page_size = 100,
        delay_seconds = 0.01,
        num_retries = 3
    )

    search = arxiv.Search(
        query=keyword,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    papers = []
    results = client.results(search)
    for result in results:
        papers.append({
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "abstract": result.summary,
            "pdf_url": result.pdf_url
        })
    return papers


def download_pdf(url, filename, max_retries=5, delay=2):
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url)
            response.raise_for_status()  # This will raise an exception for HTTP errors
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Successfully downloaded {filename}")
            break
        except:
            retries += 1
            print(f"Error downloading {url}. Retrying {retries}/{max_retries}...")
            time.sleep(delay)  # Wait before retrying
    else:
        print(f"Failed to download {url} after {max_retries} attempts.")


papers = fetch_papers_paginated("SrRuO3 PLD growth", max_results=2000)

for paper in tqdm(papers):
    print("Title:", paper["title"])
    print("Abstract:", paper["abstract"])
    print("PDF:", paper["pdf_url"])
    file_name = (paper["title"].replace("|", " ").replace("\"", " ").replace("*", " ").replace(">", " ").replace("<"," ")
                 .replace("\\", " ").replace(".", " ").replace("/", " ").replace(":", " ").replace("?", " ").replace(" ", "_"))
    download_pdf(paper["pdf_url"], "./arxiv_papers/" + str(papers.index(paper)) + "_" + file_name + ".pdf")
    time.sleep(0.1)

with open("output.json", "w") as file:
    json.dump(papers, file, indent=4)
