(function () {
  var DATA_URL = "assets/data/parts.json";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var state = {
    data: null,
    mode: "distiller",
    layer: "root",
    selectedId: null,
    crumb: [],
  };

  var els = {
    panel: document.getElementById("schema-panel"),
    list: document.getElementById("schema-parts-list"),
    crumb: document.getElementById("schema-crumb"),
    tooltip: document.getElementById("schema-tooltip"),
    stage: document.getElementById("schema-stage"),
    svgDistiller: document.getElementById("svg-distiller"),
    svgBrewery: document.getElementById("svg-brewery"),
    modeBtns: document.querySelectorAll(".schema-modes [data-mode]"),
  };

  // mobile nav (schema page has no main.js)
  (function bindNav() {
    var toggle = document.querySelector(".nav-toggle");
    var mobile = document.getElementById("mobile-nav");
    if (!toggle || !mobile) return;
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!open));
      mobile.hidden = open;
    });
    mobile.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        toggle.setAttribute("aria-expanded", "false");
        mobile.hidden = true;
      });
    });
  })();

  if (!els.panel) return;

  function modeObj() {
    return state.data && state.data.modes ? state.data.modes[state.mode] : null;
  }

  function nodes() {
    var m = modeObj();
    return m && m.nodes ? m.nodes : {};
  }

  function getNode(id) {
    return nodes()[id] || null;
  }

  function skuMeta(skuId) {
    if (!skuId || !state.data.skus) return null;
    return state.data.skus[skuId] || state.data.skus[pad(skuId)] || null;
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

  function activeSvg() {
    return state.mode === "brewery" ? els.svgBrewery : els.svgDistiller;
  }

  function rootLayer() {
    return state.mode === "brewery" ? "brew-root" : "root";
  }

  function setMode(mode) {
    state.mode = mode;
    state.selectedId = null;
    state.crumb = [];
    state.layer = rootLayer();

    els.modeBtns.forEach(function (btn) {
      var on = btn.getAttribute("data-mode") === mode;
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });

    if (els.svgDistiller) els.svgDistiller.hidden = mode !== "distiller";
    if (els.svgBrewery) els.svgBrewery.hidden = mode !== "brewery";

    showLayer(state.layer, false);
    renderEmptyPanel();
    renderList();
    renderCrumb();
  }

  function showLayer(layerId, animate) {
    state.layer = layerId;
    var svg = activeSvg();
    if (!svg) return;
    svg.querySelectorAll(".layer").forEach(function (layer) {
      var match = layer.getAttribute("data-layer") === layerId;
      if (match) {
        layer.hidden = false;
        layer.removeAttribute("hidden");
        if (animate && !reduceMotion) {
          layer.classList.remove("is-in");
          void layer.offsetWidth;
          layer.classList.add("is-in");
        }
      } else {
        layer.hidden = true;
        layer.classList.remove("is-in");
      }
    });
    clearHotspotState();
    renderList();
    renderCrumb();
  }

  function clearHotspotState() {
    var svg = activeSvg();
    if (!svg) return;
    svg.querySelectorAll(".hotspot").forEach(function (h) {
      h.classList.remove("is-hover", "is-active", "is-dim");
    });
  }

  function highlight(id) {
    var svg = activeSvg();
    if (!svg) return;
    var layer = svg.querySelector('.layer[data-layer="' + state.layer + '"]');
    if (!layer) return;
    var hotspots = layer.querySelectorAll(".hotspot[data-id]");
    hotspots.forEach(function (h) {
      var match = h.getAttribute("data-id") === id;
      h.classList.toggle("is-active", match);
      h.classList.toggle("is-dim", !!id && !match);
    });
  }

  function drillInto(node) {
    if (!node || !node.drillable || !node.layer) return;
    state.crumb.push({
      id: node.id,
      name: node.name,
      layer: state.layer,
    });
    showLayer(node.layer, true);
    selectNode(node.id, { skipDrill: true });
  }

  function selectNode(id, opts) {
    opts = opts || {};
    var node = getNode(id);
    if (!node) return;

    if (!opts.skipDrill && opts.forceDrill && node.drillable && node.layer) {
      drillInto(node);
      return;
    }

    if (
      !opts.skipDrill &&
      state.selectedId === id &&
      node.drillable &&
      node.layer &&
      opts.fromClick
    ) {
      drillInto(node);
      return;
    }

    state.selectedId = id;
    highlight(id);
    renderPanel(node);
    renderList();
    renderCrumb();
  }

  function renderEmptyPanel() {
    els.panel.innerHTML =
      '<p class="schema-panel__empty">Наведите или коснитесь узла на схеме. Сборки с «▸» открываются повторным тапом или кнопкой «Провалиться».</p>';
  }

  function renderPanel(node) {
    var sku = skuMeta(node.skuId);
    var skuLine = node.skuId
      ? '<div class="schema-panel__sku">SKU ' + pad(node.skuId) + "</div>"
      : '<div class="schema-panel__sku">Узел схемы</div>';
    var facts = (node.facts || [])
      .map(function (f) {
        return "<li>" + escapeHtml(f) + "</li>";
      })
      .join("");
    var price = sku && sku.price ? '<div class="schema-panel__price">' + escapeHtml(sku.price) + "</div>" : "";
    var actions = [];
    if (node.skuId) {
      actions.push(
        '<a class="btn btn--primary btn--sm" href="index.html#sku-' +
          pad(node.skuId) +
          '">Карточка товара</a>'
      );
      actions.push('<a class="btn btn--ghost btn--sm" href="index.html#catalog">В каталог</a>');
    }
    if (node.drillable && node.layer) {
      actions.push(
        '<button type="button" class="btn btn--ghost btn--sm" id="schema-drill">Провалиться</button>'
      );
    }

    els.panel.innerHTML =
      skuLine +
      "<h2>" +
      escapeHtml(node.name) +
      "</h2>" +
      '<p class="schema-panel__desc">' +
      escapeHtml(node.description || "") +
      "</p>" +
      (facts ? '<ul class="schema-panel__facts">' + facts + "</ul>" : "") +
      price +
      (actions.length ? '<div class="schema-panel__actions">' + actions.join("") + "</div>" : "");

    var drill = document.getElementById("schema-drill");
    if (drill) {
      drill.addEventListener("click", function () {
        drillInto(node);
      });
    }
  }

  function layerHotspotIds() {
    var svg = activeSvg();
    if (!svg) return [];
    var layer = svg.querySelector('.layer[data-layer="' + state.layer + '"]');
    if (!layer) return [];
    var ids = [];
    layer.querySelectorAll(".hotspot[data-id]").forEach(function (h) {
      var id = h.getAttribute("data-id");
      if (ids.indexOf(id) === -1) ids.push(id);
    });
    return ids;
  }

  function renderList() {
    if (!els.list) return;
    els.list.innerHTML = layerHotspotIds()
      .map(function (id) {
        var n = getNode(id);
        if (!n) return "";
        var sub = n.skuId ? "SKU " + pad(n.skuId) : n.drillable ? "сборка" : "узел";
        var active = id === state.selectedId ? " is-active" : "";
        return (
          "<li><button type=\"button\" class=\"" +
          active.trim() +
          "\" data-pick=\"" +
          escapeHtml(id) +
          "\">" +
          escapeHtml(n.name) +
          "<small>" +
          escapeHtml(sub) +
          "</small></button></li>"
        );
      })
      .join("");
  }

  function renderCrumb() {
    if (!els.crumb) return;
    var m = modeObj();
    var parts = [];
    parts.push({
      label: m ? m.name.split(" / ")[0] : "Аппарат",
      action: "root",
    });
    state.crumb.forEach(function (c, i) {
      parts.push({ label: c.name, action: "crumb", index: i });
    });
    if (state.selectedId) {
      var n = getNode(state.selectedId);
      var label = n ? n.name : state.selectedId;
      var last = parts[parts.length - 1];
      if (!last || last.label !== label) {
        parts.push({ label: label, action: null });
      }
    }

    els.crumb.innerHTML = parts
      .map(function (p, i) {
        var sep = i ? '<span class="schema-crumb__sep">›</span>' : "";
        if (p.action === "root") {
          return sep + '<button type="button" data-crumb="root">' + escapeHtml(p.label) + "</button>";
        }
        if (p.action === "crumb") {
          return (
            sep +
            '<button type="button" data-crumb="idx" data-index="' +
            p.index +
            '">' +
            escapeHtml(p.label) +
            "</button>"
          );
        }
        return sep + "<button type=\"button\" disabled>" + escapeHtml(p.label) + "</button>";
      })
      .join("");
  }

  function goRoot() {
    state.crumb = [];
    state.selectedId = null;
    showLayer(rootLayer(), false);
    renderEmptyPanel();
  }

  function goCrumb(index) {
    var target = state.crumb[index];
    if (!target) return;
    state.crumb = state.crumb.slice(0, index);
    showLayer(target.layer, false);
    selectNode(target.id, { skipDrill: true });
  }

  function showTooltip(name, clientX, clientY) {
    if (!els.tooltip || !els.stage) return;
    var wrap = els.stage.querySelector(".schema-canvas-wrap");
    if (!wrap) return;
    var rect = wrap.getBoundingClientRect();
    els.tooltip.textContent = name;
    els.tooltip.style.left = clientX - rect.left + "px";
    els.tooltip.style.top = clientY - rect.top + "px";
    els.tooltip.classList.add("is-on");
  }

  function hideTooltip() {
    if (els.tooltip) els.tooltip.classList.remove("is-on");
  }

  function bindSvg(svg) {
    if (!svg) return;

    svg.addEventListener("pointerover", function (e) {
      var hs = e.target.closest(".hotspot");
      if (!hs || !svg.contains(hs)) return;
      hs.classList.add("is-hover");
      var n = getNode(hs.getAttribute("data-id"));
      if (n) showTooltip(n.name, e.clientX, e.clientY);
    });

    svg.addEventListener("pointermove", function (e) {
      if (!els.tooltip.classList.contains("is-on")) return;
      var hs = e.target.closest(".hotspot");
      if (!hs) return;
      var n = getNode(hs.getAttribute("data-id"));
      if (n) showTooltip(n.name, e.clientX, e.clientY);
    });

    svg.addEventListener("pointerout", function (e) {
      var hs = e.target.closest(".hotspot");
      if (!hs) return;
      var related =
        e.relatedTarget && e.relatedTarget.closest ? e.relatedTarget.closest(".hotspot") : null;
      if (related === hs) return;
      hs.classList.remove("is-hover");
      hideTooltip();
    });

    svg.addEventListener("click", function (e) {
      var hs = e.target.closest(".hotspot");
      if (!hs || !svg.contains(hs)) return;
      hideTooltip();
      selectNode(hs.getAttribute("data-id"), { fromClick: true });
    });

    svg.addEventListener("dblclick", function (e) {
      var hs = e.target.closest(".hotspot");
      if (!hs) return;
      e.preventDefault();
      selectNode(hs.getAttribute("data-id"), { forceDrill: true });
    });

    svg.addEventListener("keydown", function (e) {
      var hs = e.target.closest(".hotspot");
      if (!hs) return;
      if (e.key !== "Enter" && e.key !== " ") return;
      e.preventDefault();
      selectNode(hs.getAttribute("data-id"), { fromClick: true });
    });
  }

  function bindChrome() {
    els.modeBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        setMode(btn.getAttribute("data-mode"));
      });
    });

    if (els.crumb) {
      els.crumb.addEventListener("click", function (e) {
        var btn = e.target.closest("button[data-crumb]");
        if (!btn) return;
        if (btn.getAttribute("data-crumb") === "root") goRoot();
        if (btn.getAttribute("data-crumb") === "idx") {
          goCrumb(Number(btn.getAttribute("data-index")));
        }
      });
    }

    if (els.list) {
      els.list.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-pick]");
        if (!btn) return;
        selectNode(btn.getAttribute("data-pick"), { fromClick: true });
      });
    }
  }

  fetch(DATA_URL)
    .then(function (r) {
      if (!r.ok) throw new Error("load failed");
      return r.json();
    })
    .then(function (data) {
      state.data = data;
      bindSvg(els.svgDistiller);
      bindSvg(els.svgBrewery);
      bindChrome();
      setMode("distiller");
    })
    .catch(function () {
      els.panel.innerHTML =
        '<p class="schema-panel__empty">Не удалось загрузить assets/data/parts.json</p>';
    });
})();
