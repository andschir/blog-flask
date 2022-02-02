$(document).ready(function () {
    var goToTopButton = document.getElementById("gototop_button");
    window.onscroll = function() {
        scrollFunction()
        };
    function scrollFunction() {
      if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        goToTopButton.style.display = "block";
      } else {
        goToTopButton.style.display = "none";
      }
    };
    $("#gototop_button").click(function() {
        $('html,body').animate({ scrollTop: 0 }, 'fast');
        document.body.scrollTop = 0; // For Safari
    });
});