# Handoff: fire dragon in the water (hidden toy for vendaval.cat)

Branch `fire-dragon` of `ciaVENDAVAL/vendaval-web`, made 22 Nov 2026 in the Las Marikarmen session.
**Nothing is live yet.** The toy works and was tested, but it isn't wired into the site. This branch only adds two files:

- `src/fluid-dragon.js`: the toy, one self-contained file with no libraries.
- `HANDOFF-fire-dragon.md`: this note. Delete it when you merge.

## What it is

It's a variant of the long-press "Fuego" toy now live on lasmarikarmen.com (`lasmarikarmen-web/assets/js/fluid.js`).
The user liked that one and asked for this version on VENDAVAL:

- The swirls are shaped into a fire dragon, not random fire. The body is a chain of 26 points pulled by the head, with a
  head that glows white-hot, eyes, a fiery body that ripples like a snake, a thin red tail, two flapping wings at the
  shoulders, and fire breath now and then.
- In the game, the black background is replaced by deep water: a blue-green gradient with moving light patterns
  (caustics) that ripple as the fluid moves.
- The swirls around the dragon are a random mix of fire and water. In the fluid, fire is stored in the colour
  channels and water in its own channel, so they never mix into grey.
  If the water look doesn't convince, the user said gel is OK. To try that, change the colours in the `display`
  shader (`ws` block: e.g. a pink or green translucent gel).

How it behaves:
1. Long-press. A small fire dragon hatches and circles the finger, growing for 3 s.
2. Flick while holding: the dragon flies off that way, weaving and breathing fire, and dissolves. If you just let go,
   it flies off the way it was heading.
3. Keep holding 3 s more: the page fades into water, the dragon swims around and follows your finger (it wanders when
   no one is touching), and each stroke leaves a swirl of either fire or water (random per stroke).
   After 2 s without touching (or Esc), everything dissolves back into the same page at the same scroll position.

It's off when the system has reduced motion, when the accessibility option "stop animations" is on (`html.a11y-motion`),
and in `#edit`. It doesn't start on inputs, iframes, video, `.toy-buoy`, `.a11y`, `.lightbox`, or anything with `.fluid-off`.
If WebGL isn't available it does nothing. The page never scrolls while you're holding or playing, and the click or
context menu that a long press would cause is swallowed.

## The one decision to make: long-press is already taken

`src/toys.js` already uses press-and-hold (450 ms) for the juggling net (squid, crab, seaweed), which stops on release.
Both toys can't start at 450 ms. Options:

1. **Recommended: chain them.** Juggling stays at 0.45 s; the dragon starts at about 1.6 s of holding.
   Set this before loading the script: `window.FLUID_DRAGON = { holdMs: 1600 }`. In `toys.js`, stop the juggling when the
   dragon hatches: `document.addEventListener('fluiddragon:brew', function () { if (stopJuggle) stopJuggle(); });`
   (inside the IIFE, after `stopJuggle` is defined). Then the net drops into the water and the dragon is born.
2. The dragon replaces the juggling (remove `juggle` from `toys.js`).
3. The dragon only on some pages, e.g. the "Imaginary friend" show page.

Ask the user which one. Option 1 keeps everything that exists already.

Also check:
- **Bubbles:** `toys.js` spawns bubbles on every tap and drag. In the game, the canvas sits on top (z-index 9999,
  `.toys` is 60), so bubbles are hidden but still created. You can skip them while `html.fluid-game` is set.
- **Lifebuoy:** excluded (`.toy-buoy`), so flicking the lifebuoy still works.
- **Squid cursor** (`html.squid-on`, z-index max) stays above the game. That's fine, or hide it during `html.fluid-game`.

## How to wire it in

1. `build.py`, `build_static()`: add `'fluid-dragon.js'` to `for f in ('style.css', 'site.js', 'crew.js', 'toys.js')`.
2. `src/page.html`, after the `toys.js` line (about line 419):
   `<script>window.FLUID_DRAGON={holdMs:1600}</script>` (if chaining)
   `<script src="{{ R }}assets/fluid-dragon.js?v={{ version }}" defer></script>`
3. Add the `fluiddragon:brew` listener to `toys.js` (see above).
4. Document it in `UPDATING.md` / `README.md` next to the other toys.
5. `python3 build.py && python3 tools/check.py`, commit as tyle fernández <VENDAVAL@anartist.org> with `[no-translate]`
   (there are no texts), `git pull --rebase`, and push to `main`.

## Settings and tuning (all in `src/fluid-dragon.js`)

- Timings: `window.FLUID_DRAGON = { holdMs, gameMs, idleMs }` (defaults 450 / 3000 / 2000 ms).
- Events on `document`: `fluiddragon:brew`, `fluiddragon:game`, `fluiddragon:end`.
- Dragon shape: `Dragon.prototype.draw`. Body width curve `w`, colours `fire(hue, k)` (hue 0 = red … 60 = yellow),
  wings (`flap`, 4 points per wing), breath (`nextBreath`), wake (fire vs water, 50/50).
- How long trails last: `DIS.fire` / `DIS.water` per mode (higher = shorter trails, sharper dragon).
- Water look: `display` shader (`deep`, `water`, caustic strength `.55`).
- Performance: the dragon's ~30 blobs are drawn in one GPU pass (`multi` shader). Phones use a 640 px fluid
  (`resize()`). Lower it to 512 if an older phone stutters.

## Tested

Headless Chrome, phone size (390×800, touch), on `/ca/`: hatch and coil, flick and throw, letting go, entering the
game, following the finger, dissolving back after 2 s, and returning to the same scroll position. No console errors.
That browser has no graphics card (very low frame rate), so **check the real look and speed on a phone**. At 60 fps
the dragon is smoother and longer than in the test screenshots.

Credits (in the file header): fluid solver after Pavel Dobryakov's WebGL Fluid Simulation (MIT);
water light after the classic "water turbulence" caustics shader.
