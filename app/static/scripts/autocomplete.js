$(document).ready(function() {
    $.ajax({}).done(function (data) {
        $("#tags").on("keydown", function(event) {
            if (event.keyCode === $.ui.keyCode.TAB &&
            $(this).autocomplete("instance").menu.active) {
                event.preventDefault();
                }
        });
        $('#tags').autocomplete({
            minLength: 0,
            source:function(request, response) {
                $.getJSON("/autocomplete",{
                    autocomplete: request.term,
                }, function(data) {
                    response(data.json_list);
                });
            },
            focus: function() {
                return false;
            },
            select: function(event, ui) {
                var terms = this.value.split( /,\s*/ );
                terms.pop();
                terms.push(ui.item.value);
                terms.push("");
                this.value = terms.join(", ");
                return false;
            },
            open: function( event, ui ) {
                var input = $( event.target ),
                    widget = input.autocomplete( "widget" ),
                    style = $.extend( input.css( [
                        "font",
                        "border-left",
                        "padding-left"
                    ] ), {
                        position: "absolute",
                        visibility: "hidden",
                        "padding-right": 0,
                        "border-right": 0,
                        "white-space": "pre"
                    } ),
                    div = $( "<div/>" ),
                    pos = {
                        my: "left top",
                        collision: "none"
                    },
                    offset = -3; // magic number to align the text field
                widget.css( "width", "" );
                div
                    .text( input.val().replace( /\S*$/, "" ) )
                    .css( style )
                    .insertAfter( input );
                offset = Math.min(
                    Math.max( offset + div.width(), 0 ),
                    input.width() - widget.width()
                );
                div.remove();
                pos.at = "left+" + offset + " bottom";
                input.autocomplete( "option", "position", pos );
                widget.position( $.extend( { of: input }, pos ) );
            },
        });
    });
});