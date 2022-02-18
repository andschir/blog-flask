$(document).ready(function() {
    var draftId; // id of saved draft for newly created Post OR id of post being edited

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
                document.querySelector('#title_empty').innerText = '';
                document.querySelector('#editor-autosave-status').classList.add( 'busy' );
                displayStatus(editor);
              };
              setTimeout( () => {
                editorBody.config._config.autosave.save(editorBody);
                document.querySelector('#editor-autosave-status').classList.remove( 'busy' );
                displayStatus(editor);
                }, 3000
              );
            });
            window.editorTitle = editor;
        })
        .catch( error => {
            console.error( error );
        } );

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
            autosave: {
              waitingTime: 3000,
              save( editor ) {
                if (document.querySelector('#editor-autosave-status').hidden == false && countCharacters(editor.model.document) > 0) {
                    inputFields = $(".form").serializeArray();
                    inputFields.splice(0, 1); // delete CSRF token
                    inputFields[0].value = editorTitle.getData(); // replace Title and Body with cke data
                    inputFields[1].value = editorBody.getData();
                    return saveData( inputFields );
                }
              }
            },
        } )
        .then(editor => {
            editor.model.document.on('change', () => {
              if (countCharacters(editor.model.document) > 0) {
                document.querySelector('#body_empty').innerText = '';
              };
            });
            window.editorBody = editor;
            displayStatus( editorBody );
        })
        .catch( error => {
            console.error( error.stack );
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

    function saveData( array ) {
        return new Promise( resolve => {
            if (draftId) {
              array.push(draftId);
            }
            json = JSON.stringify({ input_fields: array });
            $.ajax( {
                type: "POST",
                url: "/autosave",
                contentType: 'application/json;charset=utf-8',
                dataType: 'json',
                data: json,
                success: function ( response ) {
                    resolve();
                }
            } );
        } );
    }

    function displayStatus( editor ) {
        const pendingActions = editor.plugins.get( 'PendingActions' );
        const statusIndicator = document.querySelector('#editor-autosave-status');
        btn_save = document.querySelector('#btn_save')

        if (!!btn_save) {
          if (statusIndicator.hidden == false && statusIndicator.classList.contains('busy')) {
            btn_save.classList.add( 'disabled' );
          } else {
            btn_save.classList.remove( 'disabled' );
          }
        }

        pendingActions.on( 'change:hasAny', ( evt, propertyName, newValue ) => {
            if ( newValue ) {
                statusIndicator.classList.add( 'busy' );
                if (!!btn_save && statusIndicator.hidden == false) {
                  btn_save.classList.add( 'disabled' );
                }
            } else {
                statusIndicator.classList.remove( 'busy' );
                if (!!btn_save && statusIndicator.hidden == false) {
                  btn_save.classList.remove( 'disabled' );
                }
            }
        } );
    }

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

    function createDraft() {
        return new Promise( resolve => {
            $.ajax( {
                type: "POST",
                url: "/create_draft",
                success: function ( response ) {
                  resolve( draftId = response.draft_id );
                  document.querySelector('#btn_create_draft').textContent = 'Черновик создан';
                  document.querySelector('#btn_create_draft').disabled = true;
                  document.querySelector('#btn_publish').value = 'publish_draft';
                  document.querySelector('#btn_postpone').value = 'postpone_draft';
                  document.querySelector('.page-header').textContent = `Черновик #${draftId}`
                  editorBody.config._config.autosave.save(editorBody);
                  document.querySelector('#editor-autosave-status').hidden = false;
                }
            } );
        } );
    }

    if ( window.location.href.match(/edit/) ) {
      postId = window.location.href.substring(window.location.href.lastIndexOf('/') + 1).slice(0, -1);
      draftId = postId;
      document.querySelector('#editor-autosave-status').hidden = false;
    } else if ( window.location.href.match(/create/) ) {
      document.querySelector('#btn_create_draft').addEventListener('click', (event) => {
        event.preventDefault();
        createDraft();
      });
    }

    // Validating: no empty fields
    $(".form").submit(function(e) {
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
    });
});