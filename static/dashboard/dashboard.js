(() => {
  const app = document.querySelector("[data-dashboard]");
  if (!app) {
    return;
  }

  const sidebar = app.querySelector("[data-dashboard-sidebar]");
  const drawer = app.querySelector("[data-dashboard-drawer]");
  const toggles = app.querySelectorAll("[data-dashboard-toggle]");
  const drawerToggle = app.querySelector('[data-dashboard-toggle="drawer"]');
  const frontendGroup = app.querySelector('[data-dashboard-group="frontend"]');
  const frontendToggle = app.querySelector('[data-dashboard-group-toggle="frontend"]');
  const marketplaceGroup = app.querySelector('[data-dashboard-group="marketplace"]');
  const marketplaceToggle = app.querySelector('[data-dashboard-group-toggle="marketplace"]');
  const currentUrl = app.getAttribute("data-current-url");

  const sidebarKey = "jcw-dashboard-sidebar-collapsed";
  const drawerKey = "jcw-dashboard-drawer-collapsed";
  const frontendKey = "jcw_nav_frontend_open";
  const marketplaceKey = "jcw_nav_marketplace_open";

  const setCollapsed = (element, key, value) => {
    if (!element) {
      return;
    }
    element.classList.toggle("is-collapsed", value);
    localStorage.setItem(key, value ? "1" : "0");
    if (element === drawer) {
      app.classList.toggle("drawer-collapsed", value);
      if (drawerToggle) {
        drawerToggle.textContent = value ? "<" : ">";
      }
    }
  };

  const restoreState = () => {
    setCollapsed(sidebar, sidebarKey, localStorage.getItem(sidebarKey) === "1");
    setCollapsed(drawer, drawerKey, localStorage.getItem(drawerKey) === "1");
    if (frontendGroup) {
      const stored = localStorage.getItem(frontendKey);
      const autoOpen = currentUrl === "dashboard_pages" || currentUrl === "dashboard_blog";
      const shouldOpen = autoOpen || (stored !== null && stored === "1");
      frontendGroup.classList.toggle("is-open", shouldOpen);
      if (autoOpen) {
        localStorage.setItem(frontendKey, "1");
      }
    }
    if (marketplaceGroup) {
      const stored = localStorage.getItem(marketplaceKey);
      const autoOpen =
        currentUrl === "marketplace_jcw" ||
        currentUrl === "marketplace_printlab" ||
        currentUrl === "marketplace_card_payments";
      const shouldOpen = autoOpen || (stored === null ? true : stored === "1");
      marketplaceGroup.classList.toggle("is-open", shouldOpen);
      if (autoOpen) {
        localStorage.setItem(marketplaceKey, "1");
      }
    }
  };

  restoreState();

  toggles.forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const target = toggle.getAttribute("data-dashboard-toggle");
      if (target === "sidebar") {
        setCollapsed(sidebar, sidebarKey, !sidebar.classList.contains("is-collapsed"));
      }
      if (target === "drawer") {
        setCollapsed(drawer, drawerKey, !drawer.classList.contains("is-collapsed"));
      }
    });
  });

  if (frontendGroup && frontendToggle) {
    frontendToggle.addEventListener("click", () => {
      const isOpen = frontendGroup.classList.toggle("is-open");
      localStorage.setItem(frontendKey, isOpen ? "1" : "0");
    });
  }
  if (marketplaceGroup && marketplaceToggle) {
    marketplaceToggle.addEventListener("click", () => {
      const isOpen = marketplaceGroup.classList.toggle("is-open");
      localStorage.setItem(marketplaceKey, isOpen ? "1" : "0");
    });
  }
})();
