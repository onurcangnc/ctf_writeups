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
        "Writeups",
        "Medium"  # Medium articles also displayed on GitHub Pages
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
    },
    "Medium": {
        "icon": "📰",
        "description": "Articles published on Medium"
    }
}

# Anthropic-inspired CSS for article pages
PAGE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&display=swap');

    :root {
        --bg-primary: #1A1915;
        --bg-surface: #21201C;
        --bg-elevated: #2A2924;
        --bg-code: #252420;
        --accent: #D4A27F;
        --accent-hover: #E0B595;
        --accent-dim: #B8896A;
        --text-primary: #EDEDEC;
        --text-secondary: #A8A8A4;
        --text-muted: #706F6C;
        --border: #3D3D37;
        --border-subtle: #2E2E29;
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
        font-family: 'Source Serif 4', 'Georgia', serif;
        background: var(--bg-primary);
        color: var(--text-primary);
        line-height: 1.8;
        padding: 48px 24px 80px;
        max-width: 720px;
        margin: 0 auto;
        font-size: 1.0625rem;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    .back-link {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: var(--text-secondary);
        text-decoration: none;
        font-family: 'Inter', sans-serif;
        font-size: 0.8125rem;
        font-weight: 500;
        letter-spacing: 0.02em;
        margin-bottom: 48px;
        padding: 6px 0;
        border-bottom: 1px solid transparent;
        transition: color 0.2s, border-color 0.2s;
    }

    .back-link:hover {
        color: var(--accent);
        border-bottom-color: var(--accent);
    }

    h1 {
        font-family: 'Inter', sans-serif;
        font-size: 2.25rem;
        font-weight: 700;
        line-height: 1.2;
        margin-bottom: 24px;
        color: var(--text-primary);
        letter-spacing: -0.025em;
    }

    h2 {
        font-family: 'Inter', sans-serif;
        font-size: 1.375rem;
        font-weight: 600;
        margin: 56px 0 16px;
        color: var(--text-primary);
        letter-spacing: -0.015em;
        line-height: 1.3;
        padding-bottom: 12px;
        border-bottom: 1px solid var(--border-subtle);
    }

    h3 {
        font-family: 'Inter', sans-serif;
        font-size: 1.125rem;
        font-weight: 600;
        margin: 40px 0 12px;
        color: var(--text-primary);
        letter-spacing: -0.01em;
    }

    h4 {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        margin: 32px 0 8px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.8125rem;
    }

    p {
        margin-bottom: 20px;
        color: var(--text-primary);
    }

    a {
        color: var(--accent);
        text-decoration: none;
        border-bottom: 1px solid var(--accent-dim);
        transition: color 0.2s, border-color 0.2s;
    }

    a:hover {
        color: var(--accent-hover);
        border-bottom-color: var(--accent-hover);
    }

    strong { font-weight: 600; color: var(--text-primary); }

    img {
        max-width: 100%;
        height: auto;
        border-radius: 8px;
        margin: 32px 0;
        border: 1px solid var(--border);
    }

    code {
        font-family: 'JetBrains Mono', monospace;
        background: var(--bg-code);
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.85em;
        color: var(--accent);
        border: 1px solid var(--border-subtle);
    }

    pre {
        background: var(--bg-surface);
        padding: 20px 24px;
        border-radius: 8px;
        overflow-x: auto;
        margin: 28px 0;
        border: 1px solid var(--border);
    }

    pre code {
        background: none;
        padding: 0;
        border: none;
        color: var(--text-primary);
        font-size: 0.8125rem;
        line-height: 1.7;
    }

    blockquote {
        border-left: 2px solid var(--accent-dim);
        padding: 4px 0 4px 24px;
        margin: 28px 0;
        color: var(--text-secondary);
        font-style: italic;
    }

    blockquote p { margin-bottom: 8px; }

    ul, ol {
        margin: 16px 0 20px 20px;
    }

    li {
        margin-bottom: 8px;
        padding-left: 4px;
    }

    li::marker {
        color: var(--text-muted);
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 28px 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
    }

    th, td {
        padding: 12px 16px;
        text-align: left;
        border-bottom: 1px solid var(--border-subtle);
    }

    th {
        font-weight: 600;
        color: var(--text-secondary);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        border-bottom: 1px solid var(--border);
    }

    tr:hover td { background: var(--bg-surface); }

    hr {
        border: none;
        height: 1px;
        background: var(--border-subtle);
        margin: 48px 0;
    }

    .meta {
        display: flex;
        gap: 20px;
        margin-bottom: 40px;
        padding-bottom: 24px;
        border-bottom: 1px solid var(--border-subtle);
        font-family: 'Inter', sans-serif;
        font-size: 0.8125rem;
        color: var(--text-muted);
    }

    .meta-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    ::selection {
        background: rgba(212, 162, 127, 0.25);
        color: var(--text-primary);
    }

    @media (max-width: 640px) {
        body { padding: 32px 16px 60px; font-size: 1rem; }
        h1 { font-size: 1.75rem; }
        h2 { font-size: 1.25rem; margin-top: 40px; }
        pre { padding: 16px; margin: 20px -16px; border-radius: 0; border-left: 0; border-right: 0; }
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
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
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
                <div class="card-meta">{doc['modified']}</div>
            </a>"""
            cards.append(card)

        section = f"""
        <section class="category">
            <div class="category-header">
                <span class="category-icon">{meta['icon']}</span>
                <h2 class="category-title">{cat_name}</h2>
                <span class="category-count">{len(docs)}</span>
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
    """Generate index HTML inline without template file — Anthropic editorial style."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Onurcan Genc — Knowledge Base</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #1A1915;
            --bg-surface: #21201C;
            --bg-elevated: #2A2924;
            --bg-card: #21201C;
            --bg-card-hover: #2A2924;
            --accent: #D4A27F;
            --accent-hover: #E0B595;
            --accent-dim: #B8896A;
            --accent-glow: rgba(212, 162, 127, 0.08);
            --text-primary: #EDEDEC;
            --text-secondary: #A8A8A4;
            --text-muted: #706F6C;
            --border: #3D3D37;
            --border-subtle: #2E2E29;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        .container {{
            max-width: 960px;
            margin: 0 auto;
            padding: 64px 32px;
        }}

        /* ── Header ── */
        header {{
            margin-bottom: 72px;
        }}

        .header-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 48px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .wordmark {{
            font-weight: 600;
            font-size: 1rem;
            color: var(--text-primary);
            letter-spacing: -0.02em;
        }}

        .nav-links {{
            display: flex;
            gap: 24px;
        }}

        .nav-links a {{
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.8125rem;
            font-weight: 500;
            transition: color 0.2s;
        }}

        .nav-links a:hover {{ color: var(--text-primary); }}

        .hero {{
            max-width: 640px;
        }}

        .hero-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.6875rem;
            font-weight: 500;
            color: var(--accent);
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 16px;
        }}

        h1 {{
            font-size: clamp(2rem, 5vw, 2.75rem);
            font-weight: 700;
            line-height: 1.15;
            letter-spacing: -0.03em;
            margin-bottom: 16px;
            color: var(--text-primary);
        }}

        .subtitle {{
            font-family: 'Source Serif 4', Georgia, serif;
            font-size: 1.125rem;
            line-height: 1.6;
            color: var(--text-secondary);
        }}

        /* ── Stats ── */
        .stats {{
            display: flex;
            gap: 40px;
            margin-top: 40px;
        }}

        .stat {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .stat-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text-primary);
        }}

        .stat-label {{
            font-size: 0.75rem;
            font-weight: 500;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}

        .stat-divider {{
            width: 1px;
            background: var(--border-subtle);
            align-self: stretch;
        }}

        /* ── Categories ── */
        .category {{
            margin-bottom: 56px;
        }}

        .category-header {{
            display: flex;
            align-items: baseline;
            gap: 12px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-subtle);
        }}

        .category-icon {{
            font-size: 1.125rem;
        }}

        .category-title {{
            font-size: 1.125rem;
            font-weight: 600;
            letter-spacing: -0.01em;
        }}

        .category-count {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-left: auto;
        }}

        /* ── Cards ── */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }}

        .card {{
            display: block;
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 20px 24px;
            text-decoration: none;
            color: inherit;
            transition: background 0.2s, border-color 0.2s, box-shadow 0.2s;
        }}

        .card:hover {{
            background: var(--bg-card-hover);
            border-color: var(--border);
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
        }}

        .card-title {{
            font-size: 0.9375rem;
            font-weight: 600;
            margin-bottom: 6px;
            color: var(--text-primary);
            letter-spacing: -0.01em;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .card-title::after {{
            content: '\\2197';
            font-size: 0.875rem;
            color: var(--text-muted);
            opacity: 0;
            transition: opacity 0.2s, color 0.2s;
        }}

        .card:hover .card-title::after {{
            opacity: 1;
            color: var(--accent);
        }}

        .card-description {{
            font-size: 0.8125rem;
            color: var(--text-secondary);
            line-height: 1.5;
            margin-bottom: 12px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .card-meta {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.6875rem;
            color: var(--text-muted);
        }}

        /* ── Footer ── */
        footer {{
            margin-top: 80px;
            padding-top: 32px;
            border-top: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .copyright {{
            font-size: 0.8125rem;
            color: var(--text-muted);
        }}

        .footer-links {{
            display: flex;
            gap: 24px;
        }}

        .footer-links a {{
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.8125rem;
            font-weight: 500;
            transition: color 0.2s;
        }}

        .footer-links a:hover {{ color: var(--accent); }}

        /* ── Responsive ── */
        @media (max-width: 640px) {{
            .container {{ padding: 40px 20px; }}
            .header-top {{ flex-direction: column; gap: 16px; align-items: flex-start; }}
            .stats {{ gap: 24px; flex-wrap: wrap; }}
            .stat-divider {{ display: none; }}
            .cards-grid {{ grid-template-columns: 1fr; }}
            footer {{ flex-direction: column; gap: 16px; align-items: flex-start; }}
        }}

        /* ── Animations ── */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .category {{
            animation: fadeIn 0.5s ease-out backwards;
        }}
        .category:nth-child(1) {{ animation-delay: 0.05s; }}
        .category:nth-child(2) {{ animation-delay: 0.1s; }}
        .category:nth-child(3) {{ animation-delay: 0.15s; }}
        .category:nth-child(4) {{ animation-delay: 0.2s; }}
        .category:nth-child(5) {{ animation-delay: 0.25s; }}

        ::selection {{
            background: rgba(212, 162, 127, 0.25);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-top">
                <div class="wordmark">onurcangnc</div>
                <nav class="nav-links">
                    <a href="https://github.com/onurcangnc" target="_blank">GitHub</a>
                    <a href="https://medium.com/@onurcangnc" target="_blank">Medium</a>
                    <a href="https://linkedin.com/in/onurcangnc" target="_blank">LinkedIn</a>
                </nav>
            </div>
            <div class="hero">
                <div class="hero-label">Knowledge Base</div>
                <h1>Security Research &amp; Technical Writing</h1>
                <p class="subtitle">CTF writeups, vulnerability analysis, cheat sheets, and deep dives into offensive security.</p>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">{total_docs}</div>
                        <div class="stat-label">Documents</div>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat">
                        <div class="stat-value">{total_categories}</div>
                        <div class="stat-label">Categories</div>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat">
                        <div class="stat-value">5</div>
                        <div class="stat-label">CVEs</div>
                    </div>
                </div>
            </div>
        </header>
        <main>
            {''.join(sections)}
        </main>
        <footer>
            <p class="copyright">Built with Obsidian + GitHub Actions</p>
            <nav class="footer-links">
                <a href="https://github.com/onurcangnc" target="_blank">GitHub</a>
                <a href="https://medium.com/@onurcangnc" target="_blank">Medium</a>
                <a href="https://linkedin.com/in/onurcangnc" target="_blank">LinkedIn</a>
            </nav>
        </footer>
    </div>
</body>
</html>"""

if __name__ == '__main__':
    print("🚀 Starting Obsidian to HTML conversion...\n")
    categories = discover_documents()

    if categories:
        generate_index_html(categories)
    else:
        print("⚠ No markdown files found in configured directories.")
        print(f"  Checked: {', '.join(CONFIG['base_dirs'])}")

    print("\n✅ Done!")