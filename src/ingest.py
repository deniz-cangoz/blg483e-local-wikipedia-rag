import json
import re
from pathlib import Path
from typing import Dict, List
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from config import PEOPLE, PLACES, RAW_DIR


WIKIPEDIA_BASE_URL = "https://en.wikipedia.org/wiki/"


def slugify_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")


def fetch_wikipedia_page(title: str) -> str:
    url = WIKIPEDIA_BASE_URL + quote(title.replace(" ", "_"))

    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "BLG483E-Local-Wikipedia-RAG/1.0"},
    )
    response.raise_for_status()
    return response.text


def extract_clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    content = soup.find("div", {"id": "mw-content-text"})
    if content is None:
        return ""

    for unwanted in content.select(
        "script, style, table, .navbox, .infobox, .metadata, .reference, .reflist"
    ):
        unwanted.decompose()

    paragraphs = content.find_all("p")
    texts: List[str] = []

    for paragraph in paragraphs:
        text = paragraph.get_text(" ", strip=True)
        text = re.sub(r"\[[^\]]*\]", "", text)
        text = re.sub(r"\s+", " ", text).strip()

        if len(text) > 80:
            texts.append(text)

    return "\n\n".join(texts)


def ingest_entity(title: str, entity_type: str) -> Dict[str, str]:
    print(f"[INGEST] Fetching {entity_type}: {title}")

    html = fetch_wikipedia_page(title)
    clean_text = extract_clean_text(html)

    if not clean_text:
        raise ValueError(f"No clean text extracted for {title}")

    record = {
        "title": title,
        "type": entity_type,
        "source": "wikipedia",
        "url": WIKIPEDIA_BASE_URL + quote(title.replace(" ", "_")),
        "text": clean_text,
    }

    output_path = RAW_DIR / f"{entity_type}_{slugify_title(title)}.json"
    output_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[OK] Saved: {output_path}")
    return record


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    all_entities = [(title, "person") for title in PEOPLE]
    all_entities += [(title, "place") for title in PLACES]

    success_count = 0

    for title, entity_type in all_entities:
        try:
            ingest_entity(title, entity_type)
            success_count += 1
        except Exception as exc:
            print(f"[ERROR] Failed {title}: {exc}")

    print(f"\nDone. Successfully ingested {success_count}/{len(all_entities)} entities.")


if __name__ == "__main__":
    main()