(function () {
  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(function () {
    if (window.console && typeof window.console.log === "function") {
      window.console.log("JCW editor loaded");
    }
    var toggle = document.getElementById("jcw-edit-toggle");
    var previewToggle = document.getElementById("jcw-preview-toggle");
    var heroSettingsToggle = document.getElementById("jcw-hero-settings-toggle");
    if (!toggle && !previewToggle && !heroSettingsToggle) {
      return;
    }
    var body = document.body;
    var previewClass = "jcw-edit-preview";
    var hoveredSection = null;
    var hoveredField = null;
    var selectedField = null;
    var activeField = null;
    var originalValue = "";
    var isSaving = false;
    var badge = null;
    var statusEl = document.getElementById("jcw-save-status");
    var editorBar = document.getElementById("jcw-editor-bar");
    var heroSettings = null;
    var modal = null;
    var modalBackdrop = null;
    var activeSection = null;
    var siteMode = window.JCW_SITE_MODE || "other";

    var debugEnabled = window.location.search.indexOf("debug_editor=1") !== -1;

    var hasHeroSlider = function () {
      return Boolean(document.querySelector('[data-jcw-hero-slider="1"]'));
    };

    var setState = function (isPreview) {
      if (isPreview) {
        body.classList.add(previewClass);
        toggle.textContent = "Editing";
        toggle.setAttribute("aria-pressed", "false");
      } else {
        body.classList.remove(previewClass);
        toggle.textContent = "Preview";
        toggle.setAttribute("aria-pressed", "true");
      }
    };

    var applyEditorOffset = function () {
      if (!editorBar) {
        document.documentElement.style.setProperty("--jcw-editorbar-h", "0px");
        body.classList.remove("jcw-edit-mode");
        return;
      }
      var height =
        editorBar.offsetHeight || editorBar.getBoundingClientRect().height || 0;
      document.documentElement.style.setProperty("--jcw-editorbar-h", height + "px");
      body.classList.add("jcw-edit-mode");

    };

    var setStatus = function (text, isError) {
      if (!statusEl) {
        return;
      }
      statusEl.textContent = text;
      if (isError) {
        statusEl.style.color = "#fca5a5";
      } else {
        statusEl.style.color = "";
      }
    };

    var ensureBadge = function () {
      if (badge) {
        return badge;
      }
      badge = document.createElement("div");
      badge.className = "jcw-field-badge";
      badge.setAttribute("role", "status");
      badge.setAttribute("aria-live", "polite");
      document.body.appendChild(badge);
      return badge;
    };

    var positionBadge = function (target) {
      if (!target) {
        if (badge) {
          badge.style.display = "none";
        }
        return;
      }
      var rect = target.getBoundingClientRect();
      var el = ensureBadge();
      el.textContent = target.getAttribute("data-jcw-field") || "";
      el.style.display = "block";
      el.style.left = window.scrollX + rect.left + "px";
      el.style.top = window.scrollY + rect.top - 24 + "px";
    };

    var setHover = function (field, section) {
      if (hoveredField !== field) {
        if (hoveredField) {
          hoveredField.classList.remove("jcw-hover");
        }
        hoveredField = field;
        if (hoveredField) {
          hoveredField.classList.add("jcw-hover");
        }
      }
      if (hoveredSection !== section) {
        if (hoveredSection) {
          hoveredSection.classList.remove("jcw-hover");
        }
        hoveredSection = section;
        if (hoveredSection) {
          hoveredSection.classList.add("jcw-hover");
        }
      }
    };

    var clearSelection = function () {
      if (selectedField) {
        selectedField.classList.remove("jcw-selected");
        selectedField = null;
      }
      positionBadge(null);
    };

    var getCookie = function (name) {
      var value = "; " + document.cookie;
      var parts = value.split("; " + name + "=");
      if (parts.length === 2) {
        return parts.pop().split(";").shift();
      }
      return "";
    };

    var getApiUrl = function (path) {
      var lang = document.documentElement.lang || "en";
      var normalized = path;
      while (normalized.charAt(0) === "/") {
        normalized = normalized.slice(1);
      }
      return "/" + lang + "/dashboard/api/" + normalized;
    };

    var saveField = function (field, value) {
      if (isSaving) {
        return Promise.resolve(false);
      }
      var fieldId = field.getAttribute("data-jcw-field-id");
      var fieldKey = field.getAttribute("data-jcw-field");
      var language = document.documentElement.lang || "en";
      isSaving = true;
      setStatus("Saving...", false);
      return fetch(getApiUrl("inline-save/"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        credentials: "same-origin",
        body: JSON.stringify({
          field_id: fieldId,
          field_key: fieldKey,
          value: value,
          language: language,
        }),
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("Save failed");
          }
          return response.json();
        })
        .then(function (data) {
          if (!data.ok) {
            throw new Error(data.error || "Save failed");
          }
          setStatus("Saved", false);
          field.textContent = data.value || "";
          return true;
        })
        .catch(function () {
          setStatus("Error", true);
          return false;
        })
        .finally(function () {
          isSaving = false;
      });
    };

    var loadHeroSettings = function () {
      if (heroSettings) {
        return heroSettings;
      }
      var defaults = {
        background: {
          mode: "color",
          image_url: "",
          color: "#0f172a",
          pattern: "dots",
          pattern_color: "#ffffff",
          overlay: 0.2,
        },
        slider: {
          autoplay: true,
          delay: 5000,
          transition: "fade",
          text_effect: "none",
        },
        slides: [
          {
            title: "",
            subtitle: "",
            ctaLabel: "",
            ctaUrl: "",
            mediaUrl: "",
          },
        ],
        effects: {
          particles: { enabled: false, density: 50, speed: 2, color: "#ffffff" },
          snow: { enabled: false, intensity: 30 },
        },
      };
      if (window.JCW_HERO && typeof window.JCW_HERO === "object") {
        heroSettings = Object.assign({}, defaults, window.JCW_HERO);
        if (!heroSettings.background) {
          heroSettings.background = defaults.background;
        }
        if (!heroSettings.slider) {
          heroSettings.slider = defaults.slider;
        }
        if (!heroSettings.effects) {
          heroSettings.effects = defaults.effects;
        }
        if (!heroSettings.slides || !heroSettings.slides.length) {
          heroSettings.slides = defaults.slides;
        }
        return heroSettings;
      }
      var script = document.getElementById("jcw-hero-settings");
      if (!script) {
        heroSettings = defaults;
        return heroSettings;
      }
      try {
        var parsed = JSON.parse(script.textContent);
        heroSettings = Object.assign({}, defaults, parsed || {});
        if (!heroSettings.background) {
          heroSettings.background = defaults.background;
        }
        if (!heroSettings.slider) {
          heroSettings.slider = defaults.slider;
        }
        if (!heroSettings.effects) {
          heroSettings.effects = defaults.effects;
        }
        if (!heroSettings.slides || !heroSettings.slides.length) {
          heroSettings.slides = defaults.slides;
        }
        return heroSettings;
      } catch (err) {
        heroSettings = defaults;
        return heroSettings;
      }
    };

    var applyHeroBackground = function (settings, sectionEl) {
      if (!sectionEl || !settings || !settings.background) {
        return;
      }
      var target = sectionEl;
      var mode = settings.background.mode || "color";
      var imageUrl = settings.background.image_url || "";
      var color = settings.background.color || "#0f172a";
      var pattern = settings.background.pattern || "dots";
      var patternColor = settings.background.pattern_color || "#ffffff";
      var overlay = Number(settings.background.overlay || 0);
      if (mode === "image" && imageUrl) {
        target.style.backgroundImage = "url(" + imageUrl + ")";
        target.style.backgroundSize = "cover";
        target.style.backgroundPosition = "center";
      } else if (mode === "pattern") {
        target.style.backgroundImage =
          "radial-gradient(circle at 1px 1px," +
          patternColor +
          " 1px, transparent 0)";
        target.style.backgroundSize = "16px 16px";
        target.style.backgroundPosition = "0 0";
      } else {
        target.style.backgroundImage = "";
      }
      target.style.backgroundColor = color;
      var overlayEl = target.querySelector(".jcw-hero-overlay");
      if (overlayEl) {
        overlayEl.style.opacity = overlay.toString();
      }
    };

    var applyParticles = function (settings) {
      if (!settings || !settings.effects || !settings.effects.particles) {
        return;
      }
      if (!window.pJSDom || !window.pJSDom[0] || !window.pJSDom[0].pJS) {
        return;
      }
      var particles = settings.effects.particles;
      var pjs = window.pJSDom[0].pJS;
      var cfg = pjs.particles || {};
      cfg.number = cfg.number || {};
      cfg.move = cfg.move || {};
      cfg.color = cfg.color || {};
      cfg.number.value = particles.density || cfg.number.value;
      cfg.move.speed = particles.speed || cfg.move.speed;
      cfg.color.value = particles.color || cfg.color.value;
      if (typeof pjs.fn.particlesRefresh === "function") {
        pjs.fn.particlesRefresh();
      }
    };

    var ensureModal = function () {
      if (modal) {
        return modal;
      }
      modalBackdrop = document.createElement("div");
      modalBackdrop.className = "jcw-modal-backdrop";
      modal = document.createElement("div");
      modal.className = "jcw-modal";
      modal.innerHTML =
        '<div class="jcw-modal__header">' +
        '<h3>Hero Settings</h3>' +
        '<button type="button" class="jcw-modal__close" aria-label="Close">×</button>' +
        "</div>" +
        '<div class="jcw-modal__body">' +
        '<div class="jcw-modal__divider">Background</div>' +
        '<label class="jcw-modal__row"><span>Mode</span>' +
        '<select data-setting="background.mode">' +
        '<option value="image">Image</option>' +
        '<option value="color">Color</option>' +
        '<option value="pattern">Pattern</option>' +
        "</select></label>" +
        '<label class="jcw-modal__row"><span>Image URL</span><input type="url" data-setting="background.image_url" placeholder="https://"></label>' +
        '<label class="jcw-modal__row"><span>Color</span><input type="color" data-setting="background.color"></label>' +
        '<label class="jcw-modal__row"><span>Pattern</span>' +
        '<select data-setting="background.pattern">' +
        '<option value="dots">Dots</option>' +
        '<option value="grid">Grid</option>' +
        '<option value="waves">Waves</option>' +
        "</select></label>" +
        '<label class="jcw-modal__row"><span>Pattern color</span><input type="color" data-setting="background.pattern_color"></label>' +
        '<label class="jcw-modal__row"><span>Overlay</span><input type="range" min="0" max="0.8" step="0.05" data-setting="background.overlay"></label>' +
        '<div class="jcw-modal__divider">Slider</div>' +
        '<label class="jcw-modal__row"><span>Autoplay</span><input type="checkbox" data-setting="slider.autoplay"></label>' +
        '<label class="jcw-modal__row"><span>Delay (ms)</span><input type="number" min="0" step="100" data-setting="slider.delay"></label>' +
        '<label class="jcw-modal__row"><span>Transition</span>' +
        '<select data-setting="slider.transition">' +
        '<option value="fade">Fade</option>' +
        '<option value="slide">Slide</option>' +
        "</select></label>" +
        '<label class="jcw-modal__row"><span>Text effect</span>' +
        '<select data-setting="slider.text_effect">' +
        '<option value="none">None</option>' +
        '<option value="type">Type</option>' +
        '<option value="glow">Glow</option>' +
        '<option value="wipe">Wipe</option>' +
        "</select></label>" +
        '<div class="jcw-modal__divider">Slides</div>' +
        '<div class="jcw-modal__slides" data-slides></div>' +
        '<button type="button" class="jcw-modal__button jcw-modal__button--ghost" data-action="add-slide">Add slide</button>' +
        '<div class="jcw-modal__divider">Effects</div>' +
        '<label class="jcw-modal__row"><span>Particles (Premium)</span><input type="checkbox" data-setting="effects.particles.enabled"></label>' +
        '<label class="jcw-modal__row"><span>Density</span><input type="range" min="0" max="100" data-setting="effects.particles.density"></label>' +
        '<label class="jcw-modal__row"><span>Speed</span><input type="range" min="0" max="10" step="1" data-setting="effects.particles.speed"></label>' +
        '<label class="jcw-modal__row"><span>Color</span><input type="color" data-setting="effects.particles.color"></label>' +
        '<label class="jcw-modal__row"><span>Snow (Premium)</span><input type="checkbox" data-setting="effects.snow.enabled"></label>' +
        '<label class="jcw-modal__row"><span>Intensity</span><input type="range" min="0" max="100" data-setting="effects.snow.intensity"></label>' +
        "</div>" +
        '<div class="jcw-modal__footer">' +
        '<button type="button" class="jcw-modal__button" data-action="save">Save</button>' +
        "</div>";
      document.body.appendChild(modalBackdrop);
      document.body.appendChild(modal);

      var closeButtons = modal.querySelectorAll(".jcw-modal__close");
      closeButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
          closeModal();
        });
      });
      modalBackdrop.addEventListener("click", closeModal);
      var saveButton = modal.querySelector("[data-action='save']");
      if (saveButton) {
        saveButton.addEventListener("click", function () {
          saveHeroSettings();
        });
      }
      var addSlide = modal.querySelector("[data-action='add-slide']");
      if (addSlide) {
        addSlide.addEventListener("click", function () {
          var settings = loadHeroSettings();
          settings.slides.push({
            title: "",
            subtitle: "",
            ctaLabel: "",
            ctaUrl: "",
            mediaUrl: "",
          });
          renderSlides();
        });
      }
      return modal;
    };

    var closeModal = function () {
      if (modal) {
        modal.classList.remove("is-open");
      }
      if (modalBackdrop) {
        modalBackdrop.classList.remove("is-open");
      }
    };

    var renderSlides = function () {
      if (!modal) {
        return;
      }
      var container = modal.querySelector("[data-slides]");
      if (!container) {
        return;
      }
      container.innerHTML = "";
      var settings = loadHeroSettings();
      settings.slides.forEach(function (slide, index) {
        var row = document.createElement("div");
        row.className = "jcw-modal__slide";
        row.innerHTML =
          '<div class="jcw-modal__slide-row">' +
          '<label>Title<input type="text" data-slide-field="title" data-slide-index="' +
          index +
          '" value="' +
          (slide.title || "") +
          '"></label>' +
          '<label>Subtitle<input type="text" data-slide-field="subtitle" data-slide-index="' +
          index +
          '" value="' +
          (slide.subtitle || "") +
          '"></label>' +
          '<label>CTA Label<input type="text" data-slide-field="ctaLabel" data-slide-index="' +
          index +
          '" value="' +
          (slide.ctaLabel || "") +
          '"></label>' +
          '<label>CTA URL<input type="url" data-slide-field="ctaUrl" data-slide-index="' +
          index +
          '" value="' +
          (slide.ctaUrl || "") +
          '"></label>' +
          '<label>Media URL<input type="url" data-slide-field="mediaUrl" data-slide-index="' +
          index +
          '" value="' +
          (slide.mediaUrl || "") +
          '"></label>' +
          '<button type="button" class="jcw-modal__button jcw-modal__button--ghost" data-action="remove-slide" data-slide-index="' +
          index +
          '">Remove</button>' +
          "</div>";
        container.appendChild(row);
      });
      container.querySelectorAll("[data-action='remove-slide']").forEach(function (btn) {
        btn.addEventListener("click", function () {
          var index = parseInt(btn.getAttribute("data-slide-index"), 10);
          var settings = loadHeroSettings();
          settings.slides.splice(index, 1);
          if (!settings.slides.length) {
            settings.slides.push({
              title: "",
              subtitle: "",
              ctaLabel: "",
              ctaUrl: "",
              mediaUrl: "",
            });
          }
          renderSlides();
        });
      });
      container.querySelectorAll("[data-slide-field]").forEach(function (input) {
        input.addEventListener("input", function () {
          var index = parseInt(input.getAttribute("data-slide-index"), 10);
          var field = input.getAttribute("data-slide-field");
          var settings = loadHeroSettings();
          if (!settings.slides[index]) {
            settings.slides[index] = {};
          }
          settings.slides[index][field] = input.value;
        });
      });
    };

    var openHeroModal = function (sectionEl) {
      activeSection = sectionEl;
      var current = loadHeroSettings();
      var dialog = ensureModal();
      var inputs = dialog.querySelectorAll("[data-setting]");
      inputs.forEach(function (input) {
        var key = input.getAttribute("data-setting");
        var value = key.split(".").reduce(function (acc, part) {
          return acc && acc[part] !== undefined ? acc[part] : null;
        }, current);
        if (input.type === "checkbox") {
          input.checked = Boolean(value);
        } else if (value !== null && value !== undefined) {
          input.value = value;
        }
      });
      renderSlides();
      modal.classList.add("is-open");
      modalBackdrop.classList.add("is-open");
      if (debugEnabled && window.console && typeof window.console.log === "function") {
        window.console.log("Hero modal opened");
      }
    };

    var saveHeroSettings = function () {
      var dialog = ensureModal();
      var settings = loadHeroSettings();
      var inputs = dialog.querySelectorAll("[data-setting]");
      inputs.forEach(function (input) {
        var key = input.getAttribute("data-setting");
        var path = key.split(".");
        var value = input.type === "checkbox" ? input.checked : input.value;
        if (input.type === "number" || input.type === "range") {
          value = input.value === "" ? 0 : Number(input.value);
        }
        var current = settings;
        for (var i = 0; i < path.length; i += 1) {
          var part = path[i];
          var isLast = i === path.length - 1;
          if (isLast) {
            current[part] = value;
          } else {
            current[part] = current[part] || {};
            current = current[part];
          }
        }
      });
      setStatus("Saving...", false);
      return fetch(getApiUrl("section-settings/"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        credentials: "same-origin",
        body: JSON.stringify({
          page: "home",
          section_key: activeSection
            ? activeSection.getAttribute("data-jcw-section")
            : "hero",
          settings: settings,
        }),
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("Save failed");
          }
          return response.json();
        })
        .then(function (data) {
          if (!data.ok) {
            throw new Error(data.error || "Save failed");
          }
          setStatus("Saved", false);
          heroSettings = data.settings || settings;
          window.JCW_HERO = heroSettings;
          if (typeof window.JCW_HERO_APPLY === "function") {
            window.JCW_HERO_APPLY(heroSettings);
          }
          applyParticles(heroSettings);
          applyHeroBackground(heroSettings, activeSection);
          closeModal();
        })
        .catch(function () {
          setStatus("Error", true);
        });
    };

    var stopEditing = function (restore) {
      if (!activeField) {
        return;
      }
      if (restore) {
        activeField.textContent = originalValue;
      }
      activeField.removeAttribute("contenteditable");
      activeField = null;
      originalValue = "";
    };

    var startEditing = function (field) {
      if (activeField && activeField !== field) {
        stopEditing(true);
      }
      activeField = field;
      originalValue = field.textContent || "";
      field.setAttribute("contenteditable", "true");
      field.focus();
    };

    setState(false);
    applyEditorOffset();
    window.requestAnimationFrame(applyEditorOffset);
    setTimeout(applyEditorOffset, 100);
    setTimeout(applyEditorOffset, 300);
    window.addEventListener("resize", applyEditorOffset);

    var setPreviewAttr = function (isPreview) {
      if (isPreview) {
        document.documentElement.setAttribute("data-jcw-preview", "1");
      } else {
        document.documentElement.removeAttribute("data-jcw-preview");
      }
    };

    var updatePreviewButton = function (isPreview) {
      if (!previewToggle) {
        return;
      }
      previewToggle.textContent = isPreview ? "Preview ON" : "Preview OFF";
      previewToggle.setAttribute("aria-pressed", isPreview ? "true" : "false");
    };

    var heroAvailable = hasHeroSlider();
    if (heroSettingsToggle && !(heroAvailable && siteMode === "main")) {
      heroSettingsToggle.style.display = "none";
      heroSettingsToggle.setAttribute("aria-disabled", "true");
    }

    if (toggle) {
      toggle.addEventListener("click", function () {
        var isPreview = body.classList.contains(previewClass);
        setState(!isPreview);
        setPreviewAttr(!isPreview);
        updatePreviewButton(!isPreview);
      });
    }

    if (previewToggle) {
      updatePreviewButton(false);
      previewToggle.addEventListener("click", function () {
        var isPreview = body.classList.contains(previewClass);
        var next = !isPreview;
        if (next) {
          body.classList.add(previewClass);
        } else {
          body.classList.remove(previewClass);
        }
        setPreviewAttr(next);
        updatePreviewButton(next);
      });
    }

    var heroSection = document.querySelector("[data-jcw-section='home.hero'], [data-jcw-section='page.hero'], [data-jcw-section='hero']");
    if (heroSection) {
      var currentSettings = loadHeroSettings();
      applyHeroBackground(currentSettings, heroSection);
      applyParticles(currentSettings);
    }

    document.addEventListener("mousemove", function (event) {
      if (!body.classList.contains("edit-mode")) {
        return;
      }
      if (body.classList.contains(previewClass)) {
        setHover(null, null);
        return;
      }
      var target = event.target;
      var field = target.closest("[data-jcw-field]");
      var section = target.closest("[data-jcw-section]");
      if (field && section && section.contains(field)) {
        setHover(field, null);
      } else {
        setHover(null, section);
      }
    });

    document.addEventListener("click", function (event) {
      if (!body.classList.contains("edit-mode")) {
        return;
      }
      if (body.classList.contains(previewClass)) {
        return;
      }

      var link = event.target.closest("a");
      if (link && !event.altKey) {
        event.preventDefault();
      }

      var field = event.target.closest("[data-jcw-field]");
      if (!field) {
        var hero = event.target.closest('[data-jcw-section="hero"]');
        if (
          hero &&
          heroAvailable &&
          siteMode === "main" &&
          !event.target.closest("[data-jcw-field]")
        ) {
          openHeroModal(hero);
        }
        clearSelection();
        return;
      }
      if (selectedField && selectedField !== field) {
        selectedField.classList.remove("jcw-selected");
      }
      selectedField = field;
      selectedField.classList.add("jcw-selected");
      positionBadge(field);
      if (field.getAttribute("data-jcw-type") === "text") {
        startEditing(field);
      }
    });

    if (heroSettingsToggle) {
      heroSettingsToggle.addEventListener("click", function () {
        if (!heroAvailable || siteMode !== "main") {
          return;
        }
        var heroRoot = document.querySelector('[data-jcw-section="hero"]');
        if (heroRoot) {
          openHeroModal(heroRoot);
        }
      });
    }

    if (debugEnabled) {
      var heroRootDebug = document.querySelector('[data-jcw-section="hero"]');
      var fieldsDebug = document.querySelectorAll("[data-jcw-field]");
      if (window.console && typeof window.console.log === "function") {
        window.console.log("JCW editor debug", {
          host: window.location.host,
          siteMode: siteMode,
          hasHeroSlider: heroAvailable,
          heroRoot: Boolean(heroRootDebug),
          fieldCount: fieldsDebug.length,
          heroSource: window.JCW_HERO_SOURCE,
        });
        window.console.log("JCW_HERO typeof", typeof window.JCW_HERO, window.JCW_HERO);
      }
    }

    document.addEventListener("keydown", function (event) {
      if (!activeField) {
        return;
      }
      if (event.key === "Escape") {
        event.preventDefault();
        stopEditing(true);
        setStatus("Saved", false);
      }
      if (event.key === "Enter") {
        event.preventDefault();
        var value = activeField.textContent || "";
        var normalized = value.replace(/\s+/g, " ").trim();
        if (normalized === originalValue.trim()) {
          stopEditing(false);
          return;
        }
        var fieldToSave = activeField;
        saveField(fieldToSave, normalized).then(function () {
          stopEditing(false);
        });
      }
    });

    document.addEventListener("blur", function (event) {
      if (!activeField) {
        return;
      }
      if (event.target !== activeField) {
        return;
      }
      var value = activeField.textContent || "";
      var normalized = value.replace(/\s+/g, " ").trim();
      if (normalized === originalValue.trim()) {
        stopEditing(false);
        return;
      }
      var fieldToSave = activeField;
      saveField(fieldToSave, normalized).then(function () {
        stopEditing(false);
      });
    }, true);
  });
})();
    if (typeof window.JCW_HERO_APPLY !== "function") {
      window.JCW_HERO_APPLY = function (config) {
        window.JCW_HERO = config;
        if (
          window.JCW_HERO_SLIDER &&
          typeof window.JCW_HERO_SLIDER.destroy === "function"
        ) {
          window.JCW_HERO_SLIDER.destroy();
        }
        if (typeof window.JCW_HERO_INIT === "function") {
          window.JCW_HERO_SLIDER = window.JCW_HERO_INIT(config);
        }
      };
    }
