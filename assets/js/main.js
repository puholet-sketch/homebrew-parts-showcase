(function () {
  var toggle = document.querySelector(".nav-toggle");
  var mobile = document.getElementById("mobile-nav");

  if (toggle && mobile) {
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
  }

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var partsCache = null;
  var activeCategory = "all";
  var searchQuery = "";

  function pad(id) {
    id = String(id || "");
    if (/^\d+$/.test(id) && id.length < 3) {
      while (id.length < 3) id = "0" + id;
    }
    return id;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function tgHref(label) {
    return (
      "https://t.me/puholet?text=" +
      encodeURIComponent("Заказ: " + (label || "SKU"))
    );
  }

  function loadParts() {
    if (partsCache) return Promise.resolve(partsCache);
    return fetch("assets/data/parts.json")
      .then(function (r) {
        if (!r.ok) throw new Error("parts.json");
        return r.json();
      })
      .then(function (data) {
        partsCache = data;
        return data;
      });
  }

  function observeReveal(root) {
    var cards = (root || document).querySelectorAll(".card.reveal:not(.is-visible)");
    if (reduce || !("IntersectionObserver" in window)) {
      cards.forEach(function (el) {
        el.classList.add("is-visible");
      });
      return;
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    cards.forEach(function (el) {
      io.observe(el);
    });
  }

  function factsHtml(facts) {
    return (facts || [])
      .slice(0, 3)
      .map(function (f) {
        var icon = f.icon || "seal";
        var text = f.text || "";
        return (
          '<li class="facts-bar__item">' +
          '<span class="facts-bar__icon" aria-hidden="true"><svg viewBox="0 0 24 24"><use href="#i-' +
          escapeHtml(icon) +
          '"></use></svg></span>' +
          '<span class="facts-bar__text">' +
          escapeHtml(text) +
          "</span></li>"
        );
      })
      .join("");
  }

  function cardHtml(id, sku) {
    var name = sku.name || "";
    var use = sku.use || "";
    var price = sku.price || "";
    var img = sku.image || "";
    var cat = sku.category || "";
    return (
      '<article class="card reveal" id="sku-' +
      escapeHtml(id) +
      '" data-sku="' +
      escapeHtml(id) +
      '" data-category="' +
      escapeHtml(cat) +
      '">' +
      '<button type="button" class="card__hit" data-open-sku="' +
      escapeHtml(id) +
      '" aria-label="Открыть карточку: ' +
      escapeHtml(name) +
      '">' +
      '<div class="card__media">' +
      '<div class="card__photo">' +
      '<img src="' +
      escapeHtml(img) +
      '" alt="' +
      escapeHtml(name) +
      '" width="600" height="600" loading="lazy" />' +
      "</div>" +
      '<ul class="facts-bar" aria-label="Факты о товаре">' +
      factsHtml(sku.facts) +
      "</ul>" +
      "</div>" +
      "</button>" +
      '<div class="card__body">' +
      '<span class="card__sku">SKU ' +
      escapeHtml(id) +
      (sku.categoryName
        ? ' · <span class="card__cat">' + escapeHtml(sku.categoryName) + "</span>"
        : "") +
      "</span>" +
      '<h3 class="card__title">' +
      '<button type="button" class="card__title-btn" data-open-sku="' +
      escapeHtml(id) +
      '">' +
      escapeHtml(name) +
      "</button></h3>" +
      '<p class="card__use"><span class="card__use-label">Для чего</span> ' +
      escapeHtml(use) +
      "</p>" +
      '<div class="card__price">' +
      escapeHtml(price) +
      "</div>" +
      '<div class="card__actions">' +
      '<button type="button" class="btn btn--ghost btn--sm" data-open-sku="' +
      escapeHtml(id) +
      '">Подробнее</button>' +
      '<a class="btn btn--primary btn--sm" href="' +
      tgHref(sku.tg || name) +
      '" target="_blank" rel="noopener">Заказать</a>' +
      "</div></div></article>"
    );
  }

  function filteredSkus(data) {
    var skus = data.skus || {};
    var ids = Object.keys(skus).sort();
    var q = searchQuery.trim().toLowerCase();
    return ids.filter(function (id) {
      var s = skus[id];
      if (activeCategory !== "all" && s.category !== activeCategory) return false;
      if (!q) return true;
      var hay = (
        (s.name || "") +
        " " +
        (s.use || "") +
        " " +
        (s.categoryName || "") +
        " " +
        id
      ).toLowerCase();
      return hay.indexOf(q) !== -1;
    });
  }

  function renderFilters(data) {
    var wrap = document.getElementById("catalog-filters");
    if (!wrap) return;
    var cats = data.categories || [];
    var counts = { all: Object.keys(data.skus || {}).length };
    Object.keys(data.skus || {}).forEach(function (id) {
      var c = data.skus[id].category || "other";
      counts[c] = (counts[c] || 0) + 1;
    });

    var html =
      '<button type="button" class="cat-chip' +
      (activeCategory === "all" ? " is-active" : "") +
      '" data-cat="all">Все <span>' +
      counts.all +
      "</span></button>";

    cats.forEach(function (c) {
      var n = counts[c.id] || 0;
      if (!n) return;
      html +=
        '<button type="button" class="cat-chip' +
        (activeCategory === c.id ? " is-active" : "") +
        '" data-cat="' +
        escapeHtml(c.id) +
        '">' +
        escapeHtml(c.name) +
        " <span>" +
        n +
        "</span></button>";
    });

    html +=
      '<label class="catalog-search"><span class="visually-hidden">Поиск</span>' +
      '<input type="search" id="catalog-search" placeholder="Поиск по названию…" value="' +
      escapeHtml(searchQuery) +
      '" /></label>';

    wrap.innerHTML = html;
  }

  function renderCatalog(data) {
    var grid = document.getElementById("catalog-grid");
    var meta = document.getElementById("catalog-meta");
    if (!grid) return;
    renderFilters(data);
    var ids = filteredSkus(data);
    if (meta) {
      meta.textContent =
        ids.length === 0
          ? "Ничего не найдено — смените категорию или запрос."
          : "Показано " + ids.length + " из " + Object.keys(data.skus || {}).length;
    }
    if (!ids.length) {
      grid.innerHTML = '<p class="catalog-empty">Нет позиций в этой выборке.</p>';
      return;
    }
    grid.innerHTML = ids
      .map(function (id) {
        return cardHtml(id, data.skus[id]);
      })
      .join("");
    observeReveal(grid);
  }

  function bindToolbar(data) {
    var wrap = document.getElementById("catalog-filters");
    if (!wrap || wrap.dataset.bound) return;
    wrap.dataset.bound = "1";
    wrap.addEventListener("click", function (e) {
      var btn = e.target.closest(".cat-chip");
      if (!btn) return;
      activeCategory = btn.getAttribute("data-cat") || "all";
      renderCatalog(data);
    });
    wrap.addEventListener("input", function (e) {
      if (e.target && e.target.id === "catalog-search") {
        searchQuery = e.target.value || "";
        renderCatalog(data);
      }
    });
  }

  /* --- Product detail modal --- */
  var modal = document.getElementById("sku-modal");
  var lastFocus = null;

  function closeModal() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    document.body.classList.remove("sku-modal-open");
    if (location.hash && /^#sku-\d{2,3}$/.test(location.hash)) {
      history.replaceState(null, "", location.pathname + location.search + "#catalog");
    }
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function openModal(skuId, fromEl) {
    if (!modal) return;
    skuId = pad(skuId);
    lastFocus = fromEl || document.activeElement;

    loadParts()
      .then(function (data) {
        var sku = (data.skus && data.skus[skuId]) || null;
        if (!sku) return;

        var img = document.getElementById("sku-modal-img");
        var factsEl = document.getElementById("sku-modal-facts");
        var skuEl = document.getElementById("sku-modal-sku");
        var titleEl = document.getElementById("sku-modal-title");
        var useEl = document.getElementById("sku-modal-use");
        var priceEl = document.getElementById("sku-modal-price");
        var orderEl = document.getElementById("sku-modal-order");
        var schemaEl = document.getElementById("sku-modal-schema");

        if (img) {
          img.src = sku.image || "";
          img.alt = sku.name || "";
        }
        if (skuEl) {
          skuEl.textContent =
            "SKU " +
            skuId +
            (sku.categoryName ? " · " + sku.categoryName : "");
        }
        if (titleEl) titleEl.textContent = sku.name || "";
        if (useEl) useEl.textContent = sku.use || "";
        if (priceEl) priceEl.textContent = sku.price || "";
        if (orderEl) orderEl.href = tgHref(sku.tg || sku.name || skuId);
        if (schemaEl) {
          schemaEl.href = "schema.html";
          schemaEl.textContent = "Схема аппарата";
        }

        if (factsEl) {
          factsEl.innerHTML = factsHtml(sku.facts);
        }

        modal.hidden = false;
        document.body.classList.add("sku-modal-open");
        if (location.hash !== "#sku-" + skuId) {
          history.replaceState(null, "", "#sku-" + skuId);
        }
        var closeBtn = modal.querySelector(".sku-modal__close");
        if (closeBtn) closeBtn.focus();
        var card = document.getElementById("sku-" + skuId);
        if (card) card.scrollIntoView({ block: "nearest" });
      })
      .catch(function () {
        /* ignore */
      });
  }

  document.addEventListener("click", function (e) {
    var close = e.target.closest("[data-close-modal]");
    if (close) {
      e.preventDefault();
      closeModal();
      return;
    }
    var open = e.target.closest("[data-open-sku]");
    if (open) {
      e.preventDefault();
      openModal(open.getAttribute("data-open-sku"), open);
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeModal();
  });

  function openFromHash() {
    var m = location.hash && location.hash.match(/^#sku-(\d{2,3})$/);
    if (m) openModal(m[1]);
  }

  loadParts()
    .then(function (data) {
      renderCatalog(data);
      bindToolbar(data);
      openFromHash();
    })
    .catch(function () {
      var grid = document.getElementById("catalog-grid");
      if (grid) {
        grid.innerHTML =
          '<p class="catalog-empty">Не удалось загрузить каталог. Обновите страницу.</p>';
      }
    });

  window.addEventListener("hashchange", openFromHash);
})();
