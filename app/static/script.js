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



var next_button_clicked = 0;
$(function() {
    $('#next_button').click(function() {
        next_button_clicked = 1
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
    $("#image_1").on('load', function(){
        $("#image_1_link").attr('href', json_result.image_1_src)
        $("#image_1_title").html(json_result.image_1_title)
        $("#image_1_score").css('visibility', 'hidden')
        $("#vote_button_1").prop('disabled', false);

    })
    $("#image_2").attr('src',json_result.image_2_src)
    $("#image_2").on('load',function(){
        $("#image_2_link").attr('href', json_result.image_2_src)
        $("#image_2_title").html(json_result.image_2_title)
        $("#image_2_score").css('visibility', 'hidden')
        $("#vote_button_2").prop('disabled', false);

    })
    enable_buttons()
}

function update_images_validation(data)
{
    json_result = jQuery.parseJSON(data);

    $("#image_1").attr('src',json_result.image_1_src)
    $("#image_1_link").attr('href', json_result.image_1_src)
    $("#image_1_id").html(json_result.image_1_id)
    $("#image_1_title").html(json_result.image_1_title)

    $("#image_2").attr('src',json_result.image_2_src)
    $("#image_2_link").attr('href', json_result.image_2_src)
    $("#image_2_id").html(json_result.image_2_id)
    $("#image_2_title").html(json_result.image_2_title)

}



function click_next_button(){
    if(next_button_clicked == 0)
    {    
        $("#next_button").click()
        next_button_clicked = 1
    }
}

function grade_result(json_data)
{

    if(json_result.correct == 1)
    {
        $("#feedback_symbol").attr('src','../static/200px-Checkmark_green.svg.png')
        $("#feedback_symbol").attr('width','100%')

    }
    else
    {
        $("#feedback_symbol").attr('src','../static/200px-X_mark.svg.png')
        $("#feedback_symbol").attr('width','100%')

    }
    
    $("#feedback_symbol").one('load', function(){
        $("#feedback_symbol").css('visibility', 'visible')   
        $("#correct_percentage").html(json_data['percent_correct'])
    })

    if(json_data.show_survey == 1)
    {
        $("#survey_message").css('visibility','visible')
    }

    next_button_clicked = 0
    setTimeout(click_next_button, 1000)
}

function disable_buttons()
{

    $("#vote_button_1").prop('disabled', true);
    $("#vote_button_2").prop('disabled', true);

}

function enable_buttons()
{
    $("#feedback_symbol").css('visibility','hidden')
}

