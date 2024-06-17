document.addEventListener("DOMContentLoaded", function() {
    fetch('https://www.cheapshark.com/api/1.0/deals')
        .then(response => response.json())
        .then(data => {
            initializeCarousel(data.slice(0, 10), 'carousel1', 'carousel-text1');
            initializeCarousel(data.slice(10, 20), 'carousel2', 'carousel-text2');
            initializeCarousel(data.slice(20, 30), 'carousel3', 'carousel-text3');
        })
        .catch(error => console.error('Error fetching data:', error));
});

function initializeCarousel(data, carouselId, textId) {
    const carousel = document.getElementById(carouselId);
    const carouselText = document.getElementById(textId);
    data.forEach((deal, index) => {
        const img = document.createElement('img');
        img.src = deal.thumb;
        img.classList.add('carousel-image');
        if (index === 0) {
            img.classList.add('active');
            carouselText.innerHTML = `<h2>${deal.title}</h2><p>Price: $${deal.salePrice}</p>`;
        }
        carousel.appendChild(img);
    });
    startCarousel(data, carouselId, textId);
}

function startCarousel(data, carouselId, textId) {
    let currentIndex = 0;
    setInterval(() => {
        const images = document.querySelectorAll(`#${carouselId} .carousel-image`);
        const carouselText = document.getElementById(textId);
        images[currentIndex].classList.remove('active');
        currentIndex = (currentIndex + 1) % images.length;
        images[currentIndex].classList.add('active');
        carouselText.innerHTML = `<h2>${data[currentIndex].title}</h2><p>Price: $${data[currentIndex].salePrice}</p>`;
    }, 3000);
}
