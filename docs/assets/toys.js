// Toys for touch and mouse (pointer events, so they work in every browser). Off with the accessibility option "stop animations".
// 1 Tap/click or swipe/drag: soap bubbles (tap a bubble to pop it). 2 Press and hold: juggling a squid, a crab and seaweed out of a fishing net.
// Keep holding (1.6 s): fluid-dragon.js takes over (fire dragon, then the water game); on 'fluiddragon:brew' the net flies up and the creatures scatter.
// 3 A lifebuoy floats around the back-to-top button; flick it to throw it; when it stops it fades out and reappears on the button.
(function () {
  var root = document.documentElement;
  function off() { return root.classList.contains('a11y-motion'); }
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  var layer = document.createElement('div');
  layer.className = 'toys'; layer.setAttribute('aria-hidden', 'true');
  document.body.appendChild(layer);
  function el(cls, html) { var d = document.createElement('div'); d.className = cls; if (html) d.innerHTML = html; layer.appendChild(d); return d; }
  function at(d, x, y) { d.style.transform = 'translate(' + x + 'px,' + y + 'px)'; }

  // ---------- bubbles ----------
  var bubbles = [];
  function spawn(x, y) {
    if (bubbles.length > 40 || root.classList.contains('fluid-game')) return;
    var s = 14 + Math.random() * 30, b = el('toy-bub'), o = { el: b, x: x, y: y, s: s };
    b.style.width = b.style.height = s + 'px'; b.style.margin = (-s / 2) + 'px 0 0 ' + (-s / 2) + 'px';
    bubbles.push(o); at(b, x, y);
    var t = 0, vy = -(0.6 + Math.random() * 0.9), ph = Math.random() * 6, max = 60 + Math.random() * 50;
    (function step() {
      if (!b.isConnected) return; t++; o.y += vy; o.x += Math.sin(t / 18 + ph) * 0.6; at(b, o.x, o.y);
      if (o.y < -40) kill(o, false); else if (t > max) kill(o, true); else requestAnimationFrame(step);
    })();
  }
  function kill(o, pop) {
    var i = bubbles.indexOf(o); if (i > -1) bubbles.splice(i, 1);
    if (pop) { var p = el('toy-pop'); p.style.width = p.style.height = o.s + 'px'; p.style.margin = (-o.s / 2) + 'px 0 0 ' + (-o.s / 2) + 'px'; at(p, o.x, o.y); setTimeout(function () { p.remove(); }, 300); }
    o.el.remove();
  }
  function hitBubble(x, y) {
    for (var i = bubbles.length - 1; i >= 0; i--) { var o = bubbles[i]; if (Math.hypot(o.x - x, o.y - y) < o.s / 2 + 10) { kill(o, true); return true; } }
    return false;
  }

  // ---------- juggling ----------
  var THINGS = [
    '<svg viewBox="0 0 60 40" width="42" height="42"><path d="M44 20 L52 7 L59 20 L52 33 Z" fill="#d9a3de" stroke="#3b1940" stroke-width="1.1"/><path d="M27 11 Q46 9 58 20 Q46 31 27 29 Z" fill="#8f4a96" stroke="#3b1940" stroke-width="1.3"/><circle cx="40" cy="15" r="1.6" fill="#f5b83d"/><circle cx="47" cy="22" r="1.3" fill="#f5b83d"/><ellipse cx="24" cy="20" rx="9" ry="10" fill="#b56fbd" stroke="#3b1940" stroke-width="1.3"/><g fill="none" stroke="#b56fbd" stroke-width="2.6" stroke-linecap="round"><path d="M17 15 Q10 11 4 14"/><path d="M16 18 Q9 17 2 19"/><path d="M16 22 Q9 23 2 22"/><path d="M17 25 Q10 29 4 27"/></g><circle cx="21" cy="17" r="4.2" fill="#fff" stroke="#3b1940" stroke-width=".9"/><circle cx="19" cy="17" r="2.1" fill="#0d2233"/></svg>',
    '<svg viewBox="0 0 60 50" width="42" height="42"><g stroke="#7a1d10" stroke-width="2.4" stroke-linecap="round" fill="none"><path d="M18 30 L8 36 L4 44"/><path d="M20 34 L12 42 L10 48"/><path d="M42 30 L52 36 L56 44"/><path d="M40 34 L48 42 L50 48"/><path d="M20 24 L10 16"/><path d="M40 24 L50 16"/><path d="M26 18 L24 9"/><path d="M34 18 L36 9"/></g><path d="M4 14 Q2 4 10 3 Q16 4 13 10 L9 9 Q10 14 4 14Z" fill="#e8492e" stroke="#7a1d10" stroke-width="1.4"/><path d="M56 14 Q58 4 50 3 Q44 4 47 10 L51 9 Q50 14 56 14Z" fill="#e8492e" stroke="#7a1d10" stroke-width="1.4"/><ellipse cx="30" cy="27" rx="15" ry="10" fill="#e8492e" stroke="#7a1d10" stroke-width="1.6"/><circle cx="24" cy="8" r="3.4" fill="#fff" stroke="#7a1d10" stroke-width="1"/><circle cx="36" cy="8" r="3.4" fill="#fff" stroke="#7a1d10" stroke-width="1"/><circle cx="24" cy="8.6" r="1.6" fill="#0d2233"/><circle cx="36" cy="8.6" r="1.6" fill="#0d2233"/><path d="M25 30 Q30 33 35 30" fill="none" stroke="#7a1d10" stroke-width="1.4" stroke-linecap="round"/></svg>',
    '<svg viewBox="0 0 40 60" width="42" height="42"><g stroke="#1f5e2e" stroke-width="1.3" stroke-linejoin="round"><path d="M20 58 C14 48 26 40 18 30 C12 22 22 14 17 3 C25 12 18 22 24 30 C31 40 20 48 24 58Z" fill="#3fae5a"/><path d="M14 58 C8 50 14 44 8 36 C5 31 8 25 5 20 C11 26 9 32 13 37 C18 44 12 50 18 58Z" fill="#6fd38a"/><path d="M26 58 C31 51 27 45 32 39 C35 35 33 29 36 25 C38 31 38 36 35 41 C31 47 34 52 30 58Z" fill="#2f8f47"/></g><circle cx="21" cy="20" r="1.6" fill="#b9f0c6"/><circle cx="11" cy="40" r="1.3" fill="#b9f0c6"/></svg>'
  ];
  var NET = '<svg viewBox="0 0 96 56" width="96" height="56"><defs><pattern id="toy-mesh" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path d="M0 0H9M0 0V9" stroke="#2f8fe0" stroke-width="1.6" fill="none"/></pattern><clipPath id="toy-bag"><path d="M6 14 Q48 70 90 14 Z"/></clipPath></defs><path d="M6 14 Q48 70 90 14 Z" fill="rgba(47,143,224,.18)"/><rect width="96" height="56" fill="url(#toy-mesh)" clip-path="url(#toy-bag)"/><path d="M6 14 Q48 70 90 14" fill="none" stroke="#2f8fe0" stroke-width="1.6"/><ellipse cx="48" cy="14" rx="42" ry="9" fill="none" stroke="#1a5fb0" stroke-width="4"/><ellipse cx="48" cy="14" rx="42" ry="9" fill="none" stroke="#6fb6f2" stroke-width="1.4"/></svg>';
  var anchor = { x: 0, y: 0 }, stopJuggle = null;
  function juggle() {
    var net = el('toy-net', NET), cs = THINGS.map(function (s) { return el('toy-thing', s); }), t0 = performance.now(), raf, tPrev = t0;
    var pos = cs.map(function () { return { x: anchor.x, y: anchor.y, r: 0, vx: 0, vy: 0 }; });   // kept for the scatter
    (function step() {
      var now = performance.now(), dt = Math.max(0.008, (now - tPrev) / 1000), t = (now - t0) / 1100; tPrev = now; at(net, anchor.x, anchor.y);
      cs.forEach(function (c, i) {
        var ph = (t + i / 3) % 1, left = Math.floor(t + i / 3) % 2 === 0, hx = left ? -30 : 30;
        var x = anchor.x + hx - 2 * hx * ph, y = anchor.y - 40 - Math.sin(Math.PI * ph) * 170;
        var r = ph * 540 * (left ? 1 : -1), P = pos[i];
        P.vx = (x - P.x) / dt; P.vy = (y - P.y) / dt; P.x = x; P.y = y; P.r = r;
        c.style.transform = 'translate(' + x + 'px,' + y + 'px) rotate(' + r + 'deg)';
      });
      raf = requestAnimationFrame(step);
    })();
    holding = false; lock(true); clearSel();
    stopJuggle = function () { cancelAnimationFrame(raf); cs.forEach(function (c) { c.remove(); }); net.remove(); stopJuggle = null; scatterJuggle = null; lock(false); };
    scatterJuggle = function (cx, cy) { cancelAnimationFrame(raf); stopJuggle = null; scatterJuggle = null; lock(false); scatter(net, cs, pos, cx, cy); };
  }

  // The dragon hatches (fluid-dragon.js, 'fluiddragon:brew'): the net is yanked up out of the screen and the three creatures
  // burst out in three directions, drifting on curving currents (drag + a slowly turning swirl), tumbling, and fading.
  // While they fly they stir the dragon's fluid (window.fluidDragonStir): the crab leaves fire, squid and seaweed water.
  var scatterJuggle = null;
  function rnd(a, b) { return a + Math.random() * (b - a); }
  function scatter(net, cs, pos, cx, cy) {
    var t0 = performance.now(), last = t0, turn = Math.random() * 6.28, stir = window.fluidDragonStir || function () {};
    var N = { x: cx, y: cy, vx: rnd(-80, 80), vy: -320, r: 0, vr: rnd(-90, 90) };
    var ps = cs.map(function (c, i) {
      var P = pos[i], a = turn + i * 2.094 + rnd(-0.35, 0.35), sp = rnd(600, 850);       // three directions, 120° apart
      return { el: c, x: P.x, y: P.y, vx: P.vx * 0.35 + Math.cos(a) * sp, vy: P.vy * 0.35 + Math.sin(a) * sp, r: P.r,
               vr: rnd(300, 720) * (Math.random() < 0.5 ? -1 : 1), sw: rnd(1.8, 3.4), ph: Math.random() * 6.28, kind: i === 1 ? 'fire' : 'water' };
    });
    stir(cx, cy, 0, -600, 'water', 1.2);                                                // the net leaves a gulp of water
    (function step() {
      var now = performance.now(), dt = Math.min(0.05, (now - last) / 1000), t = (now - t0) / 1000; last = now;
      // net: accelerates upwards, sways, turns a little, grows and fades
      N.vy -= 1500 * dt; N.vx += Math.sin(t * 9) * 600 * dt; N.x += N.vx * dt; N.y += N.vy * dt; N.r += N.vr * dt;
      net.style.transform = 'translate(' + N.x + 'px,' + N.y + 'px) rotate(' + N.r + 'deg) scale(' + (1 + t * 0.5) + ')';
      net.style.opacity = Math.max(0, Math.min(1, (1.2 - t) / 0.6));
      if (t < 0.6) stir(N.x, N.y + 20, N.vx * 0.3, -N.vy * 0.25, 'water', 0.25);
      ps.forEach(function (p) {
        var drag = Math.exp(-1.0 * dt), w = Math.sin(t * p.sw + p.ph) * 2.4 * dt, c = Math.cos(w), s2 = Math.sin(w);
        var vx = (p.vx * c - p.vy * s2) * drag, vy = (p.vx * s2 + p.vy * c) * drag - 45 * dt;   // curving current, slight lift
        p.vx = vx; p.vy = vy; p.x += vx * dt; p.y += vy * dt; p.r += p.vr * dt; p.vr *= Math.exp(-0.7 * dt);
        p.el.style.transform = 'translate(' + p.x + 'px,' + p.y + 'px) rotate(' + p.r + 'deg) scale(' + (1 + t * 0.35) + ')';
        p.el.style.opacity = Math.max(0, Math.min(1, (2.3 - t) / 0.9));
        if (t < 1.8) stir(p.x, p.y, vx * 0.5, vy * 0.5, p.kind, p.kind === 'fire' ? 0.18 : 0.6);
      });
      if (t < 2.3) requestAnimationFrame(step);
      else { cs.forEach(function (c) { c.remove(); }); net.remove(); }
    })();
  }

  // ---------- input: pointer events (mouse, pen, touch); touchmove adds bubbles while a finger scrolls ----------
  var holdT, holding = false, start = null, last = 0, kind = '';
  // While a hold is pending (touch/pen) or juggling: no text selection, no copy/callout menu, so the browser's own long press can't cancel the juggling.
  // A mouse keeps normal drag-to-select until the juggling actually starts.
  function lock(on) { root.classList.toggle('toy-hold', on); }
  function clearSel() { var s = window.getSelection && getSelection(); if (s && s.removeAllRanges) s.removeAllRanges(); }
  function cancelHold() { clearTimeout(holdT); if (holding) { holding = false; if (!stopJuggle) lock(false); } }
  function blocking() { return !!stopJuggle || (holding && kind !== 'mouse'); }
  document.addEventListener('selectstart', function (e) { if (blocking()) e.preventDefault(); });
  document.addEventListener('contextmenu', function (e) { if (blocking()) e.preventDefault(); });
  var NOHOLD = 'a,button,input,textarea,select,label,summary,img,video,.toy-buoy,.a11y,.lightbox';
  function trail(x, y) { var n = performance.now(); if (n - last < 150) return; last = n; spawn(x, y); }
  document.addEventListener('pointerdown', function (e) {
    if (off() || !e.isPrimary || (e.pointerType === 'mouse' && e.button !== 0)) return;
    if (e.target.closest && e.target.closest('.toy-buoy,.a11y,.lightbox')) return;
    kind = e.pointerType; start = { x: e.clientX, y: e.clientY }; anchor = start;
    if (!hitBubble(e.clientX, e.clientY)) spawn(e.clientX, e.clientY);
    cancelHold();
    if (!(e.target.closest && e.target.closest(NOHOLD))) { holding = true; if (kind !== 'mouse') lock(true); holdT = setTimeout(juggle, 450); }
  });
  document.addEventListener('pointermove', function (e) {
    if (off() || !start || !e.isPrimary) return;
    if (stopJuggle) { anchor = { x: e.clientX, y: e.clientY }; return; }
    if (Math.hypot(e.clientX - start.x, e.clientY - start.y) > 12) cancelHold();
    if (Math.hypot(e.clientX - start.x, e.clientY - start.y) > 6) trail(e.clientX, e.clientY);
  });
  document.addEventListener('touchmove', function (e) {
    if (off() || !start || stopJuggle) return; var p = e.touches[0];
    if (Math.hypot(p.clientX - start.x, p.clientY - start.y) > 12) cancelHold();   // a trembling finger still counts as holding
    trail(p.clientX, p.clientY);
  }, { passive: true });
  function end() { start = null; cancelHold(); if (stopJuggle) stopJuggle(); }
  document.addEventListener('fluiddragon:brew', function (e) {
    var d = e.detail || anchor;
    if (scatterJuggle) scatterJuggle(d.x, d.y); else if (stopJuggle) stopJuggle();
  });
  document.addEventListener('pointerup', end);
  document.addEventListener('pointercancel', function () { cancelHold(); if (stopJuggle) stopJuggle(); if (kind !== 'touch') start = null; });  // a finger that starts scrolling keeps its bubble trail
  document.addEventListener('touchend', end, { passive: true });
  document.addEventListener('touchcancel', end, { passive: true });

  // ---------- lifebuoy around the back-to-top button ----------
  var toTop = document.querySelector('.to-top');
  if (!toTop) return;
  var buoy = document.createElement('div');
  buoy.className = 'toy-buoy'; buoy.setAttribute('aria-hidden', 'true');
  buoy.innerHTML = '<svg viewBox="0 0 100 100" width="72" height="72"><circle class="toy-grab" cx="50" cy="50" r="40" fill="none" stroke="transparent" stroke-width="26"/><circle cx="50" cy="50" r="40" fill="none" stroke="#f5ebdd" stroke-width="18"/><g fill="none" stroke="#e8492e" stroke-width="18"><path d="M50 10 A40 40 0 0 1 78.3 21.7"/><path d="M90 50 A40 40 0 0 1 78.3 78.3"/><path d="M50 90 A40 40 0 0 1 21.7 78.3"/><path d="M10 50 A40 40 0 0 1 21.7 21.7"/></g><circle cx="50" cy="50" r="49" fill="none" stroke="#0d2233" stroke-width="2"/><circle cx="50" cy="50" r="31" fill="none" stroke="#0d2233" stroke-width="2"/></svg>';
  document.body.appendChild(buoy);
    var x = 0, y = 0, vx = 0, vy = 0, rot = 0, drag = false, hist = [], still = 0, away = false, fading = false;
  function home() { var r = toTop.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; }
  function tick(now) {
    var show = !off() && !toTop.hidden;
    buoy.classList.toggle('toy-hide', !show);
    if (show) {
      var h = home(), W = innerWidth, H = innerHeight;
      if (!drag) {
        x += vx; y += vy; rot += vx * 1.1; vx *= .975; vy *= .975;
        if (x < 36) { x = 36; vx = -vx * .6 } if (x > W - 36) { x = W - 36; vx = -vx * .6 }
        if (y < 36) { y = 36; vy = -vy * .6 } if (y > H - 36) { y = H - 36; vy = -vy * .6 }
        if (!away) { x = h.x; y = h.y; }
        else {
          if (Math.hypot(vx, vy) < .5) still++; else still = 0;
          if (still > 25 && !fading) {
            fading = true; buoy.classList.add('toy-gone');
            setTimeout(function () { vx = vy = 0; rot = 0; away = false; fading = false; buoy.classList.remove('toy-gone'); }, 500);
          }
        }
      }
      var bob = reduce || drag ? 0 : Math.sin(now / 650) * 2;
      buoy.style.transform = 'translate(' + x + 'px,' + (y + bob) + 'px) rotate(' + (rot + (reduce || drag ? 0 : Math.sin(now / 900) * 4)) + 'deg)';
    }
    requestAnimationFrame(tick);
  }
  // touch events on a large invisible pad (easier to catch than the thin ring); a tap without moving still opens "back to top"
  var pad = document.createElement('div'); pad.className = 'toy-pad'; buoy.appendChild(pad);
  var t0, sx, sy;
  pad.addEventListener('pointerdown', function (e) {
    if (fading || off() || !e.isPrimary) return; e.preventDefault(); e.stopPropagation();
    try { pad.setPointerCapture(e.pointerId); } catch (err) {}
    drag = true; still = 0; vx = vy = 0; t0 = performance.now(); sx = e.clientX; sy = e.clientY;
    hist = [{ x: e.clientX, y: e.clientY, t: t0 }];
  });
  pad.addEventListener('pointermove', function (e) {
    if (!drag) return;
    if (!away && Math.hypot(e.clientX - sx, e.clientY - sy) > 6) away = true;
    if (away) { x = e.clientX; y = e.clientY; }
    hist.push({ x: e.clientX, y: e.clientY, t: performance.now() }); if (hist.length > 12) hist.shift();
  });
  function letGo(e) {
    if (!drag) return; drag = false;
    if (!away) { if (e && e.type === 'pointerup') toTop.click(); return; }   // a tap or click = the up button
    var now = performance.now(), z = hist[hist.length - 1], a = z;
    for (var i = hist.length - 1; i >= 0 && now - hist[i].t < 120; i--) a = hist[i];   // speed of the last 120 ms
    var dt = Math.max(16, z.t - a.t);
    vx = (z.x - a.x) / dt * 16 * 1.4; vy = (z.y - a.y) / dt * 16 * 1.4;
    var sp = Math.hypot(vx, vy), max = 45; if (sp > max) { vx *= max / sp; vy *= max / sp; }
  }
  pad.addEventListener('pointerup', letGo); pad.addEventListener('pointercancel', letGo);
  requestAnimationFrame(tick);
})();
