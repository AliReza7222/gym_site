$(document).ready(function() {

    $('#send-link').click(function(e) {
        $('#load-message').html('Please wait, the code will be sent soon  .....');
        $('#load').removeClass('hide');
        e.preventDefault(); // prevent the link from navigating to a new page
        $.ajax({
            url: 'create_code/', // replace with your own URL
            type: 'GET',
            dataType: 'json',
            success: function(response) {
                $('#load').addClass('hide');
                $('#message').html(response.message);
                $('#info-msg').show();
                $('#timer').removeClass('hide');
                var timeleft = 80; // set the countdown timer for 80 seconds
                var downloadTimer = setInterval(function(){
                    timeleft--;
                    $('#timer').text( " Code expiration time : " + '   '+ "00:" + timeleft + " " + 'sec');
                    $('#timer').css('background-color', '#ABF5F2');
                    if(timeleft <= 0){
                        clearInterval(downloadTimer);
                        $('#timer').addClass('hide');
                        $('#timer').css('background-color', '#FFFFFF');
                        $('#message-error').html('Time is up try again !');
                        $('#error').show();
                    }
                }, 1000);
            },
            error: function(xhr, status, error) {
                console.log('Error:', error);
                $('#load').addClass('hide');
                $('#message-error').html("A problem occurred, the code could not be sent, try again.");
                $('#error').show();
            }
        });
    });

});
