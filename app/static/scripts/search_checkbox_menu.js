$(document).ready(function(){
  $(".search-checkbox-menu").on("change", "input[type='checkbox']", function() {
    $(this).closest("li").toggleClass("active", this.checked);
  });
  $('body').on('click', '.search-checkbox-menu', function (e) {
    e.stopPropagation();
  });
});
