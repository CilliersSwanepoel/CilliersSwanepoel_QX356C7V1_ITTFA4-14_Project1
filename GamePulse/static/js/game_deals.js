const currencyRates = {
    USD: 1,
    EUR: 0.85,
    GBP: 0.75,
    ZAR: 18
};

function changeCurrency() {
    const currency = document.getElementById('currency').value;
    const dealPrices = document.querySelectorAll('.deal-price');
    
    dealPrices.forEach(priceElement => {
        const basePrice = parseFloat(priceElement.getAttribute('data-price'));
        const convertedPrice = (basePrice * currencyRates[currency]).toFixed(2);
        
        priceElement.innerText = `Sale Price: ${currency} ${convertedPrice}`;
    });
}

function searchGames() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const dealsList = document.getElementById('dealsList');
    const dealItems = dealsList.getElementsByClassName('deal-item');

    for (let i = 0; i < dealItems.length; i++) {
        const title = dealItems[i].getElementsByTagName("h2")[0];
        if (title.innerHTML.toLowerCase().indexOf(filter) > -1) {
            dealItems[i].style.display = "";
        } else {
            dealItems[i].style.display = "none";
        }
    }
}

function clearSearch() {
    const input = document.getElementById('searchInput');
    input.value = '';
    searchGames(); // Reapply filter to show all items
}

document.addEventListener('DOMContentLoaded', function() {
    changeCurrency(); // Set initial currency based on default value in the dropdown
});
