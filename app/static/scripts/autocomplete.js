$(document).ready(function() {
    $.ajax({}).done(function (data) {
        $('#tags').autocomplete({
            source:function(request, response) {
                $.getJSON("/autocomplete",{
                    autocomplete: request.term,
                }, function(data) {
                    response(data.json_list);
                });
            },
            minLength: 2,
        });
    });
});