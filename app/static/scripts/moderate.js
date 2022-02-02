$(document).ready(function () {
  var comment_admin = document.querySelector('.comment_admin');
  $(".moderate_checkbox").click(function() {
    if($(this).next().hasClass('moderate_checkbox_active')) {
      $(this).next().removeClass('moderate_checkbox_active');
      comment_admin.style.display = "none";
    }
    else {
      $(this).next().addClass('moderate_checkbox_active');
      comment_admin.style.display = "inline";
    }
   });
});