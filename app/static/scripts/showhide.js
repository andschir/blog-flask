$(document).ready(function() {
    var em = parseFloat(getComputedStyle($(".post-body div").parent()[0]).fontSize);
    var divheight = $(".post-body div").children().parent()[0].clientHeight/em;
    var divs = document.querySelectorAll('div.post-body-realsize');
    var showhides = document.querySelectorAll('div.showhide');
    var needed_height;

    divs.forEach(function(div, divnumber) {
      var sizer = div.parentElement;
      var realsizer = sizer.children[0];
      if (!!div.getElementsByTagName('img')[0]) {
        var firstImage = div.getElementsByTagName('img')[0];
        firstImage.onload = function() {
          var firstImageSize = firstImage.parentElement.clientHeight;
        }
        sizer.setAttribute('style','transition: 0s');
        // TODO: Value in px is hardcoded. need container for showhide and post-edited
        sizer.style.height = (firstImage.height + 60) + 'px';
      }

      console.log(realsizer.clientHeight);
      console.log(sizer.clientHeight);
      if (realsizer.clientHeight > sizer.clientHeight ) {
            showhides[divnumber].children[0].text = 'Показать полностью';
      }
    });

    $(".showhide a").on("click", function() {
      var $this = $(this);
      var parent = $this.parent().prev()[0]
      var content = $this.parent().prev().children()[0]
      var linkText = $this.text().toUpperCase();

      if (!!content.getElementsByTagName('img')[0]) {
        var firstImage = content.getElementsByTagName('img')[0];
        firstImage.onload = function() {
          var firstImageSize = firstImage.parentElement.clientHeight;
        }
        parent.setAttribute('style','');
        needed_height = (firstImage.height + 60) + 'px';
      }

      if (parent.clientHeight < content.clientHeight) {
        parent.style.height = content.clientHeight + 10 + "px";
        linkText = "Скрыть";
      } else {
        if (!!firstImage) {
          parent.style.height = needed_height;
        } else {
          parent.style.height = '5em';
        }
        linkText = "Показать полностью";
      }

      $this.text(linkText);
      event.preventDefault()
    });
});
