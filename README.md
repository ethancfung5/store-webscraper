# Forest City One Piece Sealed Monitor

This is a small Python script that monitors the **Forest City Collectibles – One Piece Sealed** collection page and sends a **Discord notification** whenever items are **added** or **removed**.

It is intended for **personal use only** and is configured to scrape politely (low frequency, simple HTML parsing).

---

## What It Does

- Periodically fetches the collection page:
  - `https://forestcitycollectibles.com/collections/one-piece-sealed-1`
- Extracts all product titles and links using a CSS selector.
- Compares the current product list with a locally stored JSON **snapshot**.
- Detects:
  - **New items added**
  - **Existing items removed**
- Sends a **Discord message** (via webhook) summarizing the changes.
- Updates the snapshot so the same changes do not trigger repeated alerts.

---

## Requirements

- Python 3.8+
- Dependencies:
  - `requests`
  - `beautifulsoup4`

Install them with:

```bash
pip install requests beautifulsoup4
