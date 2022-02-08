$(document).ready(function() {
    var modal = document.querySelector('#modal_outer');
    var delta;

    modal.scale = 1;

    modal.addEventListener('wheel', e => {
      var deltaScale = (e.deltaY < 0) ? .1 : -.1;

      e.preventDefault();
      modal.scale = modal.scale + deltaScale;
      modal.style.transform = `scale(${modal.scale})`;
    });

    $('#imageModal').on('shown.bs.modal', function () {
      delta = modal.offsetTop;
    });
    $('#imageModal').on('hidden.bs.modal', function () {
      modal.style.left = 0 +"px";
      modal.style.top = 0 + "px";
    });

    document.querySelector("#modal_inner").addEventListener("mousedown", function (e) {
      if (e.which == 1) { // Left mouse button only
        var mouseX = e.clientX;
        var mouseY = e.clientY;
        var modalX = modal.offsetLeft;
        var modalY = modal.offsetTop;

        window.ondragstart = function() { return false; }
        document.addEventListener("mousemove", move);

        function move(e){
          var mouse_dx = e.clientX - mouseX;
          var mouse_dy = e.clientY - mouseY;

          modal.style.position = 'relative';
          modal.style.left = modalX + mouse_dx + "px";
          modal.style.top = modalY + mouse_dy - delta + "px";
        }
        document.addEventListener("mouseup", function () {
          document.removeEventListener("mousemove", move);
        })
      }
    })
});
