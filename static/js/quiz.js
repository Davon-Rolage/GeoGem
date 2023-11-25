const numQuestions = document.getElementById('num_questions').textContent;
let learnedWordsIds = new Set();
let incorrectlyAnswered = [];
let quizScore = 0;
let x, y;

// Get mouse position when interacting with the question_form_review
$(document).on("mouseup", '.question_options input', function(e) {
    x = e.clientX;
    y = e.clientY;
});

function handleOptionsQuiz(questionForm) {
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
        success: function (choice) {
            if (choice.is_correct) {
                colorAnswer(clickedInput, is_correct=true);
                playSuccessSound();
                drawSuccessCircle(x-30, y-30);
                // Disable other inputs
                questionForm.find('input[type="submit"]').css('pointer-events', 'none');

                if (questionForm.hasClass('question_form_review')) {
                    // Populate example span
                    $('#span_word_example').html(choice.example_span);
                }

            } else {
                colorAnswer(clickedInput, is_correct=false);
                // Disable only this input
                clickedInput.css('pointer-events', 'none');

                // Add this question to the list of incorrectly answered questions if it's not already there
                if (!incorrectlyAnswered.includes(questionId)) {
                    incorrectlyAnswered.push(questionId);
                }
            }
            quizScore = numQuestions - incorrectlyAnswered.length;
        }
    })
}

// (review quiz) AJAX request to check whether answer is correct
$(".question_form_review").on('submit', function(e) {
    e.preventDefault();
    const questionForm = $(this);
    handleOptionsQuiz(questionForm);
});

// (multiple choice quiz) AJAX request to check whether answer is correct
$(".question_form_multiple_choice").on('submit', function(e) {
    e.preventDefault();
    const questionForm = $(this);
    handleOptionsQuiz(questionForm);
});

// (learn quiz) AJAX request to add a word to the list of learned words
$(".question_form_learn").on("submit", function(e) {
    e.preventDefault();
    const questionForm = $(this);
    $.ajax({
        type: "POST",
        url: questionForm.attr('action'),
        data: {
            'is_last': questionForm.find('input[name="is_last"]').val(),
            'question_id': questionForm.find('input[name="question_id"]').val(),
            'learning_block': document.getElementById("learning_block").textContent.replace(/"/g, ''),
            'csrfmiddlewaretoken': questionForm.find('input[name="csrfmiddlewaretoken"]').val()
        },
        success: function (data) {
            if (data.created) {
                learnedWordsIds.add(data.user_word_id)
            }
            if (data.is_last) {
                quizResults('learn');
            }
        }
    })
})

let currentQuestionCounter = 1;
/**
 * Moves to the next or previous question.
 *
 * @param {number} go_next - If set to 1, moves to the next question. If set to 0, moves to the previous question.
 */
function move(go_next = 1) {
    document.getElementById("word" + currentQuestionCounter).style.display = "none";
    go_next ? currentQuestionCounter++ : currentQuestionCounter--;
    document.getElementById("word" + currentQuestionCounter).style.display = "block";
}

// Play success sound when answer is correct
function playSuccessSound() {
    const audioCorrectAnswer = document.getElementById('audioCorrectAnswer');
    audioCorrectAnswer.play();
}

// Change background color and text color of the chosen input
function colorAnswer(clickedInput, is_correct) {
    color = is_correct ? '#4CAF50' : '#f44336';
    clickedInput.css({
        'background-color': color,
        'color': 'white'
    });
}

// Draw success circle
function drawSuccessCircle(x, y) {
    let div = document.createElement("div");
    div.style = "position: absolute; left: " + x + "px; top: " + y + "px;";
    div.innerHTML = '<div style="width: 30px; height: 30px; border-radius: 50%; background-color: green; display: flex; justify-content: center; align-items: center;"><span style="color: white; font-size: 16px;">+1</span></div>';
    document.body.append(div);
    gsap.to(div, {duration: 1, opacity: 0, y: -50, ease: "power1.out", onComplete: function() { div.remove(); }});
}

// Populate quiz results form and submit
function quizResults(quizMode) {
    const resultsForm = $("#form-results");
    const learningBlock = document.getElementById("learning_block").textContent.replace(/"/g, '');
    let userWordIds;
    let numQuestions;
    let questionsForms;
    
    if (quizMode == 'learn') {
        questionsForms = $(".question_form_learn");
        numQuestions = questionsForms.length;
        userWordIds = Array.from(learnedWordsIds);
        quizScore = -1;
    } else if (quizMode == 'review') {
        questionsForms = $(".question_form_review");
        numQuestions = questionsForms.length;
        userWordIds = questionsForms.find("input[name=question_id]").map((i, el) => el.value).get();
    } else if (quizMode == 'multiple_choice') {
        questionsForms = $(".question_form_multiple_choice");
        numQuestions = questionsForms.length;
        userWordIds = questionsForms.find("input[name=question_id]").map((i, el) => el.value).get();
    }

    $("<input>", { name: "learning_block", value: learningBlock }).appendTo(resultsForm);
    $("<input>", { name: "quiz_words", value: userWordIds }).appendTo(resultsForm);
    $("<input>", { name: "quiz_score", value: quizScore }).appendTo(resultsForm);
    $("<input>", { name: "num_questions", value: numQuestions }).appendTo(resultsForm);
    $("<input>", { name: "quiz_mode", value: quizMode }).appendTo(resultsForm);
    resultsForm.submit();
}
