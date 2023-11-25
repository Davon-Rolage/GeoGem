$(document).ready(function() {
    activateTooltips();
});

// Activate bootstrap tooltips
function activateTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl)
    })
}

// AJAX request to reset the test block
$("#form_reset_test_block").on("submit", function(e) {
  e.preventDefault();
  const resetTestBlockForm = $(this);
  $.ajax({
      type: "POST",
      url: resetTestBlockForm.attr('action'),
      data: {
          'csrfmiddlewaretoken': resetTestBlockForm.find('input[name="csrfmiddlewaretoken"]').val()
      },
      success: function (data) {
          if (data.success) {
            // Display a check icon and hide in 2 seconds
            let checkIcon = $(".icon-success");
            checkIcon.css("display", "inline");
            setTimeout(function() {
                checkIcon.hide();
            }, 2000);
          }
      }
  })
})