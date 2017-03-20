var dataList = [];

function getItems() {
    console.log('vill hämta kontakter')
    $.ajax({
        headers: User.getInfo(),
        url: 'https://doltishkey.pythonanywhere.com/exhibitor/contacts',
        method: 'GET',
        success: function(data){
            console.log(data)
            json = $.parseJSON(data);
            addItem(json);
            label.init(json['labels']);
        }
    });
 };



function addItem(data){

    dataList = data['connections'];
    myLabels = data['labels'];

    function compare(a,b) {
          if (a.attendant.first_name < b.attendant.first_name)
            return -1;
          if (a.attendant.first_name > b.attendant.first_name)
            return 1;
          return 0;
    }
    dataList.sort(compare);

    //console.log(dataList[0].attendant.email);

    for(i = 0; i < dataList.length; i++){
        if (dataList[i].comment == null) {
            dataList[i].comment = ''
        }
        labels = []
        labelText = []
        if( dataList[i].labels.length > 0){
            dataLabels = dataList[i].labels
            for (j = 0; j < dataLabels.length; j++){
                labels.push(dataLabels[j]['id']);
                labelText.push(' ' + dataLabels[j]['text']);
            };
        };

        labelString = JSON.stringify(labels)

        if(labelText.length > 0){
            labelTextItem = 'Taggar:' + labelText
        }
        else{
            labelTextItem = ''
        }


        $('#VisitorInfo').append(
            '<li data-tags="'+labelString+'" data-frontEnd-id="' +dataList[i].attendant.front_end_id+'" \
            data-id="'+dataList[i].attendant.id+'">\
                <p class="dataId">' +  dataList[i].attendant.id + '</p>\
                <p class="visitorName">' + dataList[i].attendant.first_name + ' ' + dataList[i].attendant.surname +'</p>\
                <p style="font-size:13px;">'+ labelTextItem +'</p>\
                <div class="changeInfo">Redigera Info</div>\
                <section class="overlay"></section>\
                <div class="showMe">\
                    <p>"' + dataList[i].comment + '"</p>\
                    <table>\
                    <thead>\
                          <tr>\
                            <th>Email</th>\
                            <th>Skola</th>\
                            <th>Kommun</th>\
                          </tr>\
                        </thead>\
                        <tbody>\
                          <tr>\
                            <td>' + dataList[i].attendant.email + '</td>\
                            <td>' + dataList[i].attendant.school + '</td>\
                            <td>' + dataList[i].attendant.commune + '</td>\
                          </tr>\
                        </tbody>\
                        <thead>\
                            <tr>\
                            <th>Yrkesroll</th>\
                            <th>Årskurser</th>\
                            <th>Ämnen</th>\
                            </tr>\
                        </thead>\
                        <body>\
                            <tr>\
                            <td>' + dataList[i].attendant.profession + '</td>\
                            <td>' + dataList[i].attendant.teaching_years + '</td>\
                            <td>' + dataList[i].attendant.subjects + '</td>\
                            </tr>\
                        </body>\
                    </table>\
                </div>\
            </li>'
        );
    };

    $('.visitorName').click(function(){
        toggleDisplay(this);
    })
    $('.changeInfo').hide();
    $('.overlay').hide();

    $('.changeInfo').click(function(event){
        var thisParent = event.target.parentNode;
        var frontendID = $(thisParent).attr('data-frontEnd-id');
        var backendID = $(thisParent).attr('data-id');
        for (k = 0; k < dataList.length; k++){
            if (dataList[k].attendant.id == backendID){
                editInfo(dataList[k], myLabels, thisParent);
            }
        }
    });
};


function editInfo(connections, myLabels, parentObj, clicked_button){
    var myVar = $(parentObj).find('.overlay');
    $(myVar).html('<div id="close-overlay">X</div>\
            <div id="handleEveryLabel">Ändra taggar</div>\
            <section id="infoBox">\
                <div id="edithLabels">\
                    <ul id="completeLabelList">\
                        <li class="tags" id="addTagBtn"><div id="addLabel">Ny Tagg<div id="plus">+</div></div></li>\
                    </ul>\
                    <div id="addLabelForm"></div>\
                </div>\
                <form id="connectionForm">\
                    <ul id="tags">\
                    </ul>\
                    <textarea id="comment">' + connections.comment + '</textarea>\
                    <div id="saveInfoBtn">Spara</div>\
                </form>\
            </section>');

    $('#close-overlay').click(function(){
        $(myVar).html('')
        $(myVar).slideToggle(300);
    });
    $(myVar).slideToggle(300);

    hideLabelMenu();
    show_hide_info();
    $('#handleEveryLabel').on('click',function(){
        show_hide_labels();
    });

    var myLabels = $.parseJSON(myLabels);
    connectionLabels = doLabelList(connections.labels)
    labelsOnConnection(myLabels, connectionLabels);

    $('#saveInfoBtn').click(function(){
        saveInfo(connections.id);
    });

    $('#connectionForm').find('#tags').on('click', '.tags', function(){
        chooseLabel($(this));
    });
    addLable.eventHandlers();
    deleteLabel.eventHandler();
    return;
}

//Visar en bekräftelse på att användaren vill ta bort utställare/besökare
function confirmDelete() {

    //var clickedItem = item.parentNode.childNodes[2];
    //var user = item.parentNode.childNodes[1];
    //var mail = $(clickedItem).text();
    user = 'Me'
    mail = 'Text'

    //user = $(user).text();


    swal({
        title: "Är du säker på att du vill ta bort ?" ,
        text: "Detta går inte att ångra.",
        type: "warning",
        showCancelButton: true,
        confirmButtonColor: "#FF465D",
        confirmButtonText: "Ta bort utställare",
        cancelButtonText: "Avbryt",
        closeOnConfirm: false,
        closeOnCancel: false },

        function(isConfirm) {
            if (isConfirm) {
                deleteItem(item);
                swal("Borttagen!", user + " har blivit borttagen", "success");
            } else {
                swal("Avbruten", "Ingenting togs bort", "success");   } });
}

//Tar bort utställare/besökare
function deleteItem(item) {
    console.log('Användaren togs bort på låtsas');
}

//Confirmbox för att skicka mail till utställare/besökare
function confirmEmail(item) {

    var clickedItem = item.parentNode.childNodes[2];
    var user = item.parentNode.childNodes[1];
    var mail = $(clickedItem).text();

    user = $(user).text();

    swal({
        title: "Är du säker på att du vill skicka mail till " + user + "?" ,
        text: "Detta går inte att ångra.",
        type: "info",
        showCancelButton: true,
        confirmButtonColor: "#21D3A5",
        confirmButtonText: "Skicka mail",
        cancelButtonText: "Avbryt",
        closeOnConfirm: false,
        closeOnCancel: false },

        function(isConfirm) {
            if (isConfirm) {
                sendEmail(item);
                swal("Skickat!", user + " har fått ett mail", "success");
            } else {
                swal("Avbruten", "Ingenting skickades", "success");   } });
}

//Skicka mail till vald utställare/besökare från listan
function sendEmail(item) {

    var clickedItem = item.parentNode.childNodes[2];
    var mail = $(clickedItem).text();

    console.log(mail);
}

//Visar innehåll för ett specifikt list item
function toggleDisplay(clicked) {
    var myParent = $(clicked).parent();
    $(myParent).find(".showMe").slideToggle(200, 'linear');
    $(myParent).find(".changeInfo").slideToggle(200, 'linear');
}
//Ta bort tagg
$(document).ready(function(){
    $(".tags").on("taphold",function(){
        var answer = confirm("Är du säker på att du vill ta bort denna tagg?");
        if (answer == true) {
            $(this).remove();
        } else {
        }
  });
});

//Filtrera efter tagg
$(document).ready(function(){
    var selectedTags = [];
    $(".tags").on("click",function(){
        var tagName = $(this).text();

        selectedTags.push(tagName);
        console.log(selectedTags);


        if (selectedTags === undefined || selectedTags.length == 0) {
            selectedTags.push(tagName);
            console.log('Sparat!');
        } else if (selectedTags.includes(tagName)) {
            selectedTags.splice(tagName);
            console.log('Borttaget');
        } else {
            selectedTags.push(tagName);
            console.log('Sparat!');
                        }
    console.log(selectedTags);
    });
});

        /*for (var i = 0; i < dataList.length; i++) {
            if (dataList[i].attendant.subjects == tagName) {
                console.log(dataList[i]);
            }
        }*/

var label = (function(){

    var state = {
        'labelDisplay':[]
    }

    var init = function(labels){
        labels = $.parseJSON(labels)
        for(i = 0; i < labels.length; i++){
            $('#tags').append(
                '<li class="tags" data-label-val="'+labels[i].id+'">'+labels[i].text+'</li>'
            );
        }
        eventHandler()
    }

    var eventHandler = function(){
        $('.tags').click(function(){
            clicked = $(this).data('label-val')
            indexOfCliked = $.inArray(clicked, state.labelDisplay);
            if(indexOfCliked == -1){
                state.labelDisplay.push($(this).data('label-val'));
                $(this).addClass('active')
            }
            else{
                state.labelDisplay.splice(indexOfCliked, 1)
                $(this).removeClass('active')
            }
            updateContactList()
        });
    };

    var updateContactList = function(){
        contacts = $('#VisitorInfo').find('li')
        $(contacts).each(function(){
            if(state.labelDisplay.length == 0){
                $(this).show();
            }
            else{
                /*try{
                    var contactLabels = $.makeArray($(this).data('tags').split(','));
                }
                catch(err){
                    var contactLabels = $.makeArray($(this).data('tags'));
                }*/
                var contactLabels = $.makeArray($(this).data('tags'));
                var display = []
                var length = contactLabels.length
                for(i = 0; i < length; i++){
                    if($.inArray(parseInt(contactLabels[i]), state.labelDisplay) != -1){
                        display.push(true)
                    }
                    else{
                        display.push(false)
                    }
                }
                if($.inArray(true, display) != -1){
                    $(this).show();
                }
                else{
                    $(this).hide();
                }
            }
        });
    };



    return{
        init:init,
    }

}());

var ajaxComponents = (function(){

    var state = {}

    var setUrl = function(){
        if(window.location.href.indexOf("attendant") > -1) {
            return 'https://doltishkey.pythonanywhere.com/attendant/'
        }
        else{
            return 'https://doltishkey.pythonanywhere.com/exhibitor/'
        }
    };

    var sendAjax = function(url){
        $.ajax({
            headers: User.getInfo(),
            url: url,
            type: state.delete ? 'DELETE' : 'POST',
            dataType: 'JSON',
            success: function(response) {
                if(state.delete == true){
                    removeNode()
                }
                else{
                    removeSpinner()
                }
            }
        });
    };

    var eventListenerRemove = function(){
        $('.listButton.delete').click(function(){
            state.clickedItem = this
            state.node = $(this).parent()
            state.delete = true
            userName = state.node.find('p').first().text()
            var confirmer = confirm("Vill du verkigen ta bort "+ userName +"?");
            if (confirmer == true) {
                remove(state.node)
            }
        });
    };

    var eventListenerMail = function(){
        $('.listButton.mail').click(function(){
            state.clickedItem = this
            state.node = $(this).parent()
            state.delete = false
            userName = state.node.find('p').first().text()
            var confirmer = confirm("Vill du skicka mejl igen till "+ userName +"?");
            if (confirmer == true) {
                mail(state.node)
            }
        });
    };

    var btnToSpinner = function(){
        newImg = state.delete ? 'delete_loader' : 'mail_loader';
        $(state.clickedItem).attr("src", '/static/img/'+newImg+'.png');
        $(state.clickedItem).addClass('spin')
    };

    var remove = function(){
        id = state.node.data('id')
        url = setUrl()+id
        btnToSpinner()
        sendAjax(url)
    }

    var mail = function(){
        id = state.node.data('id')
        url = setUrl()+id+'/sendemail/'
        btnToSpinner()
        sendAjax(url)
    }

    var removeSpinner = function(){
        $(state.clickedItem).attr("src", '/static/img/complete_mail.png');
        $(state.clickedItem).removeClass('spin')
    };

    var removeNode = function(){
        $(state.node).toggle(1000)
    };

    return{
        eventListenerRemove:eventListenerRemove,
        eventListenerMail:eventListenerMail,
    }


}());


var addExhibitor = (function(){

    var sendAjax = function(form){
        $('#spinner').show()
         $(":submit").attr("disabled", true);
        $.ajax({
            headers: User.getInfo(),
            url: "https://doltishkey.pythonanywhere.com/exhibitor/",
            type: 'POST',
            data:$(form).serialize(),
            dataType: 'JSON',
            success: function(response) {
                $('#spinner').hide()
                $(":submit").removeAttr("disabled");
                if (response.status == true){
                    message.success('Utställaren är tillagd!')
                    $('.target').val('');
                }
                else{
                    message.error('Något gick fel', response.error)
                }
            }
        });
    };

    var eventListener = function(){
        $('#add_exhibitor_form').submit(function(event){
            event.preventDefault(event);
            sendAjax(this);
        });
    };

    return{
        eventListener:eventListener,
    }

}());


var message = (function(){

    var clear = function(){
        $('#message').html('')
    };

    var flash = function(node){
        $('#message').append(node)
        $('#message').toggle()
        window.setTimeout(function(){
            $('#message').toggle(1500)
        }, 4000)
    };

    var error = function(message, errors){
        clear()
        node = '<p id="error_message">'+message+'</p>'
        flash(node)
    };

    var success = function(message){
        clear()
        node = '<p id="success_message">'+message+'</p>'
        flash(node)
    };

    return{
        error:error,
        success:success,
    }
}());

$(document).ready(function() {
    if(window.location.href.indexOf("index") > -1) {
           getItems();
    }
    addExhibitor.eventListener();
    ajaxComponents.eventListenerMail();
    ajaxComponents.eventListenerRemove();
});
