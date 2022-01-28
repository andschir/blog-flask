$(document).ready(function() {
    $.ajax({
        url: '../autocomplete'
    }).done(function (data) {
        $('#tags').autocomplete({
            source:function(request, response) {
                $.getJSON("autocomplete",{
                    autocomplete: request.term,
                }, function(data) {
                    response(data.json_list);
                });
            },
            minLength: 2,
        });
    });
});