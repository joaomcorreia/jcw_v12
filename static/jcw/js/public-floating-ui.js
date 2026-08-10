(function () {
  function getCookie(name) {
    var match = document.cookie.match(new RegExp("(^|; )" + name.replace(/[.*+?^${}()|[\\]\\]/g, "\\$&") + "=([^;]*)"));
    return match ? decodeURIComponent(match[1]) : "";
  }

  function appendMessage(container, label, text) {
    var item = document.createElement("p");
    var strong = document.createElement("strong");
    strong.textContent = label + ": ";
    item.appendChild(strong);
    item.appendChild(document.createTextNode(text));
    container.appendChild(item);
    container.scrollTop = container.scrollHeight;
  }

  function initBackToTop() {
    var button = document.querySelector("[data-jcw-back-to-top]");
    if (!button) return;
    function syncVisibility() {
      button.classList.toggle("is-visible", window.scrollY > 360);
    }
    button.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
    window.addEventListener("scroll", syncVisibility, { passive: true });
    syncVisibility();
  }

  function initClippy() {
    var shell = document.querySelector("[data-jcw-clippy]");
    if (!shell) return;
    var toggle = shell.querySelector("[data-jcw-clippy-toggle]");
    var panel = shell.querySelector(".jcw-clippy-panel");
    var close = shell.querySelector("[data-jcw-clippy-close]");
    if (!toggle || !panel) return;

    function setOpen(isOpen) {
      panel.hidden = !isOpen;
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    }
    toggle.addEventListener("click", function () { setOpen(panel.hidden); });
    if (close) close.addEventListener("click", function () { setOpen(false); });
    document.querySelectorAll("[data-jcw-clippy-open]").forEach(function (trigger) {
      trigger.addEventListener("click", function (event) {
        event.preventDefault();
        setOpen(true);
      });
    });
    document.addEventListener("click", function (event) {
      if (!shell.contains(event.target)) setOpen(false);
    });

    var endpoint = shell.dataset.jcwAssistantEndpoint;
    var language = shell.dataset.jcwAssistantLanguage || "en";
    var form = shell.querySelector("[data-jcw-assistant-form]");
    var input = shell.querySelector("[data-jcw-assistant-input]");
    var messages = shell.querySelector("[data-jcw-assistant-messages]");
    var status = shell.querySelector("[data-jcw-assistant-status]");
    var clear = shell.querySelector("[data-jcw-assistant-clear]");
    if (!endpoint || !form || !input || !messages) return;

    function setStatus(text) {
      status.textContent = text || "";
      status.hidden = !text;
    }
    function request(body) {
      return fetch(endpoint, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        },
        body: new URLSearchParams(body),
        credentials: "same-origin"
      }).then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) throw new Error(data.error || "Assistant unavailable.");
          return data;
        });
      });
    }
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var message = input.value.trim();
      if (!message) return;
      appendMessage(messages, "You", message);
      input.value = "";
      setStatus("Assistant is thinking...");
      request({ message: message, conversation_language: language })
        .then(function (data) {
          appendMessage(messages, "JCW Assistant", data.answer);
          setStatus("");
        })
        .catch(function (error) { setStatus(error.message); });
    });
    if (clear) {
      clear.addEventListener("click", function () {
        request({ action: "clear" }).then(function () {
          messages.textContent = "";
          setStatus("");
        }).catch(function (error) { setStatus(error.message); });
      });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    initBackToTop();
    initClippy();
  });
})();