/* =========================================================
   REVTECH INSTITUTE
   Main JavaScript
   ========================================================= */


/* ---------- SOCIAL HUB ---------- */

const socialHub = document.querySelector(".social-hub");
const socialToggle = document.querySelector(".social-toggle");

if (socialHub && socialToggle) {

    socialToggle.addEventListener("click", () => {

        socialHub.classList.toggle("active");

    });

}


/* ---------- MOBILE MORE MENU ---------- */

const moreButton = document.getElementById(
    "mobile-more-button"
);

const moreMenu = document.getElementById(
    "mobile-more-menu"
);

const closeMoreMenu = document.getElementById(
    "close-more-menu"
);


if (moreButton && moreMenu) {

    moreButton.addEventListener("click", () => {

        moreMenu.classList.toggle("active");

    });

}


if (closeMoreMenu && moreMenu) {

    closeMoreMenu.addEventListener("click", () => {

        moreMenu.classList.remove("active");

    });

}


/* Close More menu when clicking outside */

document.addEventListener("click", (event) => {

    if (
        moreMenu &&
        moreButton &&
        moreMenu.classList.contains("active") &&
        !moreMenu.contains(event.target) &&
        !moreButton.contains(event.target)
    ) {

        moreMenu.classList.remove("active");

    }

});

/* ---------- ACTIVE MOBILE NAV ---------- */

const currentPath = window.location.pathname;

const mobileNavItems = document.querySelectorAll(
    ".mobile-bottom-nav > a"
);

mobileNavItems.forEach((item) => {

    const itemPath = new URL(
        item.href
    ).pathname;

    if (
        currentPath === itemPath ||
        (
            itemPath !== "/" &&
            currentPath.startsWith(itemPath)
        )
    ) {

        item.classList.add("active");

    }

});