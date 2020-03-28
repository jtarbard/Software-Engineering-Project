//Loads the cookie box if the user has not accepted cookies

$(document).ready(function() {
    $("#cookies").ready(function(){
        $("#cookies").slideDown("slow");
    });
    $("#CookieAccept").click(function () {
        document.cookie = "cookie_accept=True;";
        $("#cookies").slideUp("slow");
        $("#invisible").fadeOut("slow");
    });
});
