let levelProgress = JSON.parse(document.getElementById("level-progress").textContent);
levelProgress = levelProgress * 100;
$("#level-progress-bar").css("width", levelProgress + "%");
$("#level-progress-label").text(levelProgress + "%");