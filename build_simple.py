# -*- coding: utf-8 -*-
"""
SIMPLE VERSION: Just add the basic columns first, no dropdown yet
"""

# Read backup
with open(r'c:\Users\irsha\Downloads\Test\formulad_workshop\workshop\templates\workshop\jobcard\jobcard_form.html.backup', 'r', encoding='utf-8') as f:
    content = f.read()

print("Step 1: Reading backup...")

# Add {% load static %}
content = content.replace(
    "{% extends 'workshop/base.html' %}\r\n",
    "{% extends 'workshop/base.html' %}\r\n{% load static %}\r\n"
)
print("Step 2: Added {% load static %}")

# Update header - SIMPLE VERSION (no 3-dot yet)
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
                            <div class="swipe-cell col-total text-end">Customer Price</div>
                            {% endif %}
                        </div>"""

content = content.replace(old_header, new_header)
print("Step 3: Updated header (6 columns)")

# Update data rows - SIMPLE VERSION (just add shop column, keep total visible)
old_row = """                            <div class="swipe-row">
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
                                    {{ s_form.unit_price }}
                                </div>
                                <div class="swipe-cell col-total">
                                    {{ s_form.total_price }}
                                </div>
                                {% endif %}
                            </div>"""

new_row = """                            <div class="swipe-row spare-row" data-original-status="{{ s_form.instance.status }}">
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
                                <div class="swipe-cell col-total">
                                    {{ s_form.total_price }}
                                </div>
                                {% endif %}
                            </div>"""

content = content.replace(old_row, new_row)
print("Step 4: Updated data rows (added shop column)")

# Update empty form - SIMPLE VERSION
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
        <div class="swipe-cell col-total">
            {{ spare_formset.empty_form.total_price }}
        </div>
        {% endif %}
    </div>
</div>'''

content = content.replace(old_empty, new_empty)
print("Step 5: Updated empty form")

# Add date fields (hidden for now, will add dropdown UI later)
# Add them after total_price in the data row
content = content.replace(
    '''                                <div class="swipe-cell col-total">
                                    {{ s_form.total_price }}
                                </div>
                                {% endif %}
                            </div>
                            {% endfor %}''',
    '''                                <div class="swipe-cell col-total">
                                    {{ s_form.total_price }}
                                    <div class="d-none">{{ s_form.ordered_date }}</div>
                                    <div class="d-none">{{ s_form.received_date }}</div>
                                </div>
                                {% endif %}
                            </div>
                            {% endfor %}'''
)
print("Step 6: Added hidden date fields")

# Write file
with open(r'c:\Users\irsha\Downloads\Test\formulad_workshop\workshop\templates\workshop\jobcard\jobcard_form.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*60)
print("SUCCESS! Simple version created")
print("="*60)
print("\nYou should now see:")
print("- Part Name | Qty | Shop | Status | Shop Price | Customer Price")
print("- Date fields are hidden (we'll add dropdown UI next)")
print("\nRefresh browser with Ctrl+Shift+R")
