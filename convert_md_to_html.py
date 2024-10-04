import markdown2
import os

# Find all markdown files then create HTML with all of them.
for file in os.listdir('.'):
    if file.endswith('.md'):
        html_file = f"{file[:-3]}.html"
        with open(file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        html_content = markdown2.markdown(markdown_content)
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f'{html_file} başarıyla güncellendi.')
