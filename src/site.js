// VENDAVAL — small helpers, no tracking
(function () {
  // mobile menu
  var btn = document.querySelector('.menu-btn'), nav = document.getElementById('nav');
  if (btn) {
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open);
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('#nav > ul a')) { nav.classList.remove('open'); btn.setAttribute('aria-expanded', false); }
    });
  }

  // hero carousel: one photo per show, changes every 6 s (stops for reduced motion)
  var root = document.documentElement;
  var slides = document.querySelectorAll('.slide'), dots = document.querySelectorAll('.dots button'), cur = 0, timer;
  function show(n) {
    slides[cur].classList.remove('on'); slides[cur].setAttribute('aria-hidden', 'true'); if (dots[cur]) dots[cur].removeAttribute('aria-current');
    cur = (n + slides.length) % slides.length;
    slides[cur].classList.add('on'); slides[cur].removeAttribute('aria-hidden'); if (dots[cur]) dots[cur].setAttribute('aria-current', 'true');
    var im = slides[cur].querySelector('img'); if (im) im.loading = 'eager';
    var sl = document.querySelector('.slide-link'), d = dots[cur];
    if (sl && d) { sl.href = d.dataset.href; sl.querySelector('span').textContent = d.dataset.name; }
  }
  if (slides.length > 1) {
    dots.forEach(function (d, i) { d.addEventListener('click', function () { clearInterval(timer); show(i); }); });
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) timer = setInterval(function () { if (!root.classList.contains('a11y-motion')) show(cur + 1); }, 6000);
  }

  // open menus (language, other languages…) close when clicking anywhere else, opening another one, or pressing Esc
  function closeMenus(except) {
    document.querySelectorAll('details[open]').forEach(function (d) { if (d !== except && !d.contains(except)) d.removeAttribute('open'); });
  }
  document.addEventListener('click', function (e) { closeMenus(e.target.closest('details a') ? null : e.target.closest('details')); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var d = document.activeElement && document.activeElement.closest('details[open]');
    closeMenus(null); if (d) { var s = d.querySelector('summary'); if (s) s.focus(); }
  });

  // "back to top" links: scroll the page itself (the header is sticky, so jumping to it does nothing)
  document.querySelectorAll('a[href="#top"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var smooth = !root.classList.contains('a11y-motion') && !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      window.scrollTo({ top: 0, behavior: smooth ? 'smooth' : 'auto' });
      var b = document.querySelector('.brand'); if (b) b.focus({ preventScroll: true });
      try { history.replaceState(null, '', location.pathname + location.search); } catch (err) {}
    });
  });

  // floating "back to top" after the first screen
  var toTop = document.querySelector('.to-top');
  if (toTop) {
    var onScroll = function () { toTop.hidden = window.scrollY < window.innerHeight * 0.8; };
    window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  }

  // accessibility panel: text size, contrast, underlined links, spacing, stop animations (saved in this browser only)
  var a11yBtn = document.querySelector('.a11y-btn'), panel = document.getElementById('a11y-panel');
  var A = { fs: 0, dark: false, contrast: false, links: false, spacing: false, motion: false, easy: false };
  try { var saved = JSON.parse(localStorage.getItem('vendaval-a11y') || '{}'); for (var k in saved) if (k in A) A[k] = saved[k]; } catch (e) {}
  function applyA11y() {
    root.classList.remove('fs1', 'fs2', 'fs3', 'fs-1', 'fs-2'); if (A.fs) root.classList.add('fs' + A.fs);
    root.classList.toggle('a11y-dark', !!A.dark);
    if (panel) { panel.querySelector('[data-a="day"]').setAttribute('aria-pressed', !A.dark); panel.querySelector('[data-a="night"]').setAttribute('aria-pressed', !!A.dark); }
    ['contrast', 'links', 'spacing', 'motion', 'easy'].forEach(function (k) {
      root.classList.toggle('a11y-' + k, !!A[k]);
      var b = panel && panel.querySelector('[data-a="' + k + '"]'); if (b) b.setAttribute('aria-pressed', !!A[k]);
    });
    if (A.motion) clearInterval(timer);
    try { localStorage.setItem('vendaval-a11y', JSON.stringify(A)); } catch (e) {}
  }
  applyA11y();
  if (a11yBtn && panel) {
    a11yBtn.addEventListener('click', function () {
      var open = panel.hidden; panel.hidden = !open; a11yBtn.setAttribute('aria-expanded', open);
      if (open) panel.querySelector('button').focus();
    });
    // close when clicking anywhere outside the panel
    document.addEventListener('click', function (e) {
      if (!panel.hidden && !panel.contains(e.target) && !a11yBtn.contains(e.target)) { panel.hidden = true; a11yBtn.setAttribute('aria-expanded', false); }
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) { panel.hidden = true; a11yBtn.setAttribute('aria-expanded', false); a11yBtn.focus(); } });
    panel.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return; var a = b.dataset.a;
      if (a === 'bigger') A.fs = Math.min(3, A.fs + 1);
      else if (a === 'smaller') A.fs = Math.max(-2, A.fs - 1);
      else if (a === 'day') A.dark = false;
      else if (a === 'night') A.dark = true;
      else if (a === 'reset') A = { fs: 0, dark: false, contrast: false, links: false, spacing: false, motion: false, easy: false };
      else A[a] = !A[a];
      applyA11y();
    });
  }

  // agenda: move past dates using today's date (the page may be older than today)
  var today = new Date().toISOString().slice(0, 10);
  document.querySelectorAll('.agenda').forEach(function (ag) {
    var up = ag.querySelector('.timeline.up'), past = ag.querySelector('.timeline.past');
    if (!up) return;
    Array.prototype.slice.call(up.children).reverse().forEach(function (li) {
      if (li.dataset.end < today) { if (past) past.insertBefore(li, past.firstChild); else li.remove(); }
    });
    var max = +up.dataset.max; if (max) Array.prototype.slice.call(up.children, max).forEach(function (li) { li.remove(); });
    var none = ag.querySelector('.none'); if (none) none.hidden = up.children.length > 0;
  });

  // click-to-load YouTube (no request to YouTube before the click)
  document.querySelectorAll('.lite').forEach(function (box) {
    box.querySelector('.play').addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = box.dataset.src; f.allow = 'autoplay; encrypted-media; picture-in-picture'; f.allowFullscreen = true;
      f.title = this.getAttribute('aria-label');
      box.innerHTML = ''; box.appendChild(f);
    });
  });

  // gallery lightbox
  var lb = document.querySelector('.lightbox');
  if (lb && lb.showModal) {
    var lbImg = lb.querySelector('img'), gals = Array.prototype.slice.call(document.querySelectorAll('.gal')), at = 0;
    function lbShow(i) {
      at = (i + gals.length) % gals.length;   // endless loop
      var a = gals[at]; lbImg.src = a.href; lbImg.alt = a.querySelector('img').alt;
    }
    gals.forEach(function (a, i) {
      a.addEventListener('click', function (e) { e.preventDefault(); lbShow(i); lb.showModal(); });
    });
    var one = gals.length < 2;
    lb.querySelectorAll('.lb-nav').forEach(function (b) { b.hidden = one; });
    lb.querySelector('.lb-prev').addEventListener('click', function (e) { e.stopPropagation(); lbShow(at - 1); });
    lb.querySelector('.lb-next').addEventListener('click', function (e) { e.stopPropagation(); lbShow(at + 1); });
    lbImg.addEventListener('click', function (e) { e.stopPropagation(); lbShow(at + 1); });
    lb.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') lbShow(at - 1);
      if (e.key === 'ArrowRight') lbShow(at + 1);
    });
    var x0 = null;   // swipe on phones
    lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) lbShow(at + (dx < 0 ? 1 : -1));
    });
    lb.addEventListener('click', function () { lb.close(); });
  }

  // contact form (Web3Forms); falls back to email if no key is set
  var form = document.querySelector('.form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var st = form.querySelector('.status'), key = form.dataset.key, data = new FormData(form);
      if (!key || key.indexOf('REPLACE') === 0) {
        var body = []; data.forEach(function (v, k) { if (['access_key', 'botcheck', 'subject'].indexOf(k) < 0 && v) body.push(k + ': ' + v); });
        location.href = 'mailto:VENDAVAL@anartist.org?subject=' + encodeURIComponent(data.get('subject')) + '&body=' + encodeURIComponent(body.join('\n'));
        return;
      }
      st.className = 'status'; st.textContent = form.dataset.sending;
      fetch(form.action, { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (j.success) { form.reset(); st.className = 'status ok'; st.textContent = form.dataset.ok; }
          else throw 0;
        })
        .catch(function () { st.className = 'status err'; st.textContent = form.dataset.err; });
    });
  }
})();

// Squid cursor (mouse/trackpad only): looks left; over links and buttons it grabs and looks at the viewer; blinks on click.
// Off for touch-only screens and with the "stop animations" option; normal cursor in text fields.
(function () {
  var root = document.documentElement;
  if (!window.matchMedia || !window.matchMedia('(any-pointer: fine)').matches) return;
  var NS = 'http://www.w3.org/2000/svg';
  var box = document.createElement('div');
  box.className = 'squid'; box.setAttribute('aria-hidden', 'true');
  // drawn pointing left, then tilted like an arrow cursor: the pointy mantle tip is the click point (top-left)
  box.innerHTML = '<svg viewBox="0 0 52 46" width="44" height="39" overflow="visible"><g transform="translate(3 3) rotate(38) translate(-2 -20)">' +
    '<g class="sq-body">' +
      '<path class="sq-fin" d="M5 20 L12 8 L17 20 L12 32 Z"/>' +
      '<path class="sq-mantle" d="M2 20 Q12 10 31 11 L31 29 Q12 30 2 20 Z"/>' +
      '<circle class="sq-spot" cx="18" cy="16" r="1.5"/><circle class="sq-spot" cx="23" cy="23" r="1.3"/><circle class="sq-spot" cx="12" cy="21" r="1"/>' +
      '<ellipse class="sq-head" cx="37" cy="20" rx="8" ry="9.5"/>' +
    '</g>' +
    '<g class="sq-arms sq-idle"><path d="M43 15 Q50 11 58 13"/><path d="M44 18 Q51 17 59 19"/><path d="M44 22 Q51 23 59 21"/><path d="M43 25 Q50 29 58 27"/></g>' +
    '<g class="sq-arms sq-grab"><path d="M43 15 Q53 7 56 12 Q57 16 53 15"/><path d="M44 18 Q53 15 57 18 Q58 21 54 20"/><path d="M44 22 Q53 25 57 22 Q57 19 54 20"/><path d="M43 25 Q53 33 56 28 Q56 25 53 25"/></g>' +
    '<g class="sq-eyes sq-side"><circle class="sq-white" cx="37" cy="17" r="4.2"/><circle class="sq-pupil" cx="35" cy="17" r="2.1"/></g>' +
    '<g class="sq-eyes sq-front"><circle class="sq-white" cx="33" cy="17" r="3.4"/><circle class="sq-white" cx="41" cy="17" r="3.4"/><circle class="sq-pupil" cx="33" cy="18" r="1.8"/><circle class="sq-pupil" cx="41" cy="18" r="1.8"/></g>' +
    '<g class="sq-lids"><path class="lid-side" d="M33.5 17.5 Q37 19.5 40.5 17.5"/><path class="lid-front" d="M29.6 17.5 Q33 19.5 36.4 17.5"/><path class="lid-front" d="M37.6 17.5 Q41 19.5 44.4 17.5"/></g>' +
    '</g></svg>';
  var on = false, blinkT;
  function off() {
    return root.classList.contains('a11y-motion');
  }
  function textField(el) {
    return el && el.closest && el.closest('input:not([type=button]):not([type=submit]):not([type=checkbox]):not([type=radio]),textarea,select,[contenteditable=""],[contenteditable=true]');
  }
  function grabbable(el) {
    return el && el.closest && el.closest('.toy-pad,a,button,summary,label,[role=button],input[type=button],input[type=submit],input[type=checkbox],input[type=radio],.gallery img,[data-lb]');
  }
  document.body.appendChild(box);
  document.addEventListener('mousemove', function (e) {
    if (off()) { if (on) { root.classList.remove('squid-on'); on = false; } return; }
    if (!on) { root.classList.add('squid-on'); on = true; }
    // hotspot = the pointy tip of the mantle (top-left of the drawing)
    box.style.transform = 'translate(' + (e.clientX - 2.5) + 'px,' + (e.clientY - 2.5) + 'px)';
    var t = e.target;
    box.classList.toggle('hide', !!textField(t));
    box.classList.toggle('grab', !!grabbable(t));
  }, { passive: true });
  document.addEventListener('mouseleave', function () { box.classList.add('hide'); });
  document.addEventListener('mouseenter', function () { box.classList.remove('hide'); });
  document.addEventListener('mousedown', function () {
    if (!on) return;
    box.classList.add('blink'); clearTimeout(blinkT);
    blinkT = setTimeout(function () { box.classList.remove('blink'); }, 180);
  });
})();
