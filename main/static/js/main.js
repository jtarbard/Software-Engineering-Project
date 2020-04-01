

$(document).ready(function() {

    $('.alert').alert();

    setTimeout(function() {
        $(".alert").alert('close');
    }, 5000);
});
