#!/usr/bin/env python3
"""
Obsidian to HTML Converter
Converts all Markdown files from Obsidian vault to HTML for GitHub Pages.
Supports multiple categories/directories, not just CTF writeups.
"""

import markdown2
import os
import re
import json
from pathlib import Path
from datetime import datetime

# Configuration
CONFIG = {
    "base_dirs": [
        "TryHackMe",
        "HackTheBox", 
        "CheatSheets",
        "Notes",
        "Research",
        "Blog",
        "Projects",
        "Writeups"
    ],
    "exclude_files": ["README.md", "TryHackMe.md", "index.md", "_index.md"],
    "exclude_dirs": [".obsidian", ".git", "templates", "attachments", "_templates"],
    "output_file": "index.html"
}

# Category icons and descriptions
CATEGORY_META = {
    "TryHackMe": {
        "icon": "🎯",
        "description": "TryHackMe CTF challenge writeups and solutions"
    },
    "HackTheBox": {
        "icon": "📦",
        "description": "HackTheBox machine writeups and walkthroughs"
    },
    "CheatSheets": {
        "icon": "📋",
        "description": "Quick reference guides and command cheat sheets"
    },
    "Notes": {
        "icon": "📝",
        "description": "Technical notes and learning materials"
    },
    "Research": {
        "icon": "🔬",
        "description": "Security research and vulnerability analysis"
    },
    "Blog": {
        "icon": "✍️",
        "description": "Blog posts and articles"
    },
    "Projects": {
        "icon": "🚀",
        "description": "Project documentation and guides"
    },
    "Writeups": {
        "icon": "📄",
        "description": "General CTF and challenge writeups"
    }
}

# Modern CSS for converted HTML pages
PAGE_CSS = """
<style>
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-code: #1a1a24;
        --accent: #00ff88;
        --accent-dim: #00cc6a;
        --text: #e4e4e7;
        --text-dim: #a1a1aa;
        --border: #27272a;
    }
    
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    body {
        font-family: 'Segoe UI', system-ui, sans-serif;
        background: var(--bg-primary);
        color: var(--text);
        line-height: 1.8;
        padding: 40px 20px;
        max-width: 900px;
        margin: 0 auto;
    }
    
    .back-link {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: var(--accent);
        text-decoration: none;
        font-size: 0.875rem;
        margin-bottom: 32px;
        padding: 8px 16px;
        background: var(--bg-secondary);
        border-radius: 8px;
        border: 1px solid var(--border);
        transition: all 0.3s;
    }
    
    .back-link:hover {
        background: var(--bg-code);
        border-color: var(--accent);
    }
    
    h1 {
        font-size: 2.5rem;
        margin-bottom: 16px;
        color: var(--text);
        border-bottom: 2px solid var(--accent);
        padding-bottom: 16px;
    }
    
    h2 {
        font-size: 1.75rem;
        margin: 48px 0 16px;
        color: var(--text);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    h2::before {
        content: '##';
        color: var(--accent);
        font-family: monospace;
        font-size: 1rem;
    }
    
    h3 {
        font-size: 1.25rem;
        margin: 32px 0 12px;
        color: var(--text-dim);
    }
    
    p { margin-bottom: 16px; }
    
    a {
        color: var(--accent);
        text-decoration: none;
        border-bottom: 1px solid transparent;
        transition: border-color 0.3s;
    }
    
    a:hover { border-bottom-color: var(--accent); }
    
    img {
        max-width: 100%;
        height: auto;
        border-radius: 12px;
        margin: 24px 0;
        border: 1px solid var(--border);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    code {
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        background: var(--bg-code);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.9em;
        color: var(--accent);
        border: 1px solid var(--border);
    }
    
    pre {
        background: var(--bg-secondary);
        padding: 20px;
        border-radius: 12px;
        overflow-x: auto;
        margin: 24px 0;
        border: 1px solid var(--border);
        position: relative;
    }
    
    pre::before {
        content: 'terminal';
        position: absolute;
        top: 8px;
        right: 12px;
        font-size: 0.75rem;
        color: var(--text-dim);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    pre code {
        background: none;
        padding: 0;
        border: none;
        color: var(--text);
    }
    
    blockquote {
        border-left: 3px solid var(--accent);
        padding-left: 20px;
        margin: 24px 0;
        color: var(--text-dim);
        font-style: italic;
    }
    
    ul, ol {
        margin: 16px 0 16px 24px;
    }
    
    li {
        margin-bottom: 8px;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 24px 0;
    }
    
    th, td {
        padding: 12px 16px;
        text-align: left;
        border: 1px solid var(--border);
    }
    
    th {
        background: var(--bg-secondary);
        color: var(--accent);
        font-weight: 600;
    }
    
    tr:nth-child(even) { background: var(--bg-secondary); }
    
    hr {
        border: none;
        height: 1px;
        background: var(--border);
        margin: 40px 0;
    }
    
    .meta {
        display: flex;
        gap: 24px;
        margin-bottom: 32px;
        padding: 16px;
        background: var(--bg-secondary);
        border-radius: 8px;
        font-size: 0.875rem;
        color: var(--text-dim);
    }
    
    .meta-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }
</style>
"""

def replace_obsidian_links(content: str) -> str:
    """Convert Obsidian-style links to standard Markdown/HTML."""
    # Image links: ![[image.png]] -> ![](./images/image.png)
    content = re.sub(
        r'!\[\[(.*?)\]\]',
        lambda m: f'![{os.path.basename(m.group(1))}](./images/{os.path.basename(m.group(1))})',
        content
    )
    
    # Wiki links: [[Page]] -> Page (just text, no link for now)
    content = re.sub(r'\[\[([^\]|]+)\]\]', r'\1', content)
    
    # Wiki links with alias: [[Page|Alias]] -> Alias
    content = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', content)
    
    return content

def extract_title(content: str, filename: str) -> str:
    """Extract title from markdown content or filename."""
    # Try to find H1
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    
    # Fallback to filename
    return filename.replace('.md', '').replace('-', ' ').replace('_', ' ').title()

def extract_description(content: str) -> str:
    """Extract first paragraph as description."""
    # Remove frontmatter
    content = re.sub(r'^---.*?---\s*', '', content, flags=re.DOTALL)
    
    # Remove H1
    content = re.sub(r'^#\s+.+$', '', content, re.MULTILINE)
    
    # Get first paragraph
    paragraphs = re.findall(r'^[A-Za-z].+', content, re.MULTILINE)
    if paragraphs:
        desc = paragraphs[0][:150]
        if len(paragraphs[0]) > 150:
            desc += '...'
        return desc
    
    return "No description available."

def convert_md_to_html(md_path: Path) -> dict:
    """Convert a markdown file to HTML and return metadata."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract metadata before conversion
    title = extract_title(content, md_path.name)
    description = extract_description(content)
    
    # Convert Obsidian links
    content = replace_obsidian_links(content)
    
    # Convert to HTML with extras
    html_content = markdown2.markdown(
        content,
        extras=['fenced-code-blocks', 'tables', 'strike', 'task_list']
    )
    
    # Get file stats
    stat = md_path.stat()
    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
    
    # Calculate relative path to index.html based on directory depth
    depth = len(md_path.parts) - 1  # -1 for the filename itself
    back_path = '../' * depth + 'index.html' if depth > 0 else 'index.html'
    
    # Build full HTML
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    {PAGE_CSS}
</head>
<body>
    <a href="{back_path}" class="back-link">← Back to Index</a>
    <div class="meta">
        <span class="meta-item">📅 Updated: {modified}</span>
        <span class="meta-item">📂 {md_path.parent.name}</span>
    </div>
    <article>
        {html_content}
    </article>
</body>
</html>"""
    
    # Write HTML file
    html_path = md_path.with_suffix('.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✓ Converted: {md_path} -> {html_path}")
    
    return {
        'title': title,
        'description': description,
        'path': str(html_path),
        'modified': modified,
        'category': md_path.parts[0] if len(md_path.parts) > 1 else 'Uncategorized'
    }

def discover_documents() -> dict:
    """Discover all markdown files organized by category."""
    categories = {}
    
    for base_dir in CONFIG['base_dirs']:
        if not os.path.exists(base_dir):
            continue
            
        docs = []
        for root, dirs, files in os.walk(base_dir):
            # Filter excluded directories
            dirs[:] = [d for d in dirs if d not in CONFIG['exclude_dirs']]
            
            for file in files:
                if file.endswith('.md') and file not in CONFIG['exclude_files']:
                    md_path = Path(root) / file
                    try:
                        doc = convert_md_to_html(md_path)
                        docs.append(doc)
                    except Exception as e:
                        print(f"✗ Error converting {md_path}: {e}")
        
        if docs:
            categories[base_dir] = docs
    
    return categories

def generate_index_html(categories: dict):
    """Generate the main index.html with all categories."""
    
    # Calculate totals
    total_docs = sum(len(docs) for docs in categories.values())
    total_categories = len(categories)
    
    # Build category sections
    category_sections = []
    
    for cat_name, docs in sorted(categories.items()):
        meta = CATEGORY_META.get(cat_name, {"icon": "📁", "description": "Documents"})
        
        cards = []
        for doc in sorted(docs, key=lambda x: x['modified'], reverse=True):
            card = f"""
            <a href="{doc['path']}" class="card">
                <h3 class="card-title">{doc['title']}</h3>
                <p class="card-description">{doc['description']}</p>
                <div class="card-meta">
                    <span class="card-tag">📅 {doc['modified']}</span>
                </div>
            </a>"""
            cards.append(card)
        
        section = f"""
        <section class="category">
            <div class="category-header">
                <div class="category-icon">{meta['icon']}</div>
                <div>
                    <h2 class="category-title">{cat_name}</h2>
                </div>
                <span class="category-count">{len(docs)} documents</span>
            </div>
            <div class="cards-grid">
                {''.join(cards)}
            </div>
        </section>"""
        
        category_sections.append(section)
    
    # Read template and inject content
    template_path = Path(__file__).parent / 'index_template.html'
    
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()
        html = html.replace('<!-- CATEGORIES -->', '\n'.join(category_sections))
        html = html.replace('id="total-docs">0', f'id="total-docs">{total_docs}')
        html = html.replace('id="total-categories">0', f'id="total-categories">{total_categories}')
    else:
        # Use inline template
        html = generate_inline_index(category_sections, total_docs, total_categories)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✓ Generated index.html with {total_docs} documents in {total_categories} categories")

def generate_inline_index(sections: list, total_docs: int, total_categories: int) -> str:
    """Generate index HTML inline without template file."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Onurcan's Knowledge Base</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-card: #1a1a24;
            --bg-card-hover: #22222e;
            --accent-primary: #00ff88;
            --accent-secondary: #00cc6a;
            --accent-glow: rgba(0, 255, 136, 0.15);
            --text-primary: #e4e4e7;
            --text-secondary: #a1a1aa;
            --text-muted: #71717a;
            --border-color: #27272a;
            --border-accent: #00ff8833;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Space Grotesk', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
        }}
        .bg-grid {{
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-image: 
                linear-gradient(rgba(0, 255, 136, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 136, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
            z-index: 0;
        }}
        .bg-glow {{
            position: fixed;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle at 30% 20%, rgba(0, 255, 136, 0.08) 0%, transparent 40%),
                        radial-gradient(circle at 70% 80%, rgba(0, 200, 100, 0.05) 0%, transparent 40%);
            pointer-events: none;
            z-index: 0;
        }}
        .container {{
            position: relative;
            z-index: 1;
            max-width: 1200px;
            margin: 0 auto;
            padding: 60px 24px;
        }}
        header {{ text-align: center; margin-bottom: 80px; }}
        .logo {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.875rem;
            color: var(--accent-primary);
            letter-spacing: 4px;
            text-transform: uppercase;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }}
        .logo::before, .logo::after {{
            content: '';
            width: 40px;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--accent-primary));
        }}
        .logo::after {{
            background: linear-gradient(90deg, var(--accent-primary), transparent);
        }}
        h1 {{
            font-size: clamp(2.5rem, 6vw, 4rem);
            font-weight: 700;
            margin-bottom: 16px;
            background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-primary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .subtitle {{
            font-size: 1.125rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 48px;
            margin-top: 40px;
            padding: 24px;
            background: var(--bg-secondary);
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }}
        .stat {{ text-align: center; }}
        .stat-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--accent-primary);
        }}
        .stat-label {{
            font-size: 0.875rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .category {{ margin-bottom: 60px; }}
        .category-header {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-color);
        }}
        .category-icon {{
            width: 48px; height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--accent-glow);
            border: 1px solid var(--border-accent);
            border-radius: 12px;
            font-size: 1.5rem;
        }}
        .category-title {{ font-size: 1.5rem; font-weight: 600; }}
        .category-count {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.875rem;
            color: var(--text-muted);
            margin-left: auto;
        }}
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            text-decoration: none;
            color: inherit;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        .card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 3px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            opacity: 0;
            transition: opacity 0.3s;
        }}
        .card:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border-accent);
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 40px var(--accent-glow);
        }}
        .card:hover::before {{ opacity: 1; }}
        .card-title {{
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .card-title::after {{
            content: '→';
            font-family: 'JetBrains Mono', monospace;
            color: var(--accent-primary);
            opacity: 0;
            transform: translateX(-8px);
            transition: all 0.3s;
        }}
        .card:hover .card-title::after {{
            opacity: 1;
            transform: translateX(0);
        }}
        .card-description {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-bottom: 16px;
        }}
        .card-meta {{
            display: flex;
            gap: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--text-muted);
        }}
        .card-tag {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            background: var(--bg-secondary);
            border-radius: 6px;
        }}
        footer {{
            text-align: center;
            padding: 40px 0;
            border-top: 1px solid var(--border-color);
            margin-top: 60px;
        }}
        .footer-links {{
            display: flex;
            justify-content: center;
            gap: 32px;
            margin-bottom: 24px;
        }}
        .footer-links a {{
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.875rem;
            transition: color 0.3s;
        }}
        .footer-links a:hover {{ color: var(--accent-primary); }}
        .copyright {{ font-size: 0.875rem; color: var(--text-muted); }}
        @media (max-width: 768px) {{
            .stats {{ flex-direction: column; gap: 24px; }}
            .cards-grid {{ grid-template-columns: 1fr; }}
        }}
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .category {{ animation: fadeInUp 0.6s ease-out backwards; }}
        .category:nth-child(1) {{ animation-delay: 0.1s; }}
        .category:nth-child(2) {{ animation-delay: 0.2s; }}
        .category:nth-child(3) {{ animation-delay: 0.3s; }}
        .category:nth-child(4) {{ animation-delay: 0.4s; }}
    </style>
</head>
<body>
    <div class="bg-grid"></div>
    <div class="bg-glow"></div>
    <div class="container">
        <header>
            <div class="logo">onurcangnc</div>
            <h1>Knowledge Base</h1>
            <p class="subtitle">Security research, CTF writeups, cheat sheets, and technical documentation.</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{total_docs}</div>
                    <div class="stat-label">Documents</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{total_categories}</div>
                    <div class="stat-label">Categories</div>
                </div>
                <div class="stat">
                    <div class="stat-value">5</div>
                    <div class="stat-label">CVEs Published</div>
                </div>
            </div>
        </header>
        <main>
            {''.join(sections)}
        </main>
        <footer>
            <div class="footer-links">
                <a href="https://github.com/onurcangnc" target="_blank">GitHub</a>
                <a href="https://medium.com/@onurcangnc" target="_blank">Medium</a>
                <a href="https://linkedin.com/in/onurcangnc" target="_blank">LinkedIn</a>
            </div>
            <p class="copyright">Built with Obsidian + GitHub Actions</p>
        </footer>
    </div>
</body>
</html>"""

def publish_to_medium_if_enabled(md_path: Path, title: str, content: str):
    """Publish to Medium if cookies are configured."""
    if not os.environ.get('MEDIUM_COOKIES') and not os.path.exists('.medium_cookies.json'):
        return

    try:
        from medium_publisher import MediumPublisher
        publisher = MediumPublisher()
        result = publisher.publish(str(md_path), method='playwright')
        if result.success:
            print(f"  ✓ Medium: {result.url}")
        else:
            print(f"  ⚠ Medium failed: {result.error}")
    except ImportError:
        print("  ⚠ medium_publisher.py not found")
    except Exception as e:
        print(f"  ⚠ Medium error: {e}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Convert Obsidian markdown to HTML')
    parser.add_argument('--medium', action='store_true', help='Also publish to Medium as draft')
    args = parser.parse_args()

    print("🚀 Starting Obsidian to HTML conversion...\n")
    categories = discover_documents()

    if categories:
        generate_index_html(categories)

        # Publish to Medium if enabled
        if args.medium or os.environ.get('MEDIUM_PUBLISH', '').lower() == 'true':
            print("\n📝 Publishing to Medium...")
            for cat_name, docs in categories.items():
                for doc in docs:
                    md_path = Path(doc['path']).with_suffix('.md')
                    if md_path.exists():
                        content = md_path.read_text(encoding='utf-8')
                        print(f"\n  → {doc['title']}")
                        publish_to_medium_if_enabled(md_path, doc['title'], content)
    else:
        print("⚠ No markdown files found in configured directories.")
        print(f"  Checked: {', '.join(CONFIG['base_dirs'])}")

    print("\n✅ Done!")