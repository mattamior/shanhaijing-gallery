(() => {
  const VOLUME_ORDER = [
    "南山经",
    "西山经",
    "北山经",
    "东山经",
    "中山经",
    "海外南经",
    "海外西经",
    "海外北经",
    "海外东经",
    "海内南经",
    "海内西经",
    "海内北经",
    "海内经",
    "大荒东经",
    "大荒南经",
    "大荒西经",
    "大荒北经",
  ];

  const PRIORITY_ORDER = { 高: 0, 中: 1, 低: 2 };

  const el = {
    grid: document.getElementById("grid"),
    statsReady: document.getElementById("stat-ready"),
    statsTotal: document.getElementById("stat-total"),
    statsShown: document.getElementById("stat-shown"),
    volume: document.getElementById("filter-volume"),
    priority: document.getElementById("filter-priority"),
    readyOnly: document.getElementById("filter-ready"),
    search: document.getElementById("filter-search"),
    modal: document.getElementById("modal"),
    modalArt: document.getElementById("modal-art"),
    modalName: document.getElementById("modal-name"),
    modalSource: document.getElementById("modal-source"),
    modalBlurb: document.getElementById("modal-blurb"),
    modalTags: document.getElementById("modal-tags"),
    modalHolo: document.getElementById("modal-holo"),
    modalClose: document.getElementById("modal-close"),
    modalBackdrop: document.getElementById("modal-backdrop"),
  };

  let all = [];
  let bySlug = new Map();

  function primaryVolume(volume) {
    return String(volume || "").split(/\s*\/\s*/)[0].trim();
  }

  function volumeSortKey(volume) {
    const v = primaryVolume(volume);
    const i = VOLUME_ORDER.indexOf(v);
    return i === -1 ? 999 : i;
  }

  function fillVolumeOptions(creatures) {
    const set = new Set(creatures.map((c) => primaryVolume(c.volume)).filter(Boolean));
    const vols = [...set].sort((a, b) => volumeSortKey(a) - volumeSortKey(b));
    for (const v of vols) {
      const opt = document.createElement("option");
      opt.value = v;
      opt.textContent = v;
      el.volume.appendChild(opt);
    }
  }

  function filtered() {
    const vol = el.volume.value;
    const pri = el.priority.value;
    const readyOnly = el.readyOnly.checked;
    const q = el.search.value.trim().toLowerCase();

    return all
      .filter((c) => {
        if (readyOnly && c.status !== "ready") return false;
        if (vol && primaryVolume(c.volume) !== vol && !(c.volume || "").includes(vol))
          return false;
        if (pri && c.priority !== pri) return false;
        if (q) {
          const hay = `${c.name} ${c.csvName || ""} ${c.volume} ${c.blurb} ${c.source}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      })
      .sort((a, b) => {
        if (a.status === "ready" && b.status !== "ready") return -1;
        if (b.status === "ready" && a.status !== "ready") return 1;
        const pd = (PRIORITY_ORDER[a.priority] ?? 9) - (PRIORITY_ORDER[b.priority] ?? 9);
        if (pd) return pd;
        const vd = volumeSortKey(a.volume) - volumeSortKey(b.volume);
        if (vd) return vd;
        return a.name.localeCompare(b.name, "zh");
      });
  }


  /** 4:3 母图 → 3:4 展示框：cover + focus；竖图不强制 */
  function applyArtCrop(img, c) {
    const aspect = String(c.aspect || "").replace(/\s/g, "");
    if (aspect !== "4:3" && aspect !== "4/3") return;
    img.classList.add("art--from-4x3");
    const crop = c.crop || {};
    const fx = Math.max(0, Math.min(1, Number(crop.focusX ?? 0.5)));
    const fy = Math.max(0, Math.min(1, Number(crop.focusY ?? 0.45)));
    const zoom = Math.max(1, Math.min(3, Number(crop.zoom ?? 1)));
    img.style.objectFit = "cover";
    img.style.objectPosition = `${fx * 100}% ${fy * 100}%`;
    if (zoom > 1) {
      img.style.transform = `scale(${zoom})`;
      img.style.transformOrigin = `${fx * 100}% ${fy * 100}%`;
    }
  }

  function render() {
    const list = filtered();
    el.statsShown.textContent = String(list.length);
    el.grid.replaceChildren();

    if (!list.length) {
      const empty = document.createElement("div");
      empty.className = "empty";
      empty.textContent = "没有符合筛选的异兽";
      el.grid.appendChild(empty);
      return;
    }

    const frag = document.createDocumentFragment();
    for (const c of list) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "card";
      btn.dataset.slug = c.slug;
      btn.setAttribute("aria-label", `${c.name}，${c.status === "ready" ? "已出图" : "待出图"}`);

      const art = document.createElement("div");
      art.className = "card__art";

      if (c.art && c.status === "ready") {
        const img = document.createElement("img");
        img.src = c.art;
        img.alt = c.name;
        img.loading = "lazy";
        applyArtCrop(img, c);
        art.appendChild(img);
      } else {
        const ph = document.createElement("div");
        ph.className = "card__placeholder";
        ph.innerHTML = '<div class="mark" aria-hidden="true"></div><span>待出图</span>';
        art.appendChild(ph);
      }

      const badge = document.createElement("span");
      badge.className = "card__badge" + (c.status === "ready" ? " ready" : "");
      badge.textContent = c.status === "ready" ? "已出图" : "待出图";
      art.appendChild(badge);

      const body = document.createElement("div");
      body.className = "card__body";
      const name = document.createElement("h3");
      name.className = "card__name";
      name.textContent = c.name;
      const meta = document.createElement("p");
      meta.className = "card__meta";
      meta.textContent = `${primaryVolume(c.volume)} · ${c.priority || "—"}`;
      body.append(name, meta);

      btn.append(art, body);
      btn.addEventListener("click", () => openDetail(c.slug));
      frag.appendChild(btn);
    }
    el.grid.appendChild(frag);
  }


  let modalAnimTimer = 0;
  function stopModalAnim() {
    if (modalAnimTimer) {
      cancelAnimationFrame(modalAnimTimer);
      modalAnimTimer = 0;
    }
  }
  function startModalAnim(imgOrEl, anim) {
    stopModalAnim();
    if (!anim || !(anim.frames > 0)) return;
    const fps = Math.max(1, anim.fps || 8);
    const interval = 1000 / fps;
    let i = 0, last = 0;
    if (anim.format === "sequence" && Array.isArray(anim.urls) && anim.urls.length) {
      const urls = anim.urls;
      imgOrEl.src = urls[0];
      const tick = (t) => {
        if (t - last >= interval) {
          last = t;
          i = (i + 1) % urls.length;
          imgOrEl.src = urls[i];
        }
        modalAnimTimer = requestAnimationFrame(tick);
      };
      modalAnimTimer = requestAnimationFrame(tick);
      return;
    }
    if (anim.format === "sheet" && anim.sheet) {
      const cols = anim.cols || 1;
      const rows = anim.rows || 1;
      const n = anim.frames;
      imgOrEl.style.backgroundImage = `url("${anim.sheet}")`;
      imgOrEl.style.backgroundRepeat = "no-repeat";
      imgOrEl.style.backgroundSize = `${cols * 100}% ${rows * 100}%`;
      const paint = (idx) => {
        const c = idx % cols;
        const r = Math.floor(idx / cols) % rows;
        imgOrEl.style.backgroundPosition = `${c * -100}% ${r * -100}%`;
      };
      paint(0);
      const tick = (t) => {
        if (t - last >= interval) {
          last = t;
          i = (i + 1) % n;
          paint(i);
        }
        modalAnimTimer = requestAnimationFrame(tick);
      };
      modalAnimTimer = requestAnimationFrame(tick);
    }
  }

  function openDetail(slug, pushHash = true) {
    const c = bySlug.get(slug);
    if (!c) return;

    el.modalName.textContent = c.name;
    el.modalSource.textContent = c.source || `《山海经·${c.volume}》`;
    el.modalBlurb.textContent = c.blurb || "";

    el.modalTags.replaceChildren();
    for (const [label, value] of [
      ["篇目", primaryVolume(c.volume)],
      ["优先级", c.priority || "—"],
      ["状态", c.status === "ready" ? "已出图" : "待出图"],
    ]) {
      const tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = `${label} · ${value}`;
      el.modalTags.appendChild(tag);
    }

    stopModalAnim();
    el.modalArt.replaceChildren();
    if (c.art && c.status === "ready") {
      const anim = c.anim && c.anim.frames > 0 ? c.anim : null;
      if (anim && anim.format === "sheet" && anim.sheet) {
        const sheet = document.createElement("div");
        sheet.className = "modal__art-sheet";
        sheet.setAttribute("role", "img");
        sheet.setAttribute("aria-label", c.name);
        el.modalArt.appendChild(sheet);
        startModalAnim(sheet, anim);
      } else {
        const img = document.createElement("img");
        img.src = c.art;
        img.alt = c.name;
        applyArtCrop(img, c);
        el.modalArt.appendChild(img);
        if (anim && anim.format === "sequence") startModalAnim(img, anim);
      }
    } else {
      const ph = document.createElement("div");
      ph.className = "placeholder";
      ph.textContent = "待出图";
      el.modalArt.appendChild(ph);
    }

    if (c.holoUrl) {
      el.modalHolo.hidden = false;
      el.modalHolo.href = c.holoUrl;
    } else {
      el.modalHolo.hidden = true;
      el.modalHolo.removeAttribute("href");
    }

    el.modal.hidden = false;
    document.body.style.overflow = "hidden";
    el.modalClose.focus();

    if (pushHash) {
      const next = `#/${slug}`;
      if (location.hash !== next) history.pushState({ slug }, "", next);
    }
  }

  function closeDetail(clearHash = true) {
    stopModalAnim();
    el.modal.hidden = true;
    document.body.style.overflow = "";
    if (clearHash && location.hash.startsWith("#/")) {
      history.pushState({}, "", location.pathname + location.search);
    }
  }

  function routeFromHash() {
    const m = location.hash.match(/^#\/([a-z0-9-]+)/i);
    if (m && bySlug.has(m[1])) openDetail(m[1], false);
    else closeDetail(false);
  }

  el.modalClose.addEventListener("click", () => closeDetail(true));
  el.modalBackdrop.addEventListener("click", () => closeDetail(true));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !el.modal.hidden) closeDetail(true);
  });
  window.addEventListener("popstate", routeFromHash);
  window.addEventListener("hashchange", routeFromHash);

  for (const node of [el.volume, el.priority, el.readyOnly, el.search]) {
    node.addEventListener("input", render);
    node.addEventListener("change", render);
  }

  fetch("data/creatures.json")
    .then((r) => {
      if (!r.ok) throw new Error(`creatures.json ${r.status}`);
      return r.json();
    })
    .then((data) => {
      all = data.creatures || [];
      bySlug = new Map(all.map((c) => [c.slug, c]));
      el.statsReady.textContent = String(data.ready ?? all.filter((c) => c.status === "ready").length);
      el.statsTotal.textContent = String(data.total ?? all.length);
      fillVolumeOptions(all);
      render();
      routeFromHash();
    })
    .catch((err) => {
      el.grid.innerHTML = `<div class="empty">加载失败：${String(err.message || err)}</div>`;
    });
})();
