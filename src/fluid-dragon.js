/* Fire dragon in the water — hidden toy (WebGL fluid). Adapted from Las Marikarmen's "Fuego" toy (lasmarikarmen-web/assets/js/fluid.js).
   Long-press anywhere: a little fire dragon hatches and coils around the finger, growing.
   Flick while holding (or just let go): the dragon flies off across the screen in that direction, breathing fire, and dissolves.
   Keep holding GAME_MS more: the page turns into deep water with moving light; the dragon swims/flies around (it follows your finger),
   your strokes leave swirls of fire or water; stop touching for IDLE_MS (or press Esc) and it all dissolves back into the page.
   Off with reduced motion (system setting or the accessibility option, html.a11y-motion) and in #edit.
   Settings (optional, before this script): window.FLUID_DRAGON = { holdMs: 1600, gameMs: 3000, idleMs: 2000 }.
   Events on document: 'fluiddragon:brew', 'fluiddragon:game', 'fluiddragon:end' (e.g. to stop other toys).
   Fluid solver after Pavel Dobryakov's WebGL Fluid Simulation (MIT, github.com/PavelDoGreat/WebGL-Fluid-Simulation);
   water light pattern after the classic "water turbulence" caustics shader. */
(function () {
  'use strict';
  var html = document.documentElement, body = document.body;
  if (!body || window.__fluidDragon) return;
  window.__fluidDragon = true;
  var CFG = window.FLUID_DRAGON || {};
  var HOLD_MS = CFG.holdMs || 450, GAME_MS = CFG.gameMs || 3000, IDLE_MS = CFG.idleMs || 2000, SLOP = 12, FLICK = 0.45; // px/ms
  function off() {
    var rm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches, ed = false;
    try { ed = location.hash === '#edit' || !!sessionStorage.getItem('ls-edit'); } catch (e) {}
    return rm || ed || html.classList.contains('a11y-motion') || html.classList.contains('is-editing');
  }
  function emit(name) { try { document.dispatchEvent(new CustomEvent('fluiddragon:' + name)); } catch (e) {} }

  /* ---------- styles ---------- */
  var st = document.createElement('style');
  st.textContent =
    '.fluid-dragon{position:fixed;inset:0;width:100%;height:100%;z-index:9999;pointer-events:none;display:none;transition:opacity 1.2s ease;touch-action:none}' +
    '.fluid-dragon.is-on{display:block}.fluid-dragon.is-game{pointer-events:auto;cursor:crosshair}' +
    'html.fluid-hold,html.fluid-hold *{-webkit-user-select:none!important;user-select:none!important;-webkit-touch-callout:none!important}' +
    'html.fluid-game{overflow:hidden}';
  document.head.appendChild(st);
  var cv = document.createElement('canvas');
  cv.className = 'fluid-dragon';
  cv.setAttribute('aria-hidden', 'true');
  body.appendChild(cv);

  /* ---------- WebGL fluid ---------- */
  var gl, ext, P = {}, vel, dye, divg, curlT, pres, ready = false, failed = false, MULTI = 0;
  var VS = 'precision highp float;attribute vec2 aPosition;varying vec2 vUv,vL,vR,vT,vB;uniform vec2 texelSize;' +
    'void main(){vUv=aPosition*.5+.5;vL=vUv-vec2(texelSize.x,0.);vR=vUv+vec2(texelSize.x,0.);vT=vUv+vec2(0.,texelSize.y);vB=vUv-vec2(0.,texelSize.y);gl_Position=vec4(aPosition,0.,1.);}';
  var H = 'precision mediump float;precision mediump sampler2D;varying highp vec2 vUv,vL,vR,vT,vB;';
  var HH = '#ifdef GL_FRAGMENT_PRECISION_HIGH\nprecision highp float;\n#else\nprecision mediump float;\n#endif\nprecision mediump sampler2D;varying highp vec2 vUv,vL,vR,vT,vB;';
  var FS = {
    clear: H + 'uniform sampler2D uTexture;uniform float value;void main(){gl_FragColor=value*texture2D(uTexture,vUv);}',
    // dye: rgb = fire (shown as pure glowing hue), a = water (shown as light blue-green swirls). They never mix into grey.
    display: HH + 'uniform sampler2D uTexture,uVelocity;uniform float uBg,uTime,uAspect;' +
      'float caustic(vec2 uv,float t){vec2 p=uv*6.28318-250.;vec2 i=p;float c=1.;' +
      'for(int n=0;n<4;n++){float tt=t*(1.-(3.5/float(n+1)));i=p+vec2(cos(tt-i.x)+sin(tt+i.y),sin(tt-i.y)+cos(tt+i.x));' +
      'c+=1./length(vec2(p.x/(sin(i.x+tt)/.005),p.y/(cos(i.y+tt)/.005)));}c/=4.;c=1.17-pow(c,1.4);return pow(abs(c),8.);}' +
      'void main(){vec4 d=max(texture2D(uTexture,vUv),0.);vec2 v=texture2D(uVelocity,vUv).xy;float w=d.a;' +
      'vec2 q=vec2(vUv.x*uAspect,vUv.y)/max(uAspect,1.)*.95+v*.00035;float c=clamp(caustic(clamp(q,0.,1.),uTime*.35+23.),0.,1.);' +
      'vec3 deep=mix(vec3(.0,.035,.09),vec3(.0,.16,.26),vUv.y);vec3 water=deep+vec3(.2,.55,.6)*c*.55;' +
      'float ws=smoothstep(0.,1.2,w);water=mix(water,vec3(.08,.5,.62)+vec3(.55,.85,.9)*smoothstep(.9,2.6,w)*.5,ws*.65);' +
      'vec4 o=vec4(water,1.)*uBg;float wa=ws*.5*(1.-uBg);o=vec4(vec3(.1,.58,.72)*wa,wa)+(1.-wa)*o;' +
      'vec3 f=d.rgb;float m=max(f.r,max(f.g,f.b));vec3 hue=f/max(m,.0001);hue=mix(hue,vec3(1.,.96,.82),smoothstep(1.1,3.,m));' +
      'float fa=smoothstep(0.,.75,m);o=vec4(hue*fa,fa)+(1.-fa)*o;o.rgb+=hue*smoothstep(.3,2.,m)*.12*uBg;gl_FragColor=o;}',
    splat: H + 'uniform sampler2D uTarget;uniform float aspectRatio,radius;uniform vec4 color;uniform vec2 point;' +
      'void main(){vec2 p=vUv-point;p.x*=aspectRatio;gl_FragColor=texture2D(uTarget,vUv)+exp(-dot(p,p)/radius)*color;}',
    // up to 24 splats in one pass (the dragon's body): uP = x, y, radius; uC = colour or velocity
    multi: H + 'uniform sampler2D uTarget;uniform float aspectRatio;uniform int uN;uniform vec4 uP[24];uniform vec4 uC[24];' +
      'void main(){vec4 a=texture2D(uTarget,vUv);for(int i=0;i<24;i++){if(i>=uN)break;vec2 p=vUv-uP[i].xy;p.x*=aspectRatio;a+=exp(-dot(p,p)/uP[i].z)*uC[i];}gl_FragColor=a;}',
    advection: H + 'uniform sampler2D uVelocity,uSource;uniform highp vec2 texelSize;uniform float dt;uniform vec4 dissipation;' +
      'void main(){vec2 c=vUv-dt*texture2D(uVelocity,vUv).xy*texelSize;gl_FragColor=texture2D(uSource,c)/(1.+dissipation*dt);}',
    divergence: H + 'uniform sampler2D uVelocity;void main(){float L=texture2D(uVelocity,vL).x,R=texture2D(uVelocity,vR).x,T=texture2D(uVelocity,vT).y,B=texture2D(uVelocity,vB).y;' +
      'vec2 C=texture2D(uVelocity,vUv).xy;if(vL.x<0.)L=-C.x;if(vR.x>1.)R=-C.x;if(vT.y>1.)T=-C.y;if(vB.y<0.)B=-C.y;gl_FragColor=vec4(.5*(R-L+T-B),0.,0.,1.);}',
    curl: H + 'uniform sampler2D uVelocity;void main(){float L=texture2D(uVelocity,vL).y,R=texture2D(uVelocity,vR).y,T=texture2D(uVelocity,vT).x,B=texture2D(uVelocity,vB).x;' +
      'gl_FragColor=vec4(.5*(R-L-T+B),0.,0.,1.);}',
    vorticity: H + 'uniform sampler2D uVelocity,uCurl;uniform float curl,dt;void main(){float L=texture2D(uCurl,vL).x,R=texture2D(uCurl,vR).x,T=texture2D(uCurl,vT).x,B=texture2D(uCurl,vB).x,C=texture2D(uCurl,vUv).x;' +
      'vec2 f=.5*vec2(abs(T)-abs(B),abs(R)-abs(L));f/=length(f)+.0001;f*=curl*C;f.y*=-1.;vec2 v=texture2D(uVelocity,vUv).xy+f*dt;gl_FragColor=vec4(clamp(v,-1000.,1000.),0.,1.);}',
    pressure: H + 'uniform sampler2D uPressure,uDivergence;void main(){float L=texture2D(uPressure,vL).x,R=texture2D(uPressure,vR).x,T=texture2D(uPressure,vT).x,B=texture2D(uPressure,vB).x;' +
      'gl_FragColor=vec4((L+R+B+T-texture2D(uDivergence,vUv).x)*.25,0.,0.,1.);}',
    gradient: H + 'uniform sampler2D uPressure,uVelocity;void main(){float L=texture2D(uPressure,vL).x,R=texture2D(uPressure,vR).x,T=texture2D(uPressure,vT).x,B=texture2D(uPressure,vB).x;' +
      'vec2 v=texture2D(uVelocity,vUv).xy-vec2(R-L,T-B);gl_FragColor=vec4(v,0.,1.);}'
  };

  function init() {
    if (ready || failed) return ready;
    try {
      var opts = { alpha: true, depth: false, stencil: false, antialias: false, premultipliedAlpha: true, preserveDrawingBuffer: false };
      gl = cv.getContext('webgl2', opts);
      var gl2 = !!gl;
      if (!gl) gl = cv.getContext('webgl', opts) || cv.getContext('experimental-webgl', opts);
      if (!gl) throw 'no webgl';
      var half, linear;
      if (gl2) { gl.getExtension('EXT_color_buffer_float'); linear = true; half = gl.HALF_FLOAT; }
      else { var hf = gl.getExtension('OES_texture_half_float'); if (!hf) throw 'no half float'; half = hf.HALF_FLOAT_OES; linear = !!gl.getExtension('OES_texture_half_float_linear'); }
      var fmt = function (i, f) {
        if (!gl2) return testFmt(gl.RGBA, gl.RGBA, half) ? { i: gl.RGBA, f: gl.RGBA } : null;
        if (testFmt(i, f, half)) return { i: i, f: f };
        if (i === gl.R16F) return fmt(gl.RG16F, gl.RG);
        if (i === gl.RG16F) return fmt(gl.RGBA16F, gl.RGBA);
        return null;
      };
      ext = { half: half, filter: linear ? gl.LINEAR : gl.NEAREST,
        rgba: fmt(gl2 ? gl.RGBA16F : gl.RGBA, gl.RGBA), rg: fmt(gl2 ? gl.RG16F : gl.RGBA, gl2 ? gl.RG : gl.RGBA), r: fmt(gl2 ? gl.R16F : gl.RGBA, gl2 ? gl.RED : gl.RGBA) };
      if (!ext.rgba || !ext.rg || !ext.r) throw 'no render format';
      var vs = compile(gl.VERTEX_SHADER, VS);
      for (var k in FS) {
        if (k === 'multi' && gl.getParameter(gl.MAX_FRAGMENT_UNIFORM_VECTORS) < 64) continue;
        try { P[k] = program(vs, FS[k]); } catch (e) { if (k !== 'multi') throw e; }
      }
      MULTI = P.multi ? 24 : 0;
      var vb = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, vb);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, -1, 1, 1, 1, 1, -1]), gl.STATIC_DRAW);
      var ib = gl.createBuffer();
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ib);
      gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array([0, 1, 2, 0, 2, 3]), gl.STATIC_DRAW);
      gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
      gl.enableVertexAttribArray(0);
      resize(true);
      ready = true;
    } catch (e) { failed = true; if (window.console) console.info('fluid dragon off:', e); }
    return ready;
  }
  function testFmt(i, f, t) {
    var tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texImage2D(gl.TEXTURE_2D, 0, i, 4, 4, 0, f, t, null);
    var fb = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, fb);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
    var ok = gl.checkFramebufferStatus(gl.FRAMEBUFFER) === gl.FRAMEBUFFER_COMPLETE;
    gl.deleteFramebuffer(fb); gl.deleteTexture(tex);
    return ok;
  }
  function compile(type, src) {
    var s = gl.createShader(type);
    gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw gl.getShaderInfoLog(s);
    return s;
  }
  function program(vs, fs) {
    var p = gl.createProgram();
    gl.attachShader(p, vs); gl.attachShader(p, compile(gl.FRAGMENT_SHADER, fs));
    gl.bindAttribLocation(p, 0, 'aPosition');
    gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw gl.getProgramInfoLog(p);
    var u = {}, n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
    for (var i = 0; i < n; i++) { var name = gl.getActiveUniform(p, i).name; u[name.replace('[0]', '')] = gl.getUniformLocation(p, name); }
    return { p: p, u: u };
  }
  function use(pr) { gl.useProgram(pr.p); return pr.u; }
  function fbo(w, h, f, filter) {
    gl.activeTexture(gl.TEXTURE0);
    var tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, filter);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, filter);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D, 0, f.i, w, h, 0, f.f, ext.half, null);
    var fb = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, fb);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
    gl.viewport(0, 0, w, h); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
    return { fb: fb, w: w, h: h, attach: function (id) { gl.activeTexture(gl.TEXTURE0 + id); gl.bindTexture(gl.TEXTURE_2D, tex); return id; } };
  }
  function dbl(w, h, f, filter) {
    var a = fbo(w, h, f, filter), b = fbo(w, h, f, filter);
    return { w: w, h: h, tx: 1 / w, ty: 1 / h, read: a, write: b, swap: function () { var t = this.read; this.read = this.write; this.write = t; } };
  }
  function res(r) {
    var w = gl.drawingBufferWidth, h = gl.drawingBufferHeight, a = w / h; if (a < 1) a = 1 / a;
    var lo = Math.round(r), hi = Math.round(r * a);
    return w > h ? { w: hi, h: lo } : { w: lo, h: hi };
  }
  function resize(force) {
    var dpr = Math.min(window.devicePixelRatio || 1, 1.5);
    var w = Math.round(innerWidth * dpr), h = Math.round(innerHeight * dpr);
    if (!force && cv.width === w && cv.height === h) return;
    cv.width = w; cv.height = h;
    var small = Math.min(innerWidth, innerHeight) < 600;
    var s = res(small ? 112 : 144), d = res(small ? 640 : 1024);
    vel = dbl(s.w, s.h, ext.rg, ext.filter);
    dye = dbl(d.w, d.h, ext.rgba, ext.filter);
    divg = fbo(s.w, s.h, ext.r, gl.NEAREST);
    curlT = fbo(s.w, s.h, ext.r, gl.NEAREST);
    pres = dbl(s.w, s.h, ext.r, gl.NEAREST);
  }
  function blit(t) {
    if (t) { gl.viewport(0, 0, t.w, t.h); gl.bindFramebuffer(gl.FRAMEBUFFER, t.fb); }
    else { gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight); gl.bindFramebuffer(gl.FRAMEBUFFER, null); }
    gl.drawElements(gl.TRIANGLES, 6, gl.UNSIGNED_SHORT, 0);
  }

  var DIS = { fire: 2, water: 0.5, vel: 0.25 }, BG = 0, BG_TO = 0, T0 = performance.now();
  function step(dt) {
    gl.disable(gl.BLEND);
    var u = use(P.curl); gl.uniform2f(u.texelSize, vel.tx, vel.ty); gl.uniform1i(u.uVelocity, vel.read.attach(0)); blit(curlT);
    u = use(P.vorticity); gl.uniform2f(u.texelSize, vel.tx, vel.ty); gl.uniform1i(u.uVelocity, vel.read.attach(0)); gl.uniform1i(u.uCurl, curlT.attach(1));
    gl.uniform1f(u.curl, 22); gl.uniform1f(u.dt, dt); blit(vel.write); vel.swap();
    u = use(P.divergence); gl.uniform2f(u.texelSize, vel.tx, vel.ty); gl.uniform1i(u.uVelocity, vel.read.attach(0)); blit(divg);
    u = use(P.clear); gl.uniform1i(u.uTexture, pres.read.attach(0)); gl.uniform1f(u.value, 0.8); blit(pres.write); pres.swap();
    u = use(P.pressure); gl.uniform2f(u.texelSize, vel.tx, vel.ty); gl.uniform1i(u.uDivergence, divg.attach(0));
    for (var i = 0; i < 20; i++) { gl.uniform1i(u.uPressure, pres.read.attach(1)); blit(pres.write); pres.swap(); }
    u = use(P.gradient); gl.uniform2f(u.texelSize, vel.tx, vel.ty); gl.uniform1i(u.uPressure, pres.read.attach(0)); gl.uniform1i(u.uVelocity, vel.read.attach(1)); blit(vel.write); vel.swap();
    u = use(P.advection); gl.uniform2f(u.texelSize, vel.tx, vel.ty);
    var vid = vel.read.attach(0); gl.uniform1i(u.uVelocity, vid); gl.uniform1i(u.uSource, vid);
    gl.uniform1f(u.dt, dt); gl.uniform4f(u.dissipation, DIS.vel, DIS.vel, DIS.vel, DIS.vel); blit(vel.write); vel.swap();
    gl.uniform1i(u.uVelocity, vel.read.attach(0)); gl.uniform1i(u.uSource, dye.read.attach(1));
    gl.uniform4f(u.dissipation, DIS.fire, DIS.fire, DIS.fire, DIS.water); blit(dye.write); dye.swap();
  }
  function render(now) {
    gl.disable(gl.BLEND); gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.viewport(0, 0, gl.drawingBufferWidth, gl.drawingBufferHeight); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
    var u = use(P.display);
    gl.uniform1i(u.uTexture, dye.read.attach(0)); gl.uniform1i(u.uVelocity, vel.read.attach(1));
    gl.uniform1f(u.uBg, BG); gl.uniform1f(u.uTime, (now - T0) / 1000); gl.uniform1f(u.uAspect, cv.width / cv.height);
    blit(null);
  }

  /* splats are queued in screen pixels, then drawn: x, y, radius px, colour [r,g,b,water], velocity px/s */
  var Q = [];
  function put(x, y, r, col, vx, vy) { Q.push([x, y, r, col, vx || 0, vy || 0]); }
  function flush() {
    if (!Q.length) return;
    var asp = cv.width / cv.height, ih = innerHeight;
    var pts = Q.map(function (s) { return [s[0] / innerWidth, 1 - s[1] / ih, (s[2] / ih) * (s[2] / ih), s[3], s[4] / innerWidth * vel.w, -s[5] / ih * vel.h]; });
    Q = [];
    if (MULTI) {
      for (var i = 0; i < pts.length; i += MULTI) {
        var g = pts.slice(i, i + MULTI), PP = [], CV = [], CD = [];
        g.forEach(function (s) { PP.push(s[0], s[1], s[2], 0); CV.push(s[4], s[5], 0, 0); CD.push(s[3][0], s[3][1], s[3][2], s[3][3]); });
        var u = use(P.multi);
        gl.uniform1f(u.aspectRatio, asp); gl.uniform1i(u.uN, g.length); gl.uniform4fv(u.uP, PP);
        gl.uniform4fv(u.uC, CV); gl.uniform1i(u.uTarget, vel.read.attach(0)); blit(vel.write); vel.swap();
        gl.uniform4fv(u.uC, CD); gl.uniform1i(u.uTarget, dye.read.attach(0)); blit(dye.write); dye.swap();
      }
    } else {
      pts.forEach(function (s) {
        var u = use(P.splat);
        gl.uniform1f(u.aspectRatio, asp); gl.uniform2f(u.point, s[0], s[1]); gl.uniform1f(u.radius, s[2]);
        gl.uniform4f(u.color, s[4], s[5], 0, 0); gl.uniform1i(u.uTarget, vel.read.attach(0)); blit(vel.write); vel.swap();
        gl.uniform4f(u.color, s[3][0], s[3][1], s[3][2], s[3][3]); gl.uniform1i(u.uTarget, dye.read.attach(0)); blit(dye.write); dye.swap();
      });
    }
  }
  function wipe() {
    var u = use(P.clear); gl.uniform1f(u.value, 0);
    [vel, dye, pres].forEach(function (d) { gl.uniform1i(u.uTexture, d.read.attach(0)); blit(d.write); d.swap(); });
  }
  function fire(h, k) {                                        // hue 0 (red) … 55 (yellow) → [r,g,b,0] * k
    h = Math.max(0, Math.min(60, h)) / 60;
    return [k, k * (0.12 + 0.88 * h), k * 0.06 * h, 0];
  }
  function water(k) { return [0, 0, 0, k]; }
  function rnd(a, b) { return a + Math.random() * (b - a); }

  /* ---------- the dragon: a chain of points pulled by its head ---------- */
  var N = 26;
  function Dragon(x, y, ang, size) {
    this.p = []; this.size = size; this.ang = ang; this.t = 0; this.breath = 0; this.nextBreath = 1.2; this.live = true;
    for (var i = 0; i < N; i++) this.p.push({ x: x - Math.cos(ang) * i * 3, y: y - Math.sin(ang) * i * 3 });
  }
  Dragon.prototype.seg = function () { return 9 * this.size; };
  Dragon.prototype.moveHead = function (x, y) {
    var h = this.p[0], dx = x - h.x, dy = y - h.y;
    if (dx || dy) this.ang = Math.atan2(dy, dx);
    h.x = x; h.y = y;
    var L = this.seg();
    for (var i = 1; i < N; i++) {
      var a = this.p[i - 1], b = this.p[i], ex = b.x - a.x, ey = b.y - a.y, d = Math.hypot(ex, ey) || 1;
      b.x = a.x + ex / d * L; b.y = a.y + ey / d * L;
    }
  };
  Dragon.prototype.draw = function (dt, k) {               // k: overall brightness (0..1)
    var s = this.size, t = this.t += dt, f = dt * 60, p = this.p, i, u, a, b;
    if (!this.live || k <= 0) return;
    for (i = 0; i < N; i += 1) {                            // body + tail
      if (i % 2 && i < N - 4) continue;
      u = i / (N - 1); a = p[Math.max(i - 1, 0)]; b = p[Math.min(i + 1, N - 1)];
      var tx = b.x - a.x, ty = b.y - a.y, tl = Math.hypot(tx, ty) || 1; tx /= tl; ty /= tl;        // towards the tail
      var w = (0.45 + 0.55 * Math.sin(Math.PI * Math.min(1, (u + 0.1) / 0.75))) * (1 - u * 0.8);
      var wave = Math.sin(t * 7 - i * 0.45) * 55 * w;
      put(p[i].x, p[i].y, (3 + 9 * w) * s, fire(50 - u * 50, k * (0.16 + 0.16 * w) * f),
        tx * 20 - ty * wave, ty * 20 + tx * wave);
    }
    // head, jaw and eyes: hot white-yellow
    var hx = p[0].x, hy = p[0].y, fx = Math.cos(this.ang), fy = Math.sin(this.ang), nx = -fy, ny = fx;
    put(hx, hy, 10 * s, fire(55, k * 0.45 * f), fx * 40, fy * 40);
    put(hx + fx * 9 * s, hy + fy * 9 * s, 6 * s, fire(60, k * 0.35 * f), fx * 60, fy * 60);
    for (var e = -1; e <= 1; e += 2) put(hx - fx * 6 * s + nx * e * 7 * s, hy - fy * 6 * s + ny * e * 7 * s, 3.5 * s, fire(20, k * 0.5 * f), nx * e * 40, ny * e * 40);
    // wings at the shoulders, flapping
    var A = p[4], A2 = p[6], bx = A.x - A2.x, by = A.y - A2.y, bl = Math.hypot(bx, by) || 1; bx /= bl; by /= bl;   // forward at the shoulders
    var flap = Math.sin(t * 5.5), dflap = Math.cos(t * 5.5);
    for (var side = -1; side <= 1; side += 2) {
      var phi = 0.5 + 0.55 * flap, sx = -by * side, sy = bx * side;
      var wx = sx * Math.cos(phi) - bx * Math.sin(phi), wy = sy * Math.cos(phi) - by * Math.sin(phi);
      for (var j = 1; j <= 4; j++) {
        var d = j * 11 * s, cx = A.x + wx * d - bx * j * j * 1.5 * s, cy = A.y + wy * d - by * j * j * 1.5 * s;
        put(cx, cy, (8 - 1.3 * j) * s, fire(38 - j * 6, k * 0.26 * f), (-bx * 2 + sx) * dflap * d * 1.2, (-by * 2 + sy) * dflap * d * 1.2);
      }
    }
    // fire breath now and then
    this.nextBreath -= dt;
    if (this.nextBreath <= 0) { this.breath = 0.55; this.nextBreath = rnd(1.6, 3.2); }
    if (this.breath > 0) {
      this.breath -= dt;
      for (var m = 1; m <= 3; m++) put(hx + fx * (12 + m * 10) * s, hy + fy * (12 + m * 10) * s, (5 + m * 2) * s,
        fire(55 - m * 8, k * 0.55 * f), fx * 1100 + rnd(-150, 150), fy * 1100 + rnd(-150, 150));
    }
    // the wake: random swirls of fire and water around the body
    if (Math.random() < 0.35 * f) {
      var q = p[Math.floor(rnd(3, N))], sd = Math.random() < 0.5 ? -1 : 1, off = rnd(14, 38) * s;
      var ox = q.x + nx * sd * off + rnd(-8, 8), oy = q.y + ny * sd * off + rnd(-8, 8), spin = rnd(250, 550) * sd;
      put(ox, oy, rnd(9, 18) * s, Math.random() < 0.5 ? fire(rnd(0, 45), k * rnd(0.4, 0.9)) : water(k * rnd(1, 2.2)), fx * spin, fy * spin);
    }
  };

  /* ---------- the toy ---------- */
  var mode = 'idle', raf = 0, last = 0, fadeAt = 0;
  var hold = null, brew = null, dragon = null, fly = null, ptrs = {}, lastPlay = 0, suppressClick = 0, wander = null, wanderT = 0;

  function show() {
    if (!cv.classList.contains('is-on')) { cv.classList.add('is-on'); resize(); wipe(); }
    cv.style.opacity = '1';
    if (!raf) { last = performance.now(); raf = requestAnimationFrame(loop); }
  }
  function startFade() { mode = 'fade'; fadeAt = performance.now(); DIS.fire = 3; DIS.water = 1.6; DIS.vel = 0.6; BG_TO = 0; }
  function stopAll() {
    mode = 'idle'; cancelAnimationFrame(raf); raf = 0; dragon = null; fly = null; BG = BG_TO = 0;
    cv.classList.remove('is-on', 'is-game'); html.classList.remove('fluid-game', 'fluid-hold');
    emit('end');
  }
  function scale() { return Math.max(0.8, Math.min(1.6, Math.min(innerWidth, innerHeight) / 420)); }

  function loop(now) {
    raf = requestAnimationFrame(loop);
    var dt = Math.min((now - last) / 1000, 1 / 30); last = now;
    if (!dt) return;
    resize();
    BG += (BG_TO - BG) * Math.min(1, dt * 2.5);

    if (mode === 'brew' && brew) {                          // the little dragon hatches and coils around the finger
      var age = Math.min(1, (now - brew.t0) / GAME_MS);
      dragon.size = scale() * (0.45 + 0.4 * age);
      brew.a += dt * (3.2 + age * 2.5);
      var R = (16 + 42 * age) * scale();
      dragon.moveHead(brew.x + Math.cos(brew.a) * R, brew.y + Math.sin(brew.a) * R);
      dragon.draw(dt, 0.55 + 0.45 * age);
      if (Math.random() < 0.1) put(brew.x + rnd(-R, R), brew.y + rnd(-R, R), rnd(8, 14), water(rnd(0.4, 0.9)), rnd(-200, 200), rnd(-200, 200));
      if (now - brew.t0 > GAME_MS) startGame();
    } else if (fly && dragon) {                             // thrown: flies off in a weaving line
      fly.t += dt;
      var an = fly.ang + Math.sin(fly.t * 6) * 0.35, h = dragon.p[0];
      dragon.moveHead(h.x + Math.cos(an) * fly.speed * dt, h.y + Math.sin(an) * fly.speed * dt);
      dragon.draw(dt, Math.max(0, 1 - fly.t / 2.2));
      var tail = dragon.p[N - 1], M = 120;
      if (fly.t > 2.4 || (tail.x < -M || tail.y < -M || tail.x > innerWidth + M || tail.y > innerHeight + M) &&
          (h.x < -M || h.y < -M || h.x > innerWidth + M || h.y > innerHeight + M)) { fly = null; dragon.live = false; }
    } else if (mode === 'game' && dragon) {                 // swims around, follows a finger
      var tgt = null;
      for (var id in ptrs) { tgt = ptrs[id]; break; }
      if (!tgt) {
        if (!wander || now > wanderT || Math.hypot(wander.x - dragon.p[0].x, wander.y - dragon.p[0].y) < 60) {
          wander = { x: rnd(0.15, 0.85) * innerWidth, y: rnd(0.15, 0.85) * innerHeight }; wanderT = now + 2600;
        }
        tgt = wander;
      }
      var hd = dragon.p[0], want = Math.atan2(tgt.y - hd.y, tgt.x - hd.x), diff = Math.atan2(Math.sin(want - dragon.ang), Math.cos(want - dragon.ang));
      var dist = Math.hypot(tgt.x - hd.x, tgt.y - hd.y), sp = (260 + Math.min(dist, 400)) * scale();
      var na = dragon.ang + Math.max(-1, Math.min(1, diff)) * dt * 4 + Math.sin(dragon.t * 3) * dt * 0.8;
      dragon.moveHead(hd.x + Math.cos(na) * sp * dt, hd.y + Math.sin(na) * sp * dt);
      dragon.size += (scale() - dragon.size) * dt;
      dragon.draw(dt, 1);
      if (now - lastPlay > IDLE_MS && !Object.keys(ptrs).length) endGame();
    }

    if (mode === 'fade' && !fly && now - fadeAt > 1500) {
      cv.style.opacity = '0';
      if (now - fadeAt > 2900) { flush(); stopAll(); return; }
    }
    flush();
    step(dt);
    render(now);
  }

  function startBrew(h) {
    if (!init()) return;
    mode = 'brew'; DIS.fire = 3.2; DIS.water = 1.1; DIS.vel = 0.35; BG = BG_TO = 0; fly = null;
    brew = { id: h.id, x: h.x, y: h.y, t0: performance.now(), a: Math.random() * 6.28, hist: [[h.x, h.y, performance.now()]] };
    dragon = new Dragon(h.x + 16, h.y, brew.a + 1.57, scale() * 0.45);
    html.classList.add('fluid-hold');
    show();
    emit('brew');
    if (navigator.vibrate) try { navigator.vibrate(12); } catch (e) {}
  }
  function release() {
    var b = brew; brew = null; suppressClick = performance.now();
    html.classList.remove('fluid-hold');
    var hs = b.hist, now = performance.now(), i = hs.length - 1;
    while (i > 0 && now - hs[i - 1][2] < 90) i--;
    var dtm = Math.max(now - hs[i][2], 16), vx = (b.x - hs[i][0]) / dtm, vy = (b.y - hs[i][1]) / dtm, sp = Math.hypot(vx, vy);
    // flicked: flies that way, fast; let go: flies off the way it was heading
    fly = sp > FLICK ? { ang: Math.atan2(vy, vx), speed: Math.max(700, Math.min(sp * 1000 * 1.1, 2200)), t: 0 }
                     : { ang: dragon.ang, speed: 520, t: 0 };
    dragon.nextBreath = 0.05;
    startFade();
  }
  function startGame() {
    var b = brew; brew = null;
    ptrs[b.id] = { x: b.x, y: b.y, kind: 'fire', h: rnd(10, 50) };
    mode = 'game'; DIS.fire = 2.8; DIS.water = 0.35; DIS.vel = 0.2; BG_TO = 1; lastPlay = performance.now();
    html.classList.remove('fluid-hold'); html.classList.add('fluid-game');
    cv.classList.add('is-game');
    emit('game');
    if (navigator.vibrate) try { navigator.vibrate([20, 40, 30]); } catch (e) {}
    for (var i = 0; i < 16; i++) {                         // splash: a ring of water and fire
      var a = i / 16 * Math.PI * 2;
      put(b.x, b.y, 22, i % 2 ? water(2) : fire(rnd(10, 50), 0.9), Math.cos(a) * 1500, Math.sin(a) * 1500);
    }
    dragon.nextBreath = 0.3;
  }
  function endGame() {
    ptrs = {}; suppressClick = performance.now();
    cv.classList.remove('is-game'); html.classList.remove('fluid-game');
    if (dragon) dragon.live = false;
    startFade();
  }
  function cancelHold() { if (hold) { clearTimeout(hold.timer); hold = null; html.classList.remove('fluid-hold'); } }

  var SKIP = 'input,textarea,select,option,[contenteditable],video,audio,iframe,canvas,.fluid-off,.toy-buoy,.a11y,.a11y-panel,.lightbox,[role="slider"]';
  addEventListener('pointerdown', function (e) {
    if (mode === 'game') {
      var q = ptrs[e.pointerId] = { x: e.clientX, y: e.clientY, kind: Math.random() < 0.5 ? 'fire' : 'water', h: rnd(0, 50) };
      put(e.clientX, e.clientY, 20, q.kind === 'fire' ? fire(q.h, 0.8) : water(1.8), rnd(-500, 500), rnd(-500, 500));
      lastPlay = performance.now();
      return;
    }
    if (hold || brew) { cancelHold(); return; }              // a second finger (pinch) cancels
    if (!e.isPrimary || (e.pointerType === 'mouse' && e.button !== 0) || off()) return;
    if (e.target.closest && e.target.closest(SKIP)) return;
    var h = { id: e.pointerId, x: e.clientX, y: e.clientY };
    h.timer = setTimeout(function () { if (hold === h) { hold = null; startBrew(h); } }, HOLD_MS);
    hold = h;
    if (e.pointerType !== 'mouse') html.classList.add('fluid-hold');
  }, true);

  addEventListener('pointermove', function (e) {
    if (hold && e.pointerId === hold.id && Math.hypot(e.clientX - hold.x, e.clientY - hold.y) > SLOP) cancelHold();
    if (brew && e.pointerId === brew.id) {
      brew.x = e.clientX; brew.y = e.clientY;
      brew.hist.push([e.clientX, e.clientY, performance.now()]); if (brew.hist.length > 12) brew.hist.shift();
    }
    if (mode === 'game') {
      var q = ptrs[e.pointerId];
      if (q || e.pointerType === 'mouse' && e.buttons) {
        if (!q) q = ptrs[e.pointerId] = { x: e.clientX, y: e.clientY, kind: Math.random() < 0.5 ? 'fire' : 'water', h: rnd(0, 50) };
        var dx = e.clientX - q.x, dy = e.clientY - q.y;
        if (dx || dy) {
          put(e.clientX, e.clientY, 14, q.kind === 'fire' ? fire(q.h, 0.3) : water(0.7), dx * 60, dy * 60);
          lastPlay = performance.now();
        }
        q.x = e.clientX; q.y = e.clientY;
      }
    }
  }, true);

  function up(e) {
    if (hold && e.pointerId === hold.id) cancelHold();
    if (brew && e.pointerId === brew.id) {
      if (e.type === 'pointercancel') { brew = null; html.classList.remove('fluid-hold'); fly = { ang: dragon.ang, speed: 520, t: 0 }; startFade(); }
      else release();
    }
    if (ptrs[e.pointerId]) { delete ptrs[e.pointerId]; lastPlay = performance.now(); }
  }
  addEventListener('pointerup', up, true);
  addEventListener('pointercancel', up, true);

  addEventListener('touchmove', function (e) { if (brew || mode === 'game') e.preventDefault(); }, { passive: false, capture: true });
  addEventListener('contextmenu', function (e) { if (hold || brew || mode === 'game' || performance.now() - suppressClick < 600) e.preventDefault(); }, true);
  addEventListener('click', function (e) {
    if (mode === 'game' || performance.now() - suppressClick < 450) { e.preventDefault(); e.stopPropagation(); }
  }, true);
  addEventListener('keydown', function (e) { if (e.key === 'Escape' && mode === 'game') endGame(); });
  addEventListener('blur', function () {
    cancelHold();
    if (brew) { brew = null; html.classList.remove('fluid-hold'); fly = { ang: dragon.ang, speed: 520, t: 0 }; startFade(); }
    if (mode === 'game') endGame();
  });
  document.addEventListener('visibilitychange', function () { if (document.hidden && raf) { cancelHold(); brew = null; ptrs = {}; stopAll(); } });
})();
