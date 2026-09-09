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
  var cards = document.querySelectorAll(".card.reveal");

  if (reduce || !("IntersectionObserver" in window)) {
    cards.forEach(function (el) {
      el.classList.add("is-visible");
    });
  } else {
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

  /* --- Product detail modal --- */
  var modal = document.getElementById("sku-modal");
  var partsCache = null;
  var lastFocus = null;

  function pad(id) {
    id = String(id || "");
    return id.length === 1 ? "0" + id : id;
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

  function closeModal() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    document.body.classList.remove("sku-modal-open");
    if (location.hash && /^#sku-\d{2}$/.test(location.hash)) {
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
        if (skuEl) skuEl.textContent = "SKU " + skuId;
        if (titleEl) titleEl.textContent = sku.name || "";
        if (useEl) useEl.textContent = sku.use || "";
        if (priceEl) priceEl.textContent = sku.price || "";
        if (orderEl) orderEl.href = tgHref(sku.tg || sku.name || skuId);
        if (schemaEl) schemaEl.href = "schema.html#sku-" + skuId;

        if (factsEl) {
          factsEl.innerHTML = (sku.facts || [])
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

        modal.hidden = false;
        document.body.classList.add("sku-modal-open");
        if (location.hash !== "#sku-" + skuId) {
          history.replaceState(null, "", "#sku-" + skuId);
        }
        var closeBtn = modal.querySelector(".sku-modal__close");
        if (closeBtn) closeBtn.focus();
        /* scroll catalog card into view behind modal for context */
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
    var m = location.hash && location.hash.match(/^#sku-(\d{2})$/);
    if (m) openModal(m[1]);
  }

  openFromHash();
  window.addEventListener("hashchange", openFromHash);
})();
