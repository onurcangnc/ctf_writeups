import markdown2
import os

# Base directory for your TryHackMe Markdown files
base_dir = './TryHackMe'

# Function to replace image paths in Markdown content
def replace_image_paths(markdown_content, md_dir):
    """
    Replace 'images/' with the relative path from the Markdown file's directory.
    This will point to the 'images' folder inside the same folder as the Markdown file.
    """
    return markdown_content.replace("images/", f"{md_dir}/images/")

# Walk through the TryHackMe directory and convert .md files to HTML
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith('.md') and file != "README.md":  # Exclude README.md
            md_file = os.path.join(root, file)
            html_file = os.path.join(root, f"{file[:-3]}.html")  # Change .md to .html
            
            with open(md_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # Get the directory where the Markdown file is located
            md_dir = os.path.basename(root)

            # Replace local image paths with the correct paths from the 'images' folder inside the same directory
            markdown_content_with_images = replace_image_paths(markdown_content, md_dir)

            # Convert the updated Markdown content to HTML
            html_content = markdown2.markdown(markdown_content_with_images)

            # Write the HTML content to a file
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            print(f'{html_file} file successfully created.')
