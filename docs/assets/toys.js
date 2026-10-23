// Touch toys (touchscreens only; the mouse keeps the squid cursor). Off with the accessibility option "stop animations".
// 1 Tap or swipe: soap bubbles (tap a bubble to pop it). 2 Press and hold: juggling a squid, a crab and seaweed out of a fishing net.
// 3 A lifebuoy floats around the back-to-top button; flick it to throw it; when it stops it fades out and reappears on the button.
(function () {
  var root = document.documentElement;
  if (!('ontouchstart' in window) && !(navigator.maxTouchPoints > 0)) return;
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
    if (bubbles.length > 40) return;
    var s = 14 + Math.random() * 30, b = el('toy-bub'), o = { el: b, x: x, y: y, s: s };
    b.style.width = b.style.height = s + 'px'; b.style.margin = (-s / 2) + 'px 0 0 ' + (-s / 2) + 'px';
    bubbles.push(o); at(b, x, y);
    var t = 0, vy = -(0.6 + Math.random() * 0.9), ph = Math.random() * 6, max = 200 + Math.random() * 160;
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
    var net = el('toy-net', NET), cs = THINGS.map(function (s) { return el('toy-thing', s); }), t0 = performance.now(), raf;
    (function step() {
      var t = (performance.now() - t0) / 1100; at(net, anchor.x, anchor.y);
      cs.forEach(function (c, i) {
        var ph = (t + i / 3) % 1, left = Math.floor(t + i / 3) % 2 === 0, hx = left ? -30 : 30;
        var x = anchor.x + hx - 2 * hx * ph, y = anchor.y - 40 - Math.sin(Math.PI * ph) * 170;
        c.style.transform = 'translate(' + x + 'px,' + y + 'px) rotate(' + (ph * 540 * (left ? 1 : -1)) + 'deg)';
      });
      raf = requestAnimationFrame(step);
    })();
    stopJuggle = function () { cancelAnimationFrame(raf); cs.forEach(function (c) { c.remove(); }); net.remove(); stopJuggle = null; };
  }

  // ---------- touch handling (passive: never blocks scrolling or taps) ----------
  var holdT, start = null, last = 0;
  var NOHOLD = 'a,button,input,textarea,select,label,summary,img,video,.toy-buoy,.a11y,.lightbox';
  document.addEventListener('touchstart', function (e) {
    if (off() || e.touches.length > 1) return;
    var p = e.touches[0]; start = { x: p.clientX, y: p.clientY }; anchor = start;
    if (e.target.closest && e.target.closest('.toy-buoy,.a11y,.lightbox')) return;
    if (!hitBubble(p.clientX, p.clientY)) for (var i = 0; i < 3; i++) spawn(p.clientX + (Math.random() - .5) * 20, p.clientY + (Math.random() - .5) * 20);
    clearTimeout(holdT);
    if (!(e.target.closest && e.target.closest(NOHOLD))) holdT = setTimeout(juggle, 450);
  }, { passive: true });
  document.addEventListener('touchmove', function (e) {
    if (off() || !start) return; var p = e.touches[0];
    if (stopJuggle) { anchor = { x: p.clientX, y: p.clientY }; return; }
    if (Math.hypot(p.clientX - start.x, p.clientY - start.y) > 12) clearTimeout(holdT);
    var n = performance.now(); if (n - last < 60) return; last = n; spawn(p.clientX, p.clientY);
  }, { passive: true });
  function end() { start = null; clearTimeout(holdT); if (stopJuggle) stopJuggle(); }
  document.addEventListener('touchend', end, { passive: true });
  document.addEventListener('touchcancel', end, { passive: true });

  // ---------- lifebuoy around the back-to-top button ----------
  var toTop = document.querySelector('.to-top');
  if (!toTop) return;
  var buoy = document.createElement('div');
  buoy.className = 'toy-buoy'; buoy.setAttribute('aria-hidden', 'true');
  buoy.innerHTML = '<svg viewBox="0 0 100 100" width="72" height="72"><circle class="toy-grab" cx="50" cy="50" r="40" fill="none" stroke="transparent" stroke-width="26"/><circle cx="50" cy="50" r="40" fill="none" stroke="#f5ebdd" stroke-width="18"/><g fill="none" stroke="#e8492e" stroke-width="18"><path d="M50 10 A40 40 0 0 1 78.3 21.7"/><path d="M90 50 A40 40 0 0 1 78.3 78.3"/><path d="M50 90 A40 40 0 0 1 21.7 78.3"/><path d="M10 50 A40 40 0 0 1 21.7 21.7"/></g><circle cx="50" cy="50" r="49" fill="none" stroke="#0d2233" stroke-width="2"/><circle cx="50" cy="50" r="31" fill="none" stroke="#0d2233" stroke-width="2"/></svg>';
  document.body.appendChild(buoy);
  var grab = buoy.querySelector('.toy-grab');
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
  grab.addEventListener('pointerdown', function (e) { if (fading) return; drag = true; away = true; still = 0; vx = vy = 0; hist = []; grab.setPointerCapture(e.pointerId); });
  grab.addEventListener('pointermove', function (e) { if (!drag) return; x = e.clientX; y = e.clientY; hist.push({ x: x, y: y, t: performance.now() }); if (hist.length > 6) hist.shift(); });
  grab.addEventListener('pointerup', function () {
    drag = false; if (hist.length > 1) { var a = hist[0], z = hist[hist.length - 1], dt = Math.max(16, z.t - a.t); vx = (z.x - a.x) / dt * 16; vy = (z.y - a.y) / dt * 16; }
  });
  grab.addEventListener('pointercancel', function () { drag = false; });
  requestAnimationFrame(tick);
})();
