
/* RevTech main homepage navigation */

document.addEventListener("DOMContentLoaded", function () {
    const menuButton = document.getElementById("rth-menu-toggle");
    const navLinks = document.getElementById("rth-nav-links");

    if (!menuButton || !navLinks) {
        return;
    }

    function closeMenu() {
        navLinks.classList.remove("is-open");
        menuButton.classList.remove("is-open");
        menuButton.setAttribute("aria-expanded", "false");
        menuButton.setAttribute("aria-label", "Open navigation menu");
    }

    menuButton.addEventListener("click", function () {
        const isOpen = navLinks.classList.toggle("is-open");

        menuButton.classList.toggle("is-open", isOpen);
        menuButton.setAttribute("aria-expanded", String(isOpen));
        menuButton.setAttribute(
            "aria-label",
            isOpen ? "Close navigation menu" : "Open navigation menu"
        );
    });

    navLinks.querySelectorAll("a").forEach(function (link) {
        link.addEventListener("click", closeMenu);
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    window.addEventListener("resize", function () {
        if (window.innerWidth > 700) {
            closeMenu();
        }
    });
});
