import os
import re

def update_template_base(file_path, old_base, new_base):
    """Update the base template in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the extends tag
    pattern = re.compile(r'{%\s*extends\s*[\'"]' + old_base + r'[\'"]\s*%}')
    updated_content = pattern.sub(f'{{% extends \'{new_base}\' %}}', content)
    
    # Fix URL references if needed
    updated_content = updated_content.replace('{% url \'employees:dashboard\' %}', '{% url \'Hr:dashboard\' %}')
    updated_content = updated_content.replace('{% url \'home\' %}', '{% url \'accounts:home\' %}')
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    return True

def find_and_update_templates(base_dir, old_base, new_base):
    """Find all templates that extend a specific base template and update them."""
    updated_templates = []
    pattern = re.compile(r'{%\s*extends\s*[\'"]' + old_base + r'[\'"]\s*%}')
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if pattern.search(content):
                        if update_template_base(file_path, old_base, new_base):
                            updated_templates.append(file_path)
    
    return updated_templates

if __name__ == "__main__":
    base_dir = "Hr/templates/Hr"
    old_base = "base_updated.html"
    new_base = "Hr/base_hr.html"
    
    updated_templates = find_and_update_templates(base_dir, old_base, new_base)
    
    print(f"Updated {len(updated_templates)} templates from '{old_base}' to '{new_base}':")
    for template in updated_templates:
        print(f"- {template}")
