(function () {
  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(function () {
    var nav = document.querySelector("[data-jcw-nav]");
    if (nav) {
      var onScroll = function () {
        nav.classList.toggle("jcw-nav-scrolled", window.scrollY > 10);
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }

    var mobileToggle = document.querySelector("[data-jcw-mobile-toggle]");
    var mobileMenu = document.querySelector("[data-jcw-mobile-menu]");
    if (mobileToggle && mobileMenu) {
      mobileToggle.addEventListener("click", function () {
        mobileMenu.classList.toggle("is-open");
      });
    }

    var dropdownToggles = document.querySelectorAll("[data-jcw-dropdown-toggle]");
    dropdownToggles.forEach(function (toggle) {
      toggle.addEventListener("click", function (event) {
        if (window.matchMedia("(max-width: 768px)").matches) {
          event.preventDefault();
          var menu = toggle.parentElement.querySelector(".jcw-dropdown-menu");
          if (menu) {
            menu.classList.toggle("is-open");
          }
        }
      });
    });

    var sidebarToggle = document.querySelector("[data-jcw-sidebar-toggle]");
    var sidebar = document.querySelector("[data-jcw-right-sidebar]");
    var overlay = document.querySelector("[data-jcw-right-sidebar-overlay]");

    function closeSidebar() {
      if (sidebar) {
        sidebar.classList.remove("is-open");
      }
      if (overlay) {
        overlay.classList.remove("is-open");
      }
    }

    function toggleSidebar() {
      if (sidebar) {
        sidebar.classList.toggle("is-open");
      }
      if (overlay) {
        overlay.classList.toggle("is-open");
      }
    }

    if (sidebarToggle) {
      sidebarToggle.addEventListener("click", function (event) {
        event.preventDefault();
        toggleSidebar();
      });
    }

    if (overlay) {
      overlay.addEventListener("click", closeSidebar);
    }

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeSidebar();
      }
    });
  });
})();
