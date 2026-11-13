from typing import Any, Dict
import requests


def notify_discord(webhook_url: str, paper_data: Dict[str, Any]) -> bool:
    title = paper_data.get("title", "Untitled Research Paper")
    category = paper_data.get("category", "General")
    summary = paper_data.get("summary", "No summary provided.")
    keywords = ", ".join(paper_data.get("keywords", []))
    filename = paper_data.get("filename", "")

    payload = {
        "content": f"New paper processed: **{title}**",
        "embeds": [
            {
                "title": title,
                "description": summary,
                "fields": [
                    {"name": "Category", "value": category, "inline": True},
                    {"name": "Filename", "value": filename, "inline": True},
                    {"name": "Keywords", "value": keywords or "None", "inline": False},
                ],
            }
        ],
    }

    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        print(f"Notif sent for {title}")
        return True
    except Exception as exc:
        print(f"Error while sending notif: {exc}")
        return False
