# Xelos legacy web app (Mk1.5.1 controllers)

A static page that controls Mk1.5.1 controllers. It doesn't change the firmware. It sends the same `GET` commands the Flutter app sent, to `promethean.local` / `promethean2.local` / `promethean3.local` / `promethean4.local` on port 80.

Files to publish: `index.html`, `xelos-mark.png`, `promethean-logo.png`, `favicon.png`, `apple-touch-icon.png`. No build step and no backend. (`logo.png` from the first version is no longer used.)

## Why it needs to be reachable over both HTTP and HTTPS

The controllers only accept plain `http://` on the home LAN. Browsers handle that differently:

| Browser | Copy that works | Why |
|---|---|---|
| Chrome / Edge 142+ (Android, desktop) | `https://` | Local Network Access lets an HTTPS page call a private IP or `.local` name after the user taps Allow. Chrome blocks this from `http://` pages. |
| Safari / any iPhone browser, Firefox, older Chrome | `http://` | No Local Network Access. An HTTPS page would be blocked as mixed content. |

The page decides on load and redirects itself to the right scheme, so customers only ever get one link. Add `?stay=1` to stop the redirect when testing.

## Hosting (one hostname, both schemes)

Use one name, for example `xelos.prometheanlighting.com`, served on both `http://` and `https://`:

1. Create an S3 bucket and upload the five files.
2. Put a CloudFront distribution in front of it with an ACM certificate for the hostname, and set **Viewer protocol policy = HTTP and HTTPS**. Don't redirect HTTP to HTTPS.
3. Point a DNS CNAME for the hostname at the distribution.
4. On the main site (Shopify, judging by the `/pages/...` URLs), add a page or button that links to `https://xelos.prometheanlighting.com`.

**HSTS check before launch:** run `curl -sI https://prometheanlighting.com | grep -i strict`. If the header includes `includeSubDomains`, browsers will force the subdomain to HTTPS and the iPhone path breaks. If that happens, host the plain copy on a separate domain and set `CONFIG.plainUrl` / `CONFIG.secureUrl` at the top of the script in `index.html`.

## Testing

- **UI flow, no hardware needed:** run `python3 mock_controller.py`, serve this folder with `python3 -m http.server 8080`, then open `http://localhost:8080/?host=127.0.0.1:8099`. Every command the page sends is printed. `BAD` marks a path the firmware doesn't handle.
- **Real hardware:** you need a controller running Mk1.5.1 (the house unit runs v2 now). Flash one of the `Con1`–`Con4` builds to a spare ESP32. Then test from:
  - an Android phone in Chrome (HTTPS copy, expect the Allow prompt), and
  - an iPhone in Safari (HTTP copy, no prompt).
- `?host=192.168.x.x` points controller button 1 at a specific IP.

## Light preview

The roofline and the effect tiles run a JavaScript copy of the Mk1.5.1 effect math (`patternCalls()`): the same palette lookup, the same per-frame `startIndex += motion` and `gHue++`, the same fade amounts and `beatsin16` timing. The firmware draws the effect across all 1,014 bulbs; the preview squeezes it onto 41 bulbs (22 on the tiles), so moving-dot effects cross the roof at the right tempo but look denser. Frame rate is assumed to be about 30 per second, which is what a WS2811 string that long allows. Galaxy, Bounce and Random use the firmware's rainbow hues and ignore the selected colors, same as on the house.

## Behavior notes (from the Mk1.5.1 source)

- **Connection check:** the page uses `/time` to check the connection. Never request `/` or unknown paths. The firmware's `handle_NotFound` calls `loop()` again and `server.begin(80)`.
- **Command queue:** commands are sent one at a time because the firmware's single-threaded `WebServer` chokes on bursts. Sliders send at most every ~350 ms and once more on release.
- **Timer:** the firmware clock is `MST7MDT,M4.1.0,M10.5.0`, which uses the pre-2007 US daylight-saving dates. The page converts the phone's local time to that clock. The controller is an hour off from real time between the second Sunday in March and the first Sunday in April, and the page compensates for that too. Timer settings live in controller RAM, so a power loss clears them. That's the firmware's behavior.
- **Fixes over the old app:**
  - **Fresh Start:** the old app sent `FrestStart` (a typo), so that button never worked. The page now sends `FreshStart`.
  - **Brightness:** the old app sent values like `128.0`. The page sends integers.
  - **Renamed palettes:** Tiffany's → Robin's Egg, Lucky Charms → Rainbow Clover, Moster Mash → Monster Mash. Only the displayed names changed. The page sends the same firmware codes.
- **Left out on purpose:**
  - Music mode.
  - Firmware update (it pointed at the old S3 `.bin`).
  - Zones and individual-bulb addressing. The old app didn't expose them either.
