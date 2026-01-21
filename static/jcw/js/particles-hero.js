(function () {
  if (window.JCW_PARTICLES_ENABLED !== true) {
    return;
  }

  var config = window.JCW_PARTICLES_CONFIG;
  if (!config || typeof config !== "object") {
    return;
  }

  function initParticles() {
    if (!window.particlesJS) {
      window.setTimeout(initParticles, 50);
      return;
    }

    try {
      window.particlesJS("particles-js", config);
    } catch (err) {
      return;
    }
  }

  initParticles();
})();
