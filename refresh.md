# How the Bot Office data gets refreshed

The 3D scene draws whatever is in `data.json`. Nothing on the page is invented:
speech bubbles, the departures board, statuses, timelines and routines all come
from that file. Only the walking around is ambient animation.

## Where the data comes from
Each bot's own chat history (its transcript), read with `ReadTranscript` /
`SearchTranscripts` by the Work Place bot. Times are converted to Asia/Baghdad (UTC+3).
**Everything published must be scrubbed**: no PNRs, routes tied to bookings, booking/BMS
refs, passenger names, booking error codes, email addresses, URLs or other personal
details. Write general lines such as "Sent a ticketing-failure alert at 10:58".

## Refresh steps (what a future run does)
1. List Ali's own bots (currently Release Presentation Bot `1065fcb2-...` and
   BMS Ticketing Failed Bot `9e6f2ec7-...`). Skip Work Place and the built-in Grok Bot.
   Any new bot Ali creates gets appended to the `bots` array.
2. For each bot, call `ReadTranscript` with `in=<bot id>` (page back with `before`
   until you reach "This is the start of the transcript" or have enough recent items).
3. From what the bot and Ali actually said, write for that bot:
   - `role`: what the bot is for (from Ali's first request).
   - `activity`: up to ~10 newest items, each `{time (ISO, +03:00), summary (one line)}`.
   - `routines`: from `UpdateRoutine` results in the transcript (name, schedule, state
     enabled/paused). If none are visible, leave `[]` and set `routinesNote`.
   - `lastActive`: time of the latest item. `latest`: the bot's last message to Ali, shortened.
   - `status`: `active` (working on something right now), `idle` (finished its last task),
     or `paused` (Ali paused it / its routines). `statusText`: one short line.
4. Update `generatedAt` and save `data.json`.
5. Run `python3 embed.py` - it copies `data.json` into the inline block in
   `index.html`, so the page also works when opened straight from disk (file://).
6. Check nothing private slipped in, e.g.
   `grep -niE "PNR|@|http|ERR\.|[A-Z]{6}" data.json` and review any hits.
7. Commit and push to the GitHub Pages repo (`gulf-air-bot-office`, branch `main`):
   `git add data.json index.html && git commit -m "Refresh bot activity" && git push`.
   GitHub Pages republishes within a minute or two. The live site re-fetches
   `data.json` every 60 seconds, so open tabs pick up the change without a reload.
   (`screenshot.png` stays local; it is in `.gitignore`.)

## How the page picks up changes
- Opened from a web server (http/https): it re-fetches `data.json` every 60 seconds,
  so replacing `data.json` on the server is enough; new bots get a new gate desk
  (A1, A2, A3 ...) laid out automatically, five per row.
- Opened from disk (file://): it uses the inline copy, so step 5 is needed.

## Adding a bot by hand
Copy one object in `bots`, give it a new `id`, `name`, `short` (2-4 letters for the
monitor), optional `color` (hex), and fill the fields above. Then run `python3 embed.py`.

## Running it locally
    cd bot-office && python3 -m http.server 8765
    # open http://localhost:8765/
