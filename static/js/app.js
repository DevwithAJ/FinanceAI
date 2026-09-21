document.addEventListener("DOMContentLoaded", () => {
  initSmartSplash();
  initToasts();
  initAnalysisLoader();
  initScrollReveal();
  initBackToTop();
});

function initSmartSplash() {
  const splash = document.getElementById("financeSplash");
  if (!splash) return;

  const statusText = document.getElementById("splashStatusText");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const bypass = new URLSearchParams(window.location.search).has("nosplash");
  const alreadyShown = sessionStorage.getItem("financeai_splash") === "shown";

  if (reduceMotion || bypass || alreadyShown) {
    splash.remove();
    return;
  }

  document.body.classList.add("splash-active");
  splash.setAttribute("aria-hidden", "false");

  const messages = [
    "Initializing FinanceAI...",
    "Loading analytics services...",
    "Checking system modules...",
    "Preparing financial insights...",
    "FinanceAI ready ✓"
  ];

  let index = 0;
  const interval = window.setInterval(() => {
    index += 1;
    if (index < messages.length && statusText) {
      statusText.textContent = messages[index];
    }
  }, 520);

  window.setTimeout(() => {
    window.clearInterval(interval);
    if (statusText) statusText.textContent = messages[messages.length - 1];
    splash.classList.add("splash-hide");
    document.body.classList.remove("splash-active");
    sessionStorage.setItem("financeai_splash", "shown");

    window.setTimeout(() => splash.remove(), 750);
  }, 2700);
}

function initToasts() {
  document.querySelectorAll(".finance-toast").forEach((toast, index) => {
    const close = toast.querySelector(".toast-close");
    const dismiss = () => {
      toast.classList.add("toast-hide");
      window.setTimeout(() => toast.remove(), 350);
    };

    if (close) close.addEventListener("click", dismiss);
    window.setTimeout(dismiss, 4500 + index * 250);
  });
}

function initAnalysisLoader() {
  const loader = document.getElementById("analysisLoader");
  if (!loader) return;

  const message = document.getElementById("analysisLoaderText");

  document.querySelectorAll(".finance-analysis-form").forEach((form) => {
    form.addEventListener("submit", () => {
      const moduleName = form.dataset.analysisName || "FinanceAI";
      if (message) {
        message.textContent = `Validating inputs and running ${moduleName} analysis...`;
      }
      loader.classList.add("show");
      loader.setAttribute("aria-hidden", "false");
      document.body.classList.add("analysis-loading");
    });
  });
}

function initScrollReveal() {
  const selectors = [
    ".finance-stat",
    ".finance-section-heading",
    ".finance-module-card",
    ".workflow-card",
    ".platform-card",
    ".tech-item",
    ".finance-team-card",
    ".responsible-section",
    ".finance-final-cta"
  ];

  const elements = document.querySelectorAll(selectors.join(","));
  if (!elements.length) return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion || !("IntersectionObserver" in window)) {
    elements.forEach((el) => el.classList.add("reveal-visible"));
    return;
  }

  elements.forEach((el, index) => {
    el.classList.add("reveal");
    el.style.setProperty("--reveal-delay", `${Math.min(index % 5, 4) * 55}ms`);
  });

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("reveal-visible");
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -35px 0px" });

  elements.forEach((el) => observer.observe(el));
}

function initBackToTop() {
  const button = document.getElementById("backToTop");
  if (!button) return;

  const update = () => button.classList.toggle("show", window.scrollY > 600);
  window.addEventListener("scroll", update, { passive: true });
  update();

  button.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

// FinanceAI 2.0 transaction category switcher
(function () {
  function syncTransactionCategories() {
    const type = document.getElementById("transactionType");
    const select = document.getElementById("transactionCategory");
    if (!type || !select) return;
    const kind = type.value;
    let first = null;
    Array.from(select.options).forEach((opt) => {
      const visible = opt.dataset.kind === kind;
      opt.hidden = !visible;
      opt.disabled = !visible;
      if (visible && !first) first = opt;
    });
    if (!select.selectedOptions.length || select.selectedOptions[0].disabled) {
      if (first) first.selected = true;
    }
  }
  document.addEventListener("DOMContentLoaded", () => {
    const type = document.getElementById("transactionType");
    if (!type) return;
    type.addEventListener("change", syncTransactionCategories);
    syncTransactionCategories();
  });
})();
