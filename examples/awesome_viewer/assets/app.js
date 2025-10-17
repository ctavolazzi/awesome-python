(function () {
    const DATA = window.APP_DATA || [];
    const TOTALS = window.APP_TOTALS || { total_categories: 0, total_entries: 0 };

    const resultsContainer = document.getElementById('results');
    const searchInput = document.getElementById('search');
    const clearButton = document.getElementById('clear-filters');
    const categoryList = document.getElementById('category-list');
    const statCategories = document.getElementById('stat-categories');
    const statEntries = document.getElementById('stat-entries');
    const statTotals = document.getElementById('stat-totals');
    const focusCard = document.getElementById('focus-card');
    const focusTitle = document.getElementById('focus-title');
    const focusCount = document.getElementById('focus-count');
    const focusList = document.getElementById('focus-list');
    const focusNote = document.getElementById('focus-note');
    const focusEmpty = document.getElementById('focus-empty');
    const focusPrev = document.getElementById('focus-prev');
    const focusNext = document.getElementById('focus-next');
    const focusPosition = document.getElementById('focus-position');

    const slugify = (value) => value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

    statTotals.textContent = `${TOTALS.total_categories.toLocaleString()} categories · ${TOTALS.total_entries.toLocaleString()} entries`;

    let selectedCategory = null;
    let focusIndex = 0;
    let filteredCache = DATA;
    let categoryButtons = [];

    const getSearchTokens = (value) => value.toLowerCase().split(/\s+/).filter(Boolean);

    const updateActiveButtons = () => {
        for (const { value, button } of categoryButtons) {
            const isActive = value === selectedCategory || (!value && !selectedCategory);
            button.classList.toggle('category-button--active', isActive);
        }
    };

    const updateHash = () => {
        if (selectedCategory) {
            location.hash = slugify(selectedCategory);
        } else {
            history.replaceState(null, '', location.pathname + location.search);
        }
    };

    const filterCategories = () => {
        const query = searchInput.value.trim();
        if (!query && !selectedCategory) {
            return DATA;
        }

        const tokens = getSearchTokens(query);
        return DATA.filter((category) => {
            if (selectedCategory && category.title !== selectedCategory) {
                return false;
            }

            if (!tokens.length) {
                return true;
            }

            return tokens.every((token) => {
                if (category.title.toLowerCase().includes(token)) {
                    return true;
                }
                return category.items.some((entry) => {
                    return (
                        entry.name.toLowerCase().includes(token) ||
                        entry.description.toLowerCase().includes(token)
                    );
                });
            });
        });
    };

    const renderStats = (categories) => {
        const visibleEntries = categories.reduce((count, category) => count + category.items.length, 0);
        statCategories.textContent = categories.length.toLocaleString();
        statEntries.textContent = visibleEntries.toLocaleString();
    };

    const renderEmptyState = () => {
        resultsContainer.innerHTML = '';
        const empty = document.createElement('div');
        empty.className = 'empty-state';
        empty.innerHTML = '<h2>No matches found</h2><p>Adjust your filters or search for different keywords.</p>';
        resultsContainer.appendChild(empty);
        focusCard.hidden = true;
        focusEmpty.hidden = false;
        focusNote.hidden = true;
        focusPosition.textContent = '0 / 0';
    };

    const renderFocus = () => {
        if (!filteredCache.length) {
            renderEmptyState();
            return;
        }

        focusEmpty.hidden = true;
        focusCard.hidden = false;
        const category = filteredCache[focusIndex];
        focusTitle.textContent = category.title;
        focusCount.textContent = `${category.items.length} entries`;
        focusCount.hidden = category.items.length === 0;
        focusPosition.textContent = `${focusIndex + 1} / ${filteredCache.length}`;

        focusList.innerHTML = '';
        const fragment = document.createDocumentFragment();
        const previewItems = category.items.slice(0, 5);
        for (const entry of previewItems) {
            const li = document.createElement('li');
            const link = document.createElement('a');
            link.href = entry.url;
            link.textContent = entry.name;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            li.appendChild(link);
            const description = document.createElement('p');
            description.className = 'focus-note';
            description.textContent = entry.description;
            li.appendChild(description);
            fragment.appendChild(li);
        }
        focusList.appendChild(fragment);

        const remaining = category.items.length - previewItems.length;
        if (remaining > 0) {
            focusNote.hidden = false;
            focusNote.textContent = `…and ${remaining} more entries`;
        } else {
            focusNote.hidden = true;
        }
    };

    const renderResults = () => {
        resultsContainer.innerHTML = '';
        if (!filteredCache.length) {
            renderEmptyState();
            return;
        }

        const fragment = document.createDocumentFragment();
        for (const category of filteredCache) {
            const section = document.createElement('section');
            section.className = 'category-card';
            section.id = category.slug;

            const title = document.createElement('h2');
            title.textContent = category.title;
            section.appendChild(title);

            const list = document.createElement('ul');
            list.className = 'entry-list';
            for (const entry of category.items) {
                const li = document.createElement('li');
                li.className = 'entry';
                const link = document.createElement('a');
                link.href = entry.url;
                link.textContent = entry.name;
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
                const description = document.createElement('p');
                description.textContent = entry.description;

                li.appendChild(link);
                li.appendChild(description);
                list.appendChild(li);
            }
            section.appendChild(list);
            fragment.appendChild(section);
        }
        resultsContainer.appendChild(fragment);
    };

    const refresh = ({ resetFocus = false } = {}) => {
        filteredCache = filterCategories();
        renderStats(filteredCache);
        renderResults();
        if (resetFocus) {
            focusIndex = 0;
        }
        renderFocus();
    };

    const buildCategoryButtons = () => {
        categoryList.innerHTML = '';
        categoryButtons = [];
        const fragment = document.createDocumentFragment();

        const makeButton = (label, value) => {
            const li = document.createElement('li');
            const button = document.createElement('button');
            button.type = 'button';
            button.textContent = label;
            button.className = 'category-button';
            button.addEventListener('click', () => {
                if (value === null) {
                    selectedCategory = null;
                } else {
                    selectedCategory = value;
                }
                focusIndex = 0;
                updateActiveButtons();
                updateHash();
                refresh({ resetFocus: true });
            });
            li.appendChild(button);
            fragment.appendChild(li);
            categoryButtons.push({ value, button });
        };

        makeButton('All categories', null);
        for (const category of DATA) {
            const label = `${category.title} (${category.items.length})`;
            makeButton(label, category.title);
        }

        categoryList.appendChild(fragment);
    };

    const applyHashSelection = () => {
        const slug = decodeURIComponent(location.hash.replace(/^#/, ''));
        if (!slug) {
            return;
        }
        const match = DATA.find((category) => category.slug === slug || slugify(category.title) === slug);
        if (match) {
            selectedCategory = match.title;
        }
    };

    searchInput.addEventListener('input', () => {
        refresh({ resetFocus: true });
    });

    searchInput.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && searchInput.value) {
            searchInput.value = '';
            refresh({ resetFocus: true });
            event.preventDefault();
        }
    });

    clearButton.addEventListener('click', () => {
        searchInput.value = '';
        selectedCategory = null;
        focusIndex = 0;
        updateActiveButtons();
        updateHash();
        refresh({ resetFocus: true });
        searchInput.focus();
    });

    focusPrev.addEventListener('click', () => {
        if (!filteredCache.length) {
            return;
        }
        focusIndex = (focusIndex - 1 + filteredCache.length) % filteredCache.length;
        renderFocus();
    });

    focusNext.addEventListener('click', () => {
        if (!filteredCache.length) {
            return;
        }
        focusIndex = (focusIndex + 1) % filteredCache.length;
        renderFocus();
    });

    document.addEventListener('keydown', (event) => {
        if (event.target && event.target.tagName === 'INPUT') {
            return;
        }
        if (event.key === '[') {
            focusPrev.click();
        } else if (event.key === ']') {
            focusNext.click();
        }
    });

    buildCategoryButtons();
    applyHashSelection();
    updateActiveButtons();
    refresh({ resetFocus: true });
})();
