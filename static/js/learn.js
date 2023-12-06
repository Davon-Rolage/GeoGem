let levelProgress = JSON.parse(document.getElementById("level-progress").textContent);
levelProgress = Math.round(levelProgress * 100 * 10) / 10;
$("#level-progress-bar").css("width", levelProgress + "%");
$("#level-progress-label").text(levelProgress + "%");
