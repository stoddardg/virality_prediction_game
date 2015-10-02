$(function() {
    $('#vote_button_1').click(function() {
        $.ajax({
            url: '/record_vote',
            data: {choice : 1},
            success: function(data ) {
                json_result = jQuery.parseJSON(data);
                $("#image_1_score").html(json_result.image_1_karma);
                $("#image_2_score").html(json_result.image_2_karma);
                $("#image_1_score").css('visibility', 'visible');
                $("#image_2_score").css('visibility', 'visible');
                disable_buttons()
              
            }
        });
    });
});


$(function() {
    $('#vote_button_2').click(function() {
        $.ajax({
            url: '/record_vote',
            data: {choice : 2},
            success: function(data ) {
                json_result = jQuery.parseJSON(data);
                $("#image_1_score").html(json_result.image_1_karma);
                $("#image_2_score").html(json_result.image_2_karma);
                $("#image_1_score").css('visibility', 'visible');
                $("#image_2_score").css('visibility', 'visible');
               disable_buttons()
              
            }
        });
    });
});

$(function() {
    $('#not_sure_button').click(function() {
        $.ajax({
            url: '/record_vote',
            data: {choice : 0},
            success: function(data ) {
                json_result = jQuery.parseJSON(data);
                $("#image_1_score").html(json_result.image_1_karma);
                $("#image_2_score").html(json_result.image_2_karma);
                $("#image_1_score").css('visibility', 'visible');
                $("#image_2_score").css('visibility', 'visible');
               disable_buttons()
              
            }
        });
    });
});

$(function() {
    $('#error_button').click(function() {
        $.ajax({
            url: '/log_error',
            data: {choice : -1},
            success: update_images
        });
    });
});


$(function() {
    $('#next_button').click(function() {
        $.ajax({
            url: '/get_next_images',
            success: update_images
        })
        });
});



function update_images(data)
{
    json_result = jQuery.parseJSON(data);

    $("#image_1").attr('src',json_result.image_1_src)
    $("#image_1_title").html(json_result.image_1_title)
    $("#image_1_score").css('visibility', 'hidden')


    $("#image_2").attr('src',json_result.image_2_src)
    $("#image_2_title").html(json_result.image_2_title)
    $("#image_2_score").css('visibility', 'hidden')

    enable_buttons()

}

function disable_buttons()
{
    // $("#next_button").removeClass('disabled');
    $("#next_button").prop('disabled',false);

    $("#vote_button_1").prop('disabled', true);
    $("#vote_button_2").prop('disabled', true);
    $("#not_sure_button").prop('disabled', true);
    $("#error_button").prop('disabled', true);


    // $("#vote_button_1").addClass('disabled');
    // $("#vote_button_2").addClass('disabled');
    // $("#not_sure_button").addClass('disabled');
    // $("#error_button").addClass('disabled');
}

function enable_buttons()
{
    $("#next_button").prop('disabled',true);

    $("#vote_button_1").prop('disabled', false);
    $("#vote_button_2").prop('disabled', false);
    $("#not_sure_button").prop('disabled', false);
    $("#error_button").prop('disabled', false);
    // $("#next_button").addClass('disabled');
    // $("#vote_button_1").removeClass('disabled');
    // $("#vote_button_2").removeClass('disabled');
    // $("#not_sure_button").removeClass('disabled');
    // $("#error_button").removeClass('disabled');
}

