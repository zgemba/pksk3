/**
 * Created by blaz on 29.12.2016.
 */

function openModal() {
    document.onkeydown = function (e) {
        switch (e.keyCode) {
            case 27:            // esc
                closeModal();
                break;
            case 37:            // <-
                plusSlides(-1);
                break;
            case 39:            // ->
                plusSlides(1);
                break;
        }
    };
    document.getElementById('myModal').style.display = "block";
}

function closeModal() {
    document.onkeydown = undefined;
    document.getElementById('myModal').style.display = "none";
}

var slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n) {
    showSlides(slideIndex += n);
}

function currentSlide(n) {
    showSlides(slideIndex = n);
}

function showSlides(n) {
    var i;
    var slides = document.getElementsByClassName("lb_mySlides");
    var captionText = document.getElementById("lb_caption");
    if (n > slides.length) {
        slideIndex = 1
    }
    if (n < 1) {
        slideIndex = slides.length
    }
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    slides[slideIndex - 1].style.display = "block";
    captionText.innerHTML = slides[slideIndex - 1].getElementsByTagName("IMG")[0].alt;
}