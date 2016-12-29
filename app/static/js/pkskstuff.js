/**
 * Created by blaz on 11.12.2015.
 */

function unhide(id) {
    var elem = $(id);
    elem.show();
 }

function unhide_tooltip(id) {
    unhide(id);
    elem.addClass("small");
}

function unhide_c_events() {
    var elems = $("tr.koledar_hidden");
    elems.show();
    elems.addClass("koledar_expired");
    $("#prikazi_minule").hide();
}

function confirmAction(actionUrl, prompt) {
    if (confirm(prompt)) {
        window.location.replace(actionUrl);
    }
}


function addImageField() {
    var elem = $("#expander");
    var count = elem.data("count");
    if (count++ >= 3) {
        $("#addImageButton").addClass("btn-warning").text("Dodaš lahko samo tri slike naenkrat!");
        return;
    }

    var imageFiled = '<div class="form-group">';
    imageFiled += '<label for="img' + count + '" class="col-sm-2 control-label">Slika ' + count + ':</label>';
    imageFiled += '<div class="col-sm-10"><input class="form-control" id="img' + count + '" name="img' + count + '" type="file"></div>';
    imageFiled += '<label for="img' + count + 'comment" class="col-sm-2 control-label">Opis:</label>';
    imageFiled += '<div class="col-sm-10"><input class="form-control" id="img' + count + 'comment" name="img' + count + 'comment" type="text" value=""></div>';
    imageFiled += '</div>';

    elem.data("count", count);
    elem.append(imageFiled);
}


