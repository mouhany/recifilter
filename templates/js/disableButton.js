// Disable button if field empty
(function () {
    $('.inp').keyup(function () {

        var empty = false;
        $('.inp').each(function () {
            if ($(this).val() == '') {
                empty = true;
            }
        });

        if (empty) {
            $('.btn').attr('disabled', 'disabled');
        } else {
            $('.btn').removeAttr('disabled');
        }
    });
})()