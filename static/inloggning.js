$("#logIn").submit(function(e){
  e.preventDefault();

  var input = $("#username");
  var is_email = input.val();
  if(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(is_email)){
    input.css("border", "1px solid #c7d0d2");
  }else{
    input.css("border", "1px solid red");
    $("#errorMessage1").show();
  }

  var input = $("#password");
  var is_password = input.val();
  if(is_password){
    input.css("border", "1px solid #c7d0d2");
  }else{
    input.css("border", "1px solid red");
    $("#errorMessage2").show();
  }

  $.ajax({
      url: "/login_ajax/",
      type: 'POST',
      data:$("form").serialize(),
      dataType: 'JSON',
      success: function(response) {
          if(response['logged_in']==true){
              window.location = response['url'];
          }
          else{
              console.log("Fel inloggningsuppgifter");
              $('#errorMessage3').show();
          };
      },
      error: function(response){
          console.log("Nu gick vi till error.");
      }
  });

});

$(document).ready(function() {
    $('#newPasswordForm').submit( function(e) {
        var password1 = $("#newPassword").val()
        var password2 = $("#confirmPassword").val()
        if (password1 != password2) {
            e.preventDefault();
            $('#newPasswordForm p').show();
        }
    });
})
