(function(){
    var auth = $.parseJSON(localStorage.getItem("auth"));
    if (auth === null){
        window.location = "inloggning.html";
    }

}());
