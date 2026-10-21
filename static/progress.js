/* Learning-maps progress: stored in this browser only (localStorage), no account, no tracker. */
(function () {
  "use strict";
  var KEY = "fh-progress";
  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function save(p) {
    try { localStorage.setItem(KEY, JSON.stringify(p)); } catch (e) { /* private mode: progress just won't persist */ }
  }
  var progress = load();

  /* Article pages: the "mark this step as done" toggle. */
  document.querySelectorAll(".step-done").forEach(function (btn) {
    var id = btn.dataset.series + "/" + btn.dataset.slug;
    function paint() {
      var done = !!progress[id];
      btn.classList.toggle("done", done);
      btn.textContent = done ? btn.dataset.marked : btn.dataset.label;
      btn.setAttribute("aria-pressed", done ? "true" : "false");
    }
    btn.addEventListener("click", function () {
      if (progress[id]) { delete progress[id]; } else { progress[id] = 1; }
      save(progress);
      paint();
    });
    paint();
  });

  /* Index: strike done cards and show the x/N counter of each learning map. */
  document.querySelectorAll("li[data-pc]").forEach(function (li) {
    if (progress[li.dataset.pc + "/" + li.dataset.slug]) { li.classList.add("done"); }
  });
  document.querySelectorAll(".pc-progress").forEach(function (el) {
    var key = el.dataset.pc;
    var lis = document.querySelectorAll('li[data-pc="' + key + '"]');
    if (!lis.length) { return; }
    var done = 0;
    lis.forEach(function (li) { if (progress[key + "/" + li.dataset.slug]) { done++; } });
    el.textContent = "· " + done + "/" + lis.length;
    if (done === lis.length) { el.classList.add("complete"); }
  });
})();
