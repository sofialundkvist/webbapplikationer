function callAjax(email){
    var mejl = JSON.stringify(email)
    return $.ajax({
        url: "/email_check",
        type: 'POST',
        data:{'mejl': mejl},
        dataType: 'JSON'
    });
};

function validateEmail(email){
    /*
        - Validerar email
        - Returerar ett booleanskt värde
    */
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(email)){
        return (true)
    }
    return (false)
};


function validatzor(thisobj){
    /*
        - Validerar ett värde i ett (this)
        - Presenterar felmeddelande
        - returnerar booleanskt värde
    */
    var thisValue = $(thisobj).val()
    var x = $(thisobj).parent();
    if ( !thisValue ){
        $(thisobj).css('border-color', 'red');
        $(thisobj).addClass('opaAni');
        $(x).children('.errorMsg').addClass('opaAni');
        $(x).children('.errorMsg').show();
        return false;
    }
    else if ( thisValue[0] == ' ') {
        var thisValue = thisValue.replace(thisValue[0],'');
        $(thisobj).val(thisValue);
        return validatzor(thisobj);

    }
    else if ( $(thisobj).attr('name') == 'email') {
        if ( !(validateEmail($(thisobj).val()) )){
            $(thisobj).css('border-color', 'red');
            $(thisobj).addClass('opaAni');
            $(x).children('.errorMsg').addClass('opaAni');
            $(x).children('.errorMsg').text('Skriv in en giltig email')
            $(x).children('.opaAni').show();
            //var myBool = false;
            return false;
        }
        else {
            $.when( callAjax($(thisobj).val())).done(function(response){
                //AJAX-validering
                if ( response['email'] == true ) {
                    console.log('1');
                    $(thisobj).css('border-color', '#ccc');
                    $(thisobj).removeClass('opaAni');
                    $(x).children('.errorMsg').removeClass('opaAni');
                    $(x).children('.errorMsg').hide();
                    //var myBool = true
                    //return (theBool)
                    return true;
                }
                else {
                    console.log('2');
                    $(thisobj).css('border-color', 'red');
                    $(thisobj).addClass('opaAni');
                    $(x).children('.errorMsg').addClass('opaAni');
                    $(x).children('.errorMsg').text('Angiven email är upptagen')
                    $(x).children('.opaAni').show();
                    return false;

                }
            });
            $(thisobj).css('border-color', '#ccc');
            $(thisobj).removeClass('opaAni');
            $(x).children('.errorMsg').removeClass('opaAni');
            $(x).children('.errorMsg').hide();
            return true;
        }
    }
    else {
        $(thisobj).css('border-color', '#ccc');
        $(thisobj).removeClass('opaAni');
        $(x).children('.errorMsg').removeClass('opaAni');
        $(x).children('.errorMsg').hide();
        //var myBool = true;
        return true;
    }
};


function scrollToError(){
    $('html, body').animate({
        scrollTop: $('.scrollHere').offset().top
    }, 300);
}


function addScrollClass(errorList){
    $.each(errorList, function( j ){
        if ( j == 0 ){
            var childOfParent = $(this).parent().children('p');
            $('span').parent().children('p').removeClass('scrollHere');
            childOfParent.addClass('scrollHere');
        };
    });
};


function checkInputs(){
    /*
        - Loopar igenom en lista av input-värden (.target)
        - Validerar dessa
        - Returnerar ett booleanskt värde beroende på om input-värderna validerar korrekt
    */
    var proceedCounter = 0
    var myArray = $('.target');
    $.each(myArray, function( i ){
        if( !(validatzor( $(this) )) || $(this).parent().children('.errorMsg').hasClass('opaAni')) {
            proceedCounter += 1
        };
    });

    var inputErrors = $('.opaAni');
    if (inputErrors.length > 0 ){
        addScrollClass(inputErrors);
    };

    if ( proceedCounter > 0 ){
        scrollToError();
        return (false);
    }
    else {
        return (true);
    };

};


var ajaxSubmit = (function(){

    var init = function(){
        eventListener()
    };


    var setSpinner = function(){
        $('.send').disabled = true;
        $('.send').hide();
        $('#spinner').show();
    };

    var removeSpinner = function(){
        $('.send').disabled = false;
        $('.send').show();
        $('#spinner').hide();
    }

    var sendAjax = function(form){
        $.ajax({
            type: 'POST',
            url: '/attendant/',
            data: $(form).serialize(),
            success: function(response) {
                var json = $.parseJSON(response);
                if(json['attend']=='True'){
                    window.location = json['url'];
                }
                else{
                    removeSpinner();
                    handleErrors(json['errors']);
                }
            },
            error: function(response){
                removeSpinner();
                $('#fatal_error').show();
            }
        });
    };

    var handleErrors = function(data){
        for (var k in data) {
            if (data.hasOwnProperty(k)) {
                if(data[k] == false){
                    var errorDict = mapper(k)
                    $(errorDict['parent']).children(errorDict['child']).css('border-color', 'red');
                    $(errorDict['parent']).children('.errorMsg').addClass('opaAni');
                    $(errorDict['parent']).children('.errorMsg').text(errorDict['error'])
                    $(errorDict['parent']).children('.errorMsg').show();
                }
            }
        }
        checkInputs();
    };

    var mapper = function(k){
        errorDict = {
            'exists':{
                'parent':$('#email'),
                'error': 'Angiven email är upptagen.',
                'child': 'input'
            },
            'first_name':{
                'parent': $('#firstName'),
                'error': 'Fältet får inte vara tomt.',
                'child': 'input'
            },
            'surname': {
                'parent': $('#surName'),
                'error': 'Fältet får inte vara tomt.',
                'child': 'input'
            },
            'email':{
                'parent': $('#email'),
                'error': 'Skriv in en giltig email.',
                'child': 'input'
            },
            'birth_month':{
                'parent': $('#birthDate'),
                'error': 'Du måste välja ett alternativ i listan.',
                'child': 'select'
            },
            'birth_day':{
                'parent': $('#birthDate'),
                'error': 'Du måste välja ett alternativ i listan.',
                'child': 'select'
            },
        }
        return errorDict[k]
    };

    var eventListener = function(){
        $('#attend_form').submit(function(event){
            event.preventDefault(event);
            setSpinner();
            sendAjax(this);
        });
    };


    return{
        init:init,
    };
}());


/*ONLOAD  - .ready */
$( document ).ready(function() {
    $( ".target").change(function(){
        validatzor( $(this) );
    });
    $('.example-5 .send').click(function(){
        var go = checkInputs();
        return go
    });
});


//To print out the qr-code
$(document).ready(function() {
    $("#printbutton").click(function(){
        window.print();
    });
    ajaxSubmit.init();
});
