// Carousel
let i = 0;
let images = [];
let time = 1000;

images[0] = "./static/images/1.jpg";
images[1] = "./static/images/2.jpg";
images[2] = "./static/images/3.jpg";
images[3] = "./static/images/4.jpg";
images[4] = "./static/images/5.jpg";
images[5] = "./static/images/6.jpg";
images[6] = "./static/images/7.jpg";
images[7] = "./static/images/8.jpg";
images[8] = "./static/images/9.jpg";
images[9] = "./static/images/10.jpg";
images[10] = "./static/images/11.jpg";

function change() {
    document.carousel.src = images[i];
    if (i < images.length - 1) {
        i++;
    } else {
        i = 0;
    }

    setTimeout("change()", time);
}

window.onload = change;