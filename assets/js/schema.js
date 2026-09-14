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
    back: document.getElementById("schema-back"),
    coverage: document.getElementById("schema-coverage"),
    tooltip: document.getElementById("schema-tooltip"),
    stage: document.getElementById("schema-stage"),
    svgDistiller: document.getElementById("svg-distiller"),
    svgBrewery: document.getElementById("svg-brewery"),
    modeBtns: document.querySelectorAll(".schema-modes [data-mode]"),
  };

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

  function padSku(s) {
    s = String(s == null ? "" : s).replace(/\D/g, "");
    if (!s) return "";
    while (s.length < 3) s = "0" + s;
    return s;
  }

  function skuMeta(skuId) {
    if (!skuId || !state.data || !state.data.skus) return null;
    var id = padSku(skuId);
    return state.data.skus[id] || state.data.skus[skuId] || null;
  }

  function skuImage(skuId) {
    var meta = skuMeta(skuId);
    return meta && meta.image ? meta.image : "";
  }

  function catalogFallbackHref(hint) {
    hint = hint || {};
    var params = [];
    if (hint.category) params.push("cat=" + encodeURIComponent(hint.category));
    if (hint.q) params.push("q=" + encodeURIComponent(hint.q));
    return "index.html" + (params.length ? "?" + params.join("&") : "") + "#catalog";
  }

  function categoryName(catId) {
    if (!catId || !state.data || !state.data.categories) return "";
    var hit = state.data.categories.filter(function (c) {
      return c.id === catId;
    })[0];
    return hit ? hit.name : catId;
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

  function setSvgVisible(id, on) {
    var svg = typeof id === "string" ? document.getElementById(id) : id;
    if (!svg) return;
    if (on) {
      svg.removeAttribute("hidden");
      svg.style.setProperty("display", "block", "important");
    } else {
      svg.setAttribute("hidden", "");
      svg.style.setProperty("display", "none", "important");
    }
  }

  function coverageSkus() {
    var seen = {};
    var modes = state.data.modes || {};
    Object.keys(modes).forEach(function (modeKey) {
      var modeNodes = modes[modeKey].nodes || {};
      Object.keys(modeNodes).forEach(function (nid) {
        var n = modeNodes[nid];
        if (n && n.skuId) seen[padSku(n.skuId)] = true;
      });
    });
    return Object.keys(seen).sort();
  }

  function coverageStats() {
    var modes = state.data.modes || {};
    var withSku = 0;
    var total = 0;
    Object.keys(modes).forEach(function (modeKey) {
      var modeNodes = modes[modeKey].nodes || {};
      Object.keys(modeNodes).forEach(function (nid) {
        var n = modeNodes[nid];
        if (!n || (!n.skuId && !n.catalogHint)) return;
        total++;
        if (n.skuId) withSku++;
      });
    });
    return { matched: withSku, nodes: total, unique: coverageSkus().length };
  }

  function renderCoverage() {
    if (!els.coverage || !state.data || !state.data.skus) return;
    var st = coverageStats();
    els.coverage.innerHTML =
      "SKU на схеме: <strong>" +
      st.matched +
      "/" +
      st.nodes +
      "</strong> узлов · " +
      st.unique +
      " позиций каталога";
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

    els.svgDistiller = document.getElementById("svg-distiller");
    els.svgBrewery = document.getElementById("svg-brewery");
    setSvgVisible("svg-distiller", mode === "distiller");
    setSvgVisible("svg-brewery", mode === "brewery");

    showLayer(state.layer, false);
    renderEmptyPanel();
    renderList();
    renderCrumb();
    renderCoverage();
  }

  function showLayer(layerId, animate) {
    state.layer = layerId;
    var svg = activeSvg();
    if (!svg) return;
    svg.querySelectorAll(".layer").forEach(function (layer) {
      var match = layer.getAttribute("data-layer") === layerId;
      if (match) {
        layer.removeAttribute("hidden");
        layer.style.display = "";
        if (animate && !reduceMotion) {
          layer.classList.remove("is-in");
          void layer.offsetWidth;
          layer.classList.add("is-in");
        }
      } else {
        layer.setAttribute("hidden", "");
        layer.style.display = "none";
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
      '<p class="schema-panel__empty">Наведите на деталь — подсветка по контуру. Клик открывает карточку. Повторный клик по кубу, царге, Димроту или заторнику — разрез. Спирт не продаём.</p>';
  }

  function renderPanel(node) {
    var sku = skuMeta(node.skuId);
    var img = skuImage(node.skuId);
    var photo = img
      ? '<div class="schema-panel__media"><img src="' +
        escapeHtml(img) +
        '" alt="' +
        escapeHtml((sku && sku.name) || node.name) +
        '" width="180" height="180"></div>'
      : "";
    var skuLine = sku
      ? '<div class="schema-panel__sku">SKU ' +
        padSku(node.skuId) +
        (sku.categoryName ? " · " + escapeHtml(sku.categoryName) : "") +
        "</div>"
      : '<div class="schema-panel__sku">Узел схемы</div>';
    var useText = (sku && sku.use) || "";
    var descText = node.description || "";
    var useBlock = useText
      ? '<p class="schema-panel__use"><strong>Для чего:</strong> ' + escapeHtml(useText) + "</p>"
      : descText
        ? '<p class="schema-panel__use"><strong>Для чего:</strong> ' + escapeHtml(descText) + "</p>"
        : "";
    var descExtra =
      descText && useText && descText !== useText
        ? '<p class="schema-panel__desc">' + escapeHtml(descText) + "</p>"
        : "";
    var facts = (node.facts || [])
      .map(function (f) {
        return "<li>" + escapeHtml(f) + "</li>";
      })
      .join("");
    if (!facts && sku && sku.facts && sku.facts.length) {
      facts = sku.facts
        .map(function (f) {
          return "<li>" + escapeHtml(f.text || f) + "</li>";
        })
        .join("");
    }
    var price = sku && sku.price ? '<div class="schema-panel__price">' + escapeHtml(sku.price) + "</div>" : "";
    var related = (node.related || [])
      .map(function (rid) {
        var rn = getNode(rid);
        if (!rn) return "";
        return (
          '<button type="button" class="btn btn--ghost btn--sm" data-pick="' +
          escapeHtml(rid) +
          '">' +
          escapeHtml(rn.name) +
          (rn.skuId ? " · SKU " + padSku(rn.skuId) : "") +
          "</button>"
        );
      })
      .filter(Boolean)
      .join("");
    var actions = [];
    if (sku) {
      actions.push(
        '<a class="btn btn--primary btn--sm" href="index.html#sku-' +
          padSku(node.skuId) +
          '">Открыть карточку</a>'
      );
    } else if (node.catalogHint) {
      var hint = node.catalogHint;
      var catLabel = categoryName(hint.category);
      actions.push(
        '<a class="btn btn--primary btn--sm" href="' +
          escapeHtml(catalogFallbackHref(hint)) +
          '">' +
          (hint.q ? "Искать в каталоге" : catLabel ? "Категория: " + escapeHtml(catLabel) : "Открыть каталог") +
          "</a>"
      );
      actions.push(
        '<span class="schema-panel__note">Нет точного SKU в новом каталоге' +
          (hint.note ? " — " + escapeHtml(hint.note) : ".") +
          "</span>"
      );
    }
    if (node.drillable && node.layer && node.layer !== state.layer) {
      actions.push(
        '<button type="button" class="btn btn--ghost btn--sm" id="schema-drill">Показать разрез</button>'
      );
    }

    els.panel.innerHTML =
      skuLine +
      "<h2>" +
      escapeHtml(node.name) +
      "</h2>" +
      photo +
      useBlock +
      descExtra +
      (facts ? '<ul class="schema-panel__facts">' + facts + "</ul>" : "") +
      price +
      (related ? '<div class="schema-panel__actions">' + related + "</div>" : "") +
      (actions.length ? '<div class="schema-panel__actions">' + actions.join("") + "</div>" : "");

    var drill = document.getElementById("schema-drill");
    if (drill) {
      drill.addEventListener("click", function () {
        drillInto(node);
      });
    }

    els.panel.querySelectorAll("[data-pick]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var pick = btn.getAttribute("data-pick");
        var target = getNode(pick);
        if (!target) return;
        if (target.drillable && target.layer && target.layer !== state.layer) {
          selectNode(pick, { forceDrill: true });
        } else {
          selectNode(pick, { skipDrill: true });
        }
      });
    });
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
        var sub = n.skuId
          ? "SKU " + padSku(n.skuId)
          : n.catalogHint
            ? "без точного SKU"
            : n.drillable
              ? "сборка"
              : "узел";
        var active = id === state.selectedId ? " is-active" : "";
        return (
          '<li><button type="button" class="' +
          active.trim() +
          '" data-pick="' +
          escapeHtml(id) +
          '">' +
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
        return sep + '<button type="button" disabled>' + escapeHtml(p.label) + "</button>";
      })
      .join("");

    if (els.back) {
      var canBack = state.crumb.length > 0 || !!state.selectedId;
      els.back.hidden = !canBack;
      els.back.classList.toggle("is-on", canBack);
    }
  }

  function goBack() {
    if (state.crumb.length) {
      goCrumb(state.crumb.length - 1);
      return;
    }
    if (state.selectedId) {
      state.selectedId = null;
      clearHotspotState();
      renderEmptyPanel();
      renderList();
      renderCrumb();
    }
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

  function showTooltip(node, clientX, clientY) {
    if (!els.tooltip || !els.stage || !node) return;
    var wrap = els.stage.querySelector(".schema-canvas-wrap");
    if (!wrap) return;
    var rect = wrap.getBoundingClientRect();
    var sku = skuMeta(node.skuId);
    var use = (sku && sku.use) || node.description || "";
    els.tooltip.innerHTML =
      "<strong>" +
      escapeHtml(node.name) +
      "</strong>" +
      (use ? '<span class="schema-tooltip__use">' + escapeHtml(use) + "</span>" : "");
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
      if (n) showTooltip(n, e.clientX, e.clientY);
    });

    svg.addEventListener("pointermove", function (e) {
      if (!els.tooltip.classList.contains("is-on")) return;
      var hs = e.target.closest(".hotspot");
      if (!hs) return;
      var n = getNode(hs.getAttribute("data-id"));
      if (n) showTooltip(n, e.clientX, e.clientY);
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

    if (els.back) {
      els.back.addEventListener("click", goBack);
    }

    if (els.list) {
      els.list.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-pick]");
        if (!btn) return;
        selectNode(btn.getAttribute("data-pick"), { fromClick: true });
      });
    }

    if (els.panel) {
      els.panel.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-pick]");
        if (!btn) return;
        selectNode(btn.getAttribute("data-pick"), { fromClick: true });
      });
    }
  }

  function findNodeBySku(skuId) {
    skuId = padSku(skuId);
    var modes = state.data.modes || {};
    var found = null;
    Object.keys(modes).forEach(function (modeKey) {
      if (found) return;
      var nodes = (modes[modeKey] && modes[modeKey].nodes) || {};
      Object.keys(nodes).forEach(function (nid) {
        if (found) return;
        if (padSku(nodes[nid].skuId || "") === skuId) {
          found = { mode: modeKey, id: nid };
        }
      });
    });
    return found;
  }

  function openFromHash() {
    var m = location.hash && location.hash.match(/^#sku-(\d{2,3})$/);
    if (!m) return;
    var hit = findNodeBySku(m[1]);
    if (!hit) return;
    if (hit.mode !== state.mode) setMode(hit.mode);
    selectNode(hit.id, { fromClick: true });
  }

  fetch(DATA_URL)
    .then(function (r) {
      if (!r.ok) throw new Error("parts");
      return r.json();
    })
    .then(function (data) {
      state.data = data;
      bindSvg(els.svgDistiller);
      bindSvg(els.svgBrewery);
      bindChrome();
      setMode("distiller");
      openFromHash();
      window.addEventListener("hashchange", openFromHash);
    })
    .catch(function () {
      els.panel.innerHTML =
        '<p class="schema-panel__empty">Не удалось загрузить assets/data/parts.json</p>';
    });
})();
