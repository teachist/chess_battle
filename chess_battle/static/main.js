$(document).ready(function () {
    // Manipulates for battle_list.html page
    $('#registerScores').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var firstPlayer = button.data('firstplayer');
        var secondPlayer = button.data('secondplayer');
        var firstPlayerName = button.data('firstplayername');
        var secondPlayerName = button.data('secondplayername');

        const firstPlayerNameSpan = $('#firstPlayerNameSpan')
        const secondPlayerNameSpan = $('#secondPlayerNameSpan')

        console.log(firstPlayer)
        var form = $('#modalFrom');
        var actionUrl = '/' + firstPlayer + '/' + secondPlayer + '/register-score';


        form.attr('action', actionUrl)
        firstPlayerNameSpan.text('先手：' + firstPlayerName)
        secondPlayerNameSpan.text('后手：' + secondPlayerName)

        console.log(firstPlayerNameSpan)
    });

    $('#updatePlayer').on('show.bs.modal', function (event) {
        const button = $(event.relatedTarget);
        const id = button.data('id');
        const name = button.data('name');
        const gender = button.data('gender');
        const org = button.data('org');
        const phone = button.data('phone');
        const status = button.data('status');

        var option = 0;

        if (status == 'False') {
            option = 1;
        }

        const form = $('#updatePlayerForm');
        form.find('input#id').val(id);
        form.find('input#name').val(name);
        form.find('input#gender').val(gender);
        form.find('input#org').val(org);
        form.find('input#phone').val(phone);
        form.find('select#status').val(option);
    });

    $('#deletePlayer').on('show.bs.modal', function (event) {
        const button = $(event.relatedTarget);
        const id = button.data('id');
        const name = button.data('name');

        $('#deletePlayerModalModalLabel').text("删除棋手：" + name);

        $('#deletePlayerButton').click(function () {
            $('#deletePlayer').modal('hide');
            $.post('/player/' + id + '/delete')
                .done(function (response) {
                    console.log('请求成功', response);
                })
                .fail(function (xhr, status, error) {
                    console.error('请求出错', error);
                });
        });

    });

});
