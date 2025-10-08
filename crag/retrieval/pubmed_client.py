"""
PubMed Retrieval Module for CRAG
- Search PubMed for PMIDs
- Fetch titles, abstracts, journal, year

NCBI requires an email. Set it via environment variables in Colab:
  import os
  os.environ["NCBI_EMAIL"] = "your_email@example.com"
  os.environ["NCBI_API_KEY"] = "your_key_here"
"""

import os
import time
from typing import List
import pandas as pd
from Bio import Entrez
from tqdm import tqdm

Entrez.email = os.getenv("NCBI_EMAIL")
api_key = os.getenv("NCBI_API_KEY", "").strip()
if api_key:
    Entrez.api_key = api_key

def search_pubmed(query: str, retmax: int = 30) -> List[str]:
    """Return a list of PMIDs for the query."""
    with Entrez.esearch(db="pubmed", term=query, retmax=retmax) as handle:
        record = Entrez.read(handle)
    return record.get("IdList", [])

def fetch_details(id_list: List[str]) -> pd.DataFrame:
    """Fetch details (title, abstract, journal, year) for given PMIDs."""
    rows = []
    for pmid in tqdm(id_list, desc="Fetching"):
        with Entrez.efetch(db="pubmed", id=pmid, rettype="abstract", retmode="xml") as h:
            record = Entrez.read(h)
        article = record["PubmedArticle"][0]["MedlineCitation"]["Article"]
        title = article.get("ArticleTitle", "")
        abstract = " ".join(article.get("Abstract", {}).get("AbstractText", []))
        journal = article.get("Journal", {}).get("Title", "")
        year = article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {}).get("Year", "")
        rows.append({"pmid": pmid, "title": title, "abstract": abstract, "journal": journal, "year": year})
        time.sleep(0.2)
    return pd.DataFrame(rows)
