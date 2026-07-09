(function () {
  function initBackToTop() {
    var button = document.querySelector("[data-jcw-back-to-top]");
    if (!button) {
      return;
    }

    function syncVisibility() {
      if (window.scrollY > 360) {
        button.classList.add("is-visible");
      } else {
        button.classList.remove("is-visible");
      }
    }

    button.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

    window.addEventListener("scroll", syncVisibility, { passive: true });
    syncVisibility();
  }

  function initClippyPlaceholder() {
    var shell = document.querySelector("[data-jcw-clippy]");
    if (!shell) {
      return;
    }

    var toggle = shell.querySelector("[data-jcw-clippy-toggle]");
    var panel = shell.querySelector(".jcw-clippy-panel");
    var close = shell.querySelector("[data-jcw-clippy-close]");

    if (!toggle || !panel) {
      return;
    }

    function setOpen(isOpen) {
      panel.hidden = !isOpen;
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    }

    toggle.addEventListener("click", function () {
      setOpen(panel.hidden);
    });

    if (close) {
      close.addEventListener("click", function () {
        setOpen(false);
      });
    }

    document.querySelectorAll("[data-jcw-clippy-open]").forEach(function (trigger) {
      trigger.addEventListener("click", function (event) {
        event.preventDefault();
        setOpen(true);
      });
    });

    document.addEventListener("click", function (event) {
      if (!shell.contains(event.target)) {
        setOpen(false);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initBackToTop();
    initClippyPlaceholder();
  });
})();
