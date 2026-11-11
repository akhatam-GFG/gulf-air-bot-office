#!/usr/bin/env python3
"""Copy data.json into index.html's inline <script id="bot-data"> block (offline / file:// fallback)."""
import json, re, pathlib
here = pathlib.Path(__file__).resolve().parent
data = json.loads((here / "data.json").read_text())
payload = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")
html = (here / "index.html").read_text()
pat = re.compile(r'(<script id="bot-data" type="application/json">\n).*?(\n</script>)', re.S)
assert pat.search(html), "inline data block not found"
html = pat.sub(lambda m: m.group(1) + payload + m.group(2), html, count=1)
(here / "index.html").write_text(html)
print("embedded", len(data.get("bots", [])), "bots into index.html")
