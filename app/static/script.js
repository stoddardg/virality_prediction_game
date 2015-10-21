// $(function() {
//      $('#image_1').on('click',function(){
//         var src = $(this).attr('src');
//         var img = '<img src="' + src + '" class="img-responsive"/>';
//         $('#myModal').modal();
//         $('#myModal').on('shown.bs.modal', function(){
//             $('#myModal .modal-body').html(img);
//         });
//         $('#myModal').on('hidden.bs.modal', function(){
//             $('#myModal .modal-body').html('');
//         });
//    });
// });

// $(function() {
//      $('#image_2').on('click',function(){
//         var src = $(this).attr('src');
//         var img = '<img src="' + src + '" class="img-responsive"/>';
//         $('#myModal').modal();
//         $('#myModal').on('shown.bs.modal', function(){
//             $('#myModal .modal-body').html(img);
//         });
//         $('#myModal').on('hidden.bs.modal', function(){
//             $('#myModal .modal-body').html('');
//         });
//    });
// });


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
                $("#image_1_score").html(data.image_1_karma);
                $("#image_2_score").html(data.image_2_karma);
                $("#image_1_score").css('visibility', 'visible');
                $("#image_2_score").css('visibility', 'visible');
                disable_buttons();
                grade_result(data);
              
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
                $("#image_1_score").html(data.image_1_karma);
                $("#image_2_score").html(data.image_2_karma);
                $("#image_1_score").css('visibility', 'visible');
                $("#image_2_score").css('visibility', 'visible');
               disable_buttons()
               grade_result(data);

              
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


function update_images(json_result)
{
    // json_result = jQuery.parseJSON(data);

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
    enable_buttons(json_result)
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
    console.log(json_data)

    if(json_data.correct == 1)
    {
        $("#next_button").attr('class','btn btn-success')
        $("#next_button").html("Correct!")
        if(json_data.user_choice == 1)
        {
            $("#vote_button_1").attr('class','btn btn-success')
            $("#vote_button_1").html("Correct!")
            $("#vote_button_2").attr('class','btn btn-danger')
            $("#vote_button_2").html("Wrong!")
        }
        else
        {
            $("#vote_button_2").attr('class','btn btn-success')
            $("#vote_button_2").html("Correct!")
            $("#vote_button_1").attr('class','btn btn-danger')
            $("#vote_button_1").html("Wrong!")
        }

    }
    else
    {
        $("#next_button").html("Wrong!")
        $("#next_button").attr('class','btn btn-danger')
        if(json_data.user_choice == 1)
        {
            $("#vote_button_1").attr('class','btn btn-danger')
            $("#vote_button_1").html("Wrong!")
        }
        else
        {
            $("#vote_button_2").attr('class','btn btn-danger')
            $("#vote_button_2").html("Wrong!")
        }



    }
    
    $("#num_correct").html(json_data['num_correct'])
    $("#num_wrong").html(json_data['num_wrong'])
    // $("#num_remaining").html(json_data['num_remaining'])


    if(json_data.end_of_game ==1 )
    {
        setTimeout(function(){window.location.href = '/end_game';}, 1500)    

    }
    else
    {
        next_button_clicked = 0
        setTimeout(click_next_button, 1500)

    }

    
}

function disable_buttons()
{

    $("#vote_button_1").prop('disabled', true);
    $("#vote_button_2").prop('disabled', true);

}

function enable_buttons(json_data)
{
    $("#feedback_symbol").css('visibility','hidden')
    $("#next_button").html("Skip Pair")
    $("#next_button").attr("class","btn btn-warning")
    $("#vote_button_1").attr("class","btn btn-info")
    $("#vote_button_1").html("More popular")
    $("#vote_button_2").attr("class","btn btn-info")
    $("#vote_button_2").html("More popular")

     console.log(json_data)

    $("#num_remaining").html(json_data['num_remaining'])


}


