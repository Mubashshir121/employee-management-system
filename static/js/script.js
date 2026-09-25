// Auto-dismiss flash messages after a few seconds
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".alert").forEach((alert) => {
    setTimeout(() => {
      alert.style.transition = "opacity 0.4s ease";
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });
});
// =========================
// DARK MODE TOGGLE
// =========================

const themeToggle = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");
const themeText = document.getElementById("themeText");

function updateThemeButton() {
    if (!themeToggle) return;

    const isDark = document.documentElement.classList.contains("dark-mode");

    if (isDark) {
        themeIcon.className = "fa-solid fa-sun";
        themeText.textContent = "Light Mode";
    } else {
        themeIcon.className = "fa-solid fa-moon";
        themeText.textContent = "Dark Mode";
    }
}

if (themeToggle) {
    updateThemeButton();

    themeToggle.addEventListener("click", function () {
        document.documentElement.classList.toggle("dark-mode");

        const isDark =
            document.documentElement.classList.contains("dark-mode");

        localStorage.setItem(
            "ems-theme",
            isDark ? "dark" : "light"
        );

        updateThemeButton();
    });
}