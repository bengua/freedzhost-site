// The den: a cursor halo and a slight particle parallax. Cosmetic only; the page is complete without it.
(function () {
  var den = document.querySelector(".den");
  if (!den || matchMedia("(prefers-reduced-motion: reduce)").matches || matchMedia("(pointer: coarse)").matches) return;
  var x = 0, y = 0, queued = false;
  function paint() {
    queued = false;
    var s = den.style;
    s.setProperty("--mx", x + "px");
    s.setProperty("--my", y + "px");
    s.setProperty("--px", ((x / innerWidth - .5) * -16).toFixed(1) + "px");
    s.setProperty("--py", ((y / innerHeight - .5) * -16).toFixed(1) + "px");
  }
  addEventListener("pointermove", function (e) {
    x = e.clientX; y = e.clientY;
    if (!queued) { queued = true; requestAnimationFrame(paint); }
  }, { passive: true });
})();

// Scroll reveal: content blocks fade up as they enter, once, everywhere —
// IntersectionObserver, fade + translateY(16px), staggered 60 ms per batch.
// Skipped entirely under prefers-reduced-motion.
(function () {
  "use strict";
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!("IntersectionObserver" in window)) return;
  var targets = document.querySelectorAll("main h2, main h3, main p, main li, main figure, main .card, main pre");
  if (!targets.length) return;
  var seen = new WeakSet();
  var io = new IntersectionObserver(function (entries) {
    var batch = [];
    for (var i = 0; i < entries.length; i++) {
      if (entries[i].isIntersecting) { batch.push(entries[i].target); io.unobserve(entries[i].target); }
    }
    for (var j = 0; j < batch.length; j++) {
      batch[j].style.transitionDelay = (j * 60) + "ms";
      batch[j].classList.add("in-view");
    }
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.01 });
  for (var i = 0; i < targets.length; i++) {
    var el = targets[i];
    if (seen.has(el)) continue;
    seen.add(el);
    el.classList.add("will-reveal");
    io.observe(el);
  }
})();

// FoxBot's typing state: while an agent-worked section (the daily briefing,
// prepared by the swarm) is on screen, the mascot switches from breathing to
// typing. Cosmetic only; gated on motion preference.
(function () {
  "use strict";
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!("IntersectionObserver" in window)) return;
  var sections = document.querySelectorAll("[data-agent]");
  if (!sections.length) return;
  var visible = new Set();
  var io = new IntersectionObserver(function (entries) {
    for (var i = 0; i < entries.length; i++) {
      if (entries[i].isIntersecting) visible.add(entries[i].target);
      else visible.delete(entries[i].target);
    }
    document.body.classList.toggle("agent-on", visible.size > 0);
  }, { threshold: 0.2 });
  for (var i = 0; i < sections.length; i++) io.observe(sections[i]);
})();

// Series chips on the tutorials page: filter the groups, one tap, no reload.
(function () {
  "use strict";
  var chips = document.querySelectorAll(".chips .chip");
  if (!chips.length) return;
  for (var i = 0; i < chips.length; i++) {
    chips[i].addEventListener("click", function () {
      var key = this.getAttribute("data-series");
      for (var j = 0; j < chips.length; j++) chips[j].classList.toggle("on", chips[j] === this);
      var groups = document.querySelectorAll("[data-series]:not(.chip)");
      for (var k = 0; k < groups.length; k++) {
        var show = key === "*" || groups[k].getAttribute("data-series") === key;
        groups[k].classList.toggle("hidden", !show);
      }
    });
  }
})();
