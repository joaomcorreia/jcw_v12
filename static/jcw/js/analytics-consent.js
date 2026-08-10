(function () {
  "use strict";

  var config = window.JCW_ANALYTICS_CONFIG || {};
  var storageKey = "jcw-analytics-consent";
  var banner = document.querySelector("[data-analytics-consent]");
  var hasLoadedGa = false;
  var hasLoadedClarity = false;

  function readChoice() {
    try {
      var value = window.localStorage.getItem(storageKey);
      return value === "granted" || value === "denied" ? value : null;
    } catch (error) {
      return null;
    }
  }

  function saveChoice(value) {
    try {
      window.localStorage.setItem(storageKey, value);
    } catch (error) {
      // A blocked storage implementation should fail closed.
    }
  }

  function ensureGtag() {
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag("consent", "default", {
      analytics_storage: "denied",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied",
      wait_for_update: 500
    });
  }

  function loadGa() {
    if (!config.gaMeasurementId || hasLoadedGa) return;
    hasLoadedGa = true;
    window.gtag("consent", "update", {
      analytics_storage: "granted",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied"
    });
    window.gtag("js", new Date());
    window.gtag("config", config.gaMeasurementId);
    var script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(config.gaMeasurementId);
    document.head.appendChild(script);
  }

  function loadClarity() {
    if (!config.clarityProjectId || hasLoadedClarity) return;
    hasLoadedClarity = true;
    window.clarity = window.clarity || function () {
      (window.clarity.q = window.clarity.q || []).push(arguments);
    };
    window.clarity("consent", true);
    var script = document.createElement("script");
    script.async = true;
    script.src = "https://www.clarity.ms/tag/" + encodeURIComponent(config.clarityProjectId);
    document.head.appendChild(script);
  }

  function applyChoice(choice) {
    if (choice === "granted") {
      loadGa();
      loadClarity();
    } else if (window.gtag) {
      window.gtag("consent", "update", {
        analytics_storage: "denied",
        ad_storage: "denied",
        ad_user_data: "denied",
        ad_personalization: "denied"
      });
    }
    if (banner) banner.hidden = Boolean(choice);
  }

  ensureGtag();
  var storedChoice = readChoice();
  if (storedChoice) applyChoice(storedChoice);
  else if (banner) banner.hidden = false;

  if (banner) {
    banner.addEventListener("click", function (event) {
      var action = event.target.closest("[data-analytics-consent-action]");
      if (!action) return;
      var choice = action.getAttribute("data-analytics-consent-action") === "accept" ? "granted" : "denied";
      saveChoice(choice);
      applyChoice(choice);
    });
  }
}());