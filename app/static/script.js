$(function() {
    $('#remove_button_1').click(function() {
        $.ajax({
            url: '/remove_image',
            data: {id : 1},
        });
    });
});

$(function() {
    $('#remove_button_2').click(function() {
        $.ajax({
            url: '/remove_image',
            data: {id : 2},
        });
    });
});

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
                disable_buttons();
                grade_result(json_result);
              
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
               grade_result(json_result);

              
            }
        });
    });
});

$(function() {
    $('#not_sure_button').click(function() {
        $.ajax({
            url: '/record_vote',
            data: {choice : -1},
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
    $('#tied_button').click(function() {
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
               grade_result(json_result);
              
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

$(function() {
    $('#validate_next_button').click(function() {
        $.ajax({
            url: '/get_next_images_validation',
            success: update_images_validation
        })
        });
});


function update_images(data)
{
    json_result = jQuery.parseJSON(data);

    $("#image_1").attr('src',json_result.image_1_src)
    $("#image_1_link").attr('href', json_result.image_1_src)
    $("#image_1_title").html(json_result.image_1_title)
    $("#image_1_score").css('visibility', 'hidden')



    $("#image_2").attr('src',json_result.image_2_src)
    $("#image_2_link").attr('href', json_result.image_2_src)
    $("#image_2_title").html(json_result.image_2_title)
    $("#image_2_score").css('visibility', 'hidden')

    enable_buttons()
}

function update_images_validation(data)
{
    json_result = jQuery.parseJSON(data);

    $("#image_1").attr('src',json_result.image_1_src)
    $("#image_1_link").attr('href', json_result.image_1_src)
    $("#image_1_id").html(json_result.image_1_id)
    $("#image_1_title").html(json_result.image_1_title)

    // $("#image_1_score").css('visibility', 'hidden')



    $("#image_2").attr('src',json_result.image_2_src)
    $("#image_2_link").attr('href', json_result.image_2_src)
    $("#image_2_id").html(json_result.image_2_id)
    $("#image_2_title").html(json_result.image_2_title)

    // $("#image_2_score").css('visibility', 'hidden')

    // enable_buttons()
}


function grade_result(json_data)
{
    console.log(json_data)
    if(json_result.correct == 1)
    {
        $("#feedback_symbol").attr('src','../static/200px-Checkmark_green.svg.png')
        $("#feedback_symbol").attr('width','100%')

    }
    else
    {
        $("#feedback_symbol").attr('src','../static/200px-X_mark.svg.png')
        $("#feedback_symbol").attr('width','70%')

    }
    $("#feedback_symbol").css('visibility', 'visible')   
}

function disable_buttons()
{
    $("#next_button").prop('disabled',false);

    $("#vote_button_1").prop('disabled', true);
    $("#vote_button_2").prop('disabled', true);
    $("#not_sure_button").prop('disabled', true);
    $("#error_button").prop('disabled', true);

}

function enable_buttons()
{
    $("#next_button").prop('disabled',true);
    $("#feedback_symbol").css('visibility','hidden')


    $("#vote_button_1").prop('disabled', false);
    $("#vote_button_2").prop('disabled', false);
    $("#not_sure_button").prop('disabled', false);
    $("#error_button").prop('disabled', false);
}

