$(document).ready(function(){
  // Adding modals  to Post images
  function* enumerate(iterable) {
    let i = 0;

    for (const x of iterable) {
        yield [i, x];
        i++;
    }
  }

  var imageList = document.querySelector(".post-body").getElementsByTagName('img');
  var modalImage = document.getElementById('imageModal').querySelector(".modal-body").getElementsByTagName('img')[0];

  for (var [i, image] of enumerate(imageList)) {
    wrapper = document.createElement('div');

    parent = image.parentElement;
    parent.replaceChild(wrapper, image);
    wrapper.appendChild(image);

    div = image.parentElement;
    div.setAttribute('data-bs-target', "#imageModal");
    div.setAttribute('data-bs-toggle', "modal");
    div.classList.add('imageDiv');
  }

  $(".imageDiv").click(function() {
    src = this.getElementsByTagName('img')[0].getAttribute('src');
    modalImage.setAttribute('src', src);
  });
});