(function () {
  var tabs = document.querySelectorAll(".tab");
  var panels = document.querySelectorAll("[data-panel]");
  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () {
      tabs.forEach(function (t) { t.setAttribute("aria-selected", t === tab); });
      panels.forEach(function (p) { p.hidden = p.dataset.panel !== tab.dataset.t; });
    });
  });
})();
