// AJAX request to check if answer is correct
const numQuestions = document.getElementById('num_questions').value;
let incorrectlyAnswered = [];
let score = 0;
let x, y;

$(document).on("submit", '#question-form', function(e) {
    e.preventDefault();
    const questionForm = $(this);
    const questionId = questionForm.find('input[name="question_id"]').val();

    const nextButton = questionForm.find('input[id="btn-next"]');
    nextButton.removeAttr('disabled');
    
    let clickedInput = questionForm.find('input[type="submit"]:focus');
    let answerValue = clickedInput.val();
    
    $.ajax({
        type: "POST",
        url: questionForm.attr('action'),
        data: {
            'question_id': questionId,
            'answer': answerValue,
            'csrfmiddlewaretoken': questionForm.find('input[name="csrfmiddlewaretoken"]').val()
        },
        success: function (data) {
            data = JSON.parse(data)[0];
            if (data.success == 'true') {
                colorAnswer(clickedInput, true);
                playSuccess();
                drawSuccessCircle(x-30, y-30);
                // Populate example span
                $('#span_word_example').html(data.example_span);
                // Disable other inputs
                questionForm.find('input[type="submit"]').css('pointer-events', 'none');

            } else {
                colorAnswer(clickedInput, false);
                // Disable only this input
                clickedInput.css('pointer-events', 'none');

                // Add this question to the list of incorrectly answered questions if it's not already there
                if (!incorrectlyAnswered.includes(questionId)) {
                    incorrectlyAnswered.push(questionId);
                }
            }
            score = numQuestions - incorrectlyAnswered.length;
            $('#score').html(score);
        }
    })
})

// Get mouse position when interacting with the question_form
$(document).on("mouseup", '#question-form', function(e) {
    x = e.clientX;
    y = e.clientY;
});

// Play success sound when answer is correct
function playSuccess() {
    const audioCorrectAnswer = document.getElementById('audioCorrectAnswer');
    audioCorrectAnswer.play();
}

// Change background color and text color of the chosen input
function colorAnswer(clickedInput, is_correct) {
    color = is_correct ? '#4CAF50' : '#f44336';
    clickedInput.css('background-color', color);
    clickedInput.css('color', 'white');
}

// Draw success circle
function drawSuccessCircle(x, y) {
    let div = document.createElement("div");
    div.style = "position: absolute; left: " + x + "px; top: " + y + "px;";
    div.innerHTML = '<div style="width: 30px; height: 30px; border-radius: 50%; background-color: green; display: flex; justify-content: center; align-items: center;"><span style="color: white; font-size: 16px;">+1</span></div>';
    document.body.append(div);
    gsap.to(div, {duration: 1, opacity: 0, y: -50, ease: "power1.out", onComplete: function() { div.remove(); }});
}
