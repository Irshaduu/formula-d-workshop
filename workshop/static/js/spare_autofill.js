// SPARE PARTS AUTO-FILL ENHANCED LOGIC
//
// Auto-fills ordered_date and received_date when status changes
// Prevents accidental backward status changes with confirmation

document.addEventListener('DOMContentLoaded', function () {

    // ==========================================
    // AUTO-FILL DATES ON STATUS CHANGE
    // ==========================================

    function attachSpareStatusListeners() {
        // Get all status dropdowns in spare parts section
        const statusDropdowns = document.querySelectorAll('#spare-list select[name*="status"]');

        statusDropdowns.forEach(dropdown => {
            dropdown.addEventListener('change', function () {
                const newStatus = this.value;
                const row = this.closest('.spare-row');

                if (!row) return;

                // Get date inputs in the SAME row (they're expandable cells)
                const orderedDateInput = row.querySelector('input[name*="ordered_date"]');
                const receivedDateInput = row.querySelector('input[name*="received_date"]');

                // Get original status from data attribute
                const originalStatus = row.dataset.originalStatus || 'PENDING';

                // Check if going backward
                if (isBackwardChange(originalStatus, newStatus)) {
                    if (!confirm(`Going back from ${originalStatus} to ${newStatus}. This may clear tracking dates. Continue?`)) {
                        // Revert to original
                        this.value = originalStatus;
                        return;
                    }

                    // Clear dates based on backward movement
                    // If going back to PENDING, clear both dates
                    if (newStatus === 'PENDING') {
                        if (orderedDateInput) orderedDateInput.value = '';
                        if (receivedDateInput) receivedDateInput.value = '';
                    }
                    // If going back to ORDERED (from RECEIVED), clear received_date only
                    else if (newStatus === 'ORDERED' && originalStatus === 'RECEIVED') {
                        if (receivedDateInput) receivedDateInput.value = '';
                    }
                }

                // Auto-fill ordered Date when status → ORDERED
                if (newStatus === 'ORDERED' && orderedDateInput && !orderedDateInput.value) {
                    orderedDateInput.value = getTodayDate();
                }

                // Auto-fill received_date when status → RECEIVED
                if (newStatus === 'RECEIVED' && receivedDateInput && !receivedDateInput.value) {
                    receivedDateInput.value = getTodayDate();
                }

                // Update original status for next change
                row.dataset.originalStatus = newStatus;
            });
        });
    }

    // Helper: Check if status change is backward
    function isBackwardChange(fromStatus, toStatus) {
        const statusOrder = {
            'PENDING': 0,
            'ORDERED': 1,
            'RECEIVED': 2
        };

        const fromIndex = statusOrder[fromStatus] || 0;
        const toIndex = statusOrder[toStatus] || 0;

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
            setTimeout(attachSpareStatusListeners, 100);
        });
    }
});
