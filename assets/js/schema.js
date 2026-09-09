(function () {
  var DATA_URL = "assets/data/parts-tree.json";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var state = {
    data: null,
    mode: "still",
    layer: "still-overview",
    selectedId: null,
    stack: [],
  };

  var els = {
    svg: document.getElementById("schema-svg"),
    wrap: document.getElementById("schema-canvas-wrap"),
    tooltip: document.getElementById("schema-tooltip"),
    panel: document.getElementById("schema-panel"),
    crumb: document.getElementById("schema-crumb"),
    list: document.getElementById("parts-list"),
    lead: document.getElementById("mode-lead"),
    modeBtns: document.querySelectorAll(".mode-switch__btn"),
  };

  if (!els.svg || !els.panel) return;

  function node(id) {
    return state.data && state.data.nodes ? state.data.nodes[id] : null;
  }

  function modeMeta() {
    return (state.data.modes || []).find(function (m) {
      return m.id === state.mode;
    });
  }

  function pad(s) {
    s = String(s);
    return s.length === 1 ? "0" + s : s;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, "&#39;");
  }

  function setLayer(layerId, withZoom) {
    state.layer = layerId;
    document.querySelectorAll(".schema-layer").forEach(function (g) {
      g.classList.toggle("is-active", g.getAttribute("data-layer") === layerId);
    });
    if (els.svg && withZoom && !reduceMotion) {
      els.svg.classList.add("is-zoom");
      window.setTimeout(function () {
        els.svg.classList.remove("is-zoom");
      }, 450);
    }
    renderList();
    renderCrumb();
  }

  function renderPanel(n) {
    var sku = n.skuId
      ? '<span class="schema-panel__sku">SKU ' + pad(n.skuId) + "</span>"
      : '<span class="schema-panel__sku">Узел</span>';
    var facts = (n.facts || [])
      .map(function (f) {
        return "<li>" + escapeHtml(f) + "</li>";
      })
      .join("");
    var actions = [];
    if (n.skuId) {
      actions.push(
        '<a class="btn btn--primary btn--sm" href="index.html#sku-' +
          pad(n.skuId) +
          '">Карточка товара</a>'
      );
      actions.push('<a class="btn btn--ghost btn--sm" href="index.html#catalog">В каталог</a>');
    }
    if (n.drillLayer) {
      actions.push(
        '<button type="button" class="btn btn--ghost btn--sm" data-drill="' +
          escapeAttr(n.id) +
          '">Открыть внутри</button>'
      );
    }
    var hint = n.drillLayer
      ? '<p class="schema-panel__hint">Сборка: «Открыть внутри», повторный тап или двойной клик.</p>'
      : "";

    els.panel.classList.remove("is-empty");
    els.panel.innerHTML =
      sku +
      "<h2>" +
      escapeHtml(n.name) +
      "</h2>" +
      "<p>" +
      escapeHtml(n.description || "") +
      "</p>" +
      (facts ? '<ul class="schema-panel__facts">' + facts + "</ul>" : "") +
      (actions.length
        ? '<div class="schema-panel__actions">' + actions.join("") + "</div>"
        : "") +
      hint;

    var drillBtn = els.panel.querySelector("[data-drill]");
    if (drillBtn) {
      drillBtn.addEventListener("click", function () {
        selectPart(drillBtn.getAttribute("data-drill"), { drill: true });
      });
    }
  }

  function renderList() {
    if (!els.list) return;
    var ids = [];
    document.querySelectorAll(".schema-layer.is-active .hotspot[data-part]").forEach(function (h) {
      var id = h.getAttribute("data-part");
      if (ids.indexOf(id) === -1) ids.push(id);
    });
    els.list.innerHTML = ids
      .map(function (id) {
        var n = node(id);
        if (!n) return "";
        var sku = n.skuId ? "SKU " + pad(n.skuId) : "узел";
        var active = id === state.selectedId ? " is-active" : "";
        return (
          '<li><button type="button" class="parts-list__btn' +
          active +
          '" data-part="' +
          escapeAttr(id) +
          '"><span>' +
          escapeHtml(n.name) +
          "</span><span>" +
          escapeHtml(sku) +
          "</span></button></li>"
        );
      })
      .join("");
  }

  function renderCrumb() {
    if (!els.crumb) return;
    var mode = modeMeta();
    var parts = [{ label: mode ? mode.short || mode.name : "Аппарат", action: "root" }];

    state.stack.forEach(function (s, i) {
      var n = node(s.id);
      parts.push({ label: n ? n.name : s.id, action: "stack", index: i });
    });

    if (state.selectedId) {
      var cur = node(state.selectedId);
      var last = parts[parts.length - 1];
      if (!last || last.label !== (cur && cur.name)) {
        parts.push({ label: cur ? cur.name : state.selectedId, action: null });
      }
    }

    els.crumb.innerHTML = parts
      .map(function (p, i) {
        var sep = i ? '<span class="schema-crumb__sep" aria-hidden="true">›</span>' : "";
        if (p.action === "root") {
          return sep + '<button type="button" data-crumb="root">' + escapeHtml(p.label) + "</button>";
        }
        if (p.action === "stack") {
          return (
            sep +
            '<button type="button" data-crumb="stack" data-index="' +
            p.index +
            '">' +
            escapeHtml(p.label) +
            "</button>"
          );
        }
        return sep + '<span class="schema-crumb__current">' + escapeHtml(p.label) + "</span>";
      })
      .join("");
  }

  function selectPart(id, opts) {
    opts = opts || {};
    var n = node(id);
    if (!n) return;

    if (opts.drill && n.drillLayer) {
      state.stack.push({ layer: state.layer, id: id });
      state.selectedId = id;
      setLayer(n.drillLayer, true);
      renderPanel(n);
      document.querySelectorAll(".hotspot").forEach(function (h) {
        h.classList.toggle("is-selected", h.getAttribute("data-part") === id);
      });
      return;
    }

    state.selectedId = id;
    document.querySelectorAll(".hotspot").forEach(function (h) {
      h.classList.toggle("is-selected", h.getAttribute("data-part") === id);
    });
    renderPanel(n);
    renderList();
    renderCrumb();
  }

  function goRoot() {
    state.stack = [];
    state.selectedId = null;
    setLayer(state.mode === "brew" ? "brew-overview" : "still-overview", false);
    els.panel.classList.add("is-empty");
    els.panel.innerHTML =
      '<span class="schema-panel__sku">Узел</span><h2>Выберите деталь на схеме</h2><p>Наведите или коснитесь узла. Сборки открывают следующий слой.</p>';
    document.querySelectorAll(".hotspot").forEach(function (h) {
      h.classList.remove("is-selected", "is-hover");
    });
  }

  function goStack(index) {
    var target = state.stack[index];
    if (!target) return;
    state.stack = state.stack.slice(0, index);
    setLayer(target.layer, false);
    selectPart(target.id, { drill: false });
  }

  function showTooltip(name, clientX, clientY) {
    if (!els.tooltip || !els.wrap) return;
    var rect = els.wrap.getBoundingClientRect();
    els.tooltip.textContent = name;
    els.tooltip.style.left = clientX - rect.left + "px";
    els.tooltip.style.top = clientY - rect.top + "px";
    els.tooltip.classList.add("is-on");
  }

  function hideTooltip() {
    if (els.tooltip) els.tooltip.classList.remove("is-on");
  }

  function bindHotspots() {
    els.svg.addEventListener("pointerover", function (e) {
      var hs = e.target.closest(".hotspot");
      if (!hs || !els.svg.contains(hs)) return;
      var n = node(hs.getAttribute("data-part"));
      hs.classList.add("is-hover");
      if (n) showTooltip(n.name, e.clientX, e.clientY);
    });

    els.svg.addEventListener("pointermove", function (e) {
      if (!els.tooltip.classList.contains("is-on")) return;
      var hs = e.target.closest(".hotspot");
      if (!hs) return;
      var n = node(hs.getAttribute("data-part"));
      if (n) showTooltip(n.name, e.clientX, e.clientY);
    });

    els.svg.addEventListener("pointerout", function (e) {
      var hs = e.target.closest(".hotspot");
      if (!hs) return;
      var related =
        e.relatedTarget && e.relatedTarget.closest ? e.relatedTarget.closest(".hotspot") : null;
      if (related === hs) return;
      hs.classList.remove("is-hover");
      hideTooltip();
    });

    els.svg.addEventListener("click", function (e) {
      var hs = e.target.closest(".hotspot");
      if (!hs || !els.svg.contains(hs)) return;
      var id = hs.getAttribute("data-part");
      var n = node(id);
      hideTooltip();
      if (n && n.drillLayer && state.selectedId === id) {
        selectPart(id, { drill: true });
      } else {
        selectPart(id, { drill: false });
      }
    });

    els.svg.addEventListener("dblclick", function (e) {
      var hs = e.target.closest(".hotspot");
      if (!hs) return;
      e.preventDefault();
      selectPart(hs.getAttribute("data-part"), { drill: true });
    });

    els.svg.addEventListener("keydown", function (e) {
      var hs = e.target.closest(".hotspot");
      if (!hs) return;
      if (e.key !== "Enter" && e.key !== " ") return;
      e.preventDefault();
      var id = hs.getAttribute("data-part");
      var n = node(id);
      if (n && n.drillLayer && state.selectedId === id) {
        selectPart(id, { drill: true });
      } else {
        selectPart(id, { drill: false });
      }
    });
  }

  function bindChrome() {
    els.modeBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var mode = btn.getAttribute("data-mode");
        if (mode === state.mode) return;
        state.mode = mode;
        els.modeBtns.forEach(function (b) {
          var on = b === btn;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-selected", on ? "true" : "false");
        });
        var meta = modeMeta();
        if (els.lead && meta) els.lead.textContent = meta.lead;
        goRoot();
      });
    });

    els.crumb.addEventListener("click", function (e) {
      var btn = e.target.closest("button[data-crumb]");
      if (!btn) return;
      if (btn.getAttribute("data-crumb") === "root") goRoot();
      if (btn.getAttribute("data-crumb") === "stack") {
        goStack(Number(btn.getAttribute("data-index")));
      }
    });

    els.list.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-part]");
      if (!btn) return;
      var id = btn.getAttribute("data-part");
      var n = node(id);
      if (n && n.drillLayer && state.selectedId === id) {
        selectPart(id, { drill: true });
      } else {
        selectPart(id, { drill: false });
      }
    });
  }

  fetch(DATA_URL)
    .then(function (r) {
      if (!r.ok) throw new Error("parts-tree load failed");
      return r.json();
    })
    .then(function (data) {
      state.data = data;
      bindHotspots();
      bindChrome();
      goRoot();
      var meta = modeMeta();
      if (els.lead && meta) els.lead.textContent = meta.lead;
    })
    .catch(function () {
      els.panel.classList.remove("is-empty");
      els.panel.innerHTML =
        "<h2>Не удалось загрузить схему</h2><p>Проверьте файл assets/data/parts-tree.json</p>";
    });
})();
