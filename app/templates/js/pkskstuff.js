/**
 * Created by blaz on 11.12.2015.
 */

function confirmDeletePost(id) {
    if (confirm("Potrdi brisanje prispevka")) {
        var url = '{{ url_for("main.delete_post") }}' + id;
        window.location.replace(url);
    }
}

function confirmDeleteUser(id, username) {
    if (confirm("Potrdi brisanje uporabnika " + username)) {
        var url = '{{ url_for("admin.delete_user") }}' + id;
        window.location.replace(url);
    }
}
