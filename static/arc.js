// The home arc: five scroll-driven scenes between the hero and the editorial
// content. The DOM is already the finished static composition (no script,
// reduced motion); this file makes each scene live and gives the visitor
// something to control: dissolve a subscription, open a piece of the den,
// greet a teammate, scrub the measured speeds, reach the call to action.
(function () {
  "use strict";
  var arc = document.querySelector(".arc");
  if (!arc) return;
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var narrowMq = matchMedia("(max-width: 760px)");
  var coarse = matchMedia("(pointer: coarse)").matches;
  var fr = document.documentElement.lang === "fr";
  var DPR = 1, VH = innerHeight;
  var freedCount = 0;

  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function ease(v) { return 1 - Math.pow(1 - clamp(v, 0, 1), 3); }
  function fmt(v, dec) { var s = v.toFixed(dec); return fr ? s.replace(".", ",") : s; }
  function rand(seed) { // small deterministic generator: the composition is the same on every visit
    return function () { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  }

  // Ember glows, pre-rendered once (the recipe of hero.js).
  function glowSprite(core, mid) {
    var c = document.createElement("canvas");
    c.width = c.height = 48;
    var g = c.getContext("2d");
    var grad = g.createRadialGradient(24, 24, 0, 24, 24, 24);
    grad.addColorStop(0, core);
    grad.addColorStop(0.35, mid);
    grad.addColorStop(1, "rgba(18, 16, 14, 0)");
    g.fillStyle = grad;
    g.fillRect(0, 0, 48, 48);
    return c;
  }
  var TONES = [
    glowSprite("rgba(255, 224, 176, 1)", "rgba(224, 122, 47, .55)"),
    glowSprite("rgba(255, 178, 102, 1)", "rgba(224, 122, 47, .5)"),
    glowSprite("rgba(240, 152, 79, 1)", "rgba(150, 70, 20, .5)")
  ];
  function tone() { return TONES[(Math.random() * 3) | 0]; }

  // A particle pool per scene: embers that rise, drift and fade.
  function Embers(max) { this.list = []; this.max = max; }
  Embers.prototype.add = function (x, y, vx, vy, size, span) {
    if (this.list.length >= this.max) return;
    this.list.push({ x: x, y: y, vx: vx, vy: vy, size: size, span: span, life: 0,
      tone: tone(), phase: Math.random() * 6.28 });
  };
  Embers.prototype.draw = function (ctx, dt, t, lift) {
    var l = this.list;
    for (var i = l.length - 1; i >= 0; i--) {
      var p = l[i];
      p.life += dt;
      if (p.life > p.span) { l[i] = l[l.length - 1]; l.pop(); continue; }
      p.vx *= 0.97; p.vy = p.vy * 0.98 - lift * dt;
      p.x += (p.vx + Math.sin(t * 1.7 + p.phase) * 8) * dt;
      p.y += p.vy * dt;
      var k = p.life / p.span;
      ctx.globalAlpha = Math.min(1, p.life * 6) * (1 - k) * (0.6 + 0.4 * Math.sin(t * 9 + p.phase));
      var s = p.size * (1 - k * 0.5);
      ctx.drawImage(p.tone, p.x - s, p.y - s, s * 2, s * 2);
    }
    ctx.globalAlpha = 1;
  };

  // ---- The scene shell: a sticky stage, a canvas, a scroll progress -------
  function Scene(el, impl) {
    this.el = el;
    this.stage = el.querySelector(".arc-stage");
    this.canvas = el.querySelector(".arc-canvas");
    this.ctx = this.canvas.getContext("2d");
    this.p = 0; this.vis = false; this.W = 0; this.H = 0;
    this.px = -1e4; this.py = -1e4;
    this.impl = impl;
    var self = this;
    this.stage.addEventListener("pointermove", function (ev) {
      var r = self.stage.getBoundingClientRect();
      self.px = ev.clientX - r.left; self.py = ev.clientY - r.top;
    }, { passive: true });
    this.stage.addEventListener("pointerleave", function () { self.px = self.py = -1e4; }, { passive: true });
    impl.init(this);
  }
  Scene.prototype.resize = function () {
    this.W = this.stage.clientWidth;
    this.H = this.stage.clientHeight;
    this.canvas.width = Math.round(this.W * DPR);
    this.canvas.height = Math.round(this.H * DPR);
    this.ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    this.impl.resize(this);
  };
  Scene.prototype.progress = function () {
    var r = this.el.getBoundingClientRect();
    var run = r.height - VH;
    this.p = run > 0 ? clamp(-r.top / run, 0, 1) : clamp(1 - r.top / VH, 0, 1);
  };
  Scene.prototype.local = function (el) { // an element's box, in stage pixels
    var s = this.stage.getBoundingClientRect(), r = el.getBoundingClientRect();
    return { x: r.left - s.left, y: r.top - s.top, w: r.width, h: r.height };
  };

  // ---- 1. The bill: subscription cards that dissolve into embers ----------
  var bill = {
    init: function (sc) {
      var self = this;
      this.list = sc.el.querySelector(".arc-cards");
      this.counter = sc.el.querySelector(".arc-freed");
      this.monthly = this.list.getAttribute("data-monthly");
      this.embers = new Embers(coarse ? 160 : 420);
      this.cards = [].map.call(sc.el.querySelectorAll(".arc-card"), function (li, i) {
        var c = { li: li, btn: li.querySelector(".arc-saas"), twin: li.querySelector(".arc-twin"),
          name: li.querySelector(".arc-saas-name").textContent,
          holds: li.querySelector(".arc-saas-holds").textContent,
          burn: 0, clicked: false, freed: false, hover: 0, over: false, i: i };
        if (!reduce) c.twin.tabIndex = -1; // reachable once the card is freed
        c.btn.addEventListener("click", function () {
          c.clicked = true;
        });
        c.btn.addEventListener("pointerenter", function () { c.over = true; });
        c.btn.addEventListener("pointerleave", function () { c.over = false; });
        c.btn.addEventListener("focus", function () { c.over = true; });
        c.btn.addEventListener("blur", function () { c.over = false; });
        return c;
      });
      var order = this.cards.map(function (c) { return c.i; });
      var r = rand(7);
      order.sort(function () { return r() - 0.5; });
      order.forEach(function (ci, k) { self.cards[ci].slot = k; });
      if (!reduce) this.setFreed(0);
    },
    setFreed: function (n) {
      freedCount = n;
      this.counter.textContent = n;
    },
    resize: function (sc) {
      if (reduce) return; // the static grid lays itself out
      var narrow = narrowMq.matches, W = sc.W, H = sc.H, cards = this.cards;
      var copy = sc.local(sc.el.querySelector(".arc-copy"));
      var cols = narrow ? 2 : 3, rows = Math.ceil(cards.length / cols);
      var x0 = narrow ? 14 : Math.max(copy.x + copy.w + 24, W * 0.42), x1 = W - (narrow ? 14 : 40);
      var y0 = narrow ? copy.y + copy.h + 18 : H * 0.14, y1 = H - (narrow ? 18 : 60);
      var r = rand(42), gw = (x1 - x0) / cols, gh = (y1 - y0) / rows;
      var cw = Math.min(narrow ? 168 : 200, gw - 14), ch = narrow ? 60 : 78;
      for (var i = 0; i < cards.length; i++) {
        var c = cards[i], col = i % cols, row = (i / cols) | 0;
        c.w = cw; c.h = ch;
        var jx = (gw - cw) * 0.5, jy = Math.max(0, (gh - ch) * 0.45);
        c.x = x0 + gw * (col + 0.5) + (r() - 0.5) * jx * (row % 2 ? 1.4 : 0.8);
        c.y = y0 + gh * (row + 0.5) + (r() - 0.5) * jy;
        c.depth = 0.5 + r();
        c.phase = r() * 6.28;
        c.li.style.width = cw + "px";
        c.li.style.height = ch + "px";
        this.paint(c);
      }
    },
    paint: function (c) { // the card face, and its dissolve noise, at device resolution
      var w = Math.round(c.w * DPR), h = Math.round(c.h * DPR);
      var cv = document.createElement("canvas");
      cv.width = w; cv.height = h;
      var g = cv.getContext("2d"), s = DPR, narrow = c.h < 70;
      g.scale(s, s);
      g.beginPath(); g.roundRect(0.5, 0.5, c.w - 1, c.h - 1, 10);
      var bg = g.createLinearGradient(0, 0, 0, c.h);
      bg.addColorStop(0, "#29231d"); bg.addColorStop(1, "#1c1915");
      g.fillStyle = bg; g.fill();
      g.strokeStyle = "rgba(239, 233, 224, .14)"; g.lineWidth = 1; g.stroke();
      var ic = narrow ? 30 : 42, ix = narrow ? 12 : 16, iy = (c.h - ic) / 2;
      g.beginPath(); g.roundRect(ix, iy, ic, ic, 9);
      g.fillStyle = "#efe9e0"; g.fill();
      g.fillStyle = "#12100e";
      g.font = "600 " + (narrow ? 17 : 24) + "px Fraunces, Georgia, serif";
      g.textAlign = "center"; g.textBaseline = "middle";
      g.fillText(c.name.charAt(0), ix + ic / 2, iy + ic / 2 + 1);
      g.textAlign = "left"; g.textBaseline = "alphabetic";
      var tx = ix + ic + (narrow ? 10 : 14);
      g.fillStyle = "#efe9e0";
      g.font = "600 " + (narrow ? 13 : 16) + "px Inter, system-ui, sans-serif";
      g.fillText(c.name, tx, c.h / 2 - (narrow ? 1 : 2), c.w - tx - 10);
      g.fillStyle = "rgba(239, 233, 224, .6)";
      g.font = (narrow ? 11 : 13) + "px Inter, system-ui, sans-serif";
      g.fillText(c.holds, tx, c.h / 2 + (narrow ? 14 : 18), c.w - tx - 10);
      if (!narrow) {
        g.font = "600 9px ui-monospace, monospace";
        g.fillStyle = "rgba(224, 122, 47, .85)";
        g.textAlign = "right";
        g.fillText(this.monthly.toUpperCase() + " €", c.w - 12, 18);
      }
      c.face = cv;
      c.src = g.getImageData(0, 0, w, h).data;
      c.out = document.createElement("canvas");
      c.out.width = w; c.out.height = h;
      c.octx = c.out.getContext("2d");
      c.img = c.octx.createImageData(w, h);
      // Value noise on two octaves, plus a slope: the card burns from the bottom up.
      var r = rand(101 + c.i * 13), cell = 7 * s, gx = Math.ceil(w / cell) + 2, gy = Math.ceil(h / cell) + 2;
      var lat = new Float32Array(gx * gy);
      for (var k = 0; k < lat.length; k++) lat[k] = r();
      var n = new Float32Array(w * h);
      for (var y = 0; y < h; y++) {
        for (var x = 0; x < w; x++) {
          var fx = x / cell, fy = y / cell, xi = fx | 0, yi = fy | 0, u = fx - xi, v = fy - yi;
          u = u * u * (3 - 2 * u); v = v * v * (3 - 2 * v);
          var a = lat[yi * gx + xi], b = lat[yi * gx + xi + 1], c2 = lat[(yi + 1) * gx + xi], d = lat[(yi + 1) * gx + xi + 1];
          var vn = a + (b - a) * u + (c2 - a) * v + (a - b - c2 + d) * u * v;
          var f2 = lat[((yi * 3 + 1) % gy) * gx + ((xi * 3 + 2) % gx)];
          n[y * w + x] = 0.5 * vn + 0.12 * f2 + 0.38 * (y / h);
        }
      }
      c.noise = n;
    },
    dissolve: function (c) { // the threshold pass: gone, glowing edge, or intact
      var th = c.burn * 1.12 - 0.06, band = 0.07, src = c.src, n = c.noise, out = c.img.data;
      var w = c.out.width, edgeCount = 0;
      for (var i = 0, j = 0; i < n.length; i++, j += 4) {
        var v = n[i];
        if (v < th) { out[j + 3] = 0; continue; }
        var a = src[j + 3];
        if (v < th + band) {
          var k = (v - th) / band; // 0 at the burning edge, 1 at the intact side
          out[j] = 255; out[j + 1] = 120 + 120 * (1 - k); out[j + 2] = 40 + 120 * (1 - k) * (1 - k);
          out[j + 3] = a ? 255 : 255 * (1 - k);
          if (k < 0.25 && (edgeCount++ & 63) === 0 && Math.random() < 0.5) {
            var ex = (i % w) / DPR, ey = ((i / w) | 0) / DPR;
            this.pending.push(ex, ey);
          }
        } else {
          out[j] = src[j]; out[j + 1] = src[j + 1]; out[j + 2] = src[j + 2]; out[j + 3] = a;
        }
      }
      c.octx.putImageData(c.img, 0, 0);
    },
    frame: function (sc, dt, t) {
      var ctx = sc.ctx, cards = this.cards, freed = 0, narrow = narrowMq.matches;
      ctx.clearRect(0, 0, sc.W, sc.H);
      var mx = sc.px > -1e3 ? (sc.px / sc.W - 0.5) : 0, my = sc.py > -1e3 ? (sc.py / sc.H - 0.5) : 0;
      for (var i = 0; i < cards.length; i++) {
        var c = cards[i];
        var start = 0.1 + c.slot * (narrow ? 0.058 : 0.055);
        var target = Math.max(c.clicked ? 1 : 0, clamp((sc.p - start) / 0.07, 0, 1));
        var diff = target - c.burn;
        c.burn += Math.sign(diff) * Math.min(Math.abs(diff), dt * 1.3);
        c.hover += ((c.over && c.burn < 0.01 ? 1 : 0) - c.hover) * Math.min(1, dt * 10);
        var fx = c.x + Math.cos(t * 0.5 + c.phase) * 5 - mx * 26 * c.depth;
        var fy = c.y + Math.sin(t * 0.7 + c.phase) * 7 - my * 18 * c.depth - c.hover * 6;
        var rot = Math.sin(t * 0.35 + c.phase) * 0.035;
        var sc2 = 1 + c.hover * 0.04;
        c.li.style.transform = "translate(" + (fx - c.w / 2).toFixed(1) + "px," + (fy - c.h / 2).toFixed(1) +
          "px) rotate(" + rot.toFixed(3) + "rad) scale(" + sc2.toFixed(3) + ")";
        var isFreed = c.burn >= 0.999;
        if (isFreed !== c.freed) {
          c.freed = isFreed;
          c.li.classList.toggle("is-freed", isFreed);
          c.btn.setAttribute("aria-pressed", isFreed ? "true" : "false");
          c.twin.tabIndex = isFreed ? 0 : -1;
        }
        if (isFreed) { freed++; continue; }
        ctx.save();
        ctx.translate(fx, fy);
        ctx.rotate(rot);
        ctx.scale(sc2, sc2);
        if (c.hover > 0.01) {
          ctx.globalAlpha = c.hover * 0.5;
          ctx.drawImage(TONES[1], -c.w * 0.7, -c.h * 1.2, c.w * 1.4, c.h * 2.4);
          ctx.globalAlpha = 1;
        }
        if (c.burn > 0.001) {
          this.pending = [];
          this.dissolve(c);
          ctx.drawImage(c.out, -c.w / 2, -c.h / 2, c.w, c.h);
          var cs = Math.cos(rot), sn = Math.sin(rot);
          for (var k = 0; k < this.pending.length; k += 2) {
            var lx = this.pending[k] - c.w / 2, ly = this.pending[k + 1] - c.h / 2;
            this.embers.add(fx + lx * cs - ly * sn, fy + lx * sn + ly * cs,
              (Math.random() - 0.5) * 30, -20 - Math.random() * 50, 2 + Math.random() * 5, 1 + Math.random() * 1.6);
          }
        } else {
          ctx.drawImage(c.face, -c.w / 2, -c.h / 2, c.w, c.h);
        }
        ctx.restore();
      }
      if (freed !== freedCount) this.setFreed(freed);
      ctx.globalCompositeOperation = "lighter";
      this.embers.draw(ctx, dt, t, 40);
      ctx.globalCompositeOperation = "source-over";
    }
  };

  // ---- 2. The den: the homelab map builds itself as you scroll ------------
  var den = {
    init: function (sc) {
      var self = this;
      this.fiche = sc.el.querySelector(".arc-fiche");
      this.hint = this.fiche.innerHTML;
      this.readLabel = this.fiche.getAttribute("data-read");
      this.nodes = [].map.call(sc.el.querySelectorAll(".arc-node"), function (li, i) {
        return { li: li, key: li.getAttribute("data-key"), btn: li.querySelector("button"),
          links: li.getAttribute("data-links").split(" ").filter(Boolean), i: i, on: -1 };
      });
      var byKey = {};
      this.nodes.forEach(function (n) { byKey[n.key] = n; });
      this.edges = [];
      this.nodes.forEach(function (n) {
        n.links.forEach(function (k) {
          self.edges.push({ a: byKey[k], b: n, pulse: Math.random(), speed: 0.25 + Math.random() * 0.3 });
        });
        n.btn.addEventListener("click", function () { self.open(n); });
      });
      this.sel = null;
      this.grid = document.createElement("canvas");
    },
    open: function (n) {
      this.edges.forEach(function (e) { e.a.li.classList.remove("is-near"); e.b.li.classList.remove("is-near"); });
      if (this.sel) { this.sel.li.classList.remove("is-open"); this.sel.btn.setAttribute("aria-expanded", "false"); }
      if (this.sel === n) { this.sel = null; this.fiche.innerHTML = this.hint; return; }
      this.sel = n;
      n.li.classList.add("is-open");
      this.edges.forEach(function (e) {
        if (e.a === n) e.b.li.classList.add("is-near");
        if (e.b === n) e.a.li.classList.add("is-near");
      });
      n.btn.setAttribute("aria-expanded", "true");
      var name = n.btn.querySelector("b").textContent, say = n.btn.querySelector(".arc-say").textContent;
      this.fiche.innerHTML = "";
      var h = document.createElement("h3"); h.textContent = name;
      var p = document.createElement("p"); p.textContent = say;
      var a = document.createElement("a"); a.href = n.btn.getAttribute("data-href"); a.textContent = this.readLabel + " →";
      this.fiche.append(h, p, a);
    },
    resize: function (sc) {
      this.nodes.forEach(function (n) {
        var r = sc.local(n.li.querySelector(".arc-dot"));
        n.x = r.x + r.w / 2; n.y = r.y + r.h / 2;
      });
      this.edges.forEach(function (e, i) { // each wire sags a little, alternately left and right
        var dx = e.b.x - e.a.x, dy = e.b.y - e.a.y, bow = (i % 2 ? 0.14 : -0.14);
        e.cx = (e.a.x + e.b.x) / 2 - dy * bow; e.cy = (e.a.y + e.b.y) / 2 + dx * bow;
      });
      // The blueprint: a faint dot grid, drawn once.
      var g = this.grid, step = 28;
      g.width = Math.round(sc.W * DPR); g.height = Math.round(sc.H * DPR);
      var c = g.getContext("2d");
      c.scale(DPR, DPR);
      c.fillStyle = "rgba(239, 233, 224, .16)";
      for (var y = step / 2; y < sc.H; y += step) for (var x = step / 2; x < sc.W; x += step) c.fillRect(x, y, 1, 1);
      if (reduce) this.still(sc);
    },
    start: function (n) { return 0.04 + n.i * 0.052; },
    at: function (e, q) { // a point on the wire's curve
      var u = 1 - q;
      return [u * u * e.a.x + 2 * u * q * e.cx + q * q * e.b.x, u * u * e.a.y + 2 * u * q * e.cy + q * q * e.b.y];
    },
    still: function (sc) { // reduced motion: the finished map, drawn once
      var ctx = sc.ctx;
      ctx.clearRect(0, 0, sc.W, sc.H);
      ctx.strokeStyle = "rgba(224, 122, 47, .4)"; ctx.lineWidth = 1.2;
      this.edges.forEach(function (e) { ctx.beginPath(); ctx.moveTo(e.a.x, e.a.y); ctx.quadraticCurveTo(e.cx, e.cy, e.b.x, e.b.y); ctx.stroke(); });
    },
    frame: function (sc, dt, t) {
      var ctx = sc.ctx, p = sc.p, i, n, e;
      ctx.clearRect(0, 0, sc.W, sc.H);
      ctx.globalAlpha = clamp(p * 5, 0, 1) * 0.8;
      ctx.drawImage(this.grid, 0, 0, sc.W, sc.H);
      ctx.globalAlpha = 1;
      for (i = 0; i < this.nodes.length; i++) {
        n = this.nodes[i];
        var on = ease((p - this.start(n)) / 0.06);
        if (Math.abs(on - n.on) > 0.002) { n.on = on; n.li.style.setProperty("--on", on.toFixed(3)); }
      }
      var sel = this.sel;
      ctx.lineCap = "round";
      for (i = 0; i < this.edges.length; i++) {
        e = this.edges[i];
        var k = ease((p - this.start(e.b) - 0.02) / 0.07);
        if (k <= 0) continue;
        var lit = sel && (e.a === sel || e.b === sel);
        ctx.strokeStyle = lit ? "rgba(242, 163, 92, .9)" : "rgba(239, 233, 224, .22)";
        ctx.lineWidth = lit ? 1.8 : 1;
        ctx.beginPath(); ctx.moveTo(e.a.x, e.a.y);
        var steps = Math.max(2, Math.ceil(k * 24)), pt;
        for (var st = 1; st <= steps; st++) { pt = this.at(e, k * st / steps); ctx.lineTo(pt[0], pt[1]); }
        ctx.stroke();
        var x = pt[0], y = pt[1];
        ctx.globalCompositeOperation = "lighter";
        if (k < 1) { // the drawing tip glows like a fuse
          ctx.drawImage(TONES[0], x - 14, y - 14, 28, 28);
        } else { // data travels along finished links
          e.pulse = (e.pulse + dt * e.speed * (lit ? 2.2 : 1)) % 1;
          var q = e.pulse, s = lit ? 12 : 8;
          var qp = this.at(e, q), qx = qp[0], qy = qp[1];
          ctx.globalAlpha = Math.sin(q * Math.PI) * (lit ? 1 : 0.75);
          ctx.drawImage(TONES[1], qx - s, qy - s, s * 2, s * 2);
          ctx.globalAlpha = 1;
        }
        ctx.globalCompositeOperation = "source-over";
      }
      ctx.globalCompositeOperation = "lighter";
      for (i = 0; i < this.nodes.length; i++) {
        n = this.nodes[i];
        if (n.on <= 0) continue;
        var big = (n === sel ? 46 : 26) + Math.sin(t * 2 + i) * 3;
        ctx.globalAlpha = n.on * (n === sel ? 0.9 : 0.4);
        ctx.drawImage(TONES[2], n.x - big, n.y - big, big * 2, big * 2);
      }
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = "source-over";
    }
  };

  // ---- 3. The swarm: the crew turns around a fox-fire; tap one to greet ---
  // One video element for the whole arc: it plays a greeting in the swarm, and
  // Inari's at the call to action; whoever needs it takes it.
  function playOnce(video, src) {
    if (video.getAttribute("src") !== src) video.src = src;
    video.currentTime = 0;
    var pr = video.play();
    if (pr && pr.catch) pr.catch(function () {});
  }
  var CELL_W = 112, CELL_H = 128, FRAME_RATIO = 176 / 154; // the stills crop the video frame's right edge
  var swarm = {
    init: function (sc) {
      var self = this;
      this.video = sc.el.querySelector(".arc-wave");
      this.mates = [].map.call(sc.el.querySelectorAll(".arc-mate"), function (li, i) {
        var m = { li: li, name: li.getAttribute("data-name"), i: i, btn: li.querySelector("button") };
        m.btn.addEventListener("click", function () {
          if (self.dragged) return;
          self.greet(m);
        });
        return m;
      });
      this.off = 0; this.offTarget = null; this.vel = 0; this.active = null; this.front = null;
      this.embers = new Embers(coarse ? 70 : 160);
      this.video.addEventListener("playing", function () {
        if (!self.active || self.video.parentNode !== sc.stage) return;
        self.active.li.classList.add("is-waving");
        self.video.classList.add("on");
      });
      this.video.addEventListener("ended", function () { if (self.video.parentNode === sc.stage) self.rest(); });
      this.video.addEventListener("error", function () { if (self.video.parentNode === sc.stage) self.rest(); });
      // Drag the circle: horizontal movement turns the ring; a short tap stays a tap.
      var downX = 0, lastX = 0, dragging = false;
      sc.stage.addEventListener("pointerdown", function (ev) {
        if (ev.button) return;
        downX = lastX = ev.clientX; dragging = true; self.dragged = false;
      });
      addEventListener("pointermove", function (ev) {
        if (!dragging) return;
        var dx = ev.clientX - lastX;
        lastX = ev.clientX;
        if (Math.abs(ev.clientX - downX) > 8) { self.dragged = true; self.offTarget = null; }
        if (self.dragged) { self.off += dx / (self.rx || 300) * 1.4; self.vel = dx / (self.rx || 300) * 60; }
      }, { passive: true });
      addEventListener("pointerup", function () {
        dragging = false;
        setTimeout(function () { self.dragged = false; }, 0);
      });
      this.sc = sc;
    },
    greet: function (m) {
      this.rest();
      this.active = m;
      m.li.classList.add("is-active");
      var base = this.base(), want = -m.i * 2 * Math.PI / this.mates.length - (base - this.off);
      var turn = want - this.off;
      turn -= Math.round(turn / (2 * Math.PI)) * 2 * Math.PI; // the short way round
      this.offTarget = this.off + turn;
      if (reduce) return;
      end.release();
      if (this.video.parentNode !== this.sc.stage) this.sc.stage.appendChild(this.video);
      playOnce(this.video, "/media/personas/" + m.name + ".webm");
    },
    rest: function () {
      if (this.active) this.active.li.classList.remove("is-active", "is-waving");
      this.video.classList.remove("on");
      this.active = null;
    },
    base: function () { return -this.sc.p * Math.PI * 1.5 + this.off; },
    resize: function (sc) {
      var narrow = narrowMq.matches, W = sc.W, H = sc.H;
      this.cx = narrow ? W / 2 : W * 0.6;
      this.cy = narrow ? H * 0.66 : H * 0.7;
      this.rx = narrow ? W * 0.38 : Math.min(W * 0.34, 480);
      this.ry = this.rx * (narrow ? 0.32 : 0.26);
      this.k = narrow ? 1.05 : 1.4;
    },
    frame: function (sc, dt, t) {
      var ctx = sc.ctx, N = this.mates.length;
      if (this.offTarget !== null) {
        this.off += (this.offTarget - this.off) * Math.min(1, dt * 5);
        if (Math.abs(this.offTarget - this.off) < 0.001) this.offTarget = null;
      } else if (Math.abs(this.vel) > 0.001) {
        this.off += this.vel * dt; this.vel *= Math.pow(0.04, dt);
      }
      var base = this.base(), best = null, bestD = -1;
      for (var i = 0; i < N; i++) {
        var m = this.mates[i], a = base + i * 2 * Math.PI / N + Math.PI / 2;
        var d = (Math.sin(a) + 1) / 2, s = (0.5 + 0.5 * d) * this.k;
        var x = this.cx + Math.cos(a) * this.rx, y = this.cy + Math.sin(a) * this.ry;
        m.w = CELL_W * s; m.h = CELL_H * s; m.x = x - m.w / 2; m.y = y - m.h * 0.92;
        m.li.style.transform = "translate(" + m.x.toFixed(1) + "px," + m.y.toFixed(1) + "px) scale(" + s.toFixed(3) + ")";
        m.li.style.zIndex = 10 + Math.round(d * 80);
        m.li.style.opacity = (0.35 + 0.65 * d).toFixed(2);
        if (d > bestD) { bestD = d; best = m; }
      }
      if (best !== this.front) {
        if (this.front) this.front.li.classList.remove("is-front");
        best.li.classList.add("is-front");
        this.front = best;
      }
      if (this.active) {
        var am = this.active;
        this.video.style.transform = "translate(" + am.x.toFixed(1) + "px," + am.y.toFixed(1) + "px)";
        this.video.style.width = (am.w * FRAME_RATIO).toFixed(1) + "px";
        this.video.style.height = am.h.toFixed(1) + "px";
        this.video.style.zIndex = am.li.style.zIndex;
      }
      // The fox-fire at the centre of the ring: a ground glow and its embers.
      ctx.clearRect(0, 0, sc.W, sc.H);
      ctx.globalCompositeOperation = "lighter";
      var fl = 0.8 + 0.2 * Math.sin(t * 7) * Math.sin(t * 3.1);
      ctx.save();
      ctx.translate(this.cx, this.cy);
      ctx.scale(1, this.ry / this.rx);
      var g = ctx.createRadialGradient(0, 0, 0, 0, 0, this.rx * 1.25);
      g.addColorStop(0, "rgba(224, 122, 47, " + (0.22 * fl).toFixed(3) + ")");
      g.addColorStop(1, "rgba(224, 122, 47, 0)");
      ctx.fillStyle = g;
      ctx.fillRect(-this.rx * 1.3, -this.rx * 1.3, this.rx * 2.6, this.rx * 2.6);
      ctx.restore();
      var f = this.rx * 0.18;
      ctx.globalAlpha = 0.9 * fl;
      ctx.drawImage(TONES[0], this.cx - f, this.cy - f * 1.6, f * 2, f * 2);
      ctx.globalAlpha = 1;
      var rate = coarse ? 24 : 60;
      if (Math.random() < rate * dt) {
        this.embers.add(this.cx + (Math.random() - 0.5) * f * 1.2, this.cy - f * 0.6,
          (Math.random() - 0.5) * 40, -40 - Math.random() * 60, 2 + Math.random() * 6, 1.6 + Math.random() * 2.2);
      }
      this.embers.draw(ctx, dt, t, 30);
      ctx.globalCompositeOperation = "source-over";
    }
  };

  // ---- 4. The proof: measured speeds, replayed live; scrub to follow ------
  var proof = {
    init: function (sc) {
      var self = this;
      this.code = JSON.parse(sc.el.querySelector(".arc-code").textContent);
      this.lanes = [].map.call(sc.el.querySelectorAll(".arc-lane"), function (li) {
        return { li: li, rate: parseFloat(li.getAttribute("data-rate")), pre: li.querySelector(".arc-type"),
          tok: li.querySelector(".arc-tok"), num: li.querySelector(".arc-num"), chars: -1 };
      });
      this.range = sc.el.querySelector(".arc-scrub input");
      this.out = sc.el.querySelector(".arc-t");
      this.facts = [].map.call(sc.el.querySelectorAll(".arc-big"), function (b) {
        var m = b.textContent.match(/^(\D*)([\d.,]+)(.*)$/);
        return { el: b, pre: m[1], to: parseFloat(m[2].replace(",", ".")), dec: (m[2].split(/[.,]/)[1] || "").length, post: m[3], last: "" };
      });
      this.tsec = parseFloat(this.range.value);
      this.hold = 0; this.energy = 0;
      this.range.addEventListener("input", function () { self.scrub(parseFloat(self.range.value)); });
      var bench = sc.el.querySelector(".arc-lanes"), drag = false;
      function at(ev) {
        var r = bench.getBoundingClientRect();
        self.scrub(clamp((ev.clientX - r.left) / r.width, 0, 1) * 10);
      }
      bench.addEventListener("pointerdown", function (ev) { drag = true; at(ev); });
      addEventListener("pointermove", function (ev) { if (drag) at(ev); }, { passive: true });
      addEventListener("pointerup", function () { drag = false; });
      bench.style.touchAction = "pan-y";
      if (!reduce) this.render();
    },
    scrub: function (v) {
      this.energy = Math.min(1, this.energy + Math.abs(v - this.tsec) * 0.6);
      this.tsec = v; this.hold = 1.6; this.render();
    },
    render: function () {
      var code = this.code, L = code.length;
      for (var i = 0; i < this.lanes.length; i++) {
        var ln = this.lanes[i], tokens = ln.rate * this.tsec, chars = Math.floor(tokens * 4);
        if (chars === ln.chars) continue;
        ln.chars = chars;
        var end = chars % L, lap = Math.floor(chars / L);
        var text = (lap ? code.slice(end) : "") + code.slice(0, end); // the tail of what was written
        var lines = text.split("\n");
        ln.pre.textContent = lines.slice(-3).join("\n") + "▌";
        ln.tok.textContent = Math.round(tokens);
      }
      this.range.value = this.tsec.toFixed(1);
      this.out.textContent = fmt(this.tsec, 1) + " s";
    },
    resize: function () {},
    frame: function (sc, dt, t) {
      var p = sc.p, narrow = narrowMq.matches;
      if (this.hold > 0) this.hold -= dt;
      else { this.tsec = (this.tsec + dt) % 10; this.render(); }
      var k1 = ease((p - 0.02) / 0.28);
      for (var i = 0; i < this.lanes.length; i++) this.lanes[i].num.textContent = fmt(this.lanes[i].rate * k1, 1);
      var phase2 = narrow && p > 0.52;
      sc.el.classList.toggle("is-phase2", phase2);
      var f0 = narrow ? 0.56 : 0.3;
      for (var j = 0; j < this.facts.length; j++) {
        var f = this.facts[j], kf = ease((p - f0 - j * 0.08) / 0.22);
        var s = f.pre + (f.dec ? fmt(f.to * kf, f.dec) : Math.round(f.to * kf)) + f.post;
        if (s !== f.last) { f.el.textContent = s; f.last = s; }
      }
      // Concentration lines, as in a manga panel: they flare when you scrub.
      this.energy *= Math.pow(0.15, dt);
      var ctx = sc.ctx;
      ctx.clearRect(0, 0, sc.W, sc.H);
      var e = 0.05 + this.energy * 0.5;
      var bench = this.bench || (this.bench = sc.el.querySelector(".arc-bench"));
      var b = sc.local(bench), cx = b.x + b.w / 2, cy = b.y + b.h / 2;
      var R = Math.hypot(sc.W, sc.H), r0 = Math.max(b.w, b.h) * 0.62;
      ctx.strokeStyle = "rgba(239, 233, 224, 1)";
      var lines = coarse ? 48 : 90, seed = Math.floor(t * 12);
      var rr = rand(seed + 1);
      for (var l = 0; l < lines; l++) {
        var a = (l / lines) * Math.PI * 2 + rr() * 0.05;
        var inner = r0 * (0.95 + rr() * 0.4);
        ctx.globalAlpha = e * (0.25 + rr() * 0.75) * 0.5;
        ctx.lineWidth = 0.5 + rr() * 1.6;
        ctx.beginPath();
        ctx.moveTo(cx + Math.cos(a) * inner, cy + Math.sin(a) * inner);
        ctx.lineTo(cx + Math.cos(a) * R, cy + Math.sin(a) * R);
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    }
  };

  // ---- 5. Your turn: the embers you freed gather behind the call ---------
  var end = {
    init: function (sc) {
      var self = this;
      this.recap = sc.el.querySelector(".arc-recap");
      this.host = sc.el.querySelector(".arc-host");
      this.greeted = false;
      this.embers = new Embers(coarse ? 60 : 140);
      [].forEach.call(sc.el.querySelectorAll(".arc-ctas a"), function (a) {
        a.addEventListener("pointerenter", function () { self.burst(sc, a); });
        a.addEventListener("focus", function () { self.burst(sc, a); });
      });
    },
    burst: function (sc, a) {
      if (reduce) return;
      var r = sc.local(a);
      for (var i = 0; i < 18; i++) {
        var ang = Math.random() * Math.PI * 2, v = 40 + Math.random() * 90;
        this.embers.add(r.x + r.w / 2 + Math.cos(ang) * r.w * 0.4, r.y + r.h / 2 + Math.sin(ang) * r.h * 0.4,
          Math.cos(ang) * v, Math.sin(ang) * v - 30, 2 + Math.random() * 5, 0.8 + Math.random());
      }
    },
    resize: function () {},
    greet: function () {
      var v = swarm.video, host = this.host;
      this.greeted = true;
      swarm.rest();
      host.appendChild(v);
      v.classList.remove("on");
      v.style.transform = v.style.width = v.style.height = v.style.zIndex = "";
      v.onplaying = function () { if (v.parentNode === host) { v.classList.add("on"); host.classList.add("is-waving"); } };
      playOnce(v, "/media/personas/inari.webm");
    },
    release: function () { // the swarm takes the video back; Inari keeps the still
      this.host.classList.remove("is-waving");
    },
    update: function () {
      var n = freedCount;
      if (!n) { this.recap.hidden = true; return; }
      this.recap.hidden = false;
      this.recap.textContent = this.recap.getAttribute("data-say").replace("{n}", n);
    },
    frame: function (sc, dt, t) {
      var ctx = sc.ctx;
      ctx.clearRect(0, 0, sc.W, sc.H);
      if (this.lastN !== freedCount) { this.lastN = freedCount; this.update(); }
      if (!this.greeted && sc.p > 0.35) this.greet();
      // one ember per freed subscription per second, at least a few
      var rate = 3 + freedCount * 1.2;
      if (Math.random() < rate * dt) {
        this.embers.add(Math.random() * sc.W, sc.H + 10, (Math.random() - 0.5) * 20,
          -30 - Math.random() * 50, 3 + Math.random() * 8, 5 + Math.random() * 5);
      }
      var l = this.embers.list;
      if (sc.px > -1e3) for (var i = 0; i < l.length; i++) { // they lean toward the pointer
        var dx = sc.px - l[i].x, dy = sc.py - l[i].y, d = Math.hypot(dx, dy) || 1;
        if (d < 240) { l[i].vx += dx / d * 30 * dt; l[i].vy += dy / d * 30 * dt; }
      }
      ctx.globalCompositeOperation = "lighter";
      this.embers.draw(ctx, dt, t, 6);
      ctx.globalCompositeOperation = "source-over";
    }
  };

  // ---- The engine ---------------------------------------------------------
  var impls = { bill: bill, den: den, swarm: swarm, proof: proof, end: end };
  if (!reduce) arc.classList.add("is-live");
  var scenes = [].map.call(arc.querySelectorAll(".arc-scene"), function (el) {
    return new Scene(el, impls[el.getAttribute("data-scene")]);
  });

  function resizeAll() {
    DPR = Math.min(devicePixelRatio || 1, 2);
    VH = innerHeight;
    arc.style.setProperty("--vw", document.documentElement.clientWidth + "px");
    for (var i = 0; i < scenes.length; i++) scenes[i].resize();
  }
  var resizeQueued = 0;
  addEventListener("resize", function () {
    clearTimeout(resizeQueued);
    resizeQueued = setTimeout(resizeAll, 120);
  });
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(resizeAll);
  resizeAll();

  if (reduce) { // the static composition stays; only the controls answer
    end.update();
    return;
  }

  var running = false, raf = 0, last = 0, t0 = performance.now();
  function frame(now) {
    raf = 0;
    var dt = Math.min(0.05, (now - last) / 1000 || 0.016), t = (now - t0) / 1000, any = false;
    last = now;
    for (var i = 0; i < scenes.length; i++) {
      var s = scenes[i];
      if (!s.vis) continue;
      any = true;
      s.progress();
      s.impl.frame(s, dt, t);
    }
    if (any && running) raf = requestAnimationFrame(frame);
    else running = false;
  }
  function play() {
    if (running || document.hidden) return;
    running = true;
    last = performance.now();
    raf = requestAnimationFrame(frame);
  }
  function pause() {
    running = false;
    if (raf) cancelAnimationFrame(raf);
    raf = 0;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      for (var i = 0; i < scenes.length; i++) if (scenes[i].el === en.target) scenes[i].vis = en.isIntersecting;
    });
    for (var j = 0; j < scenes.length; j++) if (scenes[j].vis) return play();
    pause();
  });
  scenes.forEach(function (s) { io.observe(s.el); });
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) pause();
    else for (var j = 0; j < scenes.length; j++) if (scenes[j].vis) return play();
  });
})();
