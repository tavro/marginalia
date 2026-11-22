(function () {
  "use strict";

  var data = {};
  try { data = JSON.parse(document.getElementById("previews").textContent); } catch (e) {}

  var pop = document.createElement("div");
  pop.className = "preview";
  pop.setAttribute("role", "tooltip");
  document.body.appendChild(pop);

  var showTimer = null, hideTimer = null, current = null;
  var canHover = window.matchMedia("(hover: hover)").matches;

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function fill(p) {
    pop.innerHTML =
      '<div class="preview-topic"><svg class="sym" aria-hidden="true"><use href="#sym-' + p.topic + '"/></svg>' +
      esc(p.topicName) + "</div>" +
      '<p class="preview-title">' + esc(p.title) + "</p>" +
      '<p class="preview-dek">' + esc(p.dek) + "</p>" +
      '<p class="preview-meta">' + esc(p.date) + " &middot; " + p.words.toLocaleString("en") +
      " words &middot; " + esc(p.confidence) + "</p>";
  }

  function place(a) {
    var r = a.getBoundingClientRect();
    var w = pop.offsetWidth, h = pop.offsetHeight;
    var x = Math.min(Math.max(8, r.left + window.scrollX), window.scrollX + document.documentElement.clientWidth - w - 8);
    var below = r.bottom + h + 14 < window.innerHeight;
    var y = below ? r.bottom + window.scrollY + 10 : r.top + window.scrollY - h - 10;
    pop.style.left = x + "px";
    pop.style.top = y + "px";
  }

  function open(a) {
    var p = data[a.getAttribute("data-preview")];
    if (!p) return;
    current = a;
    fill(p);
    place(a);
    pop.classList.add("is-open");
  }
  function close() { pop.classList.remove("is-open"); current = null; }

  if (canHover) {
    document.querySelectorAll("a[data-preview]").forEach(function (a) {
      a.addEventListener("mouseenter", function () {
        clearTimeout(hideTimer);
        showTimer = setTimeout(function () { open(a); }, 260);
      });
      a.addEventListener("mouseleave", function () {
        clearTimeout(showTimer);
        hideTimer = setTimeout(close, 180);
      });
      a.addEventListener("focus", function () { open(a); });
      a.addEventListener("blur", close);
    });
    pop.addEventListener("mouseenter", function () { clearTimeout(hideTimer); });
    pop.addEventListener("mouseleave", function () { hideTimer = setTimeout(close, 180); });
  }
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && current) close(); });

  var heads = Array.prototype.slice.call(document.querySelectorAll(".body h2[id]"));

  function currentIndex() {
    var y = window.scrollY + window.innerHeight * 0.3, idx = -1;
    for (var i = 0; i < heads.length; i++) if (heads[i].offsetTop <= y) idx = i;
    return idx;
  }

  document.addEventListener("keydown", function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var tag = (e.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea" || e.target.isContentEditable) return;
    if ((e.key === "j" || e.key === "k") && heads.length) {
      var idx = currentIndex();
      var t = e.key === "j" ? idx + 1 : idx - 1;
      if (t < 0) window.scrollTo({ top: 0 });
      else if (t < heads.length) heads[t].scrollIntoView({ block: "start" });
      e.preventDefault();
    }
  });
})();
