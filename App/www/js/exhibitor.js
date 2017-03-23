/* JS for the exhibititors QR-SCANNER-view*/

function infoUpdatedFeedback(){
    /* When connection info is succesfully saved: Sweetalerts-feedback*/
    swal({
        title: "Kontakt Uppdaterad",
        type: "success",
        confirmButtonColor: '#21D3A5',
        confirmButtonText: 'OK'
    },
    function(isConfirm){
        if (isConfirm) {
            window.location.reload();
        }
    });
};


function saveConnectionInfo(ConnectionInfo, ConnectionId){
    $.ajax({
        headers: User.getInfo(),
        type: 'POST',
        data: ConnectionInfo,
        url:'https://doltishkey.pythonanywhere.com/connection/'+ ConnectionId,
        traditional: true,
        success: function(response){
            json = $.parseJSON(response);
            if ( json == true){
                infoUpdatedFeedback();
            };
        },
        error: function(){
            $('h3').text(function(){
                return 'Ajax funka inte';
            });
        }
    });
};


function AjaxFrontEndId(id){
    /* When the searchfield user input is valid: a list of all attendants with the given ID is provided */
    $.ajax({
        headers: User.getInfo(),
        type: 'GET',
        url: 'https://doltishkey.pythonanywhere.com/attendant/' + id + '/',
        success: function(response){
            var json = $.parseJSON(response);
            if ( json !== false){
                $('#result ul').empty();
                var resultList = $('#result ul');
                $.each(json, function(index, value){
                    $(resultList).append('<li data-frontendid="' + value['front_end_id'] + '" data-userid="' + value['id'] + '">' + '<p>' + value["first_name"] + ': ' + value["email"] + '</p>' + '</li>');
                    return resultList;
                });

                $('#searchField').blur();
                $('#result ul li').click(function(){
                    /* För LIVE-VERSION
                    var theURL = 'https://doltishkey.pythonanywhere.com/attendant/' + $(this).attr('data-frontendid') + '/' + $(this).attr('data-userid');
                    */
                    var theURL = 'https://doltishkey.pythonanywhere.com/attendant/' + $(this).attr('data-frontendid') + '/' + $(this).attr('data-userid');
                    AjaxQR(theURL)
                })
                return;
            }
            else{
                $('#alertMessage').text(function(){
                    $('#result ul').empty();
                    return 'Det finns ingen med detta ID. Försök igen.';
                });
            }
        },
        error: function(){
            $('#alertMessage').text(function(){
                $('#result ul').empty();
                return 'Något gick fel. Ladda om sidan'
            });
        }
    });
};

function doLabelList(obj){
    /* Returns a list of tag-IDs korrensponding to the connection */
    var theList = []
    $.each(obj, function(i, tag){
        theList.push(tag.id);
    });
    return theList
};


function hideLabelMenu(){
    $('#infoBox').hide();
    $('#edithLabels').hide();
    $('#handleEveryLabel').hide();
};


function show_hide_info(){
    $('#handleEveryLabel').toggle(300);
    $('#infoBox').slideToggle(300);
};


function show_hide_labels(){
    var handleMyLabels = $('#handleEveryLabel');
    var formTags = $('#connectionForm').find('#tags');
    var myTags = $('#edithLabels');

    if( $(handleMyLabels).attr('class') == 'openHandleTags' ){
        $(handleMyLabels).removeClass('openHandleTags');
        $(handleMyLabels).text(function(){
            return 'Spara nya taggar'
        });
        $(handleMyLabels).css('background-color', '#0EB183');
    }
    else{
        $(handleMyLabels).addClass('openHandleTags');
        $(handleMyLabels).text( function(){
            return "Lägg till nya taggar"
        });
        $(handleMyLabels).css('background-color', '#21D3A5')
    }

    $(formTags).slideToggle(300);
    $(myTags).slideToggle(300);
};


function labelsOnConnection(myLabels, labelList){
    /* Provides a list of all the labels and the ones that is currently on a connection*/
    $.each( myLabels, function(index, label) {
        $('#completeLabelList').prepend('<li data-id="'+label.id+'" class="tags">\
            <p>'+label.text+'</p>\
            <div class="deleteLabel">X</div>\
        </li>');

        var connectionList = $('#connectionForm').find('#tags');
        if ( $.inArray(label.id, labelList) > -1 ){
            $(connectionList).prepend('<li class="tags chosenTag" data-id="'+ label.id + '">\
                <p>'+label.text +'</p>\
            </li>');
        }
        else{
            $(connectionList).prepend('<li class="tags" data-id="'+ label.id + '">\
                <p>'+label.text +'</p>\
            </li>');
        }
    });
};


function saveInfo(connectionID){
    var myComment = $('#comment').val();
    var myTags = $('.chosenTag').map(function(){
        return $(this).attr('data-id');
    }).get();

    var myInfo = {'label_nrs':myTags, 'comment':myComment};
    saveConnectionInfo(myInfo, connectionID);
}


function chooseLabel(thisobj){
    var tagClicked = thisobj
    if ( $(tagClicked).hasClass('chosenTag') ){
        $(tagClicked).removeClass('chosenTag');
    }
    else{
        $(tagClicked).addClass('chosenTag');
    }
}


function AjaxQR(x){
    /* x = the URL provided from AjaxFrontEndId or the QR code. */
    $.ajax({
        headers: User.getInfo(),
        type: 'POST',
        url:x,
        success: function(response){
            var json = $.parseJSON(response);
            if ( json !== false ){
                var labels = $.parseJSON(json.labels);
                var comments = json.connections.comment;
                if ( comments == null ){
                    var comments = "";
                }
                $('main').html('<section  class="QR">\
                    <div id="connectBox">\
                        <h3>' + json.connections.attendant.first_name + ' tillagd i dina kontakter ✓</h3>\
                        <div id="addInfo">Lägg till kommentar</div>\
                        <section id="infoBox">\
                        <div id="handleEveryLabel">Lägg till nya taggar</div>\
                            <div id="edithLabels">\
                                <ul id="completeLabelList">\
                                    <li class="tags" id="addTagBtn"><div id="addLabel">Ny Tagg<div id="plus">+</div></div></li>\
                                </ul>\
                                <div id="addLabelForm"></div>\
                            </div>\
                        <form id="connectionForm">\
                            <ul id="tags">\
                            </ul>\
                            <textarea id="comment">' + comments + '</textarea>\
                            <div id="saveInfoBtn">Spara</div>\
                        </form>\
                        </section>\
                    </div>\
                </section>')

                hideLabelMenu();
                $('#addInfo').click(function(){
                    show_hide_info();
                });
                $('#handleEveryLabel').on('click', function(){
                    show_hide_labels();
                });

                var labelList = doLabelList(json.connections.labels);
                labelsOnConnection(labels, labelList);

                $('#saveInfoBtn').click(function(){
                    saveInfo(json.connections.id);
                });

                $('#tags').on('click', '.tags', function(){
                    chooseLabel($(this));
                });
                addLable.eventHandlers();
                deleteLabel.eventHandler();
            }
            else{
                $('#alertMessage').text(function(){
                    $('#result ul').empty();
                    return "Något gick fel. Försök igen"
                });
            }
        },
        error: function(){
            window.location.href = '/utstallare/qr'
        }
    });
};


function validateAttendantID(input){
    /* check that the sign 3 to 6 is integers and sign 1-2 are letters */
    var checkNumbers = parseInt(input.substring(2,4)) + parseInt(input.substring(4,7));
    if ( Number.isInteger(checkNumbers) && !(Number.isInteger(parseInt(input.substring(0,2))))){
        return true;
    }
    else{
        return false;
    }
};


function searchForAttendant(){
    /* When user input >= 6: Validate the first 6 signs of the user input */
    $('#searchSection').submit(function(event){
        event.preventDefault(event)
    });

    $('#searchField').keyup(function    (){
        var inputVal = this.value;
        if ( inputVal.length >= 6 ){
            var sixthFirst = inputVal.substring(0,6);
            var valInput = validateAttendantID(sixthFirst)
            if ( valInput == true ){
                $('#result ul').empty();
                AjaxFrontEndId(sixthFirst);
            }
            else{
                $('#result ul').empty();
                $('#alertMessage').text(function(){
                    return 'Kontrollera ID'
                });
            };

        }
        else if ( inputVal.length <= 5 ){
            $('#result ul').empty();
            $('#alertMessage').text(function(){
                return 'Skanna QR eller ange ID'
            });
        };
    });
};


var addLable = (function(){

    var create = function(form){
        var text = $(form).find('input').first().val()
        if(text.length > 0 && text != ''){
            sendAjax(form)
        }
    };

    var createInput = function(){
        $('#addLabelForm').append(
            '<form class="newLabel" autocomplete="off">\
                <input type="text" name="labelName" placeholder="Skriv här">\
                <input type="submit" value="Spara">\
                <input type="button" class="cancelLabel" value="Avbryt">\
            </form>'
        );
        $('#addLabelForm').find('form').last().find('input').first().focus()
    };

    var createLabelNode = function(label){
        newLabelEdith = '<li data-id="'+label.id+'" class="tags">\
                        <p>'+label.text+'</p>\
                        <div class="deleteLabel">X</div>\
                    </li>'

        newLabel = '<li data-id="'+label.id+'" class="tags"><p>'+label.text+'</p></li>'
        $('#edithLabels').find('#completeLabelList').prepend(newLabelEdith);
        $('#connectionForm').find('#tags').prepend(newLabel);
        $('#content').children('#tags').prepend(newLabel);
        deleteLabel.eventHandler();
    };

    var sendAjax = function(form){
        $.ajax({
            headers: User.getInfo(),
            url: 'https://doltishkey.pythonanywhere.com/label/',
            type: 'POST',
            data:$(form).serialize(),
            dataType: 'JSON',
            success: function(response) {
                createLabelNode(response)
                $(form).remove();
            }
        });
    };

    var eventHandlers = function(){
        $('#addLabel').click(function(){
            createInput()
        });

        $('#addLabelForm').on('submit', '.newLabel', function(event){
            event.preventDefault(event);
            create(this)
        });

        $('#addLabelForm').on('click', '.cancelLabel', function(){
            $(this).parent().remove()
        });
    };

    return{
        eventHandlers:eventHandlers,
    };
}());


var deleteLabel = (function(){

    var eventHandler = function(){
        $('.tags').on('click', '.deleteLabel', function(){
            sendAjax($(this).parent())
        });
    }

    var sendAjax = function(element){
        id = element.data('id')
        $.ajax({
            headers: User.getInfo(),
            url: 'https://doltishkey.pythonanywhere.com/label/'+id,
            type: 'DELETE',
            dataType: 'JSON',
            success: function(response) {
                if(response == true){
                    $(element).remove();
                    var nodes = $('#connectionForm > #tags').find('li')
                    for(i = 0; i < nodes.length; i++){
                        if($(nodes[i]).data('id') == element.data('id')){
                            $(nodes[i]).remove()

                        }
                    }
                }
            }
        });
    };

    return{
        eventHandler:eventHandler,
    };
}());


var User = (function(){

    getInfo = function(){
        var token = $.parseJSON(localStorage.getItem("auth"))
        var id = $.parseJSON(localStorage.getItem("id"))
        return{'token':token, 'id':id}
    };

    return{
        getInfo:getInfo,
    }
}());


$( document ).ready(function(){
    searchForAttendant();
    addLable.eventHandlers()
    deleteLabel.eventHandler()
    User.getInfo()

    $('#starScan').click(function(){
        console.log('klickad!')
    });
    document.addEventListener("deviceready", onDeviceReady, false);
});


$(document).on('keydown', '#searchField', function (event) {
    $('#searchField').keydown(function() {
    if($(this).val().length > 4) {
         $('#qr-image').hide();
    } else {
         $('#qr-image').show();
    }
    });
});


function onDeviceReady() {
    $('.scanner').click(function(){
        cordova.plugins.barcodeScanner.scan(
              function (result) {
                  AjaxQR(result.text);
              },
              function (error) {
                  //alert("Scanning failed: " + error);
                  document.getElementById('alertMessage').innerHTML = 'Kunde inte läsa QR-koden, försök igen';
              },
              {
                  preferFrontCamera : false, // iOS and Android
                  showFlipCameraButton : false, // iOS and Android
                  showTorchButton : true, // iOS and Android
                  torchOn: true, // Android, launch with the torch switched on (if available)
                  prompt : "Place a barcode inside the scan area", // Android
                  resultDisplayDuration: 500, // Android, display scanned text for X ms. 0 suppresses it entirely, default 1500
                  formats : "QR_CODE,PDF_417", // default: all but PDF_417 and RSS_EXPANDED
                  orientation : "landscape", // Android only (portrait|landscape), default unset so it rotates with the device
                  disableAnimations : true, // iOS
                  disableSuccessBeep: true // iOS
              }
           );
    });
}

$(".addIcon").on("click", function(){
  $(this).css("filter", "grayscale(0%)");
});
