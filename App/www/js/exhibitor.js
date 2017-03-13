function infoUpdatedFeedback(){
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
        type: 'POST',
        data: ConnectionInfo,
        url:'/connection/'+ ConnectionId,
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
    $.ajax({
        type: 'GET',
        url: '/attendant/' + id + '/',
        success: function(response){
            var json = $.parseJSON(response);
            if ( json !== false){
                $('#result ul').empty();
                var resultList = $('#result ul');
                $.each(json, function(index, value){
                    $(resultList).append('<li data-frontendid="' + value['front_end_id'] + '" data-userid="' + value['id'] + '">' + '<p>' + value["first_name"] + ': ' + value["email"] + '</p>' + '</li>');
                    return resultList;
                });

                $('#result ul li').click(function(){
                    /* För LIVE-VERSION
                    var theURL = 'https://massa.avmediaskane.se/attendant/' + $(this).attr('data-frontendid') + '/' + $(this).attr('data-userid');
                    */
                    var theURL = '/attendant/' + $(this).attr('data-frontendid') + '/' + $(this).attr('data-userid');
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

    if( $(handleMyLabels).attr('class') == 'openHandleTags'){
        $(handleMyLabels).removeClass('openHandleTags');
        $(handleMyLabels).text(function(){
            return 'Klar'
        };
        $(handleMyLabels).css('background-color', '#0EB183')
    }
    else{
        $(handleMyLabels).addClass('openHandleTags');
        $(handleMyLabels).text( function(){
            return "Ändra taggar"
        }
        $(handleMyLabels).css('background-color', '#21D3A5')
    }

    $(formTags).slideToggle(300);
    $(myTags).slideToggle(300);
};


function labelsOnConnection(myLabels, labelList){
    $.each(myLabels, function(index, label){
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


function show_hide_info(){
    $('#handleEveryLabel').toggle(300);
    $('#infoBox').slideToggle(300);
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
    $.ajax({
        type: 'POST',
        url:x,
        success: function(response){
            var json = $.parseJSON(response);
            if (json !== false){
                var labels = $.parseJSON(json.labels);
                var comments = json.connections.comment;
                if (comments == null){
                    var comments = "";
                }
                $('main').html('<section  class="QR">\
                    <div id="connectBox">\
                        <h3>' + json.connections.attendant.first_name + ' tillagd i dina kontakter ✓</h3>\
                        <div id="addInfo">Lägg till kommentar</div>\
                        <section id="infoBox">\
                        <div id="handleEveryLabel">Ändra taggar</div>\
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
                </section>\
                <section id="contacts">\
                     <figure>\
                        <a href="/utstallare/qr">\
                            <svg class="addIcon" width="31px" height="31px" viewBox="0 0 31 31" version="1.1" xmlns="http://www.w3.org/2000/svg"\
                               xmlns:xlink="http://www.w3.org/1999/xlink">\
                                <g id="Page-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">\
                                    <g id="iPhone_added" transform="translate(-68.000000, -613.000000)" fill="#21D3A5">\
                                        <path d="M89.3125,629.46875 L84.46875,629.46875 L84.46875,634.3125 C84.46875,634.845312 84.0357188,635.28125 \   83.5,635.28125 C82.9642812,635.28125 82.53125,634.845312 82.53125,634.3125 L82.53125,629.46875 L77.6875,629.46875 C77.1517812,629.46875\ 76.71875,629.032812 76.71875,628.5 C76.71875,627.967188 77.1517812,627.53125 77.6875,627.53125 L82.53125,627.53125 L82.53125,622.6875\ C82.53125,622.154688 82.9642812,621.71875 83.5,621.71875 C84.0357188,621.71875 84.46875,622.154688 84.46875,622.6875 L84.46875,627.53125\ L89.3125,627.53125 C89.8482188,627.53125 90.28125,627.967188 90.28125,628.5 C90.28125,629.032812 89.8482188,629.46875 89.3125,629.46875\ L89.3125,629.46875 Z M83.5,613 C74.9391563,613 68,619.93625 68,628.5 C68,637.06375 74.9391563,644 83.5,644 C92.0608437,644 99,637.06375 99,628.5  C99,619.93625 92.0608437,613 83.5,613 L83.5,613 Z" id="Fill-25"></path> \
                                    </g> \
                                </g>\
                            </svg>\
                            <figcaption>Lägg till kontakt</figcaption>\
                        </a>\
                    </figure>\
                    <figure>\
                        <a href="/utstallare">\
                            <svg class="addIcon" width="31px" height="31px" viewBox="0 0 31 31" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"> \
                            <g id="Page-1" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">\
                                <g id="iPhone_added" transform="translate(-257.000000, -613.000000)">\
                                    <g id="Group-2" transform="translate(257.000000, 613.000000)">\
                                        <g id="Group">\
                                            <circle id="Oval-5" fill="#444" cx="15.5" cy="15.5" r="15.5"></circle>\
                                            <path d="M24.9097241,21.0580949 C25.6371537,22.267194 25.5777717,24.4125 25.5777717,24.4125 L5.42777171,24.4125 C5.42777171,24.4125 5.32974315,22.0888024 6.29964932,20.8797033 C6.84522155,20.3643495 8.56276373,18.6002541 11.4926886,18.1641856 C14.4024072,17.7479384 13.5133265,14.5765309 13.6143584,14.6161735 C13.7153903,14.6756373 13.594152,13.9422494 13.594152,13.9422494 C13.594152,13.9422494 11.4724823,11.9402984 11.4926886,10.1365604 C11.5331014,8.31300107 11.4926886,7.38140011 11.4926886,7.38140011 C11.4926886,7.38140011 11.8361971,3.1 14.8267411,3.1 L16.5038706,3.89285187 C19.1913189,3.89285187 19.6358593,7.38140011 19.6358593,7.38140011 L19.6358593,10.3942372 C19.6358593,10.3942372 19.2923508,12.9511845 17.6152214,13.8827855 C17.6152214,13.8827855 17.4939831,14.6161735 17.595015,14.5567096 C17.6960469,14.517067 16.7261407,17.7479384 19.6358593,18.1840069 C22.5657842,18.6002541 24.5258029,20.4039921 24.9097241,21.0580949 Z" id="Shape" fill="#FFFFFF"></path>\
                                            <path d="M15.5,29.45 C21.0642689,29.45 25.575,26.5931241 25.575,24.025 C25.575,21.4568759 21.0642689,18.6 15.5,18.6 C9.93573115,18.6 5.425,21.4568759 5.425,24.025 C5.425,26.5931241 9.93573115,29.45 15.5,29.45 Z" id="Oval-7" fill="#FFFFFF"></path>\
                                        </g>\
                                    </g>\
                                </g>\
                            </g>\
                        </svg>\
                            <figcaption>Kontakter</figcaption>\
                        </a>\
                    </figure>\
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
                return;

            }
            else{
                $('#alertMessage').text(function(){
                    $('#result ul').empty();
                    return "Något gick fel. Försök igen"
                });
            }
            return;
        },
        error: function(){
            console.log('ajax krasha');
            window.location.href = '/utstallare/qr'
        }
    });
};


function validateAttendantID(input){
    var checkNumbers = parseInt(input.substring(2,4)) + parseInt(input.substring(4,7));
    if ( Number.isInteger(checkNumbers) && !(Number.isInteger(parseInt(input.substring(0,2))))){
        return true;
    }
    else{
        return false;
    }
};


function searchForAttendant(){

    $('#searchSection').submit(function(event){
        event.preventDefault(event)
    });

    $('#searchField').keyup(function    (){
        var inputVal = this.value;

        if ( inputVal.length >= 6){
            var sixthFirst = inputVal.substring(0,6);
            var valInput = validateAttendantID(sixthFirst)
            if ( valInput == true){
                $('#result ul').empty();
                AjaxFrontEndId(sixthFirst);
                return;
            }
            else{
                $('#result ul').empty();
                $('#alertMessage').text(function(){
                    return 'Kontrollera ID'
                });
            };

        }
        else if ( inputVal.length <= 5){
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
            url: '/label/',
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
            url: '/label/'+id,
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


$( document ).ready(function(){
    searchForAttendant();
    addLable.eventHandlers()
    deleteLabel.eventHandler()

});
