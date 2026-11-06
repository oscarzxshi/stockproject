document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".clickable-row").forEach(function (row) {
        row.style.cursor = "pointer";

        row.addEventListener("click", function (event) {
            // let real links and buttons inside the row do their own thing
            if (event.target.closest("a, button")) return;
            window.location.href = row.dataset.href;
        });
    });
});