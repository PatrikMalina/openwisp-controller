document.addEventListener("DOMContentLoaded", function () {
    function filterSelect(targetSelect, allSelects) {
        const selectedValues = new Set(
            allSelects
                .filter(sel => sel !== targetSelect)
                .map(sel => sel.value)
                .filter(Boolean)
        );

        const currentValue = targetSelect.value;
        const originalOptions = targetSelect.dataset.originalOptions
            ? JSON.parse(targetSelect.dataset.originalOptions)
            : [];

        targetSelect.innerHTML = "";

        originalOptions.forEach(([value, label]) => {
            if (value === currentValue || !selectedValues.has(value)) {
                const option = new Option(label, value);
                if (value === currentValue) {
                    option.selected = true;
                }
                targetSelect.appendChild(option);
            }
        });
    }

    function filterAllSelects() {
        const selects = Array.from(document.querySelectorAll('select.device-selector'))
            .filter(sel => !sel.name.includes('__prefix__'));

        selects.forEach(select => {
            if (!select.dataset.originalOptions) {
                const allOptions = Array.from(select.options).map(opt => [opt.value, opt.text]);
                select.dataset.originalOptions = JSON.stringify(allOptions);
            }
        });

        selects.forEach(select => filterSelect(select, selects));
    }

    function attachChangeListeners() {
        const selects = Array.from(document.querySelectorAll('select.device-selector'))
            .filter(sel => !sel.name.includes('__prefix__'));

        selects.forEach(select => {
            select.removeEventListener('change', filterAllSelects);
            select.addEventListener('change', filterAllSelects);
        });
    }

    function handleNewSelect(select) {
        if (!select.name.includes('__prefix__')) {
            const selects = Array.from(document.querySelectorAll('select.device-selector'))
                .filter(sel => !sel.name.includes('__prefix__'));

            if (!select.dataset.originalOptions) {
                const allOptions = Array.from(select.options).map(opt => [opt.value, opt.text]);
                select.dataset.originalOptions = JSON.stringify(allOptions);
            }

            filterSelect(select, selects);
            attachChangeListeners();
        }
    }

    // Initial setup
    filterAllSelects();
    attachChangeListeners();

    // Watch for inline row changes
    const observer = new MutationObserver((mutationsList) => {
        let changed = false;

        mutationsList.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1 && node.matches('.form-row')) {
                    const select = node.querySelector('select.device-selector');
                    if (select) {
                        handleNewSelect(select);
                        changed = true;
                    }
                }
            });

            mutation.removedNodes.forEach(node => {
                if (node.nodeType === 1 && node.matches('.form-row')) {
                    changed = true;
                }
            });
        });

        if (changed) {
            filterAllSelects();
            attachChangeListeners();
        }
    });

    const inlineGroup = document.querySelector('.inline-group');
    if (inlineGroup) {
        observer.observe(inlineGroup, {childList: true, subtree: true});
    }
});
