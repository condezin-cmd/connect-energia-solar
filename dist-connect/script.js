const header = document.querySelector(".site-header");
const menuToggle = document.querySelector(".menu-toggle");
const navLinks = document.querySelectorAll(".site-nav a");
const samePageAnchors = document.querySelectorAll('a[href^="#"]');
const revealItems = document.querySelectorAll(".reveal");
const year = document.getElementById("year");

const syncHeaderState = () => {
  if (window.scrollY > 12) {
    header.classList.add("is-scrolled");
  } else {
    header.classList.remove("is-scrolled");
  }

  const scrollable = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollable > 0 ? `${(window.scrollY / scrollable) * 100}%` : "0%";
  document.documentElement.style.setProperty("--scroll-progress", progress);
};

if (menuToggle) {
  menuToggle.addEventListener("click", () => {
    const expanded = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!expanded));
    menuToggle.setAttribute("aria-label", expanded ? "Abrir menu" : "Fechar menu");
    header.classList.toggle("nav-open", !expanded);
  });
}

navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    header.classList.remove("nav-open");
    menuToggle?.setAttribute("aria-expanded", "false");
  });
});

samePageAnchors.forEach((link) => {
  link.addEventListener("click", (event) => {
    const hash = link.getAttribute("href");
    if (!hash || hash === "#") {
      return;
    }

    const target = document.querySelector(hash);
    if (!target) {
      return;
    }

    event.preventDefault();
    header.classList.remove("nav-open");
    menuToggle?.setAttribute("aria-expanded", "false");

    if (hash === "#topo") {
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }

    const headerOffset = (header?.offsetHeight || 0) + 18;
    const targetTop = Math.max(target.getBoundingClientRect().top + window.scrollY - headerOffset, 0);
    window.scrollTo({ top: targetTop, behavior: "smooth" });
  });
});

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        const revealGroup = entry.target.parentElement?.querySelectorAll(".reveal");
        if (revealGroup?.length) {
          const groupIndex = Array.from(revealGroup).indexOf(entry.target);
          entry.target.style.animationDelay = `${Math.min(groupIndex * 90, 280)}ms`;
        }

        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.15 }
  );

  revealItems.forEach((item) => observer.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add("is-visible"));
}

if (year) {
  year.textContent = new Date().getFullYear();
}

syncHeaderState();
window.addEventListener("scroll", syncHeaderState, { passive: true });
