$(document).ready(function() {
  if (!!document.querySelector('.post')) {
    var modal = document.querySelector('#modal_outer');
    var delta; // initial vertical offset of modal-dialog area

    $('#imageModal').on('shown.bs.modal', function () {
      delta = modal.offsetTop;
      modal.scale = 1;
    });
    $('#imageModal').on('hidden.bs.modal', function () {
      modal.style.left = 0 +"px";
      modal.style.top = 0 + "px";
      modal.scale = 1;
      modal.style.transform = `scale(${modal.scale})`;
    });

    modal.addEventListener('wheel', e => {
      var deltaScale = (e.deltaY < 0) ? .1 : -.1;

      e.preventDefault();
      modal.scale = modal.scale + deltaScale;
      if (modal.scale < 0.5) { modal.scale = 0.5 };
      modal.style.transform = `scale(${modal.scale})`;
    });

    document.querySelector("#modal_inner").addEventListener("mousedown", function (e) {
      if (e.which == 1) { // serve left mouse button click only
        var mouseX = e.clientX;
        var mouseY = e.clientY;
        var modalX = modal.offsetLeft;
        var modalY = modal.offsetTop;

        window.ondragstart = function() { return false; } // disable default image dragging
        document.addEventListener("mousemove", move);

        function move(e) {
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
  }
});
