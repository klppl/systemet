// Ensure functions are global
window.filterBeers = function () {
    console.log("filterBeers START");
    const categorySelect = document.getElementById('category-select');
    const categoryFilter = categorySelect ? categorySelect.value.trim() : '';

    const apkSelect = document.getElementById('apk-select');
    const apkFilter = apkSelect ? apkSelect.value : 'all';

    console.log('Filtering: Cat=[' + categoryFilter + '], APK=[' + apkFilter + ']');

    let minApk = 0;
    let maxApk = 100;

    if (apkFilter === 'over_2') { minApk = 2.0; }
    else if (apkFilter === '1.5_2') { minApk = 1.5; maxApk = 2.0; }
    else if (apkFilter === '1_1.5') { minApk = 1.0; maxApk = 1.5; }
    else if (apkFilter === 'under_1') { maxApk = 1.0; }

    let visibleCount = 0;
    const beers = document.querySelectorAll('.beer-card');

    beers.forEach(beer => {
        const rawCat = beer.getAttribute('data-category2') || '';
        const beerCategory2 = rawCat.trim();

        const beerApk = parseFloat(beer.getAttribute('data-apk'));

        let showBeer = true;

        // Exact match check
        if (categoryFilter && beerCategory2 !== categoryFilter) {
            showBeer = false;
        }

        if (beerApk < minApk) showBeer = false;
        if (maxApk !== 100 && beerApk > maxApk) showBeer = false;

        if (showBeer) {
            beer.classList.remove('hidden');
            visibleCount++;
        } else {
            beer.classList.add('hidden');
        }
    });

    console.log('Visible beers: ' + visibleCount);

    // Handle date visibility
    const dates = document.querySelectorAll('.date-section');
    dates.forEach(date => {
        const beersInDate = date.querySelectorAll('.beer-card:not(.hidden)');
        const hasVisibleBeers = beersInDate.length > 0;

        if (hasVisibleBeers) {
            date.style.display = '';
        } else {
            date.style.display = 'none';
        }
    });

    const resultDiv = document.getElementById('filter-results');
    if (resultDiv) {
        resultDiv.textContent = 'Visar ' + visibleCount + ' öl';
    }
};

window.sortBeers = function () {
    const sortType = document.getElementById('sort-select').value;
    const globalContainer = document.getElementById('global-beer-list');
    const dateSections = document.querySelectorAll('.date-section');

    let allBeers = [];
    document.querySelectorAll('.beer-card').forEach(beer => {
        allBeers.push(beer);
    });

    if (sortType === 'date') {
        globalContainer.style.display = 'none';
        dateSections.forEach(section => section.style.display = '');

        allBeers.forEach(beer => {
            const parentId = beer.getAttribute('data-parent-id');
            const parent = document.getElementById(parentId);
            if (parent) parent.appendChild(beer);
        });

        // Re-sort localized
        dateSections.forEach(section => {
            const list = section.querySelector('.beer-list');
            if (list) {
                const items = Array.from(list.children);
                items.sort((a, b) => {
                    const apkA = parseFloat(a.getAttribute('data-apk')) || 0;
                    const apkB = parseFloat(b.getAttribute('data-apk')) || 0;
                    return apkB - apkA;
                });
                items.forEach(item => list.appendChild(item));
            }
        });

    } else {
        dateSections.forEach(section => section.style.display = 'none');
        globalContainer.style.display = 'grid';
        globalContainer.innerHTML = '';

        allBeers.sort((a, b) => {
            let valA, valB;
            if (sortType === 'price_asc') {
                valA = parseFloat(a.getAttribute('data-price')) || 0;
                valB = parseFloat(b.getAttribute('data-price')) || 0;
                return valA - valB;
            }
            else if (sortType === 'rating_desc') {
                valA = parseFloat(a.getAttribute('data-rating')) || 0;
                valB = parseFloat(b.getAttribute('data-rating')) || 0;
                return valB - valA;
            }
            else if (sortType === 'apk_desc') {
                valA = parseFloat(a.getAttribute('data-apk')) || 0;
                valB = parseFloat(b.getAttribute('data-apk')) || 0;
                return valB - valA;
            }
            return 0;
        });

        allBeers.forEach(beer => globalContainer.appendChild(beer));
    }

    window.filterBeers();
};

// Initialize logic
document.addEventListener('DOMContentLoaded', function () {
    console.log("Initializing App...");
    try {
        const catSelect = document.getElementById('category-select');
        if (catSelect) catSelect.addEventListener('change', window.filterBeers);

        const apkSelect = document.getElementById('apk-select');
        if (apkSelect) apkSelect.addEventListener('change', window.filterBeers);

        const sortSelect = document.getElementById('sort-select');
        if (sortSelect) sortSelect.addEventListener('change', window.sortBeers);

        const toggle = document.getElementById('show-past-toggle');
        if (toggle) {
            toggle.addEventListener('change', function (e) {
                if (e.target.checked) document.body.classList.add('show-past');
                else document.body.classList.remove('show-past');
                window.filterBeers();
            });
        }
    } catch (e) { console.error(e); }

    window.filterBeers();
});
