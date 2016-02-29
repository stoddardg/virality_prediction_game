
var q1_answered = 0 
var q1_answer;
var q2_answered = 0
var q2_answer;
var q3_answered = 0 
var q3_answer;
var q4_answered = 0;
var q4_answer;
var q5_answered = 0;
var q5_answer;


$(function() {
    $('#q1-btn-group button').click(function() {
        $('#q1-btn-group button').prop('disabled',true);

        $('#q1-btn-group button').removeClass('btn-danger').addClass('btn-success ');
        $(this).addClass('btn-danger').removeClass('btn-success ');

        q1_answered = 1
        q1_answer = this.innerHTML
        show_peer_scores()


    });
});

$(function() {
    $('#q2-btn-group button').click(function() {
        $('#q2-btn-group button').prop('disabled',true);
        $('#q2-btn-group button').removeClass('btn-danger').addClass('btn-success ');
        $(this).addClass('btn-danger').removeClass('btn-success ');
        q2_answered = 1
        q2_answer = this.innerHTML
        show_peer_scores()


    });
});

$(function() {
    $('#q3-btn-group button').click(function() {
        $('#q3-btn-group button').prop('disabled',true);
        $('#q3-btn-group button').removeClass('btn-danger').addClass('btn-success ');
        $(this).addClass('btn-danger').removeClass('btn-success ');


        q3_answered = 1
        q3_answer = this.innerHTML
        show_peer_scores()


    });
});

$(function() {
    $('#q4-btn-group button').click(function() {
        $('#q4-btn-group button').prop('disabled',true);
        $('#q4-btn-group button').removeClass('btn-danger').addClass('btn-success ');
        $(this).addClass('btn-danger').removeClass('btn-success ');


        q4_answered = 1
        q4_answer = this.innerHTML
        show_peer_scores()


    });
});

$(function() {
    $('#q5-btn-group button').click(function() {
        $('#q5-btn-group button').prop('disabled',true);
        $('#q5-btn-group button').removeClass('btn-danger').addClass('btn-success ');
        $(this).addClass('btn-danger').removeClass('btn-success ');


        q5_answered = 1
        q5_answer = this.innerHTML
        show_peer_scores()


    });
});


$(function() {
    $('#opinion_question_first #opinion_button_1').click(function() {
        $(this).addClass('btn-warning').removeClass('btn-success ');
        record_opinion(1)
        $("#opinion_question_first #opinion_question").fadeOut("slow", function(){
        $("#opinion_question_first #prediction_question").css("visibility","visible").hide().fadeIn("slow")
    })

    });
});

$(function() {
    $('#opinion_question_first #opinion_button_2').click(function() {
        console.log("2 hi")
        $(this).addClass('btn-warning').removeClass('btn-success ');
        record_opinion(2)
        $("#opinion_question_first #opinion_question").fadeOut("slow", function(){
        $("#opinion_question_first #prediction_question").css("visibility","visible").hide().fadeIn("slow")
    })


    });
});






$(function() {
    $('#opinion_question_first #vote_button_1').click(function() {
        $('#vote_button_2').removeClass('btn-warning').addClass('btn-success ');
        $(this).addClass('btn-warning').removeClass('btn-success ');
        record_guess(1);
    });
});


$(function() {
    $('#opinion_question_first #vote_button_2').click(function() {
        $('#vote_button_1').removeClass('btn-warning').addClass('btn-success ');
        $(this).addClass('btn-warning').removeClass('btn-success ');
        record_guess(2);
    });
});


$(function() {
    $('#guess_question_first #opinion_button_1').click(function() {
        $(this).addClass('btn-warning').removeClass('btn-success ');
        $("#guess_question_first #opinion_question").fadeOut("slow", function(){
            record_opinion(1)
        })

    
    });
});

$(function() {
    $('#guess_question_first #opinion_button_2').click(function() {
        $(this).addClass('btn-warning').removeClass('btn-success ');
        console.log("WOOOOO2")
        $("#guess_question_first #opinion_question").fadeOut("slow", function(){
            record_opinion(2)
        })
        // record_opinion(2)


    });
});

$(function() {
    $('#guess_question_first #vote_button_1').click(function() {
        record_guess(1,function(){
        $("#guess_question_first #prediction_question").fadeOut("slow", function(){
        $("#guess_question_first #opinion_question").css("visibility","visible").hide().fadeIn("fast")
    })
    })

    });
});


$(function() {
    $('#guess_question_first #vote_button_2').click(function() {
        record_guess(2,function(){
        $("#guess_question_first #prediction_question").fadeOut("slow", function(){
        $("#guess_question_first #opinion_question").css("visibility","visible").hide().fadeIn("fast")
    })
    })
    });
});




$(function() {
    $('#guess-question-only #vote_button_1').click(function() {
        current_opinion = -1;
        opinion_ready = 1;
        record_guess(1);
    });
});


$(function() {
    $('#guess-question-only #vote_button_2').click(function() {
        opinion_ready = 1;
        current_opinion = -1;
        record_guess(2);
    });
});


function show_peer_scores()
{
    if(q1_answered == 1 && q2_answered == 1 && q3_answered ==1 && q4_answered==1 && q5_answered==1)
    {
        // $("#survey").attr("hidden", "true")
        $("#survey").fadeOut('slow', function(){

        $("#peer-scores").show()
        })
        $.ajax({
            url: '/record_survey_result',
            data: {q1_answer : JSON.stringify(q1_answer),
                    q2_answer: JSON.stringify(q2_answer),
                    q3_answer : JSON.stringify(q3_answer),
                    q4_answer : JSON.stringify(q4_answer),
                    q5_answer : JSON.stringify(q5_answer),

            },

            });



    }
}





var image_data;
function update_images(json_result)
{
    $("#image_1").attr('src',images[current_pair].image_1_url)

    $("#image_2").attr('src',images[current_pair].image_2_url)

}


var current_subreddit;

var current_pair;

var total_questions; 

var images;

var num_correct;

var user_choices = [];
var user_opinions = [];
var guess_times = [];

var user_choice_correct = [];

var image_1_reddit_id = [];

var image_2_reddit_id = [];


var image_1_loaded = 0;
var image_2_loaded = 0;

var image_load_time = 0;

$(document).ready(function(){

   $("#image_1").on('load', function(){

        image_1_loaded=1;
        display_image_data();

    })

    $("#image_2").on('load',function(){
        image_2_loaded=1;
        display_image_data();
    })


if(window.location.pathname == '/')
{ 
    console.log("hi")
    $.ajax({
            url: '/get_starting_data',
                success: function(data ) {

                console.log("loaded page called")
                current_pair = 0;
                total_questions = data.images.length;
                images = data.images;
                current_subreddit = data.current_subreddit;
                update_images();
                num_correct = 0;
                image_load_time = Date.now();
            }
        });
}

});

$( window ).resize(function() {
  resize_images_and_title()
});


function resize_images_and_title()
{




    $(".title_container").css("height", "")
    $("#outer_image_container").css("height","1000px")
    $("#image_row").css("height","1000px")
    $(".image_column").css("height","1000px")
    $(".image_title_container").css("height","1000px")
    $(".image_container").css("height", "1000px")


    console.log("outer_image_container height " + $("#outer_image_container").height())

    $('body').css('overflow', 'hidden')


    var current_page_height = $(window).height()
    console.log(current_page_height)


    max_image_height = Math.min( current_page_height*.333, Math.max($("#image_1").height(), $("#image_2").height())   )
    $(".image_container").css("height", max_image_height+"px")







    $("#image_1_link").attr('href', images[current_pair].image_1_lightbox_src)
    $("#image_1_title").css("font-size","")
    $("#image_1_title").html(images[current_pair].image_1_title)

    $("#image_2_link").attr('href', images[current_pair].image_2_lightbox_src)
    $("#image_2_title").css("font-size","")
    $("#image_2_title").html(images[current_pair].image_2_title)


    image_1_title = $("#image_1_title")
    image_1_title_height = image_1_title.height()
    
    image_2_title = $("#image_2_title")
    image_2_title_height =  image_2_title.height()


    max_title_height = Math.min($(".title_container").height(), Math.max(image_1_title_height, image_2_title_height))
    $(".title_container").css("height", (max_title_height+1)+"px")


    container_height = max_title_height + max_image_height

    $("#outer_image_container").css("height", container_height+"px")
    $("#image_row").css("height", container_height+"px")
    $(".image_column").css("height", container_height+"px")
    $(".image_title_container").css("height", container_height+"px")

    console.log("container_height " + container_height)





    console.log("max title height " + max_title_height)
    while( image_1_title_height >= max_title_height)
    {
        console.log("in loop")
        var font_size = parseFloat($("#image_1_title").css("font-size"))
        image_1_title.css("font-size", (font_size -1) + "px")
        image_1_title_height = image_1_title.height()
    }

    while( image_2_title_height >= max_title_height)
    {
        console.log("in loop")

        var font_size = parseFloat($("#image_2_title").css("font-size"))
        image_2_title.css("font-size", (font_size -1) + "px")
        image_2_title_height = image_2_title.height()
    }


    $('body').css('overflow', 'auto');


}

function display_image_data()
{

    if( image_1_loaded == 0)
    {
        return
    }
    if(image_2_loaded == 0)
    {
        return
    }

    resize_images_and_title()


    
    // $("#image_1_score").css('visibility', 'hidden')
    $("#image_1_score").html("   ")
    $("#vote_button_1").prop('disabled', false);

    $("#image_2_score").html("   ")

    // $("#image_2_score").css('visibility', 'hidden')
    $("#vote_button_2").prop('disabled', false);

    $("#image_1").css("opacity","1")
    $("#image_2").css("opacity","1")

    enable_buttons(image_data)
}




function advance_images(){
    current_pair = current_pair + 1
    update_images()
}

var opinion_ready = 0
var guess_ready = 0

var current_opinion = 0
var current_guess = 0

function record_opinion(user_opinion)
{
    console.log("record_opinion called")
    current_opinion = user_opinion
    user_opinions.push(current_opinion)
    opinion_ready = 1

    grade_result()
}

function record_guess(user_choice, callback)
{
    guess_ready = 1
    current_guess = user_choice

    user_choices.push(current_guess)

    elapsed_time = (Date.now() - image_load_time)/1000

    console.log(elapsed_time)

    guess_times.push(elapsed_time)

    $("#image_1_score").html(images[current_pair].image_1_score);
    $("#image_2_score").html(images[current_pair].image_2_score);
    // $("#image_1_score").css('visibility', 'visible');
    // $("#image_2_score").css('visibility', 'visible');


    user_choice = current_guess

    var correct_answer;
    if(images[current_pair].image_1_score == images[current_pair].image_2_score)
    {
        user_correct = 1;
        num_correct = num_correct + 1;
    }
    else
    {
        if(images[current_pair].image_1_score >= images[current_pair].image_2_score)
        {
            correct_answer = 1;
        }
        else{
            correct_answer = 2;
        }

        if(user_choice == correct_answer)
        {
            user_correct = 1;
            num_correct  = num_correct + 1;
        }
        else
        {
            user_correct = 0;
        }
    }
    user_choice_correct.push(user_correct)
    image_1_reddit_id.push(images[current_pair].image_1_reddit_id)
    image_2_reddit_id.push(images[current_pair].image_2_reddit_id)



    if(user_correct == 1)
    {
        $("#next_button").attr('class','btn btn-success')
        $("#next_button").html("Correct!")
        if(user_choice == 1)
        {
            $("#vote_button_1").attr('class','btn btn-success')
            $("#vote_button_1").html("Correct!")
        }
        else
        {
            $("#vote_button_2").attr('class','btn btn-success')
            $("#vote_button_2").html("Correct!")
        }

    }
    else
    {
        $("#next_button").html("Wrong!")
        $("#next_button").attr('class','btn btn-danger')
        if(user_choice == 1)
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


    // grade_result()
    setTimeout(function()
    {
        grade_result();
        if (callback && typeof(callback) == "function")
        {
            callback();
        }
    }, 1500)
}


function grade_result()
{

    if(opinion_ready == 0 || guess_ready == 0)
    {
        return
    }

    disable_buttons();


    
    var end_of_game = 0;
    if(current_pair == total_questions - 1)
    {
        end_of_game = 1
    }
    if(end_of_game ==1 )
    {
        $.ajax({
            url: '/record_all_votes',
            data: {votes : JSON.stringify(user_choices),
                    user_choice_correct: JSON.stringify(user_choice_correct),
                    image_1_reddit_ids : JSON.stringify(image_1_reddit_id),
                    image_2_reddit_ids : JSON.stringify(image_2_reddit_id), 
                    current_subreddit : JSON.stringify(current_subreddit),
                    opinion_votes: JSON.stringify(user_opinions),
                    guess_times: JSON.stringify(guess_times),

            },
            success : function(){
                setTimeout(function(){window.location.href = '/end_game'}, 1500) }


            });

    }
    else
    {
        advance_images()
        // setTimeout(advance_images, 1500)
    }

    
}

function disable_buttons()
{
    image_1_loaded = 0;
    image_2_loaded = 0;
    $("#vote_button_1").prop('disabled', true);
    $("#vote_button_2").prop('disabled', true);

    $("#image_1").css("opacity","")
    $("#image_2").css("opacity","")

}

function enable_buttons(json_data)
{
    $("#vote_button_1").attr("class","btn btn-info")
    $("#vote_button_1").html("Left Pic")
    $("#vote_button_2").attr("class","btn btn-info")
    $("#vote_button_2").html("Right Pic")

    // $("#num_remaining").html(total_questions - current_pair)
    $("#num_remaining").html(current_pair + 1)
        

    $('#opinion_button_1').removeClass('btn-warning').addClass('btn-success ');
    $('#opinion_button_2').removeClass('btn-warning').addClass('btn-success ');

    opinion_ready = 0
    guess_ready = 0


    $("#opinion_question_first #opinion_question").css("visibility","visible").hide().fadeIn(0)
    $("#opinion_question_first #prediction_question").css("visibility","hidden")


    $("#guess_question_first #prediction_question").css("visibility","visible").hide().fadeIn(0)
    $("#guess_question_first #opinion_question").css("visibility","hidden")

    image_load_time = Date.now();
    // $("#num_remaining").html(json_data['num_remaining'])
}


























