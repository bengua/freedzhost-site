// The home hero: kitsunebi (fox-fire) embers on canvas, Inari's nine tails on
// springs, a scripted entrance under 2.5 s, and a soft scroll parallax.
// Without script, or under prefers-reduced-motion, the hero is already a
// finished static composition — this file only ever enhances it.
(function () {
  "use strict";
  var hero = document.querySelector(".hero");
  if (!hero) return;

  // The mascot still and its name tag are the final state, so they are set
  // BEFORE the reduced-motion return: the page is complete without motion.
  // ONE teammate per page load, picked at random (the title-screen rotation).
  var mascot = hero.querySelector(".hero-mascot");
  var tag = hero.querySelector(".hero-anchor-tag");
  var teamEl = hero.querySelector(".hero-team");
  var team = teamEl ? JSON.parse(teamEl.textContent) : [];
  if (mascot && team.length) {
    var pick = team[(Math.random() * team.length) | 0];
    mascot.src = "/media/personas/" + pick[0] + ".webp";
    if (tag) { tag.textContent = pick[1]; tag.classList.add("on"); }
  }

  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var canvas = hero.querySelector(".hero-embers");
  var ctx = canvas.getContext("2d");
  var svg = hero.querySelector(".hero-inari");
  var title = hero.querySelector(".hero-title");
  var coarse = matchMedia("(pointer: coarse)").matches;
  var t0 = performance.now();

  // The title is split into letters for the entrance stagger; the H1 keeps
  // its full text content, so assistive technologies read it unchanged.
  var text = title.textContent;
  title.textContent = "";
  title.setAttribute("aria-label", text);
  for (var i = 0; i < text.length; i++) {
    var letter = document.createElement("span");
    letter.className = "hl";
    letter.setAttribute("aria-hidden", "true");
    letter.textContent = text[i];
    letter.style.setProperty("--d", 150 + i * 65 + "ms");
    title.appendChild(letter);
  }
  hero.classList.add("is-live");

  // The entrance can be skipped instantly: the first scroll, touch, key or
  // click removes the live state, and the plain-DOM final state takes over.
  var settled = false;
  function settle() {
    if (settled) return;
    settled = true;
    hero.classList.remove("is-live");
    for (var j = 0; j < embers.length; j++) embers[j].born = 0;
    removeEventListener("wheel", settle);
    removeEventListener("touchstart", settle);
    removeEventListener("keydown", settle);
    removeEventListener("pointerdown", settle);
  }
  addEventListener("wheel", settle, { passive: true });
  addEventListener("touchstart", settle, { passive: true });
  addEventListener("keydown", settle);
  addEventListener("pointerdown", settle);
  setTimeout(settle, 3200); // the show is over: nothing may linger half-drawn

  // Ember glows are pre-rendered once on small offscreen canvases: drawing a
  // sprite with drawImage is far cheaper than a radial gradient per particle.
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
    glowSprite("rgba(255, 224, 176, 1)", "rgba(224, 122, 47, .55)"),  // pale gold
    glowSprite("rgba(255, 178, 102, 1)", "rgba(224, 122, 47, .5)"),   // copper
    glowSprite("rgba(240, 152, 79, 1)", "rgba(150, 70, 20, .5)")      // deep ember
  ];

  var W = 0, H = 0, DPR = 1;
  var foxZone = null; // the fox's aura: a third of the embers rise around Inari
  function resize() {
    DPR = Math.min(devicePixelRatio || 1, 2);
    W = hero.clientWidth;
    H = hero.clientHeight;
    canvas.width = Math.round(W * DPR);
    canvas.height = Math.round(H * DPR);
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    if (svg) {
      var cr = canvas.getBoundingClientRect(), fr = svg.getBoundingClientRect();
      foxZone = { x: fr.left - cr.left - 30, y: fr.top - cr.top - 30, w: fr.width + 60, h: fr.height + 60 };
    } else {
      foxZone = null; // no cutout fox: the embers drift over the whole key art
    }
  }
  resize();
  addEventListener("resize", resize);

  // One ember: a slow rising drift, a sine wander, a flicker, a life cycle.
  var COUNT = coarse ? 50 : 150;
  var embers = [];
  function spawn(e, first) {
    if (foxZone && Math.random() < 0.33) {
      e.x = foxZone.x + Math.random() * foxZone.w;
      e.y = first ? foxZone.y + Math.random() * foxZone.h : foxZone.y + foxZone.h * (0.5 + Math.random() * 0.5);
    } else {
      e.x = Math.random() * W;
      e.y = first ? Math.random() * H : H + 12;
    }
    e.vx = 0;
    e.vy = -(0.18 + Math.random() * 0.35);
    e.size = 3 + Math.random() * 9;
    e.tone = TONES[(Math.random() * TONES.length) | 0];
    e.phase = Math.random() * Math.PI * 2;
    e.freq = 0.6 + Math.random() * 1.8;
    e.wander = 0.3 + Math.random() * 0.9;
    e.life = 0;
    e.span = 7 + Math.random() * 9; // seconds before it fades and respawns
    return e;
  }
  for (var k = 0; k < COUNT; k++) {
    var e = spawn({}, true);
    e.born = t0 + k * 8; // the first embers light one by one
    embers.push(e);
  }
  // A few large, slow wisps give the field its depth.
  var wisps = [];
  for (var w = 0; w < (coarse ? 3 : 7); w++) {
    var wisp = spawn({}, true);
    wisp.size = 30 + Math.random() * 34;
    wisp.vy = -(0.05 + Math.random() * 0.08);
    wisp.alpha = 0.10;
    wisps.push(wisp);
  }

  // The pointer, in hero pixels; on touch it fades shortly after the tap.
  var px = -9999, py = -9999, pUntil = 0;
  function onPointer(ev) {
    var r = canvas.getBoundingClientRect();
    px = ev.clientX - r.left;
    py = ev.clientY - r.top;
    pUntil = performance.now() + (ev.pointerType === "touch" ? 1500 : 8000);
  }
  hero.addEventListener("pointermove", onPointer, { passive: true });
  hero.addEventListener("pointerdown", onPointer, { passive: true });
  hero.addEventListener("pointerleave", function () { pUntil = 0; }, { passive: true });

  // Tapping the fox (the vector silhouette when present, the key art otherwise)
  // is pure play: an ember burst at the tap and a wag of the nine tails.
  var bursts = [];
  var burstTarget = svg || hero.querySelector(".hero-art");
  if (burstTarget) {
    burstTarget.style.pointerEvents = "auto";
    burstTarget.addEventListener("pointerdown", function (ev) {
      var cr = canvas.getBoundingClientRect();
      var bx = ev.clientX - cr.left, by = ev.clientY - cr.top;
      for (var bi = 0; bi < 14; bi++) {
        var ang = (bi / 14) * Math.PI * 2 + Math.random() * 0.4;
        bursts.push({ x: bx, y: by,
          vx: Math.cos(ang) * (40 + Math.random() * 70),
          vy: Math.sin(ang) * (40 + Math.random() * 70) - 30,
          size: 4 + Math.random() * 7, tone: TONES[(Math.random() * TONES.length) | 0],
          life: 0, span: 0.7 + Math.random() * 0.5 });
      }
      for (var si = 0; si < springs.length; si++) springs[si].vel += (si % 2 ? 1 : -1) * (16 + si * 2);
    }, { passive: true });
  }

  // Inari's tails: a light spring per tail, a breathing sway plus a shy
  // retreat when the pointer comes near the tail tips. Without the vector
  // silhouette (key-art hero) there are no springs — the art carries the fox.
  var tails = svg ? svg.querySelectorAll(".inari-tail") : [];
  var TIPS = [[253, 309], [317, 245], [404, 201], [504, 190], [602, 217],
              [682, 279], [731, 365], [747, 457], [731, 532]];
  var springs = [];
  for (var ti = 0; ti < tails.length; ti++) {
    tails[ti].style.transformOrigin = "414px 570px";
    springs.push({ angle: 0, vel: 0, phase: ti * 0.7, tip: TIPS[ti] || TIPS[0] });
  }

  function svgPoint(clientX, clientY) {
    var r = svg.getBoundingClientRect();
    var scale = Math.min(r.width / 720, r.height / 720);
    var ox = r.left + (r.width - 720 * scale) / 2;
    var oy = r.top + (r.height - 720 * scale); // xMidYMax: grounded at the bottom
    return [(clientX - ox) / scale, (clientY - oy) / scale];
  }

  var running = false, raf = 0, last = 0;
  function frame(now) {
    raf = running ? requestAnimationFrame(frame) : 0;
    var dt = Math.min(0.05, (now - last) / 1000 || 0.016);
    last = now;
    var t = (now - t0) / 1000;
    var pLive = now < pUntil;

    ctx.clearRect(0, 0, W, H);
    ctx.globalCompositeOperation = "lighter";

    var i, p, dx, dy, d, f;
    for (i = 0; i < wisps.length; i++) {
      p = wisps[i];
      p.x += Math.sin(t * 0.3 + p.phase) * 0.15;
      p.y += p.vy;
      if (p.y < -p.size) { spawn(p, false); p.size = 30 + Math.random() * 34; p.alpha = 0.10; }
      ctx.globalAlpha = p.alpha * (0.7 + 0.3 * Math.sin(t * p.freq + p.phase));
      ctx.drawImage(p.tone, p.x - p.size, p.y - p.size, p.size * 2, p.size * 2);
    }
    for (i = 0; i < embers.length; i++) {
      p = embers[i];
      if (now < p.born) continue;
      p.life += dt;
      if (p.life > p.span || p.y < -14) { spawn(p, false); }
      // pointer: a gentle pull from afar, a shy push when close
      if (pLive) {
        dx = px - p.x; dy = py - p.y;
        d = Math.sqrt(dx * dx + dy * dy) || 1;
        if (d < 90) { f = (90 - d) / 90 * 26; p.vx -= dx / d * f * dt; p.vy -= dy / d * f * dt; }
        else if (d < 260) { f = (1 - d / 260) * 7; p.vx += dx / d * f * dt; p.vy += dy / d * f * dt; }
      }
      p.vx *= 0.965; p.vy = p.vy * 0.985 - 0.012; // damping, then the rise wins
      p.x += (p.vx + Math.sin(t * p.wander + p.phase) * 0.22) * dt * 60;
      p.y += p.vy * dt * 60;
      var fade = Math.min(1, p.life / 1.2) * Math.max(0, 1 - p.life / p.span);
      var flicker = 0.55 + 0.45 * Math.sin(t * p.freq * 3 + p.phase);
      ctx.globalAlpha = fade * flicker * 0.9;
      ctx.drawImage(p.tone, p.x - p.size, p.y - p.size, p.size * 2, p.size * 2);
    }
    for (i = bursts.length - 1; i >= 0; i--) {
      p = bursts[i];
      p.life += dt;
      if (p.life > p.span) { bursts.splice(i, 1); continue; }
      p.vx *= 0.94; p.vy = p.vy * 0.94 + 90 * dt;
      p.x += p.vx * dt; p.y += p.vy * dt;
      ctx.globalAlpha = (1 - p.life / p.span) * 0.95;
      ctx.drawImage(p.tone, p.x - p.size, p.y - p.size, p.size * 2, p.size * 2);
    }
    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = "source-over";

    // Tails: spring toward the sway target, plus the pointer shyness.
    if (tails.length) {
      var sp = pLive ? svgPoint(px + canvas.getBoundingClientRect().left,
                                py + canvas.getBoundingClientRect().top) : null;
      for (i = 0; i < springs.length; i++) {
        var s = springs[i];
        var target = Math.sin(t * 0.8 + s.phase) * 2.1;
        if (sp) {
          dx = s.tip[0] - sp[0]; dy = s.tip[1] - sp[1];
          d = Math.sqrt(dx * dx + dy * dy);
          if (d < 240) target += (dx >= 0 ? 1 : -1) * (1 - d / 240) * 5.5;
        }
        var acc = (target - s.angle) * 22 - s.vel * 7;
        s.vel += acc * dt;
        s.angle += s.vel * dt;
        tails[i].style.transform = "rotate(" + s.angle.toFixed(2) + "deg)";
      }
    }
  }
  function play() {
    if (running) return;
    running = true;
    last = performance.now();
    raf = requestAnimationFrame(frame);
  }
  function pause() {
    running = false;
    if (raf) cancelAnimationFrame(raf);
    raf = 0;
  }

  // No work offscreen: the loop stops when the hero leaves the viewport or
  // the page is hidden, and resumes when it comes back.
  var inView = true;
  new IntersectionObserver(function (entries) {
    inView = entries[0].isIntersecting;
    inView && !document.hidden ? play() : pause();
  }).observe(hero);
  document.addEventListener("visibilitychange", function () {
    document.hidden ? pause() : (inView && play());
  });
  play();

  // The parallax: hero layers drift at different speeds while it scrolls away.
  var scQueued = false;
  function onScroll() {
    if (scQueued) return;
    scQueued = true;
    requestAnimationFrame(function () {
      scQueued = false;
      var p = Math.min(1, Math.max(0, scrollY / (H || 1)));
      hero.style.setProperty("--sc", p.toFixed(3));
    });
  }
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();
