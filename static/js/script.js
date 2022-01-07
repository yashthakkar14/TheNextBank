$(function () {
    $(document).scroll(function () {
        var $nav = $("#main-navbar");
        $nav.toggleClass("scrolled", $(this).scrollTop() > $nav.height());
    });
});

function toggleButton() {
    var x = document.getElementById("main-navbar");
    if (x.className === "navbar") {
        x.className += " responsive";
    } else {
        x.className = "navbar";
    }
}