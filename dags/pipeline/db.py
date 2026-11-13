import json
import os
import sqlite3
from typing import Any, Dict, List, Set


def init_db(db_path: str) -> None:
    dir_name = os.path.dirname(os.path.abspath(db_path))
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                filename TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                keywords TEXT NOT NULL,
                category TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_processed_filenames(db_path: str) -> Set[str]:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT filename FROM papers")
        rows = cur.fetchall()
        return {row[0] for row in rows}
    finally:
        conn.close()


def get_unprocessed_pdfs(papers_dir: str, db_path: str) -> List[str]:
    if not os.path.isdir(papers_dir):
        return []

    processed = get_processed_filenames(db_path)
    unprocessed = []
    for entry in sorted(os.listdir(papers_dir)):
        if entry.lower().endswith(".pdf") and entry not in processed:
            full_path = os.path.join(papers_dir, entry)
            if os.path.isfile(full_path):
                unprocessed.append(entry)
    return unprocessed


def save_paper_to_db(db_path: str, filename: str, metadata: Dict[str, Any]) -> None:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        keywords_json = json.dumps(metadata.get("keywords", []))
        cur.execute(
            """
            INSERT OR REPLACE INTO papers (filename, title, summary, keywords, category, processed_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                filename,
                metadata["title"],
                metadata["summary"],
                keywords_json,
                metadata["category"],
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_papers(db_path: str) -> List[Dict[str, Any]]:
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT filename, title, summary, keywords, category, processed_at
            FROM papers
            ORDER BY processed_at DESC
            """
        )
        rows = cur.fetchall()
        papers = []
        for r in rows:
            try:
                kw = json.loads(r[3]) if r[3] else []
            except Exception:
                kw = [r[3]]
            papers.append(
                {
                    "filename": r[0],
                    "title": r[1],
                    "summary": r[2],
                    "keywords": kw,
                    "category": r[4],
                    "processed_at": r[5],
                }
            )
        return papers
    finally:
        conn.close()
