$(document).ready(function() {
  function addEventListenerList(list, event, fn) {
      for (var i = 0, len = list.length; i < len; i++) {
          list[i].addEventListener(event, fn, false);
      }
  }

  function addOnClickList(list, value) {
      for (var i = 0, len = list.length; i < len; i++) {
          list[i].setAttribute('onclick', value);
      }
  }

  var deleteFormList = document.querySelectorAll('[action="/admin/post/delete/"]')
  var deleteBtnList = document.querySelectorAll('[title="Delete record"]')

  addOnClickList(deleteBtnList, 'return false;')

  addEventListenerList(deleteBtnList, 'click', function(e) {
    form = this.parentElement
    id = form.children[0].value

    if (confirm('Уверены, что хотите удалить эту запись?')) {
      $.ajax( {
          type: "POST",
          url: "/postpone_cancel",
          contentType: 'application/json',
          data: JSON.stringify({ id: id }),
          complete: function () {
              form.submit();
          }
      } );
    }
  });
});
