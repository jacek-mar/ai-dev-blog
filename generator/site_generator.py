#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static Site Generator for AI Developers Blog
Phase 3 - Content Display

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

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


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

        # Sort by published date (newest first)
        self.articles.sort(key=lambda x: x.get('published', x.get('download_date', '')), reverse=True)

        # Extract unique sources
        self.sources = sorted(set(article['source'] for article in self.articles))

        print(f"Loaded {len(self.articles)} articles from {len(self.sources)} sources")
        return self.articles

    def slugify(self, text):
        """Convert text to URL-friendly slug"""
        # Remove special characters, convert to lowercase
        slug = re.sub(r'[^\w\s-]', '', text.lower())
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = slug.strip('-')
        return slug[:100]  # Limit length

    def format_date(self, date_str):
        """Format date string for display"""
        if not date_str:
            return "Date unknown"

        try:
            # Try parsing ISO format
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return dt.strftime("%B %d, %Y")
            else:
                # Already formatted
                return date_str
        except:
            return date_str

    def get_source_color(self, source):
        """Get color for source badge"""
        colors = {
            'KiloCode': '#4A90E2',
            'Kiro': '#E94E77',
            'Google Cloud': '#4285F4',
            'Claude': '#D97757',
            'Zencoder': '#50B83C',
            'HuggingFace': '#FFD21E',
            'Windsurf': '#7C3AED',
        }
        return colors.get(source, '#6B7280')

    def generate_nav(self, current_page='index'):
        """Generate navigation HTML"""
        nav_html = '''
        <nav class="main-nav">
            <div class="nav-container">
                <a href="index.html" class="nav-brand">AI Developers Blog</a>
                <div class="nav-links">
                    <a href="index.html" class="nav-link {active_all}">All Articles</a>
                    <div class="dropdown">
                        <button class="nav-link dropdown-btn">Sources ▼</button>
                        <div class="dropdown-content">
{source_links}
                        </div>
                    </div>
                    <a href="feed.xml" class="nav-link">RSS</a>
                </div>
            </div>
        </nav>
        '''

        source_links = '\n'.join([
            f'                            <a href="sources/{self.slugify(source)}.html">{source}</a>'
            for source in self.sources
        ])

        nav_html = nav_html.format(
            active_all='active' if current_page == 'index' else '',
            source_links=source_links
        )

        return nav_html

    def generate_article_card(self, article):
        """Generate HTML for an article card"""
        slug = self.slugify(article['title'])
        source_color = self.get_source_color(article['source'])

        card_html = f'''
        <article class="article-card">
            <div class="card-header">
                <span class="source-badge" style="background-color: {source_color}">{article['source']}</span>
                <span class="article-date">{self.format_date(article.get('published', ''))}</span>
            </div>
            <h2 class="article-title">
                <a href="posts/{slug}.html">{article['title']}</a>
            </h2>
            <div class="article-meta">
                <span class="author">By {article.get('author', 'Unknown')}</span>
            </div>
            <p class="article-summary">{article.get('summary', 'No summary available.')[:300]}...</p>
            <div class="card-footer">
                <a href="posts/{slug}.html" class="read-more">Read More →</a>
                <a href="{article['link']}" class="external-link" target="_blank" rel="noopener">View Original ↗</a>
            </div>
        </article>
        '''

        return card_html

    def generate_index(self):
        """Generate index.html with all articles"""
        print("Generating index.html...")

        article_cards = '\n'.join([
            self.generate_article_card(article)
            for article in self.articles
        ])

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Developers Blog - Latest AI & Developer News</title>
    <meta name="description" content="Curated blog aggregator for AI developers. Latest news from KiloCode, Kiro, Google Cloud, Anthropic, and more.">
    <link rel="stylesheet" href="style.css">
    <link rel="alternate" type="application/rss+xml" title="AI Developers Blog RSS" href="feed.xml">
</head>
<body>
    {self.generate_nav('index')}

    <header class="site-header">
        <h1>AI Developers Blog</h1>
        <p class="site-description">Curated AI and developer news from {len(self.sources)} leading sources</p>
        <p class="site-stats">{len(self.articles)} articles • Updated {datetime.now().strftime('%B %d, %Y')}</p>
    </header>

    <main class="container">
        <div class="articles-grid">
{article_cards}
        </div>
    </main>

    <footer class="site-footer">
        <p>AI Developers Blog Aggregator</p>
        <p>Sources: {', '.join(self.sources)}</p>
        <p><a href="feed.xml">RSS Feed</a> • <a href="https://github.com/yourusername/ai-dev-blog-scraper">GitHub</a></p>
    </footer>
</body>
</html>
'''

        output_path = self.output_dir / 'index.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Generated {output_path}")

    def generate_article_page(self, article):
        """Generate individual article page"""
        slug = self.slugify(article['title'])
        source_color = self.get_source_color(article['source'])

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} - AI Developers Blog</title>
    <meta name="description" content="{article.get('summary', 'Article from AI Developers Blog')[:160]}">
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    {self.generate_nav()}

    <main class="container article-page">
        <article>
            <div class="article-header">
                <div class="breadcrumb">
                    <a href="../index.html">← Back to all articles</a>
                </div>

                <div class="article-meta-top">
                    <span class="source-badge" style="background-color: {source_color}">{article['source']}</span>
                    <span class="article-date">{self.format_date(article.get('published', ''))}</span>
                </div>

                <h1 class="article-title">{article['title']}</h1>

                <div class="article-meta">
                    <span class="author">By {article.get('author', 'Unknown')}</span>
                </div>
            </div>

            <div class="article-content">
                <div class="summary-box">
                    <h3>Summary</h3>
                    <p>{article.get('summary', 'No summary available.')}</p>
                </div>

                <div class="article-actions">
                    <a href="{article['link']}" class="btn btn-primary" target="_blank" rel="noopener">
                        Read Full Article on {article['source']} ↗
                    </a>
                </div>
            </div>
        </article>
    </main>

    <footer class="site-footer">
        <p><a href="../index.html">Back to Home</a> • <a href="../feed.xml">RSS Feed</a></p>
    </footer>
</body>
</html>
'''

        output_path = self.output_dir / 'posts' / f'{slug}.html'
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_path

    def generate_source_page(self, source):
        """Generate source-specific archive page"""
        print(f"Generating source page for {source}...")

        source_articles = [a for a in self.articles if a['source'] == source]

        article_cards = '\n'.join([
            self.generate_article_card(article)
            for article in source_articles
        ])

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{source} Articles - AI Developers Blog</title>
    <meta name="description" content="All articles from {source} on AI Developers Blog">
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    {self.generate_nav()}

    <header class="site-header">
        <h1>{source} Articles</h1>
        <p class="site-description">{len(source_articles)} articles from {source}</p>
        <p><a href="../index.html">← Back to all sources</a></p>
    </header>

    <main class="container">
        <div class="articles-grid">
{article_cards}
        </div>
    </main>

    <footer class="site-footer">
        <p><a href="../index.html">Back to Home</a> • <a href="../feed.xml">RSS Feed</a></p>
    </footer>
</body>
</html>
'''

        slug = self.slugify(source)
        output_path = self.output_dir / 'sources' / f'{slug}.html'
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Generated {output_path}")

    def generate_rss(self):
        """Generate RSS feed"""
        print("Generating RSS feed...")

        items_xml = []
        for article in self.articles[:50]:  # Limit to 50 most recent
            slug = self.slugify(article['title'])
            item_xml = f'''
        <item>
            <title>{self.escape_xml(article['title'])}</title>
            <link>https://yourusername.github.io/ai-dev-blog/posts/{slug}.html</link>
            <guid>https://yourusername.github.io/ai-dev-blog/posts/{slug}.html</guid>
            <description>{self.escape_xml(article.get('summary', ''))[:500]}</description>
            <pubDate>{self.format_rss_date(article.get('published', article.get('download_date', '')))}</pubDate>
            <author>{self.escape_xml(article.get('author', 'Unknown'))}</author>
            <category>{self.escape_xml(article['source'])}</category>
        </item>'''
            items_xml.append(item_xml)

        rss_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>AI Developers Blog</title>
        <link>https://yourusername.github.io/ai-dev-blog/</link>
        <description>Curated AI and developer news from leading sources</description>
        <language>en-us</language>
        <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>
        <atom:link href="https://yourusername.github.io/ai-dev-blog/feed.xml" rel="self" type="application/rss+xml"/>
{''.join(items_xml)}
    </channel>
</rss>
'''

        output_path = self.output_dir / 'feed.xml'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rss_xml)

        print(f"✅ Generated {output_path}")

    def escape_xml(self, text):
        """Escape special XML characters"""
        if not text:
            return ''
        return (text.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&apos;'))

    def format_rss_date(self, date_str):
        """Format date for RSS feed (RFC 822)"""
        if not date_str:
            return datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')

        try:
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date_str, '%b %d, %Y')
            return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
        except:
            return datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')

    def copy_static_assets(self):
        """Copy static assets to output directory"""
        print("Copying static assets...")

        # CSS file is already in site/ so no need to copy
        # Just ensure .nojekyll exists
        nojekyll_path = self.output_dir / '.nojekyll'
        nojekyll_path.touch()
        print(f"✅ Created {nojekyll_path}")

    def generate_all(self):
        """Generate complete static site"""
        print("="*80)
        print("AI Developers Blog - Static Site Generator")
        print("="*80)

        # Load articles
        self.load_articles()

        # Generate pages
        self.generate_index()

        print(f"\nGenerating {len(self.articles)} article pages...")
        for i, article in enumerate(self.articles, 1):
            self.generate_article_page(article)
            if i % 10 == 0:
                print(f"  Generated {i}/{len(self.articles)} article pages...")
        print(f"✅ Generated all {len(self.articles)} article pages")

        print("\nGenerating source pages...")
        for source in self.sources:
            self.generate_source_page(source)

        self.generate_rss()
        self.copy_static_assets()

        print("\n" + "="*80)
        print(f"✅ Site generation complete!")
        print(f"   Output directory: {self.output_dir.absolute()}")
        print(f"   Total pages: {len(self.articles) + len(self.sources) + 2}")
        print("="*80)
        print("\nTo view locally:")
        print(f"   python -m http.server 8000 --directory {self.output_dir}")
        print("   Open: http://localhost:8000")
        print("="*80)


def main():
    """Main entry point"""
    generator = SiteGenerator()
    generator.generate_all()


if __name__ == '__main__':
    main()
