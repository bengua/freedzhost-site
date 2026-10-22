// Campus progress: the whole state lives in this browser (localStorage), nothing is sent anywhere.
// XP come from steps done (by tutorial level) and from proofs: a command output pasted and checked
// here against the step's pattern. Data and strings come from /campus-<lang>.json (see site_build.py).
(function () {
  "use strict";
  var KEY = "fh-progress";
  var lang = document.documentElement.lang === "fr" ? "fr" : "en";
  var C = null;
  var state = load();

  function blank() { return { v: 2, steps: {}, proofs: {} }; }

  function clean(raw) {
    // Accept a v2 state (or a v1 one: {pathname: [step ids]}) and keep only well-formed entries.
    var s = blank();
    if (!raw || typeof raw !== "object") return s;
    if (raw.v !== 2) {
      Object.keys(raw).forEach(function (path) {
        if (Array.isArray(raw[path])) raw[path].forEach(function (id) {
          if (typeof id === "string" && /^[a-z0-9-]{1,60}$/.test(id)) s.steps[id] = { at: "" };
        });
      });
      return s;
    }
    var slug = /^[a-z0-9-]{1,60}$/;
    Object.keys(raw.steps || {}).forEach(function (k) {
      if (slug.test(k)) s.steps[k] = { at: String((raw.steps[k] || {}).at || "").slice(0, 40) };
    });
    Object.keys(raw.proofs || {}).forEach(function (k) {
      var p = raw.proofs[k] || {};
      if (!slug.test(k)) return;
      s.proofs[k] = {
        at: String(p.at || "").slice(0, 40),
        line: String(p.line || "").slice(0, 160),
        hash: /^[0-9a-f]{64}$/.test(p.hash || "") ? p.hash : ""
      };
    });
    return s;
  }

  function load() {
    try { return clean(JSON.parse(localStorage.getItem(KEY) || "null")); } catch (e) { return blank(); }
  }

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* private mode: progress lasts the visit */ }
  }

  function fill(text, vars) {
    return text.replace(/\{(\w+)\}/g, function (m, k) { return vars[k] !== undefined ? vars[k] : m; });
  }

  function done(slug) { return !!(state.steps[slug] || state.proofs[slug]); }

  function score() {
    var xp = 0, steps = 0;
    Object.keys(C.steps).forEach(function (s) {
      if (done(s)) { xp += C.steps[s].xp; steps += 1; }
    });
    C.badges.forEach(function (b) { if (b.step && state.proofs[b.step]) xp += b.xp; });
    var lv = C.levels[0], next = null;
    C.levels.forEach(function (l) { if (xp >= l.xp) lv = l; else if (!next) next = l; });
    return { xp: xp, steps: steps, level: lv, next: next };
  }

  function when(at) {
    if (!at) return "—";
    var d = new Date(at);
    return isNaN(d) ? at : d.toLocaleDateString(lang, { year: "numeric", month: "long", day: "numeric" });
  }

  function chip(sc, pulse) {
    document.querySelectorAll("[data-chip]").forEach(function (a) {
      a.querySelector("[data-chip-text]").textContent = C.t.lv + " " + sc.level.n + " · " + sc.xp + " XP";
      a.setAttribute("aria-label", fill(C.t.chip_aria, { level: sc.level.n, xp: sc.xp }));
      if (pulse) { a.classList.remove("pulse"); void a.offsetWidth; a.classList.add("pulse"); }
    });
  }

  function seals(root) {
    root.querySelectorAll("[data-badge]").forEach(function (li) {
      var b = C.badges.filter(function (x) { return x.id === li.dataset.badge; })[0];
      var got = !!(b && b.step && state.proofs[b.step]);
      li.classList.toggle("earned", got);
      var st = li.querySelector("[data-state]");
      if (st) st.textContent = got ? C.t.earned : C.t.to_earn;
      var view = li.querySelector(".proof-view");
      if (view) {
        view.hidden = !got;
        if (got) {
          var p = state.proofs[b.step];
          view.querySelector("[data-at]").textContent = when(p.at);
          view.querySelector("[data-line]").textContent = p.line || "—";
          view.querySelector("[data-hash]").textContent = p.hash || "—";
        }
      }
    });
  }

  function paths() {
    document.querySelectorAll(".parcours").forEach(function (path) {
      var items = path.querySelectorAll("li[data-step]");
      var count = 0, xp = 0;
      items.forEach(function (li) {
        var s = li.dataset.step, box = li.querySelector("input[type=checkbox]");
        var proven = !!state.proofs[s], on = done(s);
        box.checked = on;
        box.disabled = proven;
        li.classList.toggle("done", on);
        li.classList.toggle("proven", proven);
        if (on) { count += 1; if (C && C.steps[s]) xp += C.steps[s].xp; }
        var proof = li.querySelector(".proof");
        if (proof && C) {
          proof.hidden = false;
          proof.querySelector(".unlocked").hidden = !proven;
          if (proven && !proof.querySelector(".verdict").textContent) {
            proof.querySelector(".verdict").textContent = C.t.proved_on + " " + when(state.proofs[s].at);
          }
        }
      });
      if (C) C.badges.forEach(function (b) {
        if (b.step && state.proofs[b.step] && path.querySelector('li[data-step="' + b.step + '"]')) xp += b.xp;
      });
      var bar = path.querySelector("progress"), label = path.querySelector(".count");
      bar.hidden = false;
      bar.value = count;
      label.hidden = false;
      label.textContent = count + " / " + items.length;
      path.style.setProperty("--done", items.length ? count / items.length : 0);
      var quest = document.querySelector(".quest");
      if (quest && C) {
        quest.querySelector(".quest-xp").hidden = false;
        quest.querySelector("[data-quest-xp]").textContent = xp;
        seals(quest);
      }
    });
  }

  function profile(sc) {
    var box = document.querySelector("[data-score]");
    if (!box) return;
    box.hidden = false;
    box.querySelector("[data-level-n]").textContent = sc.level.n;
    box.querySelector("[data-level-name]").textContent = sc.level.name;
    box.querySelector("[data-xp]").textContent = sc.xp;
    box.querySelector("[data-steps]").textContent = sc.steps;
    var bar = box.querySelector("[data-next-bar]"), next = box.querySelector("[data-next]");
    if (sc.next) {
      bar.max = sc.next.xp - sc.level.xp;
      bar.value = sc.xp - sc.level.xp;
      next.textContent = fill(C.t.next, { n: sc.next.xp - sc.xp, level: sc.next.n, name: sc.next.name });
    } else {
      bar.max = 1; bar.value = 1;
      next.textContent = C.t.top;
    }
    seals(document);
    var any = false;
    document.querySelectorAll("[data-tips-step]").forEach(function (sec) {
      sec.hidden = !state.proofs[sec.dataset.tipsStep];
      any = any || !sec.hidden;
    });
    var none = document.querySelector("[data-tips-none]");
    if (none) none.hidden = any;
    document.querySelectorAll("[data-level]").forEach(function (li) {
      var n = +li.dataset.level;
      li.classList.toggle("reached", n <= sc.level.n);
      if (n === sc.level.n) li.setAttribute("aria-current", "step"); else li.removeAttribute("aria-current");
    });
    var saveBox = document.querySelector("[data-save]");
    if (saveBox) saveBox.hidden = false;
  }

  function render(pulse) {
    paths();
    if (!C) return;
    var sc = score();
    chip(sc, pulse);
    profile(sc);
    return sc;
  }

  function announce(msg) {
    var out = document.querySelector(".quest-status");
    if (out) out.textContent = msg;
  }

  function change(before, after, extra) {
    // One calm sentence: what was gained, and a level when one is reached. No sound, no confetti.
    var diff = after.xp - before.xp, msg = extra || "";
    if (!extra && diff) msg = fill(diff > 0 ? C.t.gained : C.t.lost, { xp: Math.abs(diff) });
    if (after.level.n > before.level.n) msg += " " + fill(C.t.level_up, { level: after.level.n, name: after.level.name });
    return msg.trim();
  }

  function sha256(text) {
    if (!(window.crypto && crypto.subtle && window.TextEncoder)) return Promise.resolve("");
    return crypto.subtle.digest("SHA-256", new TextEncoder().encode(text)).then(function (buf) {
      return Array.prototype.map.call(new Uint8Array(buf), function (b) { return ("0" + b.toString(16)).slice(-2); }).join("");
    }, function () { return ""; });
  }

  function check(li) {
    var s = li.dataset.step, step = C.steps[s], proof = li.querySelector(".proof");
    var verdict = proof.querySelector(".verdict");
    var text = proof.querySelector("textarea").value.slice(0, 20000);
    var m = null;
    try { m = step && step.pattern ? new RegExp(step.pattern, "im").exec(text) : null; } catch (e) { m = null; }
    if (!m) { verdict.textContent = fill(C.t.ko, { hint: step ? step.hint : "" }); return; }
    var start = text.lastIndexOf("\n", m.index) + 1, end = text.indexOf("\n", m.index);
    var line = text.slice(start, end < 0 ? undefined : end).trim().slice(0, 160);
    sha256(text).then(function (hash) {
      var before = score();
      var at = new Date().toISOString();
      state.proofs[s] = { at: at, line: line, hash: hash };
      if (!state.steps[s]) state.steps[s] = { at: at };
      save();
      var after = render(true);
      verdict.textContent = fill(C.t.ok, { xp: after.xp - before.xp });
      announce(change(before, after));
    });
  }

  function bind() {
    document.querySelectorAll(".parcours li[data-step]").forEach(function (li) {
      var box = li.querySelector("input[type=checkbox]");
      box.addEventListener("change", function () {
        var before = C ? score() : null;
        if (box.checked) state.steps[li.dataset.step] = { at: new Date().toISOString() };
        else delete state.steps[li.dataset.step];
        save();
        var after = render(box.checked);
        if (before && after) announce(change(before, after));
      });
      var btn = li.querySelector("[data-check]");
      if (btn) btn.addEventListener("click", function () { if (C) check(li); });
    });
    var exp = document.querySelector("[data-export]");
    if (exp) exp.addEventListener("click", function () {
      var data = { format: "freedzhost-progress", v: 2, exported: new Date().toISOString(), steps: state.steps, proofs: state.proofs };
      var a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
      a.download = "freedzhost-progress.json";
      document.body.appendChild(a);
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
    });
    var imp = document.querySelector("[data-import]"), status = document.querySelector("[data-save-status]");
    if (imp) imp.addEventListener("change", function () {
      var file = imp.files && imp.files[0];
      if (!file || !C) return;
      file.text().then(function (txt) {
        var raw = JSON.parse(txt);
        if (!raw || raw.format !== "freedzhost-progress") throw new Error("format");
        state = clean(raw);
        save();
        render(true);
        status.textContent = C.t.import_ok;
      }).catch(function () { status.textContent = C.t.import_ko; });
      imp.value = "";
    });
    var reset = document.querySelector("[data-reset]");
    if (reset) reset.addEventListener("click", function () {
      if (!C || !window.confirm(C.t.reset_confirm)) return;
      state = blank();
      save();
      render(false);
    });
    window.addEventListener("storage", function (e) {
      if (e.key === KEY) { state = load(); render(false); }
    });
  }

  render(false);
  bind();
  fetch("/campus-" + lang + ".json").then(function (r) { return r.json(); }).then(function (data) {
    C = data;
    render(false);
  }).catch(function () { /* without the data, the checkboxes still count */ });
})();
