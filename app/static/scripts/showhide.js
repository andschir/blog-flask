$(document).ready(function() {
    var em = parseFloat(getComputedStyle($(".post-body div").parent()[0]).fontSize);
    var divheight = $(".post-body div").children().parent()[0].clientHeight/em;
    var divs = document.querySelectorAll('div.post-body-realsize');
    var showhides = document.querySelectorAll('div.showhide');
    var needed_height;

//    window.addEventListener("wheel", event => {
//      const delta = Math.sign(event.deltaY);
//      console.info(delta);
//    });

    function zoom(event) {
      event.preventDefault();

      scale += event.deltaY * -0.01;

      // Restrict scale
      scale = Math.min(Math.max(1, scale), 4);

      // Apply scale transform
      el.style.transform = `scale(${scale})`;
    }

    let scale = 0.1;
    const el = document.querySelector('#imageModal');
    el.onwheel = zoom;


    divs.forEach(function(div, divnumber) {
      if (div.clientHeight/em > divheight) {
            showhides[divnumber].children[0].text = 'Показать полностью';
      }
      var sizer = div.parentElement;
      if (!!div.getElementsByTagName('img')[0]) {
        var firstImage = div.getElementsByTagName('img')[0];
        firstImage.onload = function() {
          var firstImageSize = firstImage.parentElement.clientHeight;
        }
        sizer.setAttribute('style','transition: 0s');
        // TODO: Value in px is hardcoded. need container for showhide and post-edited
        sizer.style.height = (firstImage.height + 60) + 'px';
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
