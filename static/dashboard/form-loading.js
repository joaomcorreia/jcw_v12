(() => {
  const forms = document.querySelectorAll("form[data-loading-form]");
  forms.forEach((form) => {
    let submitted = false;
    form.addEventListener("submit", (event) => {
      if (submitted) {
        event.preventDefault();
        return;
      }
      submitted = true;
      form.setAttribute("aria-busy", "true");
      form.querySelectorAll("button[type=submit], input[type=submit]").forEach((button) => {
        button.disabled = true;
        button.classList.add("is-loading");
        button.setAttribute("aria-disabled", "true");
        const label = form.getAttribute("data-loading-label");
        if (label && button.tagName === "BUTTON") {
          button.textContent = label;
        }
      });
    });
  });
})();
