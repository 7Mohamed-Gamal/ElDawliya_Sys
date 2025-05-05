import re

# Path to the views.py file
views_file = 'accounts/views.py'

# Read the file
with open(views_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find the create_system_notification function call with the icon parameter
pattern = r"create_system_notification\(\s*user=user,\s*title='[^']*',\s*message=f'[^']*',\s*priority='[^']*',\s*icon='[^']*'\s*\)"

# Replacement pattern without the icon parameter
replacement = lambda match: match.group(0).replace(", icon='fas fa-sign-in-alt'", "")

# Replace the pattern in the file
modified_content = re.sub(pattern, replacement, content)

# Write back to the file
with open(views_file, 'w', encoding='utf-8') as f:
    f.write(modified_content)

print("Fixed the create_system_notification call in accounts/views.py")
print("The icon parameter has been removed as it's not accepted by the function.")
