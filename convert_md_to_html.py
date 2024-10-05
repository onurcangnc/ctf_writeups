import markdown2
import os
import re

# Base directory for your TryHackMe Markdown files
base_dir = './TryHackMe'

# CSS to add to the generated HTML files
css_content = """
<style>
    body {
        font-family: Arial, sans-serif;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        line-height: 1.6;
        background-color: #f4f4f4;
    }
    h1, h2, h3 {
        color: #333;
        border-bottom: 2px solid #ddd;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    p {
        margin-bottom: 20px;
    }
    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 0 auto 20px auto;
    }
    code {
        background-color: #f9f9f9;
        border: 1px solid #ccc;
        padding: 5px;
        border-radius: 5px;
    }
    pre {
        background-color: #333;
        color: #f8f8f2;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
    }
</style>
"""

# Function to replace Obsidian image links with proper Markdown image syntax
def replace_obsidian_links(markdown_content):
    """
    This function replaces Obsidian-style image links ![[...]] with standard
    Markdown image syntax ![alt text](./images/filename), ensuring that all image paths
    follow the pattern ./images/filename.
    """
    # Regex to find Obsidian image links like ![[path_to_image]]
    obsidian_link_pattern = r'!\[\[(.*?)\]\]'
    
    # Only keep the file name and replace the path with './images/'
    markdown_content = re.sub(obsidian_link_pattern, lambda match: f'![alt text](./images/{os.path.basename(match.group(1))})', markdown_content)
    
    return markdown_content

# Walk through the TryHackMe directory and convert .md files to HTML
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.md') and file != "README.md":  # Exclude README.md
            md_file = os.path.join(root, file)
            html_file = os.path.join(root, f"{file[:-3]}.html")  # Change .md to .html
            
            with open(md_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Convert Obsidian-style links to standard Markdown syntax
            markdown_content = replace_obsidian_links(markdown_content)

            # Convert the updated Markdown content to HTML
            html_content = markdown2.markdown(markdown_content)

            # Combine the CSS and the HTML content
            full_html_content = f"<html><head>{css_content}</head><body>{html_content}</body></html>"

            # Write the full HTML content to a file
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(full_html_content)

            print(f'{html_file} file successfully created.')
