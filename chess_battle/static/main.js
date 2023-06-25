$(document).ready(function () {
    $('#csv_export').click(function () {
        $.ajax({
            url: 'http://127.0.0.1:5000/export',
            method: 'POST',
            success: function (res) {
                console.log(res)
            },
            error: function (xhr, status, error) {
                console.log(xhr.responseText)
            }
        })
    })
})