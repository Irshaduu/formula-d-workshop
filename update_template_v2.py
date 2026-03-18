# -*- coding: utf-8 -*-
"""
Simple, line-by-line template updater for spare parts section
"""
import re

# Read the file
with open(r'c:\Users\irsha\Downloads\Test\formulad_workshop\workshop\templates\workshop\jobcard\jobcard_form.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Add {% load static %} after {% extends %}
if '{% load static %}' not in ''.join(lines[:5]):
    for i, line in enumerate(lines[:5]):
        if '{% extends' in line:
            lines.insert(i+1, '{% load static %}\n')
            break

# Find and replace in spare parts header section
for i, line in enumerate(lines):
    # Update header row
    if '<div class="swipe-cell col-part">Part Name</div>' in line:
        # Check if this is in the spare parts section (look ahead for status column)
        if i+2 < len(lines) and 'col-status">Status</div>' in lines[i+2]:
            # This is the spare parts header, replace next few lines
            lines[i+1] = '                            <div class="swipe-cell col-qty text-center">Qty</div>\n'
            lines[i+2] = '                            <div class="swipe-cell col-shop">Shop</div>\n'
            lines[i+3] = '                            <div class="swipe-cell col-status">Status</div>\n'
            lines[i+4] = '                            {% if user.is_authenticated %}\n'
            lines[i+5] = '                            <div class="swipe-cell col-price text-end">Shop Price</div>\n'
            lines[i+6] = '                            <div class="swipe-cell col-actions"></div>\n'
            lines[i+7] = '                            {% endif %}\n'
            break

# Write the file back
with open(r'c:\Users\irsha\Downloads\Test\formulad_workshop\workshop\templates\workshop\jobcard\jobcard_form.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Step 1/3: Header updated")

# Now replace the spare row content - more carefully
with open(r'c:\Users\irsha\Downloads\Test\formulad_workshop\workshop\templates\workshop\jobcard\jobcard_form.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for the spare items loop - find the old row structure
old_spare_row = '''{% for s_form in spare_formset %}
                            <div class="swipe-row">
                                {{ s_form.id }}
                                <div class="d-none">{{ s_form.DELETE }}</div>
                                <div class="swipe-cell col-part">
                                    {{ s_form.spare_part_name }}
                                </div>
                                <div class="swipe-cell col-qty">
                                    {{ s_form.quantity }}
                                </div>
                                <div class="swipe-cell col-status">
                                    {{ s_form.status }}
                                </div>
                                {% if user.is_authenticated %}
                                <div class="swipe-cell col-price">
                                    {{ s_form.unit_price }}'''

new_spare_row_start = '''{% for s_form in spare_formset %}
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
                                    {{ s_form.unit_price }}'''

if old_spare_row in content:
    content = content.replace(old_spare_row, new_spare_row_start)
    print("Step 2/3: Spare row beginning updated")
else:
    print("WARNING: Could not find spare row pattern")

# Now add the 3-dot dropdown and close the row properly
old_row_end = '''                                </div>
                                <div class="swipe-cell col-total">
                                    {{ s_form.total_price }}
                                </div>
                                {% endif %}
                            </div>
                            {% endfor %}'''

new_row_end = '''                                </div>
                                
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

if old_row_end in content:
    content = content.replace(old_row_end, new_row_end)
    print("Step 2/3: Spare row end updated")

# Update empty form template
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
    print("Step 3/3: Empty form template updated")

# Add JavaScript include before {% endblock %} if not present
if "spare_autofill.js" not in content:
    content = content.replace(
        '{% endblock %}',
        '''<!-- Spare Parts Auto-fill Script -->
<script src="{% static 'js/spare_autofill.js' %}"></script>
{% endblock %}'''
    )
    print("JavaScript include added")

# Write final content
with open(r'c:\Users\irsha\Downloads\Test\formulad_workshop\workshop\templates\workshop\jobcard\jobcard_form.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Template updated successfully!")
