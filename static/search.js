// Progressive keyword search: the nav works without JS, this only filters it.
(function () {
  var cache = {};
  function load(url) {
    return cache[url] || (cache[url] = fetch(url).then(function (r) { return r.json(); }));
  }
  function norm(s) {
    return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  }
  document.querySelectorAll("form.search").forEach(function (form) {
    var input = form.querySelector("input");
    var list = form.querySelector(".results");
    var onTutos = form.closest("main") && document.querySelector("main .cards a[href]");
    function run() {
      var words = norm(input.value).split(/\s+/).filter(Boolean);
      load(form.dataset.index).then(function (index) {
        var hits = index.filter(function (e) {
          var hay = norm(e.title + " " + e.summary + " " + e.series);
          return words.every(function (w) { return hay.indexOf(w) >= 0; });
        });
        var urls = {};
        hits.forEach(function (e) { urls[e.url] = true; });
        if (onTutos) {
          document.querySelectorAll("main .cards li").forEach(function (li) {
            var a = li.querySelector("a");
            li.hidden = words.length > 0 && !urls[a.getAttribute("href")];
          });
        }
        list.textContent = "";
        if (!words.length || onTutos) { list.hidden = true; return; }
        list.hidden = false;
        hits.slice(0, 8).forEach(function (e) {
          var li = document.createElement("li"), a = document.createElement("a");
          a.href = e.url; a.textContent = e.title; li.appendChild(a); list.appendChild(li);
        });
        if (!hits.length) {
          var li = document.createElement("li"); li.textContent = form.dataset.none; list.appendChild(li);
        }
      });
    }
    input.addEventListener("input", run);
    form.addEventListener("submit", function (e) { if (onTutos) e.preventDefault(); });
  });
})();
