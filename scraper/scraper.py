#!/usr/bin/env python3
"""
AI Developers Blog Scraper
Phase 0: Local functionality with proper logging and error handling
"""
import os
import json
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from dateutil import parser as dateparser
from urllib.parse import urljoin
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
BASE_DIR = os.getcwd()
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f"scraper_{datetime.now():%Y%m%d_%H%M%S}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

logger.info("="*80)
logger.info("AI Developers Blog Scraper Starting")
logger.info(f"Log file: {log_file}")
logger.info("="*80)

POSTS_DIR = os.path.join(BASE_DIR, "posts")
DATA_FILE = os.path.join(BASE_DIR, "data/articles.json")
SOURCES_FILE = os.path.join(BASE_DIR, "sources.json")

os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# Load saved articles
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            saved_articles = json.load(f)
            logger.info(f"Loaded {len(saved_articles)} existing articles from database")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse articles.json: {e}")
            logger.warning("Starting with empty article database")
            saved_articles = []
        except Exception as e:
            logger.error(f"Unexpected error loading articles: {e}")
            raise
else:
    logger.info("No existing articles database found, starting fresh")
    saved_articles = []

saved_links = set(article["link"] for article in saved_articles)
saved_titles = set(article["title"].lower().strip() for article in saved_articles)

# Load sources
logger.info(f"Loading sources from {SOURCES_FILE}")
with open(SOURCES_FILE, "r", encoding="utf-8") as f:
    sources = json.load(f)["sources"]

logger.info(f"Loaded {len(sources)} blog sources")

new_articles = []


# ============================================================================
# KiloCode AI Enhancement Integration (Phase 4 HYBRID)
# ============================================================================

class KiloAIEnhancer:
    """
    KiloCode webhook-based AI enhancer
    Calls KiloCode webhook for article analysis
    """

    def __init__(self):
        self.webhook_url = os.environ.get('KILO_WEBHOOK_URL')
        self.webhook_secret = os.environ.get('KILO_WEBHOOK_SECRET')

        if not self.webhook_url or not self.webhook_secret:
            raise ValueError("KILO_WEBHOOK_URL and KILO_WEBHOOK_SECRET required")

        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.webhook_secret}',
            'Content-Type': 'application/json'
        })

    def enhance_article(self, article, timeout=30):
        """Enhance single article via KiloCode webhook"""
        logger.info(f"Enhancing via KiloCode: {article['title'][:60]}...")

        payload = {
            'title': article['title'],
            'content': article.get('content', article.get('summary', ''))[:5000],
            'source': article.get('source', 'Unknown'),
            'link': article['link']
        }

        try:
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()

            ai_data = response.json()

            if not self._validate_response(ai_data):
                logger.warning("Invalid AI response, using fallback")
                return self._fallback_enhancement(article)

            enhanced = {
                **article,
                'ai_summary': ai_data['summary'],
                'ai_category': ai_data['category'],
                'ai_topics': ai_data['topics'],
                'ai_technical_level': ai_data['technical_level'],
                'ai_key_insights': ai_data['key_insights'],
                'ai_recommended': ai_data['recommended'],
                'ai_enhanced': True,
                'ai_enhanced_at': datetime.now().isoformat()
            }

            logger.info(f"✅ Enhanced: {ai_data['category']} | {len(ai_data['topics'])} topics")
            return enhanced

        except requests.Timeout:
            logger.error(f"Webhook timeout for: {article['title'][:60]}")
            return self._fallback_enhancement(article)

        except requests.RequestException as e:
            logger.error(f"Webhook error: {e}")
            return self._fallback_enhancement(article)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return self._fallback_enhancement(article)

    def enhance_batch(self, articles, max_concurrent=5):
        """Enhance multiple articles concurrently"""
        logger.info(f"Enhancing {len(articles)} articles via KiloCode webhooks...")

        enhanced_articles = []

        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_article = {
                executor.submit(self.enhance_article, article): article
                for article in articles
            }

            for i, future in enumerate(as_completed(future_to_article), 1):
                try:
                    enhanced = future.result()
                    enhanced_articles.append(enhanced)
                    logger.info(f"Progress: {i}/{len(articles)}")
                except Exception as e:
                    article = future_to_article[future]
                    logger.error(f"Failed: {article['title'][:60]}")
                    enhanced_articles.append(self._fallback_enhancement(article))

        logger.info(f"✅ Batch complete: {len(enhanced_articles)} articles")
        return enhanced_articles

    def _validate_response(self, ai_data):
        """Validate webhook response"""
        required = ['summary', 'category', 'topics', 'technical_level', 'key_insights', 'recommended']
        return all(field in ai_data for field in required)

    def _fallback_enhancement(self, article):
        """Fallback when webhook fails"""
        return {
            **article,
            'ai_summary': article.get('summary', 'No summary available')[:300],
            'ai_category': 'AI/ML',
            'ai_topics': [],
            'ai_technical_level': 'intermediate',
            'ai_key_insights': [],
            'ai_recommended': False,
            'ai_enhanced': False
        }


# ============================================================================
# Article Processing Functions
# ============================================================================

def fetch_article_content(url):
    """Fetch full article content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (AI Blog Scraper; +https://github.com/ai-dev-blog-scraper)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()  # Raise exception for 4xx/5xx errors

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script, style, nav, footer tags
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())

        logger.debug(f"Fetched {len(text)} characters from {url}")
        return text[:5000]

    except requests.Timeout:
        logger.warning(f"Timeout fetching content from {url}")
        return ""
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return ""


def summarize(text):
    """
    Create summary from text using improved extraction

    Note: This is an improved extraction algorithm.
    Real AI summarization will be implemented in Phase 4.
    """
    if not text:
        return "No content available."

    # Clean up text
    text = ' '.join(text.split())  # Normalize whitespace

    if len(text) < 200:
        return text

    # Split into sentences more robustly
    # Use simple regex for sentence boundaries
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Filter out noise
    noise_patterns = [
        r'^(read more|click here|subscribe|share|tweet|comment)',
        r'^(home|about|contact|menu|search)',
        r'^\d+\s*(min|mins|minute|minutes)\s+read',
        r'^by\s+\w+',  # Author lines
    ]

    good_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()

        # Skip very short sentences (likely UI text)
        if len(sentence) < 30:
            continue

        # Skip sentences matching noise patterns
        is_noise = any(re.match(pattern, sentence.lower()) for pattern in noise_patterns)
        if is_noise:
            continue

        # Skip sentences that are mostly non-alphabetic
        alpha_chars = sum(c.isalpha() or c.isspace() for c in sentence)
        if alpha_chars / len(sentence) < 0.7:
            continue

        good_sentences.append(sentence)

        # Stop if we have enough good sentences
        if len(good_sentences) >= 10:
            break

    if not good_sentences:
        # Fallback: use first few sentences regardless
        good_sentences = sentences[:5]

    # Build summary from good sentences
    summary_parts = []
    char_count = 0
    target_length = 400

    for sentence in good_sentences:
        if char_count + len(sentence) > target_length and summary_parts:
            break

        summary_parts.append(sentence)
        char_count += len(sentence)

    summary = ' '.join(summary_parts)

    # Ensure it ends with punctuation
    if summary and not summary[-1] in '.!?':
        summary += '...'

    # Final length check
    if len(summary) > 600:
        summary = summary[:597] + "..."

    return summary if summary else "No content available."


def save_markdown(article):
    """Save article as markdown file"""
    filename_date = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
    safe_title = "".join(c for c in article["title"] if c.isalnum() or c in " -_")[:50].strip()
    filename = f"{filename_date}-{safe_title}.md"
    filepath = os.path.join(POSTS_DIR, filename)

    content = f"""---
title: "{article['title']}"
date: "{article['download_date']}"
source: "{article['source']}"
author: "{article['author']}"
link: "{article['link']}"
published: "{article['published']}"
---

{article['summary']}

[Read full article]({article['link']})
"""

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Saved markdown: {filepath}")
    except Exception as e:
        logger.error(f"Failed to save markdown {filepath}: {e}")


def scrape_html_articles(source):
    """
    Scrape articles from HTML-only blogs (no RSS)
    Returns list of article dictionaries with metadata
    """
    source_name = source["name"]
    url = source["url"]

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (AI Blog Scraper; +https://github.com/ai-dev-blog-scraper)',
        }
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        seen_urls = set()

        # Site-specific scraping strategies with metadata extraction
        if "kiro" in url.lower():
            # Kiro.dev - Next.js site with date + title + author in link text
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link['href']
                if '/blog/' not in href or href == '/blog/' or href == url:
                    continue

                full_url = urljoin(url, href)
                if full_url in seen_urls:
                    continue

                # Extract metadata from link text and parent
                raw_text = link.get_text().strip()
                if not raw_text:
                    continue

                # Find <time> tag in parent for date
                parent = link.parent
                date_str = ""
                time_tag = parent.find('time') if parent else None
                if time_tag:
                    date_str = time_tag.get_text().strip()

                # Parse title and author from raw text
                # Pattern: "Feb 13, 2026Enterprise identity and usage metricsRanjith Ramakrishnan"
                # Remove date prefix
                clean_text = re.sub(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}', '', raw_text).strip()

                # Split by capital letters to separate title from author (heuristic)
                # Keep first part as title
                parts = re.split(r'(?<=[a-z])(?=[A-Z][a-z])', clean_text, maxsplit=1)
                title = parts[0].strip() if parts else clean_text
                author = parts[1].strip() if len(parts) > 1 else ""

                articles.append({
                    'url': full_url,
                    'title': title,
                    'published': date_str,
                    'author': author
                })
                seen_urls.add(full_url)

        elif "anthropic" in url.lower():
            # Anthropic news page - has categories + date in link text
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link['href']
                if '/news/' not in href or href == '/news' or href == url:
                    continue

                full_url = urljoin(url, href)
                if full_url in seen_urls:
                    continue

                raw_text = link.get_text().strip()
                if not raw_text or len(raw_text) < 10:
                    continue

                # Find <time> tag in parent for date
                parent = link.parent
                date_str = ""
                time_tag = parent.find('time') if parent else None
                if time_tag:
                    date_str = time_tag.get_text().strip()

                # Remove category prefix (e.g., "Announcements") and date
                clean_text = re.sub(r'^[A-Z][a-z]+\s+', '', raw_text)  # Remove category
                clean_text = re.sub(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}', '', clean_text).strip()

                # Extract title (first reasonable chunk)
                title = clean_text[:150].strip() if clean_text else raw_text[:150].strip()

                articles.append({
                    'url': full_url,
                    'title': title,
                    'published': date_str,
                    'author': ""
                })
                seen_urls.add(full_url)

        elif "cloud.google.com" in url.lower():
            # Google Cloud blog - less metadata available
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link['href']
                if not re.search(r'/blog/(products|topics)/[a-z-]+/[a-z0-9-]+', href):
                    continue

                full_url = urljoin(url, href)
                if full_url in seen_urls:
                    continue

                text = link.get_text().strip()
                if not text or text == "Read article":
                    continue

                # Clean up title by removing metadata
                title = text

                # Remove author and reading time suffix (e.g., "By Michael Gerstenhaber • 5-minute read")
                title = re.sub(r'By\s+[^•]+•\s*\d+-minute read$', '', title, flags=re.IGNORECASE).strip()

                # Remove category prefixes that run into the title without space
                # Pattern: "CategoryTitle" or "Category & CategoryTitle" -> "Title"
                # Split where lowercase letter is followed by uppercase letter
                match = re.search(r'(?<=[a-z])(?=[A-Z][a-z])', title)
                if match:
                    # Found a split point - take everything after it
                    title = title[match.start():]

                # Fallback: remove common category prefixes
                title = re.sub(r'^(AI & Machine Learning|Developers & Practitioners|Infrastructure|Security & Identity|Data Analytics|Application Development|Announcements)', '', title, flags=re.IGNORECASE).strip()

                if not title:
                    title = text[:150]  # Fallback to original text if cleanup removed everything

                articles.append({
                    'url': full_url,
                    'title': title,
                    'published': "",
                    'author': ""
                })
                seen_urls.add(full_url)

        elif "windsurf" in url.lower():
            # Windsurf blog
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link['href']
                if '/blog/' not in href or href == '/blog' or href == url:
                    continue

                full_url = urljoin(url, href)
                if full_url in seen_urls:
                    continue

                text = link.get_text().strip()
                if not text:
                    continue

                articles.append({
                    'url': full_url,
                    'title': text[:150],
                    'published': "",
                    'author': ""
                })
                seen_urls.add(full_url)

        logger.info(f"Found {len(articles)} articles on {source_name} via HTML scraping")
        return articles

    except requests.RequestException as e:
        logger.error(f"Failed to scrape HTML for {source_name}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error scraping {source_name}: {e}")
        return []


# Process sources
logger.info(f"Processing {len(sources)} blog sources")

for source in sources:
    source_name = source["name"]
    logger.info(f"\n--- Processing source: {source_name} ---")

    if source.get("rss"):
        logger.info(f"Fetching RSS feed: {source['rss']}")

        try:
            feed = feedparser.parse(source["rss"])

            if feed.get('bozo') and feed.get('bozo_exception'):
                logger.error(f"Invalid RSS feed for {source_name}: {feed.bozo_exception}")
                continue

            total_entries = len(feed.entries)
            max_articles = source.get("max_articles", 20)  # Default to 20 if not specified
            entries_to_process = feed.entries[:max_articles]

            logger.info(f"Found {total_entries} entries in {source_name} RSS feed")
            if total_entries > max_articles:
                logger.info(f"Limiting to {max_articles} most recent articles (max_articles setting)")

            articles_added = 0
            for entry in entries_to_process:
                link = entry.link
                title = entry.title
                title_normalized = title.lower().strip()

                # Check for duplicates by URL or title
                if link in saved_links:
                    logger.debug(f"Skipping duplicate URL: {link}")
                    continue

                if title_normalized in saved_titles:
                    logger.debug(f"Skipping duplicate title: {title[:60]}")
                    continue

                logger.info(f"Processing: {title[:60]}...")

                content = fetch_article_content(link)
                summary = summarize(content)

                article = {
                    "title": entry.title,
                    "link": link,
                    "published": entry.get("published", ""),
                    "author": entry.get("author", "Unknown"),
                    "source": source["name"],
                    "summary": summary,
                    "download_date": datetime.now(timezone.utc).isoformat()
                }

                new_articles.append(article)
                saved_articles.append(article)
                saved_links.add(link)  # Add to set to prevent duplicates in same run
                saved_titles.add(title_normalized)  # Track title for duplicate detection
                save_markdown(article)
                articles_added += 1

            logger.info(f"Added {articles_added} new articles from {source_name}")

        except Exception as e:
            logger.error(f"Failed to process RSS feed for {source_name}: {e}", exc_info=True)
            continue

    elif source.get("scrape_type") == "html":
        logger.info(f"Using HTML scraping for {source_name}")

        try:
            # Get article links from HTML
            article_links = scrape_html_articles(source)

            if not article_links:
                logger.warning(f"No articles found on {source_name}")
                continue

            # Apply max_articles limit
            max_articles = source.get("max_articles", 20)
            article_links = article_links[:max_articles]

            logger.info(f"Processing {len(article_links)} articles from {source_name}")

            articles_added = 0
            for article_data in article_links:
                article_url = article_data['url']
                article_title = article_data['title']
                article_published = article_data['published']
                article_author = article_data['author'] or "Unknown"

                title_normalized = article_title.lower().strip()

                # Check for duplicates by URL or title
                if article_url in saved_links:
                    logger.debug(f"Skipping duplicate URL: {article_url}")
                    continue

                if title_normalized in saved_titles:
                    logger.debug(f"Skipping duplicate title: {article_title[:60]}")
                    continue

                logger.info(f"Processing: {article_title[:60]}...")

                # Fetch full content
                content = fetch_article_content(article_url)
                summary = summarize(content)

                article = {
                    "title": article_title,
                    "link": article_url,
                    "published": article_published,
                    "author": article_author,
                    "source": source["name"],
                    "summary": summary,
                    "download_date": datetime.now(timezone.utc).isoformat()
                }

                new_articles.append(article)
                saved_articles.append(article)
                saved_links.add(article_url)
                saved_titles.add(title_normalized)  # Track title for duplicate detection
                save_markdown(article)
                articles_added += 1

            logger.info(f"Added {articles_added} new articles from {source_name}")

        except Exception as e:
            logger.error(f"Failed to process HTML scraping for {source_name}: {e}", exc_info=True)
            continue

    else:
        logger.warning(f"No RSS or HTML scraping configured for {source_name}")
        continue

# ============================================================================
# AI Enhancement with KiloCode (Phase 4 HYBRID)
# ============================================================================

if os.environ.get("ENABLE_AI_ENHANCEMENT") == "true":
    logger.info("\n" + "="*80)
    logger.info("🤖 AI Enhancement via KiloCode enabled")
    logger.info("="*80)

    try:
        enhancer = KiloAIEnhancer()

        # Get new articles to enhance (articles without ai_enhanced_at timestamp)
        new_articles_to_enhance = [
            a for a in saved_articles
            if not a.get('ai_enhanced_at')
        ]

        if new_articles_to_enhance:
            logger.info(f"Found {len(new_articles_to_enhance)} articles to enhance")

            # Enhance via webhooks (concurrent processing)
            enhanced = enhancer.enhance_batch(
                new_articles_to_enhance,
                max_concurrent=5
            )

            # Update database with enhanced articles
            for enhanced_article in enhanced:
                for i, article in enumerate(saved_articles):
                    if article['link'] == enhanced_article['link']:
                        saved_articles[i] = enhanced_article
                        break

            logger.info(f"✅ Enhanced {len(enhanced)} articles via KiloCode")
        else:
            logger.info("No new articles to enhance (all already processed)")

    except ValueError as e:
        logger.warning(f"AI enhancement skipped: {e}")
        logger.info("To enable AI enhancement, set KILO_WEBHOOK_URL and KILO_WEBHOOK_SECRET environment variables")

    except Exception as e:
        logger.error(f"KiloCode AI enhancement failed: {e}", exc_info=True)
        logger.info("Continuing without AI enhancement...")

    logger.info("="*80)
else:
    logger.info("\nAI enhancement disabled (set ENABLE_AI_ENHANCEMENT=true to enable)")

# ============================================================================
# Save Database
# ============================================================================

logger.info("\nSaving articles database...")

try:
    # Atomic write - write to temp file first
    temp_file = DATA_FILE + '.tmp'
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(saved_articles, f, indent=2, ensure_ascii=False)

    # Replace old file
    if os.path.exists(DATA_FILE):
        os.replace(temp_file, DATA_FILE)
    else:
        os.rename(temp_file, DATA_FILE)

    logger.info(f"Database saved successfully: {len(saved_articles)} total articles")
except Exception as e:
    logger.error(f"Failed to save database: {e}")
    raise

logger.info("="*80)
logger.info(f"Scraping complete: {len(new_articles)} new articles added")
logger.info(f"Total articles in database: {len(saved_articles)}")
logger.info("="*80)
