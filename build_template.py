# -*- coding: utf-8 -*-
"""
Clean template builder for spare parts enhancement
Reads the backup and creates a corrected version
"""

# Read the backup file
with open(r'c:\Users\irsha\Downloads\Test\formulad_workshop\workshop\templates\workshop\jobcard\jobcard_form.html.backup', 'r', encoding='utf-8') as f:
    content = f.read()

print("Step 1/5: Reading backup file...")

# Step 1: Add {% load static %} after {% extends %}
if '{% load static %}' not in content:
    content = content.replace(
        "{% extends 'workshop/base.html' %}\r\n",
        "{% extends 'workshop/base.html' %}\r\n{% load static %}\r\n"
    )
    print("Step 2/5: Added {% load static %}")
else:
    print("Step 2/5: {% load static %} already present")

# Step 2: Update spare parts HEADER
old_header = """                        <!-- HEADER -->
                        <div class="swipe-row swipe-header">
                            <div class="swipe-cell col-part">Part Name</div>
                            <div class="swipe-cell col-qty text-center">Qty</div>
                            <div class="swipe-cell col-status">Status</div>
                            {% if user.is_authenticated %}
                            <div class="swipe-cell col-price text-end">Price</div>
                            <div class="swipe-cell col-total text-end">Total</div>
                            {% endif %}
                        </div>"""

new_header = """                        <!-- HEADER -->
                        <div class="swipe-row swipe-header">
                            <div class="swipe-cell col-part">Part Name</div>
                            <div class="swipe-cell col-qty text-center">Qty</div>
                            <div class="swipe-cell col-shop">Shop</div>
                            <div class="swipe-cell col-status">Status</div>
                            {% if user.is_authenticated %}
                            <div class="swipe-cell col-price text-end">Shop Price</div>
                            <div class="swipe-cell col-actions"></div>
                            {% endif %}
                        </div>"""

if old_header in content:
    content = content.replace(old_header, new_header)
    print("Step 3/5: Updated spare parts header")
else:
    print("WARNING: Spare parts header not found")

# Step 3: Update spare parts DATA ROWS (the tricky part)
# Find the exact section between {% for s_form in spare_formset %} and {% endfor %}

# Split content to find the spare formset section
import re

# Pattern to match the entire spare formset loop
pattern = r'({% for s_form in spare_formset %})(.*?)({% endfor %})'

def spare_row_replacement(match):
    """Replace the spare formset loop content"""
    return '''{% for s_form in spare_formset %}
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

# Find all occurrences - we need the one in the spare-list div, not the empty form
matches = list(re.finditer(pattern, content, re.DOTALL))

if len(matches) >= 1:
    # Replace only the first match (the actual data loop)
    match = matches[0]
    content = content[:match.start()] + spare_row_replacement(match) + content[match.end():]
    print("Step 4/5: Updated spare parts data rows")
else:
    print("WARNING: Spare formset loop not found")

# Step 4: Update EMPTY FORM template
old_empty = '''<div id="empty-spare-form" class="d-none">
    <div class="swipe-row">
        {{ spare_formset.empty_form.id }}
        <div class="d-none">{{ spare_formset.empty_form.DELETE }}</div>
        <div class="swipe-cell col-part">
            {{ spare_formset.empty_form.spare_part_name }}
        </div>
        <div class="swipe-cell col-qty">
            {{ spare_formset.empty_form.quantity }}
        </div>
        <div class="swipe-cell col-status">
            {{ spare_formset.empty_form.status }}
        </div>
        {% if user.is_authenticated %}
        <div class="swipe-cell col-price">
            {{ spare_formset.empty_form.unit_price }}
        </div>
        <div class="swipe-cell col-total">
            {{ spare_formset.empty_form.total_price }}
        </div>
        {% endif %}
    </div>
</div>'''

new_empty = '''<div id="empty-spare-form" class="d-none">
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

if old_empty in content:
    content = content.replace(old_empty, new_empty)
    print("Step 5/5: Updated empty form template")
else:
    print("WARNING: Empty spare form not found")

# Step 5: Add JavaScript include before last {% endblock %}
if "spare_autofill.js" not in content:
    # Find the last {% endblock %}
    last_endblock_pos = content.rfind('{% endblock %}')
    if last_endblock_pos != -1:
        js_include = '''<!-- Spare Parts Auto-fill Script -->
<script src="{% static 'js/spare_autofill.js' %}"></script>
'''
        content = content[:last_endblock_pos] + js_include + content[last_endblock_pos:]
        print("Bonus: Added JavaScript include")
    else:
        print("WARNING: Could not find {% endblock %}")
else:
    print("Bonus: JavaScript include already present")

# Write the corrected file
output_path = r'c:\Users\irsha\Downloads\Test\formulad_workshop\workshop\templates\workshop\jobcard\jobcard_form.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*50)
print("SUCCESS! Template file created successfully!")
print("="*50)
print("\nFile saved to:")
print(output_path)
print("\nRefresh browser to see changes!")
