// SPARE PARTS AUTO-FILL ENHANCED LOGIC
//
// Auto-fills ordered_date and received_date when status changes
// Prevents accidental backward status changes with Bootstrap Modal confirmation

document.addEventListener('DOMContentLoaded', function () {

    // ==========================================
    // AUTO-FILL DATES ON STATUS CHANGE
    // ==========================================

    // Variables to store state for modal confirmation
    let pendingChange = null;
    let modalInstance = null;

    function attachSpareStatusListeners() {
        // Get all status dropdowns in spare parts section
        const statusDropdowns = document.querySelectorAll('#spare-list select[name*="status"]');

        statusDropdowns.forEach(dropdown => {
            if (dropdown.dataset.listenerAttached === 'true') return;

            dropdown.addEventListener('change', function () {
                const newStatus = this.value;
                const row = this.closest('.spare-row');

                if (!row) return;

                // Get date inputs in the SAME row
                const orderedDateInput = row.querySelector('input[name*="ordered_date"]');
                const receivedDateInput = row.querySelector('input[name*="received_date"]');

                // Get original status from data attribute
                const originalStatus = row.dataset.originalStatus || 'PENDING';

                // ---------------------------------------------------------
                // 1. BACKWARD MOVEMENT CHECK 
                // ---------------------------------------------------------
                if (isBackwardChange(originalStatus, newStatus)) {

                    // REVERT IMMEDIATELY (Visual Revert)
                    this.value = originalStatus;

                    // Show Bootstrap Modal
                    showConfirmationModal(originalStatus, newStatus, row, this);
                    return;
                }

                // ---------------------------------------------------------
                // 2. FORWARD MOVEMENT (AUTO-FILL)
                // ---------------------------------------------------------
                handleForwardLogic(newStatus, orderedDateInput, receivedDateInput);

                // Update original status for next change
                row.dataset.originalStatus = newStatus;
            });

            // Mark as attached
            dropdown.dataset.listenerAttached = 'true';
        });
    }

    // ==========================================
    // MODAL LOGIC (Variables & Interaction)
    // ==========================================

    function showConfirmationModal(originalStatus, newStatus, row, dropdownElement) {
        const modalEl = document.getElementById('statusConfirmModal');
        if (!modalEl) {
            // Fallback if modal missing (should not happen)
            if (confirm(`Reverting ${originalStatus} -> ${newStatus}. Clear dates?`)) {
                applyConfirmedChange(originalStatus, newStatus, row, dropdownElement);
            }
            return;
        }

        // Initialize Bootstrap Modal (if not cached)
        if (!modalInstance) {
            modalInstance = new bootstrap.Modal(modalEl);
        }

        // Set Modal Content
        const fromEl = document.getElementById('modalFromIcon');
        const toEl = document.getElementById('modalToIcon');
        const dateTypeEl = document.getElementById('modalDateType');

        if (fromEl) fromEl.textContent = originalStatus;
        if (toEl) toEl.textContent = newStatus;

        // Determine what date will be cleared
        let dateType = "Relevant";
        if (originalStatus === 'RECEIVED' && newStatus === 'ORDERED') {
            dateType = "Received";
        } else if (newStatus === 'PENDING') {
            dateType = "Ordered & Received";
        }
        if (dateTypeEl) dateTypeEl.textContent = dateType;

        // Store state for 'Yes' click
        pendingChange = {
            originalStatus: originalStatus,
            newStatus: newStatus,
            row: row,
            dropdown: dropdownElement
        };

        // Show
        modalInstance.show();
    }

    // LISTENER FOR MODAL "YES" BUTTON
    const confirmBtn = document.getElementById('confirmStatusChangeBtn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function () {
            if (pendingChange && modalInstance) {
                // Execute the change
                applyConfirmedChange(
                    pendingChange.originalStatus,
                    pendingChange.newStatus,
                    pendingChange.row,
                    pendingChange.dropdown
                );

                // Close Modal
                modalInstance.hide();
                pendingChange = null;
            }
        });
    }

    // Execute Logic AFTER Confirmation
    function applyConfirmedChange(originalStatus, newStatus, row, dropdown) {
        const orderedDateInput = row.querySelector('input[name*="ordered_date"]');
        const receivedDateInput = row.querySelector('input[name*="received_date"]');

        // 1. Update Dropdown Value Visually (it was reverted before)
        dropdown.value = newStatus;

        // 2. Clear Dates Logic

        // Case A: RECEIVED -> ORDERED
        if (originalStatus === 'RECEIVED' && newStatus === 'ORDERED') {
            if (receivedDateInput) receivedDateInput.value = '';
        }

        // Case B: ANY -> PENDING
        else if (newStatus === 'PENDING') {
            if (orderedDateInput) orderedDateInput.value = '';
            if (receivedDateInput) receivedDateInput.value = '';
        }

        // 3. Update Status Tracker AND Dispatch Change for Color Logic
        row.dataset.originalStatus = newStatus;

        // Dispatch change event to trigger any style updates (colors, icons)
        // Since we updated dataset.originalStatus *before* this, 
        // it won't trigger the modal loop again.
        const event = new Event('change');
        dropdown.dispatchEvent(event);
    }

    // Logic for Forward moves (Auto-fill)
    function handleForwardLogic(newStatus, orderedDateInput, receivedDateInput) {
        // Case A: Status becomes ORDERED
        if (newStatus === 'ORDERED') {
            if (orderedDateInput && !orderedDateInput.value) {
                orderedDateInput.value = getTodayDate();
            }
        }

        // Case B: Status becomes RECEIVED
        if (newStatus === 'RECEIVED') {
            if (receivedDateInput && !receivedDateInput.value) {
                receivedDateInput.value = getTodayDate();
            }
        }
    }

    // Helper: Check if status change is backward
    function isBackwardChange(fromStatus, toStatus) {
        const statusOrder = {
            'PENDING': 0,
            'ORDERED': 1,
            'RECEIVED': 2
        };

        const safeFrom = (fromStatus || 'PENDING').toUpperCase();
        const safeTo = (toStatus || 'PENDING').toUpperCase();

        const fromIndex = statusOrder[safeFrom] !== undefined ? statusOrder[safeFrom] : 0;
        const toIndex = statusOrder[safeTo] !== undefined ? statusOrder[safeTo] : 0;

        return toIndex < fromIndex;
    }

    // Helper: Get today's date in YYYY-MM-DD format
    function getTodayDate() {
        const today = new Date();
        const year = today.getFullYear();
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const day = String(today.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    // Initialize on page load
    attachSpareStatusListeners();

    // Re-initialize when new spare row is added
    const addSpareBtn = document.getElementById('add-spare-btn');
    if (addSpareBtn) {
        addSpareBtn.addEventListener('click', function () {
            // Slight delay to ensure DOM is updated
            setTimeout(attachSpareStatusListeners, 200);
        });
    }
});
