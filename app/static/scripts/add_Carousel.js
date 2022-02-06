$(document).ready(function(){
  // Adding carousel classes to post-body images
  function* enumerate(iterable) {
    let i = 0;

    for (const x of iterable) {
        yield [i, x];
        i++;
    }
  }
  var postBody = document.querySelector(".post-body");
  var imageList = document.querySelector(".post-body").getElementsByTagName('img');
  var carouselList = document.querySelector(".carousel-inner").getElementsByTagName('div');

  postBody.id= "gallery";
//  postBody.setAttribute('data-bs-target', "#exampleModal");
//  postBody.setAttribute('data-bs-toggle', "modal");

  for (var [i, image] of enumerate(imageList)) {
    wrapper = document.createElement('div');

    image.classList.add("my-class");
    image.setAttribute('data-bs-target', "#carouselExample");
    image.setAttribute('data-slide-to', i);
//    image.setAttribute('data-bs-target', "#exampleModal");
//    image.setAttribute('data-bs-toggle', "modal");
    parent = image.parentElement;
    parent.replaceChild(wrapper, image);
    wrapper.appendChild(image);

    div = image.parentElement;
    div.setAttribute('data-bs-target', "#exampleModal");
    div.setAttribute('data-bs-toggle', "modal");

    src = image.getAttribute('src');

    carouselImg = carouselList[i].getElementsByTagName('img')[0]
    carouselImg.setAttribute('src', src);
  }

  for (var [i, carousel_element] of enumerate(carouselList)) {
//    console.log(carousel_element.getElementsByTagName('img')[0]);

  }


});