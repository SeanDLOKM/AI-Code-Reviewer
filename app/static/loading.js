const form = document.getElementById("repo-form");
const button = document.getElementById("repo-submit");

form.addEventListener("submit", function () {
    button.classList.add("loading");
    button.disabled = true;
});