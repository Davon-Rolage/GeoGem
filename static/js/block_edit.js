const infoWordsTable = $("#info-words-table");
const addForm = $("#form-add");
const editForm = $("#form-edit");
const wordInfoLog = $("#word-info-log");


$(document).ready(function() {
    infoWordsTable.DataTable({
        pageLength: 10,
        lengthMenu: [[5, 10, 50, 100, -1], [5, 10, 50, 100, "All"]],
        searching: false
    });
})

$("input").change(function() {
    const parentTr = $(this).closest("tr");
    const wordInfoId = parentTr.attr("id");
    const csrfToken = editForm.find('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
        type: "POST",
        url: editForm.attr("action"),
        data: {
            'csrfmiddlewaretoken': csrfToken,
            word_id: wordInfoId,
            changed_field: $(this).attr("name"),
            new_value: $(this).val()
        },
        success: function(data) {
            if (data.success) {
                const log_row = `id ${wordInfoId}: column "${data.changed_field}". "${data.old_value}" -> "${data.new_value}" at ${data.updated_at}`
                wordInfoLog.append(log_row + "\n");
                wordInfoLog.scrollTop(wordInfoLog[0].scrollHeight);
            }
        }
    })
});

addForm.on("submit", function(e) {
    e.preventDefault();
    $.ajax({
        type: "POST",
        url: $(this).attr("action"),
        data: {
            'csrfmiddlewaretoken': addForm.find('input[name="csrfmiddlewaretoken"]').val(),
            'learning_block_id': addForm.find('input[name="learning_block_id"]').val(),
            'learning_block_slug': addForm.find('input[name="learning_block_slug"]').val(),
        },
        success: function() {
            location.reload();
        }
    })
})