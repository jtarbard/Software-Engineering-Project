$(document).ready(function() {
    $("#cookies").ready(function(){
        $("#cookies").slideDown("slow");
    });
    $("#CookieAccept").click(function () {
        document.cookie = "cookie_accept=True;";
        $("#cookies").slideUp("slow");
        $("#invisible").fadeOut("slow");
    });

    $('.alert').alert();
    setTimeout(function() {
        $(".alert").alert('close');
    }, 5000);
});
