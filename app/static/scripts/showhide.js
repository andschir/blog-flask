$(document).ready(function() {
  if (!!document.querySelector('.post')) {
    var em = parseFloat(getComputedStyle($(".post-body div").parent()[0]).fontSize);
    var divs = document.querySelectorAll('div.post-body-realsize');
    var showhides = document.querySelectorAll('div.showhide');
    var needed_height;
    var adjuster = 67;

    divs.forEach(function(div, divnumber) {
      var sizer = div.parentElement;
      var realsizer = sizer.children[0];
      if (!!div.getElementsByTagName('img')[0]) {
        var firstImage = div.getElementsByTagName('img')[0];
        sizer.setAttribute('style','transition: 0s');
        // TODO: Value in px is hardcoded. need container for showhide and post-edited
        sizer.style.height = (firstImage.height + adjuster) + 'px';
      }

      if (realsizer.clientHeight > sizer.clientHeight ) {
        showhides[divnumber].children[0].text = 'Показать полностью';
      }
    });

    $(".showhide a").on("click", function() {
      var $this = $(this);
      var parent = $this.parent().prev()[0]
      var content = $this.parent().prev().children()[0]
      var linkText;

      if (!!content.getElementsByTagName('img')[0]) {
        var firstImage = content.getElementsByTagName('img')[0];
        parent.setAttribute('style','');
        needed_height = (firstImage.height + adjuster) + 'px';
      }

      if (parent.clientHeight < content.clientHeight) {
        parent.style.height = content.clientHeight + 10 + "px";
        linkText = "Скрыть";
      } else {
        if (!!firstImage) {
          parent.style.height = needed_height;
        } else {
          parent.style.height = '7.5em'; // this value should correspond with .post-body-sizer [height] style
        }
        linkText = "Показать полностью";
      }

      $this.text(linkText);
      event.preventDefault()
    });
  }
});
