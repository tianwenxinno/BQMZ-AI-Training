$(document).ready(function() {
    $('#scheduleForm').on('submit', function(event) {
        event.preventDefault();
        const participants = $('#participants').val();
        const availableTimes = $('#availableTimes').val();

        $.ajax({
            url: '/schedule',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ participants, availableTimes }),
            success: function(response) {
                $('#result').html('<p>最佳会议时间: ' + response.bestTime + '</p>');
            },
            error: function(error) {
                $('#result').html('<p>发生错误: ' + error.responseText + '</p>');
            }
        });
    });
});
