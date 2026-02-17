#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static Site Generator for AI Developers Blog
Dark Hacker News-style layout with AI summary display

Generates static HTML from scraped articles for GitHub Pages deployment
"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import re
import sys
import io
from dateutil import parser as dateparser

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SITE_URL = "https://jacek-mar.github.io/ai-dev-blog"
GITHUB_URL = "https://github.com/jacek-mar/ai-dev-blog"

AI_NOTICE = "Summaries are AI-generated. Please read the original article for full context."

COPYRIGHT_TEXT = (
    "This site provides AI-generated summaries of publicly available blog posts. "
    "All original content belongs to its respective authors. "
    "Summaries are provided for educational purposes and link to the original source. "
    'If you are a copyright holder and would like content removed, please '
    '<a href="https://github.com/jacek-mar/ai-dev-blog/issues">open an issue</a>.'
)


class SiteGenerator:
    """Generate static blog site from articles.json"""

    def __init__(self, articles_file="data/articles.json", output_dir="site"):
        self.articles_file = articles_file
        self.output_dir = Path(output_dir)
        self.articles = []
        self.sources = set()

    def load_articles(self):
        """Load articles from JSON database"""
        print(f"Loading articles from {self.articles_file}...")

        with open(self.articles_file, 'r', encoding='utf-8') as f:
            self.articles = json.load(f)

        self.articles.sort(key=self._parse_date_for_sort, reverse=True)
        self.sources = sorted(set(article['source'] for article in self.articles))

        print(f"Loaded {len(self.articles)} articles from {len(self.sources)} sources")
        return self.articles

    def slugify(self, text):
        """Convert text to URL-friendly slug"""
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[\s_]+', '-', slug)
        return slug.strip('-')[:100]

    def _parse_date_for_sort(self, article):
        """Parse article date to datetime for reliable sort (newest first).

        Tries 'published' first, falls back to 'download_date'.
        Handles ISO 8601, RFC 2822 (RSS), and human-readable formats like 'Feb 13, 2026'.
        Returns datetime.min for unparseable dates so they sink to the bottom.
        """
        for field in ('published', 'download_date'):
            date_str = (article.get(field) or '').strip()
            if not date_str:
                continue
            try:
                return dateparser.parse(date_str, ignoretz=True)
            except Exception:
                continue
        return datetime.min

    def format_date(self, date_str):
        """Format date string for display"""
        if not date_str:
            return "Unknown date"
        try:
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime("%b %d, %Y")
            return date_str
        except Exception:
            return date_str

    def get_display_date(self, article):
        """Return best available date for display.
        Shows published date if available; falls back to download_date with a 'fetched' label."""
        published = (article.get('published') or '').strip()
        if published:
            return self.format_date(published)
        download = (article.get('download_date') or '').strip()
        if download:
            return f"fetched {self.format_date(download)}"
        return "Unknown date"

    def get_source_color(self, source):
        """Get color for source badge"""
        colors = {
            'KiloCode': '#4A90E2',
            'Kiro': '#E94E77',
            'Google Cloud': '#4285F4',
            'Claude': '#D97757',
            'Anthropic': '#D97757',
            'Zencoder': '#50B83C',
            'HuggingFace': '#FFD21E',
            'Windsurf': '#7C3AED',
        }
        return colors.get(source, '#6B7280')

    def generate_css(self):
        """Generate dark Hacker News-inspired stylesheet"""
        css = """/* AI Developers Blog — Dark HN-Style Theme */
:root {
    --bg-page:    #0a0a0a;
    --bg-header:  #1a0f00;
    --bg-card:    #141414;
    --bg-notice:  #191400;
    --bg-quote:   #0d160d;
    --text:       #c8c8c8;
    --text-dim:   #888888;
    --text-muted: #555555;
    --accent:     #ff6600;
    --accent-h:   #ff8533;
    --link:       #ff9940;
    --link-h:     #ffb366;
    --border:     #222222;
    --notice-bdr: #554400;
    --quote-bdr:  #1f4a1f;
    --width:      860px;
    --pad:        24px;
    --mono: 'Courier New', Courier, monospace;
    --sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    background: var(--bg-page);
    color: var(--text);
    font-family: var(--sans);
    font-size: 14px;
    line-height: 1.6;
    min-height: 100vh;
}

a { color: var(--link); text-decoration: none; }
a:hover { color: var(--link-h); text-decoration: underline; }

/* ── NAV ─────────────────────────────────────── */
.main-nav {
    background: var(--bg-header);
    border-bottom: 2px solid var(--accent);
    position: sticky;
    top: 0;
    z-index: 100;
}
.nav-container {
    max-width: var(--width);
    margin: 0 auto;
    padding: 8px var(--pad);
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
}
.nav-brand {
    color: var(--accent) !important;
    font-family: var(--mono);
    font-weight: bold;
    font-size: 15px;
    text-decoration: none !important;
    white-space: nowrap;
}
.nav-links { display: flex; align-items: center; gap: 2px; flex-wrap: wrap; }
.nav-link {
    color: var(--text-dim) !important;
    font-size: 13px;
    padding: 4px 8px;
    border-radius: 2px;
    text-decoration: none !important;
    white-space: nowrap;
    background: none;
    border: none;
    cursor: pointer;
    font-family: inherit;
}
.nav-link:hover, .nav-link.active {
    color: var(--text) !important;
    background: rgba(255,102,0,0.12);
    text-decoration: none !important;
}
.nav-sep { color: var(--text-muted); padding: 0 2px; font-size: 12px; }

/* Dropdown */
.dropdown { position: relative; display: inline-block; }
.dropdown-content {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    background: #181818;
    border: 1px solid var(--border);
    min-width: 170px;
    z-index: 200;
    padding: 4px 0;
}
.dropdown:hover .dropdown-content { display: block; }
.dropdown-content a {
    display: block;
    padding: 6px 14px;
    color: var(--text-dim) !important;
    font-size: 13px;
}
.dropdown-content a:hover {
    background: #242424;
    color: var(--text) !important;
    text-decoration: none !important;
}

/* ── SITE HEADER ─────────────────────────────── */
.site-header {
    max-width: var(--width);
    margin: 0 auto;
    padding: 18px var(--pad) 12px;
    border-bottom: 1px solid var(--border);
}
.site-header h1 {
    font-size: 19px;
    font-family: var(--mono);
    color: var(--text);
    font-weight: normal;
    letter-spacing: 0.3px;
}
.site-header h1 span { color: var(--accent); }
.site-description { color: var(--text-dim); font-size: 13px; margin-top: 4px; }
.site-stats {
    color: var(--text-muted);
    font-size: 12px;
    margin-top: 3px;
    font-family: var(--mono);
}

/* ── AI NOTICE BANNER ────────────────────────── */
.ai-notice-banner {
    max-width: var(--width);
    margin: 8px auto 0;
    padding: 6px var(--pad);
    background: var(--bg-notice);
    border-left: 3px solid var(--notice-bdr);
    color: #aa8800;
    font-size: 12px;
    font-family: var(--mono);
}

/* ── MAIN CONTAINER ──────────────────────────── */
.container {
    max-width: var(--width);
    margin: 0 auto;
    padding: 0 var(--pad);
}

/* ── ARTICLE LIST (HN style) ─────────────────── */
.articles-list {
    margin-top: 6px;
    border-top: 1px solid var(--border);
}
.article-item {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 9px 0;
    border-bottom: 1px solid var(--border);
}
.item-number {
    color: var(--text-muted);
    font-size: 12px;
    font-family: var(--mono);
    min-width: 30px;
    text-align: right;
    padding-top: 2px;
    flex-shrink: 0;
}
.item-body { flex: 1; min-width: 0; }
.item-title {
    font-size: 14px;
    line-height: 1.4;
    margin-bottom: 3px;
}
.item-title a { color: var(--text) !important; font-weight: 500; }
.item-title a:hover { color: var(--accent) !important; text-decoration: none !important; }
.item-meta {
    font-size: 12px;
    color: var(--text-muted);
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    margin-top: 3px;
}
.source-badge {
    font-size: 11px;
    font-family: var(--mono);
    padding: 1px 6px;
    border-radius: 2px;
    color: #000 !important;
    font-weight: bold;
    text-decoration: none !important;
    flex-shrink: 0;
}
.item-actions {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-shrink: 0;
    padding-top: 3px;
}
.action-link {
    color: var(--text-muted) !important;
    font-size: 12px;
    font-family: var(--mono);
    white-space: nowrap;
}
.action-link:hover { color: var(--accent) !important; text-decoration: none !important; }

/* ── ARTICLE PAGE ────────────────────────────── */
.article-page { padding-top: 14px; padding-bottom: 40px; }

.breadcrumb {
    font-size: 12px;
    margin-bottom: 14px;
    font-family: var(--mono);
    color: var(--text-muted);
}
.breadcrumb a { color: var(--text-muted) !important; }
.breadcrumb a:hover { color: var(--accent) !important; }

.article-meta-top {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
    flex-wrap: wrap;
}
.article-date, .article-author {
    color: var(--text-muted);
    font-size: 12px;
    font-family: var(--mono);
}
h1.article-title {
    font-size: 20px;
    line-height: 1.3;
    color: var(--text);
    font-weight: 600;
    margin-bottom: 10px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}

/* AI Notice on article page */
.ai-notice {
    background: var(--bg-notice);
    border-left: 3px solid var(--notice-bdr);
    padding: 8px 12px;
    margin: 14px 0;
    font-size: 12px;
    color: #aa8800;
    font-family: var(--mono);
}

/* Summary box */
.summary-box {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 16px 20px;
    margin: 14px 0;
}
.summary-box h3, .key-insights h3, .topics-section h3 {
    font-size: 10px;
    font-family: var(--mono);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 10px;
}
.summary-box p {
    color: var(--text);
    font-size: 14px;
    line-height: 1.75;
}

/* Original quote */
.original-quote {
    background: var(--bg-quote);
    border-left: 3px solid var(--quote-bdr);
    padding: 12px 16px;
    margin: 14px 0;
}
.original-quote blockquote {
    color: #8ecf8e;
    font-size: 14px;
    font-style: italic;
    line-height: 1.65;
    margin-bottom: 6px;
}
.original-quote .attribution {
    font-size: 12px;
    color: var(--text-muted);
    font-family: var(--mono);
}

/* Key insights */
.key-insights { margin: 14px 0; }
.key-insights ul { padding-left: 18px; }
.key-insights li {
    color: var(--text-dim);
    font-size: 13px;
    margin-bottom: 5px;
    line-height: 1.5;
}

/* Topic tags */
.topics-section { margin: 14px 0; }
.topic-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.topic-tag {
    background: #1a1a1a;
    border: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 11px;
    font-family: var(--mono);
    padding: 2px 8px;
    border-radius: 2px;
}

/* Article actions */
.article-actions { margin: 20px 0; }
.btn {
    display: inline-block;
    padding: 9px 18px;
    border-radius: 2px;
    font-size: 13px;
    font-family: var(--mono);
    text-decoration: none !important;
}
.btn-primary {
    background: var(--accent);
    color: #000 !important;
    font-weight: bold;
}
.btn-primary:hover { background: var(--accent-h); }

/* ── SOURCE PAGE ─────────────────────────────── */
.source-header {
    padding: 16px 0 12px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0;
}
.source-header h1 {
    font-size: 17px;
    font-family: var(--mono);
    color: var(--text);
    font-weight: normal;
}
.source-header p {
    color: var(--text-muted);
    font-size: 12px;
    margin-top: 4px;
    font-family: var(--mono);
}

/* ── FOOTER ──────────────────────────────────── */
.site-footer {
    max-width: var(--width);
    margin: 28px auto 0;
    padding: 14px var(--pad) 20px;
    border-top: 1px solid var(--border);
    font-size: 12px;
    color: var(--text-muted);
    font-family: var(--mono);
    line-height: 1.9;
}
.site-footer a { color: var(--text-muted) !important; }
.site-footer a:hover { color: var(--accent) !important; }
.footer-copyright {
    background: #111;
    border: 1px solid var(--border);
    padding: 10px 14px;
    margin-top: 10px;
    color: var(--text-muted);
    font-size: 11px;
    line-height: 1.8;
    font-family: var(--sans);
}

/* ── RESPONSIVE ──────────────────────────────── */
@media (max-width: 768px) {
    :root { --pad: 12px; }
    h1.article-title { font-size: 17px; }
    .item-actions { flex-direction: column; gap: 3px; }
    .nav-container { gap: 8px; }
    .article-meta-top { flex-wrap: wrap; }
}
"""
        css_path = self.output_dir / 'style.css'
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css)
        print(f"✅ Generated {css_path}")

    def generate_nav(self, current_page='index', depth=''):
        """Generate navigation HTML. depth='' for root, '../' for subdirs."""
        source_links = '\n'.join([
            f'                <a href="{depth}sources/{self.slugify(src)}.html">{src}</a>'
            for src in self.sources
        ])
        active = 'active' if current_page == 'index' else ''
        return f'''
    <nav class="main-nav">
        <div class="nav-container">
            <a href="{depth}index.html" class="nav-brand">[AI Dev Blog]</a>
            <div class="nav-links">
                <a href="{depth}index.html" class="nav-link {active}">All</a>
                <span class="nav-sep">|</span>
                <div class="dropdown">
                    <button class="nav-link dropdown-btn">Sources ▾</button>
                    <div class="dropdown-content">
{source_links}
                    </div>
                </div>
                <span class="nav-sep">|</span>
                <a href="{depth}feed.xml" class="nav-link">RSS</a>
                <span class="nav-sep">|</span>
                <a href="{depth}copyright.html" class="nav-link">Copyright</a>
            </div>
        </div>
    </nav>'''

    def generate_footer(self, depth=''):
        """Generate shared footer HTML."""
        return f'''
    <footer class="site-footer">
        <div>
            <a href="{depth}index.html">Home</a> ·
            <a href="{depth}feed.xml">RSS</a> ·
            <a href="{GITHUB_URL}" target="_blank" rel="noopener">GitHub</a> ·
            <a href="{depth}copyright.html">Copyright</a>
        </div>
        <div class="footer-copyright">
            {COPYRIGHT_TEXT}
        </div>
    </footer>'''

    def generate_article_item(self, article, number, prefix=''):
        """Generate one HN-style list item for index/source pages."""
        slug = self.slugify(article['title'])
        src_color = self.get_source_color(article['source'])
        return f'''
        <div class="article-item">
            <div class="item-number">{number}.</div>
            <div class="item-body">
                <div class="item-title">
                    <a href="{prefix}posts/{slug}.html">{article['title']}</a>
                </div>
                <div class="item-meta">
                    <span class="source-badge" style="background-color:{src_color}">{article['source']}</span>
                    <span>by {article.get('author', 'Unknown')}</span>
                    <span>{self.get_display_date(article)}</span>
                </div>
            </div>
            <div class="item-actions">
                <a href="{prefix}posts/{slug}.html" class="action-link">summary&nbsp;→</a>
                <a href="{article['link']}" class="action-link" target="_blank" rel="noopener">original&nbsp;↗</a>
            </div>
        </div>'''

    def generate_index(self):
        """Generate index.html with all articles in HN list style."""
        print("Generating index.html...")

        items = '\n'.join(
            self.generate_article_item(a, i + 1, prefix='')
            for i, a in enumerate(self.articles)
        )

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Developers Blog — Latest AI & Developer News</title>
    <meta name="description" content="Curated AI developer blog aggregator. Latest posts from KiloCode, Anthropic, Google Cloud, HuggingFace, and more.">
    <link rel="stylesheet" href="style.css">
    <link rel="alternate" type="application/rss+xml" title="AI Developers Blog RSS" href="feed.xml">
</head>
<body>
    {self.generate_nav('index', depth='')}

    <header class="site-header">
        <h1><span>›</span> AI Developers Blog</h1>
        <p class="site-description">
            Curated AI and developer news from {len(self.sources)} leading sources:
            {', '.join(self.sources)}
        </p>
        <p class="site-stats">
            {len(self.articles)} articles · Updated {datetime.now().strftime('%b %d, %Y')}
        </p>
    </header>

    <div class="ai-notice-banner">⚠ {AI_NOTICE}</div>

    <main class="container">
        <div class="articles-list">
{items}
        </div>
    </main>
    {self.generate_footer(depth='')}
</body>
</html>
'''
        out = self.output_dir / 'index.html'
        with open(out, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Generated {out}")

    def generate_article_page(self, article):
        """Generate individual article page with AI summary, quote, and insights."""
        slug = self.slugify(article['title'])
        src_color = self.get_source_color(article['source'])

        # Summary: prefer ai_summary, fall back to summary
        summary_text = article.get('ai_summary') or article.get('summary', 'No summary available.')

        # Original quote block
        quote = article.get('ai_quote', '').strip()
        quote_attr = article.get('ai_quote_attribution', '').strip()
        if quote:
            quote_html = f'''
            <div class="original-quote">
                <blockquote>&#8220;{quote}&#8221;</blockquote>
                <div class="attribution">— {quote_attr or article.get('source', '')}</div>
            </div>'''
        else:
            quote_html = ''

        # Key insights list
        insights = article.get('ai_key_insights', [])
        if insights:
            items_html = '\n'.join(f'                <li>{ins}</li>' for ins in insights[:5])
            insights_html = f'''
            <div class="key-insights">
                <h3>Key Insights</h3>
                <ul>
{items_html}
                </ul>
            </div>'''
        else:
            insights_html = ''

        # Topic tags
        topics = article.get('ai_topics', [])
        if topics:
            tags_html = ''.join(f'<span class="topic-tag">{t}</span>' for t in topics)
            topics_html = f'''
            <div class="topics-section">
                <h3>Topics</h3>
                <div class="topic-tags">{tags_html}</div>
            </div>'''
        else:
            topics_html = ''

        # Difficulty / read time meta
        difficulty = article.get('ai_technical_level') or article.get('ai_difficulty', '')
        read_time = article.get('ai_read_time', '')
        meta_extras = []
        if difficulty:
            meta_extras.append(f'<span>{difficulty}</span>')
        if read_time:
            meta_extras.append(f'<span>{read_time} min read</span>')
        meta_extra_html = ' · '.join(meta_extras)

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} — AI Developers Blog</title>
    <meta name="description" content="{(article.get('summary', '') or '')[:160]}">
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    {self.generate_nav(depth='../')}

    <main class="container article-page">
        <article>
            <div class="breadcrumb">
                ← <a href="../index.html">All articles</a>
                &nbsp;/&nbsp;
                <a href="../sources/{self.slugify(article['source'])}.html">{article['source']}</a>
            </div>

            <div class="article-header">
                <div class="article-meta-top">
                    <span class="source-badge" style="background-color:{src_color}">{article['source']}</span>
                    <span class="article-date">{self.get_display_date(article)}</span>
                    <span class="article-author">by {article.get('author', 'Unknown')}</span>
                    {meta_extra_html}
                </div>
                <h1 class="article-title">{article['title']}</h1>
            </div>

            <div class="ai-notice">⚠ {AI_NOTICE}</div>

            <div class="article-content">
                <div class="summary-box">
                    <h3>AI Summary</h3>
                    <p>{summary_text}</p>
                </div>
{quote_html}
{insights_html}
{topics_html}
                <div class="article-actions">
                    <a href="{article['link']}" class="btn btn-primary" target="_blank" rel="noopener">
                        Read Full Article on {article['source']} ↗
                    </a>
                </div>
            </div>
        </article>
    </main>
    {self.generate_footer(depth='../')}
</body>
</html>
'''
        out = self.output_dir / 'posts' / f'{slug}.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, 'w', encoding='utf-8') as f:
            f.write(html)
        return out

    def generate_source_page(self, source):
        """Generate source archive page."""
        print(f"Generating source page for {source}...")
        src_articles = [a for a in self.articles if a['source'] == source]
        src_color = self.get_source_color(source)

        items = '\n'.join(
            self.generate_article_item(a, i + 1, prefix='../')
            for i, a in enumerate(src_articles)
        )

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{source} — AI Developers Blog</title>
    <meta name="description" content="Articles from {source} on AI Developers Blog">
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    {self.generate_nav(depth='../')}

    <div class="container">
        <div class="source-header">
            <h1>
                <span class="source-badge" style="background-color:{src_color}">{source}</span>
                &nbsp; Articles
            </h1>
            <p>{len(src_articles)} articles · <a href="../index.html">← all sources</a></p>
        </div>

        <div class="ai-notice-banner" style="margin:8px 0 0;">⚠ {AI_NOTICE}</div>

        <div class="articles-list">
{items}
        </div>
    </div>
    {self.generate_footer(depth='../')}
</body>
</html>
'''
        slug = self.slugify(source)
        out = self.output_dir / 'sources' / f'{slug}.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Generated {out}")

    def generate_copyright_page(self):
        """Generate copyright.html from COPYRIGHT.md content."""
        print("Generating copyright.html...")

        copyright_md_path = Path('COPYRIGHT.md')
        if copyright_md_path.exists():
            with open(copyright_md_path, 'r', encoding='utf-8') as f:
                raw = f.read()
            # Minimal md→html: headings, paragraphs, links
            raw = re.sub(r'^## (.+)$', r'<h2>\1</h2>', raw, flags=re.MULTILINE)
            raw = re.sub(r'^# (.+)$', r'<h1 style="font-size:18px;margin-bottom:12px;">\1</h1>', raw, flags=re.MULTILINE)
            raw = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', raw)
            raw = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', raw)
            raw = re.sub(r'^- (.+)$', r'<li>\1</li>', raw, flags=re.MULTILINE)
            raw = re.sub(r'((?:<li>.*</li>\n?)+)', r'<ul>\1</ul>', raw)
            raw = re.sub(r'---+', '<hr>', raw)
            paragraphs = raw.split('\n\n')
            body_html = ''
            for p in paragraphs:
                p = p.strip()
                if not p:
                    continue
                if p.startswith('<h') or p.startswith('<ul') or p.startswith('<hr'):
                    body_html += p + '\n'
                else:
                    body_html += f'<p>{p}</p>\n'
        else:
            body_html = f'<p>{COPYRIGHT_TEXT}</p>'

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Copyright — AI Developers Blog</title>
    <link rel="stylesheet" href="style.css">
    <style>
        .copyright-content {{
            max-width: var(--width);
            margin: 20px auto;
            padding: 0 var(--pad);
            line-height: 1.8;
        }}
        .copyright-content h2 {{
            font-size: 14px;
            font-family: var(--mono);
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 20px 0 8px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 4px;
        }}
        .copyright-content p, .copyright-content li {{
            color: var(--text-dim);
            font-size: 13px;
            margin-bottom: 8px;
        }}
        .copyright-content ul {{ padding-left: 18px; margin-bottom: 10px; }}
        .copyright-content hr {{ border: none; border-top: 1px solid var(--border); margin: 16px 0; }}
        .copyright-content strong {{ color: var(--text); }}
    </style>
</head>
<body>
    {self.generate_nav(depth='')}
    <div class="copyright-content">
{body_html}
    </div>
    {self.generate_footer(depth='')}
</body>
</html>
'''
        out = self.output_dir / 'copyright.html'
        with open(out, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Generated {out}")

    def generate_rss(self):
        """Generate RSS feed."""
        print("Generating RSS feed...")

        items_xml = []
        for article in self.articles[:50]:
            slug = self.slugify(article['title'])
            item_xml = f'''
        <item>
            <title>{self.escape_xml(article['title'])}</title>
            <link>{SITE_URL}/posts/{slug}.html</link>
            <guid>{SITE_URL}/posts/{slug}.html</guid>
            <description>{self.escape_xml((article.get('ai_summary') or article.get('summary', ''))[:500])}</description>
            <pubDate>{self.format_rss_date(article.get('published', article.get('download_date', '')))}</pubDate>
            <author>{self.escape_xml(article.get('author', 'Unknown'))}</author>
            <category>{self.escape_xml(article['source'])}</category>
        </item>'''
            items_xml.append(item_xml)

        rss_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>AI Developers Blog</title>
        <link>{SITE_URL}/</link>
        <description>Curated AI and developer news from leading sources</description>
        <language>en-us</language>
        <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>
        <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
{''.join(items_xml)}
    </channel>
</rss>
'''
        out = self.output_dir / 'feed.xml'
        with open(out, 'w', encoding='utf-8') as f:
            f.write(rss_xml)
        print(f"✅ Generated {out}")

    def escape_xml(self, text):
        """Escape special XML characters."""
        if not text:
            return ''
        return (text.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&apos;'))

    def format_rss_date(self, date_str):
        """Format date for RSS feed (RFC 822)."""
        if not date_str:
            return datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')
        try:
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date_str, '%b %d, %Y')
            return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
        except Exception:
            return datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')

    def copy_static_assets(self):
        """Generate CSS and ensure .nojekyll exists."""
        print("Generating static assets...")
        self.generate_css()
        nojekyll = self.output_dir / '.nojekyll'
        nojekyll.touch()
        print(f"✅ Created {nojekyll}")

    def generate_all(self):
        """Generate complete static site."""
        print("=" * 80)
        print("AI Developers Blog — Static Site Generator")
        print("=" * 80)

        self.load_articles()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.generate_index()
        self.generate_copyright_page()

        print(f"\nGenerating {len(self.articles)} article pages...")
        for i, article in enumerate(self.articles, 1):
            self.generate_article_page(article)
            if i % 10 == 0:
                print(f"  {i}/{len(self.articles)} article pages...")
        print(f"✅ Generated all {len(self.articles)} article pages")

        print("\nGenerating source pages...")
        for source in self.sources:
            self.generate_source_page(source)

        self.generate_rss()
        self.copy_static_assets()

        print("\n" + "=" * 80)
        print("✅ Site generation complete!")
        print(f"   Output: {self.output_dir.absolute()}")
        print(f"   Pages:  {len(self.articles) + len(self.sources) + 3}")
        print("=" * 80)
        print(f"\nTo view locally:")
        print(f"   python -m http.server 8000 --directory {self.output_dir}")
        print("   Open: http://localhost:8000")
        print("=" * 80)


def main():
    generator = SiteGenerator()
    generator.generate_all()


if __name__ == '__main__':
    main()
