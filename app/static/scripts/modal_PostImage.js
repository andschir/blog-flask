$(document).ready(function(){
  function* enumerate(iterable) {
    let i = 0;
    for (const x of iterable) {
        yield [i, x];
        i++;
    }
  }

  var modalDialog = document.getElementById('imageModal').querySelector(".modal-dialog");
  var postBodies = document.querySelectorAll(".post-body");
  var modalImage = document.getElementById('imageModal').querySelector(".modal-body").getElementsByTagName('img')[0];

  for (var [i, body] of enumerate(postBodies)) {
    if (!!body.getElementsByTagName('img')[0]) {
      imageList = body.getElementsByTagName('img');

      for (var [imgnumber, image] of enumerate(imageList)) {
        wrapper = document.createElement('div');
        parent = image.parentElement;
        parent.replaceChild(wrapper, image);
        wrapper.appendChild(image);

        div = image.parentElement;
        div.setAttribute('data-bs-target', "#imageModal");
        div.setAttribute('data-bs-toggle', "modal");
        div.classList.add('imageDiv');
      }
    }
  }

  $('#imageModal').on('hidden.bs.modal', function () {
    document.querySelector(".modal-caption").textContent = '';
  });

  $(".imageDiv").click(function() {
    var imageWidth = this.getElementsByTagName('img')[0].naturalWidth;
    var windowWidth = $(window).width();

    if (windowWidth > 1200) {
      if (imageWidth > 800) {
        modalDialog.style.maxWidth = '800px';
      } else {
        modalDialog.style.maxWidth = imageWidth + 'px';
      }
      modalDialog.style.margin = '0 auto';
    } else if (imageWidth > windowWidth) {
      modalDialog.style.maxWidth = '100%';
      modalDialog.style.margin = '0 auto';
    } else {
      modalDialog.style.maxWidth = imageWidth + 'px';
      modalDialog.style.margin = '0 auto';
    }

    src = this.getElementsByTagName('img')[0].getAttribute('src');
    modalImage.setAttribute('src', src);

    if (!!this.parentElement.getElementsByTagName('figcaption')[0]){
      document.querySelector(".modal-caption").textContent = this.parentElement.getElementsByTagName('figcaption')[0].textContent;
    }
  });

  function forceDownload(url) {
    var fileName = url.split('/').pop();
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.responseType = "blob";
    xhr.onload = function(){
        var urlCreator = window.URL || window.webkitURL;
        var imageUrl = urlCreator.createObjectURL(this.response);
        var tag = document.createElement('a');
        tag.href = imageUrl;
        tag.download = fileName;
        document.body.appendChild(tag);
        tag.click();
        document.body.removeChild(tag);
    }
    xhr.send();
  }

  $('#imageModal .download').on('click', function () {
    forceDownload(modalImage.getAttribute('src'));
  });
});