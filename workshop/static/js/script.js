document.addEventListener('DOMContentLoaded', function () {
    console.log("Workshop Script Loaded");

    // ==========================================
    // 1. DYNAMIC FORMSETS
    // ==========================================
    const addConcernBtn = document.getElementById('add-concern-btn');
    const addSpareBtn = document.getElementById('add-spare-btn');

    if (addConcernBtn) {
        addConcernBtn.addEventListener('click', () => {
            addFormRow('concerns', 'concern-list', 'empty-concern-form');
        });
    }

    if (addSpareBtn) {
        addSpareBtn.addEventListener('click', () => {
            addFormRow('spares', 'spare-list', 'empty-spare-form');
        });
    }

    function addFormRow(prefix, listId, emptyFormId) {
        const totalFormsInput = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
        const listContainer = document.getElementById(listId);
        const emptyFormTemplate = document.getElementById(emptyFormId); // Wrapper div

        if (!totalFormsInput || !listContainer || !emptyFormTemplate) return;

        // Get current count
        const currentCount = parseInt(totalFormsInput.value);

        // Clone the content properly
        // Note: empty-form-id div contains the row, so we take its first child
        const newRow = emptyFormTemplate.firstElementChild.cloneNode(true);

        // Regex to replace __prefix__ with current index
        const regex = new RegExp('__prefix__', 'g');
        newRow.innerHTML = newRow.innerHTML.replace(regex, currentCount);

        // Append
        listContainer.appendChild(newRow);

        // Update count
        totalFormsInput.value = currentCount + 1;

        // Re-Initialize Autocomplete for new row inputs
        initializeAutocompleteInContainer(newRow);
    }


    // ==========================================
    // 2. AUTOCOMPLETE LOGIC
    // ==========================================

    // Initial Setup
    initializeAutocompleteInContainer(document);

    function initializeAutocompleteInContainer(container) {
        const brands = container.querySelectorAll('.autocomplete-brand');
        const models = container.querySelectorAll('.autocomplete-model');
        const spares = container.querySelectorAll('.autocomplete-spare');

        brands.forEach(input => setupAutocomplete(input, 'brands'));
        models.forEach(input => setupAutocomplete(input, 'models'));
        spares.forEach(input => setupAutocomplete(input, 'spares'));
    }

    function setupAutocomplete(input, type) {
        // Find or create suggestions container
        // Based on my template, it's usually the next sibling .list-group
        let suggestionsBox = input.nextElementSibling;
        if (!suggestionsBox || !suggestionsBox.classList.contains('list-group')) {
            // Fallback if structure changes, though template ensures it exists
            return;
        }

        let timeout = null;

        input.addEventListener('input', function () {
            const query = this.value;

            // Clear previous timeout
            if (timeout) clearTimeout(timeout);

            // Hide if empty
            if (query.length < 1) {
                suggestionsBox.innerHTML = '';
                return;
            }

            // Debounce fetch
            timeout = setTimeout(() => {
                fetchSuggestions(type, query, input, suggestionsBox);
            }, 300);
        });

        // Hide on click outside
        document.addEventListener('click', function (e) {
            if (e.target !== input && e.target !== suggestionsBox) {
                suggestionsBox.innerHTML = '';
            }
        });
    }

    function fetchSuggestions(type, query, inputObj, suggestionsBox) {
        let url = `/api/autocomplete/${type}/?q=${encodeURIComponent(query)}`;

        // Logic for Dependent Model Search
        // If searching models, try to find the brand value
        if (type === 'models') {
            const brandInput = document.querySelector('.autocomplete-brand'); // Simplistic find for main form
            if (brandInput && brandInput.value) {
                url += `&brand=${encodeURIComponent(brandInput.value)}`;
            }
        }

        fetch(url)
            .then(response => response.json())
            .then(data => {
                suggestionsBox.innerHTML = '';

                if (data.length === 0) return;

                data.forEach(item => {
                    const itemDiv = document.createElement('a');
                    itemDiv.classList.add('list-group-item', 'list-group-item-action', 'py-2');
                    itemDiv.style.cursor = 'pointer';
                    itemDiv.textContent = item;

                    itemDiv.addEventListener('click', function (e) {
                        e.preventDefault(); // Prevent jump
                        inputObj.value = item;
                        suggestionsBox.innerHTML = ''; // Clear
                    });

                    suggestionsBox.appendChild(itemDiv);
                });
            })
            .catch(err => console.error('Autocomplete Error:', err));
    }

});
