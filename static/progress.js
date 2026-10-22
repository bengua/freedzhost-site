// Learning-path progress: checkbox state lives in localStorage["fh-progress"]. The track works without JS.
(function () {
  var KEY = "fh-progress", state = {};
  try { state = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) {}
  function save() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }
  document.querySelectorAll(".parcours").forEach(function (path) {
    var steps = path.querySelectorAll("li[data-step]");
    var bar = path.querySelector("progress"), count = path.querySelector(".count");
    var id = location.pathname.replace(/^\/fr\//, "/");
    var done = state[id] = state[id] || [];
    function refresh() {
      steps.forEach(function (li) {
        var on = done.indexOf(li.dataset.step) >= 0;
        li.querySelector("input").checked = on;
        li.classList.toggle("done", on);
      });
      bar.value = done.length;
      count.textContent = done.length + " / " + steps.length;
    }
    steps.forEach(function (li) {
      li.querySelector("input").addEventListener("change", function (e) {
        var s = li.dataset.step, i = done.indexOf(s);
        if (e.target.checked && i < 0) done.push(s);
        if (!e.target.checked && i >= 0) done.splice(i, 1);
        save(); refresh();
      });
    });
    bar.hidden = count.hidden = false;
    refresh();
  });
})();
