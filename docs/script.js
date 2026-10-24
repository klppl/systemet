(function () {
    'use strict';

    const STORAGE_KEY = 'systemet.list.v1';
    const kr = new Intl.NumberFormat('sv-SE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    const $ = (sel, root) => (root || document).querySelector(sel);
    const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

    const els = {
        search: $('#search'),
        category: $('#category-select'),
        apk: $('#apk-select'),
        rating: $('#rating-select'),
        sort: $('#sort-select'),
        upcoming: $('#upcoming'),
        global: $('#global-beer-list'),
        empty: $('#empty-state'),
        status: $('#filter-status'),
        statusCount: $('#filter-count'),
        slip: $('#slip'),
        slipToggle: $('#slip-toggle'),
        slipToggleSum: $('#slip-toggle-sum'),
        slipLines: $('#slip-lines'),
        slipEmpty: $('#slip-empty'),
        slipTotal: $('#slip-total'),
        slipCount: $('#slip-count'),
        slipSum: $('#slip-sum'),
        slipActions: $('#slip-actions'),
    };

    const lines = $$('.line[data-id]');
    lines.forEach((line, i) => { line.dataset.order = i; });
    const upcomingLines = lines.filter(line => !line.hasAttribute('data-past'));

    /* ---------- Saved list (localStorage, may be unavailable) ---------- */

    let saved = {};
    try {
        saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}') || {};
    } catch (e) {
        saved = {};
    }

    function persist() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
        } catch (e) { /* private mode: list lives for this visit only */ }
    }

    function snapshot(line) {
        return {
            name: line.dataset.name,
            price: parseFloat(line.dataset.price) || 0,
            date: line.dataset.date,
            shortDate: line.dataset.shortDate,
        };
    }

    function setMark(line, isSaved) {
        const btn = $('.mark', line);
        btn.setAttribute('aria-pressed', String(isSaved));
        btn.setAttribute('aria-label', (isSaved ? 'Ta bort ' : 'Spara ') + line.dataset.name + (isSaved ? ' från min lista' : ' i min lista'));
        line.classList.toggle('is-saved', isSaved);
    }

    function toggleSaved(line) {
        const id = line.dataset.id;
        const isSaved = !saved[id];
        if (isSaved) saved[id] = snapshot(line);
        else delete saved[id];
        persist();
        setMark(line, isSaved);
        renderSlip(isSaved ? id : null);
    }

    function removeSaved(id) {
        delete saved[id];
        persist();
        const line = document.getElementById('beer-' + id);
        if (line) setMark(line, false);
        renderSlip();
    }

    function dayLabel(dateStr) {
        const d = new Date(dateStr + 'T00:00:00');
        if (isNaN(d)) return dateStr;
        return d.toLocaleDateString('sv-SE', { weekday: 'short', day: 'numeric', month: 'short' }).replace('.', '');
    }

    function sortedSaved() {
        return Object.entries(saved).sort((a, b) => (a[1].date || '').localeCompare(b[1].date || ''));
    }

    function renderSlip(newId) {
        const entries = sortedSaved();
        const total = entries.reduce((sum, [, item]) => sum + (item.price || 0), 0);

        els.slipLines.textContent = '';
        let currentDay = null;
        entries.forEach(([id, item]) => {
            if (item.date !== currentDay) {
                currentDay = item.date;
                const day = document.createElement('div');
                day.className = 'slip-day';
                day.textContent = dayLabel(item.date);
                els.slipLines.appendChild(day);
            }
            const row = document.createElement('div');
            row.className = 'slip-line' + (id === newId ? ' is-new' : '');

            const link = document.createElement('a');
            link.href = '#beer-' + id;
            link.textContent = item.name;
            link.title = item.name;
            link.addEventListener('click', (e) => {
                e.preventDefault();
                revealLine(id);
            });

            const price = document.createElement('span');
            price.textContent = kr.format(item.price || 0);

            const remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'remove';
            remove.setAttribute('aria-label', 'Ta bort ' + item.name);
            remove.innerHTML = '<svg class="icon" viewBox="0 0 20 20" aria-hidden="true"><path d="M5.5 5.5l9 9M14.5 5.5l-9 9"/></svg>';
            remove.addEventListener('click', () => removeSaved(id));

            row.append(link, price, remove);
            els.slipLines.appendChild(row);
        });

        const count = entries.length;
        const has = count > 0;
        els.slipEmpty.hidden = has;
        els.slipTotal.hidden = !has;
        els.slipActions.hidden = !has;
        els.slipCount.textContent = count + ' st';
        els.slipSum.textContent = kr.format(total) + ' kr';
        els.slipToggleSum.textContent = has ? count + ' st · ' + kr.format(total) + ' kr' : 'Tom';

    }

    function copyList() {
        const entries = sortedSaved();
        let currentDay = null;
        const out = [];
        let total = 0;
        entries.forEach(([id, item]) => {
            if (item.date !== currentDay) {
                currentDay = item.date;
                out.push((out.length ? '\n' : '') + dayLabel(item.date));
            }
            out.push('  ' + item.name + ' (nr ' + id + ')  ' + kr.format(item.price) + ' kr');
            total += item.price || 0;
        });
        out.push('\nTotalt ' + entries.length + ' st  ' + kr.format(total) + ' kr');
        const text = out.join('\n');
        const btn = $('#slip-copy');
        const done = () => {
            btn.textContent = 'Kopierad';
            setTimeout(() => { btn.textContent = 'Kopiera listan'; }, 1600);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(done, () => window.prompt('Kopiera listan:', text));
        } else {
            window.prompt('Kopiera listan:', text);
        }
    }

    /* ---------- Detail rows ---------- */

    function setExpanded(line, open) {
        const btn = $('.line-main', line);
        const detail = $('.line-detail', line);
        btn.setAttribute('aria-expanded', String(open));
        detail.hidden = !open;
    }

    function revealLine(id) {
        let line = document.getElementById('beer-' + id);
        if (!line) return;
        if (line.hidden) {
            clearFilters();
        }
        setExpanded(line, true);
        if (window.matchMedia('(max-width: 1180px)').matches) setSlipOpen(false);
        line.scrollIntoView({ behavior: 'smooth', block: 'center' });
        $('.line-main', line).focus({ preventScroll: true });
    }

    /* ---------- Filter + sort ---------- */

    function currentFilters() {
        return {
            q: (els.search.value || '').trim().toLowerCase(),
            cat: els.category.value,
            apk: parseFloat(els.apk.value) || 0,
            rating: parseFloat(els.rating.value) || 0,
        };
    }

    function isFiltering(f) {
        return Boolean(f.q || f.cat || f.apk || f.rating);
    }

    function matches(line, f) {
        if (f.cat && line.dataset.category2 !== f.cat) return false;
        if (f.apk && (parseFloat(line.dataset.apk) || 0) < f.apk) return false;
        if (f.rating && (parseFloat(line.dataset.rating) || 0) < f.rating) return false;
        if (f.q) {
            const hay = line.dataset.search || '';
            if (!f.q.split(/\s+/).every(term => hay.includes(term))) return false;
        }
        return true;
    }

    function applyFilters() {
        const f = currentFilters();
        const filtering = isFiltering(f);
        let visibleUpcoming = 0;

        lines.forEach(line => {
            const show = matches(line, f);
            line.hidden = !show;
            if (show && !line.hasAttribute('data-past')) visibleUpcoming++;
        });

        $$('.day[data-date]').forEach(day => {
            const all = $$('.line', day);
            const visible = all.filter(l => !l.hidden).length;
            day.hidden = visible === 0;
            const count = $('.day-count', day);
            if (count) {
                const total = count.dataset.total;
                count.textContent = filtering ? visible + ' av ' + total + ' öl' : total + ' öl';
            }
        });

        const past = $('#past');
        if (past) past.hidden = !$$('.line', past).some(l => !l.hidden);

        [els.category, els.apk, els.rating].forEach(sel => {
            sel.classList.toggle('is-active', Boolean(sel.value) && sel.value !== '0');
        });

        els.status.hidden = !filtering;
        els.statusCount.textContent = 'Visar ' + visibleUpcoming + ' av ' + upcomingLines.length + ' kommande öl';
        els.empty.hidden = visibleUpcoming > 0;
    }

    function applySort() {
        const mode = els.sort.value;
        if (mode === 'date') {
            els.global.hidden = true;
            els.upcoming.hidden = false;
            upcomingLines
                .slice()
                .sort((a, b) => a.dataset.order - b.dataset.order)
                .forEach(line => {
                    const parent = document.getElementById(line.dataset.parentId);
                    if (parent) parent.appendChild(line);
                });
        } else {
            const key = { rating_desc: 'rating', apk_desc: 'apk', price_asc: 'price' }[mode];
            const dir = mode === 'price_asc' ? 1 : -1;
            const sorted = upcomingLines.slice().sort((a, b) => {
                const diff = ((parseFloat(a.dataset[key]) || 0) - (parseFloat(b.dataset[key]) || 0)) * dir;
                return diff || a.dataset.order - b.dataset.order;
            });
            sorted.forEach(line => els.global.appendChild(line));
            els.upcoming.hidden = true;
            els.global.hidden = false;
        }
        applyFilters();
    }

    function clearFilters() {
        els.search.value = '';
        els.category.value = '';
        els.apk.value = '0';
        els.rating.value = '0';
        applyFilters();
    }

    /* ---------- Relative day labels stay true even if the page is cached ---------- */

    function refreshRelative() {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        $$('[data-relative]').forEach(el => {
            const d = new Date(el.dataset.relative + 'T00:00:00');
            if (isNaN(d)) return;
            const delta = Math.round((d - today) / 86400000);
            let label;
            if (delta === 0) label = 'I dag';
            else if (delta === 1) label = 'I morgon';
            else if (delta === -1) label = 'I går';
            else if (delta > 1) label = 'Om ' + delta + ' dagar';
            else label = 'För ' + -delta + ' dagar sedan';
            el.textContent = label;
        });
    }

    /* ---------- Mobile slip ---------- */

    function setSlipOpen(open) {
        els.slip.classList.toggle('is-open', open);
        els.slipToggle.setAttribute('aria-expanded', String(open));
    }

    /* ---------- Wire up ---------- */

    document.addEventListener('click', (e) => {
        const mark = e.target.closest('.mark');
        if (mark) {
            toggleSaved(mark.closest('.line'));
            return;
        }
        const main = e.target.closest('.line-main');
        if (main && main.closest('.line[data-id]')) {
            setExpanded(main.closest('.line'), main.getAttribute('aria-expanded') !== 'true');
        }
    });

    let searchTimer;
    els.search.addEventListener('input', () => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(applyFilters, 80);
    });
    [els.category, els.apk, els.rating].forEach(sel => sel.addEventListener('change', applyFilters));
    els.sort.addEventListener('change', applySort);
    $('#clear-filters').addEventListener('click', clearFilters);
    $('#empty-clear').addEventListener('click', clearFilters);
    $('#slip-copy').addEventListener('click', copyList);
    $('#slip-clear').addEventListener('click', () => {
        if (!window.confirm('Tömma hela listan?')) return;
        Object.keys(saved).forEach(id => {
            const line = document.getElementById('beer-' + id);
            if (line) setMark(line, false);
        });
        saved = {};
        persist();
        renderSlip();
    });
    els.slipToggle.addEventListener('click', () => setSlipOpen(!els.slip.classList.contains('is-open')));
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && els.slip.classList.contains('is-open')) setSlipOpen(false);
    });

    lines.forEach(line => { if (saved[line.dataset.id]) setMark(line, true); });
    refreshRelative();
    renderSlip();
    applyFilters();
})();
