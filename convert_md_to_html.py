import markdown2
import os
import re

# Base directory for your TryHackMe Markdown files
base_dir = './TryHackMe'

# Function to replace Obsidian image links with proper Markdown image syntax
def replace_obsidian_links(markdown_content):
    """
    This function replaces Obsidian-style image links ![[...]] with standard
    Markdown image syntax ![alt text](./images/path_to_image), ensuring that
    all image paths follow the ./images/ pattern.
    """
    # Regex to find Obsidian image links like ![[images/path_to_image]]
    obsidian_link_pattern = r'!\[\[(.*?)\]\]'
    
    # Replace them with standard Markdown image syntax and ensure ./images/ is used
    markdown_content = re.sub(obsidian_link_pattern, r'![alt text](./images/\1)', markdown_content)
    
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

            # Write the HTML content to a file
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f'{html_file} file successfully created.')
