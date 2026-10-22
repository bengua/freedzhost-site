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
