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
  const currentUrl = app.getAttribute("data-current-url");

  const sidebarKey = "jcw-dashboard-sidebar-collapsed";
  const drawerKey = "jcw-dashboard-drawer-collapsed";
  const frontendKey = "jcw_nav_frontend_open";

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
})();
