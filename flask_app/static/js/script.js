$(document).ready(function() {
    if (window.innerWidth < 475) {
        $('.news').removeClass('col-6').addClass('col-12');
        $('.card-img-top').css('height', '15rem');
    } else {
        $('.news').removeClass('col-12').addClass('col-6');
        $('.card-img-top').css('height', '11rem');
    }
});

$('#likes').click(function() {
    var likes = $('#count-likes').html();
    $.ajax({
        type: 'GET',
        url: $(this).attr('data-url'),
        data: {'likes': likes},
        success: function(response) {
            $('#count-likes').html('');
            $('#count-likes').html(response.data);
            console.log('success');
        }
    });
    return false;
});

$('#comment').click(function() {
    if($('.show_comment').css('display') == 'none') {
         $('.show_comment').css('display', 'block');
    }else if($('.show_comment').css('display') == 'block') {
        $('.show_comment').css('display', 'none');
    }
});

$('#send-comment').submit(function() {
    var url = $(this).attr('action');
    $.ajax({
        type: 'POST',
        url: url,
        data: $(this).serialize(),
        success: function(response) {
            $('.show_comment').html('');
            $('.show_comment').html('Комментарий был успешно отправлен. Скоро он отобразится на сайте.');
            console.log('success');
        }
    });
    return false;
});

$('#bookmark').click(function() {
    var url = $(this).attr('data-url');
    $.ajax({
        type: 'GET',
        url: url,
        data: {'bookmark': $('#mark').attr('class')},
        success: function(response) {
            var counter = $(response).find('.bookmark_counter');
            $('.bookmark_counter').empty().append(counter);
            if($('#mark').hasClass('fa fa-bookmark-o fa-2x pt-2')) {
                $('#mark').removeClass('fa fa-bookmark-o fa-2x pt-2').addClass('fa fa-bookmark fa-2x pt-2');
            }else if ($('i').hasClass('fa fa-bookmark fa-2x pt-2')) {
                $('#mark').removeClass('fa fa-bookmark fa-2x pt-2').addClass('fa fa-bookmark-o fa-2x pt-2');
            }
        },
        error: function() {
            alert('для добавления в закладки вам нужно авторизоваться');
        }
    });
    return false;
});

$('.del_bookmark').click(function(){
    var url = $(this).attr('data-url');
    var news_id = $(this).attr('item-id');
    $.ajax({
        type: 'GET',
        url: url,
        data: {'news_id': news_id}, 
        success: function(response) {
            location.reload(true);
            var counter = $(response).find('.bookmark_counter');
            $('.bookmark_counter').html('').append(counter);
            var update_content = $(response).find('.results');
            $('.results').empty();
            if(update_content.length > 0) {
                $('.results').append(update_content);
            }else {
                $('.results').html('<div class="col-12"><p class="mb-5 my-3">У вас нет еще ни одной закладки для чтения</p></div>'); 
            }
        },
        error: function(error) {
            console.log(error);
        }
    });
    return false;
});

