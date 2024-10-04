import markdown2
import os

# TryHackMe klasörü içindeki alt dizinlerdeki .md dosyalarını bul ve her biri için HTML dosyası oluştur
base_dir = './TryHackMe'

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.md'):
            md_file = os.path.join(root, file)
            html_file = os.path.join(root, f"{file[:-3]}.html")  # .md'yi .html ile değiştir
            with open(md_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            html_content = markdown2.markdown(markdown_content)
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f'{html_file} başarıyla oluşturuldu.')
