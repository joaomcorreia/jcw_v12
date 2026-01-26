(function () {
  var sliderRoot = document.querySelector("[data-jcw-hero-slider]");
  if (!sliderRoot) {
    return;
  }

  var slidesContainer = sliderRoot.querySelector(".jcw-hero-slides");
  if (!slidesContainer) {
    return;
  }

  var baseSlide = slidesContainer.querySelector("[data-jcw-hero-slide]");
  if (!baseSlide) {
    return;
  }

  var currentIndex = 0;
  var timer = null;
  var dotsWrap = null;
  var prevButton = null;
  var nextButton = null;
  var slides = [];

  var getConfig = function () {
    if (window.JCW_HERO && typeof window.JCW_HERO === "object") {
      return window.JCW_HERO;
    }
    var script = document.getElementById("jcw-hero-settings");
    if (!script) {
      return null;
    }
    try {
      return JSON.parse(script.textContent);
    } catch (err) {
      return null;
    }
  };

  var clearTimer = function () {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  };

  var setActive = function (index) {
    if (!slides.length) {
      return;
    }
    if (index < 0) {
      index = slides.length - 1;
    }
    if (index >= slides.length) {
      index = 0;
    }
    slides.forEach(function (slideEl, idx) {
      if (idx === index) {
        slideEl.classList.add("is-active");
        slideEl.setAttribute("aria-hidden", "false");
      } else {
        slideEl.classList.remove("is-active");
        slideEl.setAttribute("aria-hidden", "true");
      }
    });
    if (dotsWrap) {
      Array.prototype.slice.call(dotsWrap.children).forEach(function (dot, idx) {
        if (idx === index) {
          dot.classList.add("is-active");
        } else {
          dot.classList.remove("is-active");
        }
      });
    }
    currentIndex = index;
  };

  var buildSlide = function (source, data, index) {
    var slide = source.cloneNode(true);
    slide.setAttribute("data-jcw-slide-index", index.toString());
    slide.classList.remove("is-active");
    slide.setAttribute("aria-hidden", "true");

    var titleEl =
      slide.querySelector("[data-jcw-field='hero.title']") ||
      slide.querySelector("h1");
    var subtitleEl =
      slide.querySelector("[data-jcw-field='hero.subtitle']") ||
      slide.querySelector("p");
    var ctaEl =
      slide.querySelector("[data-jcw-field='hero.cta_label']") ||
      slide.querySelector("a");

    slide.querySelectorAll("[data-jcw-field]").forEach(function (el) {
      el.removeAttribute("data-jcw-field");
      el.removeAttribute("data-jcw-field-id");
      el.removeAttribute("data-jcw-type");
      el.removeAttribute("contenteditable");
    });

    if (titleEl && data.title) {
      titleEl.textContent = data.title;
    }
    if (subtitleEl && data.subtitle) {
      subtitleEl.textContent = data.subtitle;
    }
    if (ctaEl && data.ctaLabel) {
      ctaEl.textContent = data.ctaLabel;
    }
    if (ctaEl && data.ctaUrl) {
      ctaEl.setAttribute("href", data.ctaUrl);
    }

    return slide;
  };

  var renderDots = function () {
    if (dotsWrap) {
      dotsWrap.remove();
    }
    dotsWrap = document.createElement("div");
    dotsWrap.className = "jcw-hero-dots";
    slides.forEach(function (_, idx) {
      var dot = document.createElement("button");
      dot.type = "button";
      dot.className = "jcw-hero-dot" + (idx === 0 ? " is-active" : "");
      dot.setAttribute("aria-label", "Go to slide " + (idx + 1));
      dot.addEventListener("click", function () {
        setActive(idx);
      });
      dotsWrap.appendChild(dot);
    });
    sliderRoot.appendChild(dotsWrap);
  };

  var renderArrows = function () {
    if (prevButton) {
      prevButton.remove();
      prevButton = null;
    }
    if (nextButton) {
      nextButton.remove();
      nextButton = null;
    }
    prevButton = document.createElement("button");
    prevButton.type = "button";
    prevButton.className = "jcw-hero-arrow jcw-hero-arrow--prev";
    prevButton.setAttribute("aria-label", "Previous slide");
    prevButton.textContent = "<";
    prevButton.addEventListener("click", function () {
      setActive(currentIndex - 1);
    });

    nextButton = document.createElement("button");
    nextButton.type = "button";
    nextButton.className = "jcw-hero-arrow jcw-hero-arrow--next";
    nextButton.setAttribute("aria-label", "Next slide");
    nextButton.textContent = ">";
    nextButton.addEventListener("click", function () {
      setActive(currentIndex + 1);
    });

    sliderRoot.appendChild(prevButton);
    sliderRoot.appendChild(nextButton);
  };

  var initSlider = function (config) {
    clearTimer();
    slidesContainer
      .querySelectorAll("[data-jcw-hero-slide]")
      .forEach(function (slide, idx) {
        if (idx === 0) {
          slide.classList.add("is-active");
          slide.setAttribute("aria-hidden", "false");
        } else {
          slide.remove();
        }
      });

    slides = [baseSlide];
    var slideData = (config && config.slides) || [];
    if (slideData.length > 1) {
      for (var i = 1; i < slideData.length; i += 1) {
        var clone = buildSlide(baseSlide, slideData[i] || {}, i);
        slidesContainer.appendChild(clone);
        slides.push(clone);
      }
    }

    if (config && config.slider && config.slider.show_dots) {
      renderDots();
    } else if (dotsWrap) {
      dotsWrap.remove();
      dotsWrap = null;
    }

    if (config && config.slider && config.slider.show_arrows) {
      renderArrows();
    } else {
      if (prevButton) {
        prevButton.remove();
        prevButton = null;
      }
      if (nextButton) {
        nextButton.remove();
        nextButton = null;
      }
    }

    setActive(0);

    if (config && config.slider && config.slider.autoplay && slides.length > 1) {
      var delay = Number(config.slider.delay || 5000);
      timer = setInterval(function () {
        setActive(currentIndex + 1);
      }, delay);
    }

    return {
      destroy: function () {
        clearTimer();
      },
    };
  };

  var boot = function () {
    var config = getConfig() || {};
    window.JCW_HERO_SLIDER = initSlider(config);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  window.JCW_HERO_INIT = function (config) {
    return initSlider(config || {});
  };

  if (typeof window.JCW_HERO_APPLY !== "function") {
    window.JCW_HERO_APPLY = function (config) {
      window.JCW_HERO = config;
      if (
        window.JCW_HERO_SLIDER &&
        typeof window.JCW_HERO_SLIDER.destroy === "function"
      ) {
        window.JCW_HERO_SLIDER.destroy();
      }
      window.JCW_HERO_SLIDER = initSlider(config || {});
    };
  }
})();
