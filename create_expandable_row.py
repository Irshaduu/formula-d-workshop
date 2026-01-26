"""
Create expandable row layout for spare parts
Click 3-dot → Row expands to show hidden fields below
"""

# Read current file
with open(r'c:\Users\irsha\Downloads\Test\formulad_workshop\workshop\templates\workshop\jobcard\jobcard_form.html', 'r', encoding='utf-8') as f:
    content = f.read()

print("Creating expandable row layout...")

# Find and replace the data row section with expandable version
old_row = '''                            <div class="swipe-row spare-row" data-original-status="{{ s_form.instance.status }}">
                                {{ s_form.id }}
                                <div class="d-none">{{ s_form.DELETE }}</div>
                                <div class="swipe-cell col-part">
                                    {{ s_form.spare_part_name }}
                                </div>
                                <div class="swipe-cell col-qty">
                                    {{ s_form.quantity }}
                                </div>
                                <div class="swipe-cell col-shop">
                                    {{ s_form.shop_name }}
                                </div>
                                <div class="swipe-cell col-status">
                                    {{ s_form.status }}
                                </div>
                                {% if user.is_authenticated %}
                                <div class="swipe-cell col-price">
                                    {{ s_form.unit_price }}
                                </div>
                                <div class="swipe-cell col-actions">
                                    <div class="dropdown">
                                        <button class="btn btn-sm btn-link p-0 text-muted" type="button" 
                                                data-bs-toggle="dropdown" aria-expanded="false">
                                            <i class="bi bi-three-dots-vertical"></i>
                                        </button>
                                        <div class="dropdown-menu dropdown-menu-end p-3" style="min-width: 250px;">
                                            <div class="mb-2">
                                                <label class="form-label small mb-1 text-muted">Customer Price</label>
                                                {{ s_form.total_price }}
                                            </div>
                                            <div class="mb-2">
                                                <label class="form-label small mb-1 text-muted">Ordered Date</label>
                                                {{ s_form.ordered_date }}
                                            </div>
                                            <div class="mb-0">
                                                <label class="form-label small mb-1 text-muted">Received Date</label>
                                                {{ s_form.received_date }}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                {% endif %}
                            </div>'''

new_row = '''                            <!-- Main Row -->
                            <div class="swipe-row spare-row" data-original-status="{{ s_form.instance.status }}">
                                {{ s_form.id }}
                                <div class="d-none">{{ s_form.DELETE }}</div>
                                <div class="swipe-cell col-part">
                                    {{ s_form.spare_part_name }}
                                </div>
                                <div class="swipe-cell col-qty">
                                    {{ s_form.quantity }}
                                </div>
                                <div class="swipe-cell col-shop">
                                    {{ s_form.shop_name }}
                                </div>
                                <div class="swipe-cell col-status">
                                    {{ s_form.status }}
                                </div>
                                {% if user.is_authenticated %}
                                <div class="swipe-cell col-price">
                                    {{ s_form.unit_price }}
                                </div>
                                <div class="swipe-cell col-actions">
                                    <button class="btn btn-sm btn-link p-0 text-muted toggle-details" type="button">
                                        <i class="bi bi-chevron-down"></i>
                                    </button>
                                </div>
                                {% endif %}
                            </div>
                            <!-- Expandable Details Row (hidden by default) -->
                            <div class="swipe-row spare-details" style="display: none;">
                                <div class="swipe-cell col-part"></div>
                                <div class="swipe-cell col-qty"></div>
                                <div class="swipe-cell col-shop">
                                    <label class="form-label small mb-1 text-muted">Customer Price</label>
                                    {{ s_form.total_price }}
                                </div>
                                <div class="swipe-cell col-status">
                                    <label class="form-label small mb-1 text-muted">Ordered Date</label>
                                    {{ s_form.ordered_date }}
                                </div>
                                {% if user.is_authenticated %}
                                <div class="swipe-cell col-price">
                                    <label class="form-label small mb-1 text-muted">Received Date</label>
                                    {{ s_form.received_date }}
                                </div>
                                <div class="swipe-cell col-actions"></div>
                                {% endif %}
                            </div>'''

if old_row in content:
    content = content.replace(old_row, new_row)
    print("✓ Updated spare row to expandable layout")
else:
    print("WARNING: Old row pattern not found")

# Write back
with open(r'c:\Users\irsha\Downloads\Test\formulad_workshop\workshop\templates\workshop\jobcard\jobcard_form.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Now create the JavaScript to handle toggle
js_code = '''
// Toggle expandable spare parts details
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(e) {
        if (e.target.closest('.toggle-details')) {
            const button = e.target.closest('.toggle-details');
            const row = button.closest('.spare-row');
            const detailsRow = row.nextElementSibling;
            
            if (detailsRow && detailsRow.classList.contains('spare-details')) {
                // Toggle visibility
                if (detailsRow.style.display === 'none') {
                    detailsRow.style.display = 'flex';
                    button.querySelector('i').classList.replace('bi-chevron-down', 'bi-chevron-up');
                } else {
                    detailsRow.style.display = 'none';
                    button.querySelector('i').classList.replace('bi-chevron-up', 'bi-chevron-down');
                }
            }
        }
    });
});
'''

# Append to spare_autofill.js
with open(r'c:\Users\irsha\Downloads\Test\formulad_workshop\workshop\static\js\spare_autofill.js', 'a', encoding='utf-8') as f:
    f.write('\n\n' + js_code)

print("✓ Added toggle JavaScript")
print("\n" + "="*60)
print("SUCCESS! Expandable row layout created")
print("="*60)
print("\nNow:")
print("1. Refresh browser (Ctrl+Shift+R)")
print("2. Click the chevron (v) button to expand/collapse")
print("3. Hidden fields appear in the same row style!")
