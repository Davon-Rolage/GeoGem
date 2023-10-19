// Show quiz results div
function quizResults() {
    document.getElementById("quiz").style.display = "none";
    document.getElementById("quiz-results").style.display = "block";
}

// Show one question at a time
let currentWord = 1;
function move(go_next = 1) {
        document.getElementById("word" + currentWord).style.display = "none";
        go_next ? currentWord++ : currentWord--;
        document.getElementById("word" + currentWord).style.display = "block";
}