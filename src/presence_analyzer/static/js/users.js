function initialize_users(url) {
    var loading = $('#loading');
    $.getJSON(url, function(result) {
        var dropdown = $("#user_id");
        $.each(result, function(item) {
            dropdown.append($("<option />").val(this.user_id).text(this.name)
                .data('avatar', this.avatar));
        });
        dropdown.show();
        loading.hide();
    });

    $('#user_id').change(function(){
        $('#avatar').hide();
        var avatar_url = $("#user_id").find(":selected").data('avatar');
        if (avatar_url) {
            $('#avatar').attr('src', avatar_url).show();
        }
    });
}
