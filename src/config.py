from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"

OLLAMA_HOST = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2:3b"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

COLLECTION_NAME = "wiki_rag"
TOP_K = 6

PEOPLE = [
    "Albert Einstein",
    "Marie Curie",
    "Leonardo da Vinci",
    "William Shakespeare",
    "Ada Lovelace",
    "Nikola Tesla",
    "Lionel Messi",
    "Cristiano Ronaldo",
    "Taylor Swift",
    "Frida Kahlo",
    "Isaac Newton",
    "Charles Darwin",
    "Mahatma Gandhi",
    "Nelson Mandela",
    "Pablo Picasso",
    "Vincent van Gogh",
    "Wolfgang Amadeus Mozart",
    "Ludwig van Beethoven",
    "Stephen Hawking",
    "Alan Turing",
]

PLACES = [
    "Eiffel Tower",
    "Great Wall of China",
    "Taj Mahal",
    "Grand Canyon",
    "Machu Picchu",
    "Colosseum",
    "Hagia Sophia",
    "Statue of Liberty",
    "Giza pyramid complex",
    "Mount Everest",
    "Stonehenge",
    "Acropolis of Athens",
    "Petra",
    "Angkor Wat",
    "Mount Fuji",
    "Niagara Falls",
    "Sagrada Familia",
    "Burj Khalifa",
    "Sydney Opera House",
    "Sultan Ahmed Mosque",
]
