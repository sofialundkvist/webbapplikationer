(function(){

    console.log('Körs')
    var auth = $.parseJSON(localStorage.getItem("auth"));
    if (auth === null){
        window.location = "inloggning.html";
    }

    $('#logOut').click(function(){
        console.log('Logga ut')
        localStorage.clear();
        window.location = "inloggning.html";
    });

}());
