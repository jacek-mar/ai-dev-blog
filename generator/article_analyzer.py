#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Article Analyzer and Enhancer
Analyzes scraped articles and adds AI-generated metadata for better organization and presentation
"""
import json
import re
from datetime import datetime
from pathlib import Path
import sys
import io

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# Define category keywords for rule-based classification
CATEGORY_KEYWORDS = {
    'AI Models & Releases': [
        'model', 'release', 'announce', 'launch', 'new', 'version', 'opus', 
        'gemini', 'gpt', 'claude', 'llama', 'gemma', 'minimax', 'glm',
        'available', 'introducing', 'debut', 'unveil'
    ],
    'Coding & Development': [
        'coding', 'developer', 'code', 'programming', 'software', 'engineer',
        'vs code', 'extension', 'cli', 'sdk', 'api', 'debug', 'refactor',
        'repository', 'github', 'open source', 'framework'
    ],
    'AI Agents & Automation': [
        'agent', 'automation', 'autonomous', 'agentic', 'mcp', 'tool use',
        'task', 'workflow', 'automation', 'orchestrat'
    ],
    'Cloud & Infrastructure': [
        'cloud', 'gcp', 'google cloud', 'aws', 'azure', 'infrastructure',
        'server', 'deployment', 'kubernetes', 'gke', 'compute', 'gpu',
        'nvidia', 'inference', 'serverless'
    ],
    'Security & Privacy': [
        'security', 'privacy', 'safety', 'protect', 'secure', 'vulnerability',
        'attack', 'threat', 'risk', 'compliance', 'trust'
    ],
    'Research & Benchmarks': [
        'research', 'benchmark', 'paper', 'study', 'evaluation', 'performance',
        'accuracy', 'score', 'test', 'experiment', 'academic'
    ],
    'Business & Enterprise': [
        'enterprise', 'business', 'company', 'funding', 'series', 'revenue',
        'customer', 'market', 'product', 'pricing', 'partnership'
    ],
    'Tutorials & How-To': [
        'how to', 'tutorial', 'guide', 'learn', 'getting started', 'step by step',
        'walkthrough', 'example', 'demo', 'course'
    ]
}

# Define topic extraction patterns
TOPIC_PATTERNS = {
    'OpenAI': r'\bopenai\b|\bchatgpt\b|\bgpt-4\b|\bgpt-5\b',
    'Anthropic': r'\banthropic\b|\bclaude\b|\bopus\b',
    'Google': r'\bgoogle\b|\bgemini\b|\bvertex\b|\bgcp\b',
    'Meta/LLaMA': r'\bmeta\b|\bfacebook\b|\bllama\b|\blLaMA\b',
    'Microsoft': r'\bmicrosoft\b|\bopenai\b|\bcopilot\b|\bazure\b',
    'NVIDIA': r'\bnvidia\b|\bgpu\b|\bcuda\b|\b Nim\b',
    'Hugging Face': r'\bhugging face\b|\bhub\b|\btransformers\b',
    'AWS': r'\baws\b|\bamazon\b|\bec2\b|\bsagemaker\b',
    'Open Source': r'\bopen source\b|\bopen-source\b|\bopenweight\b|\bweights\b',
    'Code Generation': r'\bcode gen\b|\bcoding\b|\bprogram\b',
    'Multimodal': r'\bmultimodal\b|\bvision\b|\bimage\b|\baudio\b|\bvideo\b',
    'Reasoning': r'\breasoning\b|\bthought\b|\bchain\b|\bdeep think\b',
    'Fine-tuning': r'\bfine-tun|\bfinetune\b|\btraining\b|\btrained\b',
    'Agents': r'\bagent\b|\bautonomous\b|\btool\b'
}


class ArticleAnalyzer:
    """AI-powered article analyzer for extracting metadata and enhancing content"""
    
    def __init__(self, articles_file="data/articles.json", output_file=None):
        self.articles_file = articles_file
        self.output_file = output_file or articles_file
        self.articles = []
        self.analysis_results = []
        
    def load_articles(self):
        """Load articles from JSON file"""
        print(f"Loading articles from {self.articles_file}...")
        
        with open(self.articles_file, 'r', encoding='utf-8') as f:
            self.articles = json.load(f)
            
        print(f"Loaded {len(self.articles)} articles")
        return self.articles
    
    def analyze_category(self, article):
        """Determine article category based on keywords"""
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        text = f"{title} {summary}"
        
        category_scores = {}
        
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            # Return the highest scoring category
            return max(category_scores, key=category_scores.get)
        return 'General'
    
    def extract_topics(self, article):
        """Extract relevant topics from article"""
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        text = f"{title} {summary}"
        
        topics = []
        for topic, pattern in TOPIC_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                topics.append(topic)
        
        return topics[:5]  # Limit to top 5 topics
    
    def analyze_sentiment(self, article):
        """Analyze sentiment from title and summary"""
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        text = f"{title} {summary}"
        
        # Simple keyword-based sentiment analysis
        positive_words = [
            'new', 'exciting', 'amazing', 'great', 'best', 'free', 'improved',
            'powerful', 'revolutionary', 'innovative', 'breaking', 'launch',
            'announce', 'release', 'available', 'now', 'introducing'
        ]
        
        negative_words = [
            'problem', 'issue', 'bug', 'fail', 'crash', 'vulnerability',
            'security', 'risk', 'threat', 'concern', 'warning', 'deprecated'
        ]
        
        neutral_words = [
            'update', 'change', 'introduces', 'releases', 'announces'
        ]
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        if pos_count > neg_count + 1:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'
    
    def generate_tags(self, article):
        """Generate relevant tags for the article"""
        tags = set()
        
        # Add source as tag
        source = article.get('source', '').strip()
        if source:
            tags.add(source)
        
        # Add topics as tags
        topics = self.extract_topics(article)
        tags.update(topics)
        
        # Add category as tag
        category = self.analyze_category(article)
        if category != 'General':
            tags.add(category)
        
        # Add key terms from title
        title = article.get('title', '')
        # Extract capitalized words as potential tags
        caps_words = re.findall(r'\b[A-Z][a-z]+\b', title)
        for word in caps_words[:3]:
            if len(word) > 3 and word not in ['The', 'This', 'That', 'Your']:
                tags.add(word)
        
        return list(tags)[:10]  # Limit to 10 tags
    
    def calculate_relevance_score(self, article):
        """Calculate relevance score based on various factors"""
        score = 50  # Base score
        
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        
        # Boost for having a summary
        if article.get('summary'):
            score += 10
            
        # Boost for recent articles
        published = article.get('published', '')
        if published:
            try:
                if 'T' in published:
                    pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                    days_old = (datetime.now() - pub_date.replace(tzinfo=None)).days
                    if days_old < 7:
                        score += 20
                    elif days_old < 14:
                        score += 10
                    elif days_old > 30:
                        score -= 10
            except:
                pass
        
        # Boost for important keywords in title
        important_keywords = ['announcing', 'introducing', 'new', 'release', 'launch']
        for keyword in important_keywords:
            if keyword in title:
                score += 5
        
        # Boost for model names and versions
        model_patterns = [r'v\d+', r'\d+\.\d+', r'gpt-\d', r'opus', r'gemini']
        for pattern in model_patterns:
            if re.search(pattern, title):
                score += 5
        
        return min(100, max(0, score))  # Clamp between 0-100
    
    def analyze_article(self, article):
        """Perform complete analysis on a single article"""
        analysis = {
            'category': self.analyze_category(article),
            'topics': self.extract_topics(article),
            'sentiment': self.analyze_sentiment(article),
            'tags': self.generate_tags(article),
            'relevance_score': self.calculate_relevance_score(article),
            'analyzed_at': datetime.now().isoformat()
        }
        
        return analysis
    
    def enhance_article(self, article):
        """Enhance article with AI-generated metadata"""
        analysis = self.analyze_article(article)
        
        # Add enhanced fields to article
        enhanced_article = article.copy()
        enhanced_article['category'] = analysis['category']
        enhanced_article['topics'] = analysis['topics']
        enhanced_article['sentiment'] = analysis['sentiment']
        enhanced_article['tags'] = analysis['tags']
        enhanced_article['relevance_score'] = analysis['relevance_score']
        enhanced_article['analyzed_at'] = analysis['analyzed_at']
        
        # Generate enhanced summary if needed
        if not enhanced_article.get('enhanced_summary'):
            enhanced_article['enhanced_summary'] = self.generate_enhanced_summary(article, analysis)
        
        return enhanced_article
    
    def generate_enhanced_summary(self, article, analysis):
        """Generate an enhanced summary with context"""
        original_summary = article.get('summary', '')
        category = analysis['category']
        topics = analysis['topics']
        
        # Create a more informative summary
        enhanced = f"[{category}] "
        
        if topics:
            enhanced += f"Topics: {', '.join(topics[:3])}. "
        
        enhanced += original_summary
        
        return enhanced
    
    def analyze_all_articles(self):
        """Analyze all articles and return enhanced list"""
        print(f"\nAnalyzing {len(self.articles)} articles...")
        
        enhanced_articles = []
        
        for i, article in enumerate(self.articles):
            enhanced = self.enhance_article(article)
            enhanced_articles.append(enhanced)
            
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(self.articles)} articles...")
        
        self.articles = enhanced_articles
        print(f"✅ Analysis complete! Enhanced {len(self.articles)} articles")
        
        return self.articles
    
    def save_enhanced_articles(self, output_file=None):
        """Save enhanced articles to JSON file"""
        output_path = output_file or self.output_file
        
        # Create backup of original file
        backup_path = f"{self.articles_file}.backup"
        if Path(self.articles_file).exists():
            import shutil
            shutil.copy(self.articles_file, backup_path)
            print(f"📁 Created backup: {backup_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved enhanced articles to {output_path}")
        return output_path
    
    def generate_analysis_report(self):
        """Generate a summary report of the analysis"""
        print("\n" + "="*50)
        print("ARTICLE ANALYSIS REPORT")
        print("="*50)
        
        # Category distribution
        categories = {}
        topics = {}
        sentiments = {}
        
        for article in self.articles:
            cat = article.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
            
            for topic in article.get('topics', []):
                topics[topic] = topics.get(topic, 0) + 1
            
            sent = article.get('sentiment', 'neutral')
            sentiments[sent] = sentiments.get(sent, 0) + 1
        
        print("\n📊 Category Distribution:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"  • {cat}: {count}")
        
        print("\n🏷️ Top Topics:")
        for topic, count in sorted(topics.items(), key=lambda x: -x[1])[:10]:
            print(f"  • {topic}: {count}")
        
        print("\n😊 Sentiment Distribution:")
        for sent, count in sorted(sentiments.items(), key=lambda x: -x[1]):
            print(f"  • {sent.capitalize()}: {count}")
        
        print("\n📈 Average Relevance Score:", 
              sum(a.get('relevance_score', 0) for a in self.articles) / len(self.articles))
        
        print("\n" + "="*50)
    
    def run(self):
        """Run the complete analysis pipeline"""
        self.load_articles()
        self.analyze_all_articles()
        self.generate_analysis_report()
        self.save_enhanced_articles()
        
        return self.articles


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Article Analyzer and Enhancer')
    parser.add_argument('--input', '-i', default='data/articles.json', 
                        help='Input articles JSON file')
    parser.add_argument('--output', '-o', default=None,
                        help='Output file (default: overwrite input)')
    parser.add_argument('--report', '-r', action='store_true',
                        help='Generate analysis report only')
    
    args = parser.parse_args()
    
    analyzer = ArticleAnalyzer(args.input, args.output)
    analyzer.run()
    
    print("\n✨ Article enhancement complete!")


if __name__ == '__main__':
    main()
