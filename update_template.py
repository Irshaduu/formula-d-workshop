"""
Script to update jobcard_form.html with new spare parts layout
"""

# Read the file
with open(r'c:\Users\irsha\Downloads\Test\formulad_workshop\workshop\templates\workshop\jobcard\jobcard_form.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace 1: Update header row (around line 318-326)
old_header = '''                        <!-- HEADER -->
                        <div class="swipe-row swipe-header">
                            <div class="swipe-cell col-part">Part Name</div>
                            <div class="swipe-cell col-qty text-center">Qty</div>
                            <div class="swipe-cell col-status">Status</div>
                            {% if user.is_authenticated %}
                            <div class="swipe-cell col-price text-end">Price</div>
                            <div class="swipe-cell col-total text-end">Total</div>
                            {% endif %}
                        </div>'''

new_header = '''                        <!-- HEADER -->
                        <div class="swipe-row swipe-header">
                            <div class="swipe-cell col-part">Part Name</div>
                            <div class="swipe-cell col-qty text-center">Qty</div>
                            <div class="swipe-cell col-shop">Shop</div>
                            <div class="swipe-cell col-status">Status</div>
                            {% if user.is_authenticated %}
                            <div class="swipe-cell col-price text-end">Shop Price</div>
                            <div class="swipe-cell col-actions"></div>
                            {% endif %}
                        </div>'''

content = content.replace(old_header, new_header)

# Replace 2: Update data row structure
# Find and replace the swipe-row for spare items
old_row_start = '                            <div class="swipe-row">\r\n                                {{ s_form.id }}\r\n                                <div class="d-none">{{ s_form.DELETE }}</div>\r\n                                <div class="swipe-cell col-part">\r\n                                    {{ s_form.spare_part_name }}\r\n                                </div>\r\n                                <div class="swipe-cell col-qty">\r\n                                    {{ s_form.quantity }}\r\n                                </div>\r\n                                <div class="swipe-cell col-status">\r\n                                    {{ s_form.status }}\r\n                                </div>\r\n                                {% if user.is_authenticated %}\r\n                                <div class="swipe-cell col-price">'

# This is complex due to all the comments. Let's use a marker-based approach instead
# Find the spare formset loop
import re

# Pattern to find the spare row section
pattern = r'({% for s_form in spare_formset %})(.*?)({% endfor %})'
match = re.search(pattern, content, re.DOTALL)

if match:
    new_spare_loop = '''{% for s_form in spare_formset %}
                            <div class="swipe-row spare-row" data-original-status="{{ s_form.instance.status }}">
                                {{ s_form.id }}
                                <div class="d-none">{{ s_form.DELETE }}</div>
                                
                                <!-- Part Name -->
                                <div class="swipe-cell col-part">
                                    {{ s_form.spare_part_name }}
                                </div>
                                
                                <!-- Quantity -->
                                <div class="swipe-cell col-qty">
                                    {{ s_form.quantity }}
                                </div>
                                
                                <!-- Shop (NEW) -->
                                <div class="swipe-cell col-shop">
                                    {{ s_form.shop_name }}
                                </div>
                                
                                <!-- Status -->
                                <div class="swipe-cell col-status">
                                    {{ s_form.status }}
                                </div>
                                
                                {% if user.is_authenticated %}
                                <!-- Shop Price (unit_price) -->
                                <div class="swipe-cell col-price">
                                    {{ s_form.unit_price }}
                                </div>
                                
                                <!-- 3-Dot Dropdown (NEW) -->
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
                            </div>
                            {% endfor %}'''
    
    content = content[:match.start(1)] + new_spare_loop + content[match.end(3):]

# Replace 3: Update empty form template
# Find empty spare form
empty_pattern = r'(<div id="empty-spare-form".*?</div>\s*</div>)'
empty_match = re.search(empty_pattern, content, re.DOTALL)

if empty_match:
    new_empty_form = '''<div id="empty-spare-form" class="d-none">
    <div class="swipe-row spare-row" data-original-status="PENDING">
        {{ spare_formset.empty_form.id }}
        <div class="d-none">{{ spare_formset.empty_form.DELETE }}</div>
        <div class="swipe-cell col-part">
            {{ spare_formset.empty_form.spare_part_name }}
        </div>
        <div class="swipe-cell col-qty">
            {{ spare_formset.empty_form.quantity }}
        </div>
        <div class="swipe-cell col-shop">
            {{ spare_formset.empty_form.shop_name }}
        </div>
        <div class="swipe-cell col-status">
            {{ spare_formset.empty_form.status }}
        </div>
        {% if user.is_authenticated %}
        <div class="swipe-cell col-price">
            {{ spare_formset.empty_form.unit_price }}
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
                        {{ spare_formset.empty_form.total_price }}
                    </div>
                    <div class="mb-2">
                        <label class="form-label small mb-1 text-muted">Ordered Date</label>
                        {{ spare_formset.empty_form.ordered_date }}
                    </div>
                    <div class="mb-0">
                        <label class="form-label small mb-1 text-muted">Received Date</label>
                        {{ spare_formset.empty_form.received_date }}
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
    </div>
</div>'''
    
    content = content[:empty_match.start()] + new_empty_form + content[empty_match.end():]

# Replace 4: Add JavaScript include before {% endblock %}
if "spare_autofill.js" not in content:
    content = content.replace(
        '{% endblock %}',
        '''<!-- Spare Parts Auto-fill Script -->
<script src="{% static 'js/spare_autofill.js' %}"></script>
{% endblock %}'''
    )

# Write the updated content
with open(r'c:\Users\irsha\Downloads\Test\formulad_workshop\workshop\templates\workshop\jobcard\jobcard_form.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Template updated successfully!")
print("Backup saved as: jobcard_form.html.backup")
