$(document).ready(function(){
  $(".showhide a").on("click", function() {
    var $this = $(this);
    var parent = $this.parent().prev()[0]
    var content = $this.parent().prev().children()[0]
    var linkText = $this.text().toUpperCase();

    if (parent.clientHeight < content.clientHeight) {
      parent.style.height = content.clientHeight + 10 + "px";
      linkText = "Скрыть";
    } else {
      parent.style.height = '5em';
      linkText = "Показать полностью";
    }

    $this.text(linkText);
    event.preventDefault()
  });
});
