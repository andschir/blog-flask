function check() {
    var em = parseFloat(getComputedStyle($(".post-body div").parent()[0]).fontSize);
    var divheight = $(".post-body div").children().parent()[0].clientHeight/em;
    var divs = document.querySelectorAll('div.post-body-realsize');
    var showhides = document.querySelectorAll('div.showhide');

    divs.forEach(function(div, divnumber) {
        if (div.clientHeight/em > divheight) {
            showhides[divnumber].children[0].text = 'Показать полностью';
        }
    });
}
document.addEventListener("DOMContentLoaded", check);