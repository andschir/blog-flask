$(document).ready(function() {
    // Title editor instance
    ClassicEditor
        .create( document.querySelector( '#title' ), {
            toolbar: {
                items: [
                    '|', 'sourceEditing',
                    '|', 'undo', 'redo',
                    '|', 'removeFormat',
                    '|', 'link',
                    '|', 'specialCharacters',
                    '|', 'italic', 'underline', 'strikethrough', 'subscript',
                        'superscript',
                    '|', 'fontColor', 'fontBackgroundColor',
                ],
                shouldNotGroupWhenFull: true
            },
        } )
        .then(editor => {
            editor.model.document.on('change', () => {
              if (countCharacters(editor.model.document) > 0) {
                document.querySelector('#title_empty').innerText = ''
              }
            });
        })
        .catch( error => {
            console.error( error );
        } );

    // Mention data-feed
    function getFeedItems( queryText ) {
        return new Promise( resolve => {
            $.ajax( {
                type: "GET",
                url: "/mention",
                data: { "mentionString": queryText.toLowerCase() },
                success: function ( response ) {
                    resolve( response.result );
                }
            } );
        } );
    }

    // Mention output customization
    function MentionCustomization( editor ) {
        editor.conversion.for( 'upcast' ).elementToAttribute( {
            view: {
                name: 'a',
                key: 'data-mention',
                classes: 'mention',
                attributes: {
                    href: true,
                    username: true,
                }
            },
            model: {
                key: 'mention',
                value: viewItem => {
                    const mentionAttribute = editor.plugins.get( 'Mention' ).toMentionAttribute( viewItem, {
                        link: viewItem.getAttribute( 'href' ),
                        username: viewItem.getAttribute( 'username' ),
                    } );

                    return mentionAttribute;
                }
            },
            converterPriority: 'high'
        } );

        editor.conversion.for( 'downcast' ).attributeToElement( {
            model: 'mention',
            view: ( modelAttributeValue, { writer } ) => {
                if ( !modelAttributeValue ) {
                    return;
                }
                console.log(modelAttributeValue.username)
                return writer.createAttributeElement( 'a', {
                    class: 'mention',
                    'data-mention': modelAttributeValue.id,
                    'username': modelAttributeValue.username,
                    'href': location.origin + '/user/' + modelAttributeValue.username
                }, {
                    // Make mention attribute to be wrapped by other attribute elements.
                    priority: 20,
                    // Prevent merging mentions together.
                    id: modelAttributeValue.uid
                } );
            },
            converterPriority: 'high'
        } );
    }

    // Body editor instance
    ClassicEditor
        .create( document.querySelector( '#body' ), {
            extraPlugins: ['SimpleUploadAdapter', MentionCustomization],
            simpleUpload: {
                uploadUrl: '/upload',
            },
            mediaEmbed: {previewsInData: true},
            mention: {
                feeds: [
                      {
                        marker: '@',
                        feed: getFeedItems,
                        minimumCharacters: 1,
                        dropdownLimit: 4,
                      }
                ]
            },
        } )
        .then(editor => {
            editor.model.document.on('change', () => {
              if (countCharacters(editor.model.document) > 0) {
                document.querySelector('#body_empty').innerText = ''
              }
            });
        })
        .catch( error => {
            console.error( error.stack );
        } );

    // Body character count
    function countCharacters(document) {
      const rootElement = document.getRoot();
      return countCharactersInElement(rootElement);

      function countCharactersInElement(node) {
        let chars = 0;

        for (const child of node.getChildren()) {
          if (child.is('text')) {
            chars += child.data.length;
          } else if (child.is('element')) {
            chars += countCharactersInElement(child);
          }
        }
        return chars;
      }
    }

    // Validating: no empty fields
    $(".form").submit(function(e) {
        var content = $('#body').val();
        html = $(content).text();
        if ($.trim(html) == '') {
            e.preventDefault();
            $.ajax({
                success: function(data) {
                    $('#body_empty').html('Пустое поле, введите текст!');
                }
            });
        }

        var content = $('#title').val();
        html = $(content).text();
        if ($.trim(html) == '') {
            e.preventDefault();
            $.ajax({
                success: function(data) {
                    $('#title_empty').html('Пустое поле, введите заголовок!');
                }
            });
        }
    });
});