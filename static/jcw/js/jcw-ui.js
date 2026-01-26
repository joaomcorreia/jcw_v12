(function () {
  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  ready(function () {
    var scrollRoot = document.scrollingElement || document.documentElement;
    if (document.body.classList.contains("embed-mode") && scrollRoot) {
      scrollRoot.setAttribute("data-embed-root", "");
    }

    var nav = document.querySelector("[data-jcw-nav]");
    if (nav) {
      var scrollTarget = document.querySelector("[data-embed-root]") || scrollRoot;
      var getScrollY = function () {
        if (scrollTarget && scrollTarget !== document.documentElement && scrollTarget !== document.body) {
          return scrollTarget.scrollTop || 0;
        }
        return window.scrollY || 0;
      };
      var onScroll = function () {
        var y = getScrollY();
        var isScrolled = y > 0;
        nav.classList.toggle("jcw-nav-scrolled", isScrolled);
        document.body.classList.toggle("scrolled", isScrolled);
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      if (scrollTarget && scrollTarget !== document.documentElement && scrollTarget !== document.body) {
        scrollTarget.addEventListener("scroll", onScroll, { passive: true });
      }
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
        var isMobile = window.matchMedia("(max-width: 768px)").matches;
        if (!isMobile) {
          return;
        }
        if (!toggle.closest("[data-jcw-mobile-menu]")) {
          return;
        }
        event.preventDefault();
        var menu = toggle.parentElement.querySelector(".jcw-dropdown-menu");
        if (!menu) {
          return;
        }
        var openMenus = document.querySelectorAll(
          "[data-jcw-mobile-menu] .jcw-dropdown-menu.is-open"
        );
        openMenus.forEach(function (openMenu) {
          if (openMenu !== menu) {
            openMenu.classList.remove("is-open");
            var openToggle = openMenu.parentElement.querySelector(
              "[data-jcw-dropdown-toggle]"
            );
            if (openToggle) {
              openToggle.setAttribute("aria-expanded", "false");
            }
          }
        });
        var isOpen = menu.classList.contains("is-open");
        if (isOpen) {
          menu.classList.remove("is-open");
          toggle.setAttribute("aria-expanded", "false");
          return;
        }
        menu.classList.add("is-open");
        toggle.setAttribute("aria-expanded", "true");
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
