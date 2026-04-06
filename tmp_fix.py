import os
files = [
    r"workshop\templates\workshop\manage\manage_dashboard.html",
    r"workshop\templates\workshop\jobcard\trash_list.html",
    r"workshop\templates\workshop\jobcard\jobcard_list.html",
    r"workshop\templates\workshop\jobcard\jobcard_form.html",
    r"workshop\templates\workshop\jobcard\jobcard_detail.html",
    r"workshop\templates\workshop\invoice\invoice_template.html",
    r"workshop\templates\workshop\dashboard\dashboard_home.html",
    r"workshop\templates\workshop\base.html",
    r"inventory\templates\inventory\manage.html",
    r"inventory\templates\inventory\category_detail.html",
    r"workshop\templates\workshop\auth\admin_login.html",
    r"workshop\templates\workshop\auth\otp_verify.html",
]

for f in files:
    if os.path.exists(f):
        # 1. Read entire content cleanly
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 2. Skip if it doesn't need replacement
        if "auth_extras" not in content:
            continue
            
        # 3. Replace strings explicitly
        new_content = content.replace("{% load auth_extras %}", "{% load custom_filters %}")
        new_content = new_content.replace("{% load static auth_extras %}", "{% load static custom_filters %}")
        
        # 4. Write back fully
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print(f"Fixed: {f}")
