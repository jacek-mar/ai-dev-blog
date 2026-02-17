# AI Developers Blog

> An automated AI-powered blog aggregator that collects, enhances, and publishes content from leading AI/ML developer blogs.

[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/jacek-mar/ai-dev-blog/python-scraper-hybrid.yml?branch=main)](https://github.com/jacek-mar/ai-dev-blog/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Kilo League](https://img.shields.io/badge/Kilo_League-Participant-blue.svg)](https://blog.kilo.ai/p/kilo-league)

## 🏆 Kilo League Project

This project was created as an entry for the [Kilo League](https://blog.kilo.ai/p/kilo-league) - the world's first competitive arena for the full AI engineering lifecycle. The league is a year-long competition designed to help developers master agentic engineering through weekly speedruns, quarterly majors, and a championship bracket with a $50,000 grand prize.

## 🎯 Overview

This project automatically aggregates technical articles from top AI and machine learning blogs, enhances them with AI-powered analysis, and publishes a beautiful static website.

**Key Features:**
- 🤖 **AI-Enhanced Content** - Articles analyzed by Claude AI for summaries, categorization, and insights
- 🔄 **Fully Automated** - Runs every 4 hours via GitHub Actions
- 🌐 **Static Site** - Fast, secure, GitHub Pages hosted
- 📊 **7 Premium Sources** - Anthropic, Google Cloud, KiloCode, and more
- 💰 **Cost Efficient** - Optimized for minimal costs using free-tier and promotional models

## 🏗️ Architecture

**Hybrid Approach:**
- **GitHub Actions** - Free scheduling and Python execution (public repos)
- **KiloCode Webhooks** - Professional AI analysis via Claude Sonnet 4.5
- **GitHub Pages** - Free static site hosting

```
GitHub Actions (every 4 hours)
  ├─ Run Python scraper
  │  └─ Call KiloCode Webhook for AI analysis
  ├─ Generate static HTML site
  └─ Deploy to GitHub Pages
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- KiloCode account (for AI webhooks)
- GitHub account (for Actions and Pages)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jacek-mar/ai-dev-blog.git
   cd ai-dev-blog
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure sources**
   Edit `sources.json` to customize blog sources

4. **Run locally (optional)**
   ```bash
   # Run scraper
   python scraper/scraper.py

   # Generate site
   python generator/site_generator.py

   # View locally
   python -m http.server 8000 --directory site
   # Open http://localhost:8000
   ```

### GitHub Deployment

1. **Fork this repository**

2. **Configure GitHub Secrets**

   Go to: **Settings → Secrets and variables → Actions**

   Add:
   - `KILO_WEBHOOK_URL` - Your KiloCode webhook endpoint
   - `KILO_WEBHOOK_SECRET` - Webhook authentication token

3. **Enable GitHub Pages**

   Go to: **Settings → Pages**
   - Source: **GitHub Actions** (not "Deploy from a branch")
   - No branch or folder selection needed — the workflow deploys from `site/` automatically
   - Note: `/site` is not available as a folder option in branch-based deployment

4. **Enable GitHub Actions**

   Workflow runs automatically every 4 hours. You can also trigger manually:
   - Go to **Actions** tab
   - Select **AI Blog Scraper - Hybrid**
   - Click **Run workflow**

## 📁 Project Structure

```
ai-dev-blog/
├── scraper/
│   └── scraper.py           # Main scraper with KiloCode integration
├── generator/
│   └── site_generator.py    # Static site generator
├── site/                     # Generated website (deployed to Pages)
│   ├── index.html
│   ├── posts/
│   └── style.css
├── data/
│   └── articles.json        # Article database
├── posts/                    # Markdown files
├── .github/
│   └── workflows/
│       └── python-scraper-hybrid.yml  # GitHub Actions workflow
├── sources.json             # Blog source configuration
└── requirements.txt         # Python dependencies
```

## 🔧 Configuration

### Blog Sources

Edit `sources.json` to add/remove blog sources:

```json
{
  "sources": [
    {
      "name": "Source Name",
      "url": "https://example.com",
      "rss": "https://example.com/feed.xml",
      "max_articles": 20
    }
  ]
}
```

### KiloCode Webhook Setup

1. Sign up at [kilo.ai](https://kilo.ai)
2. Create a new Cloud Agent (webhook-triggered)
3. Configure AI analysis:
   - **Model:** Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) is a solid default,
     but **500+ models are available** — including free-tier options (GLM-5, MiniMax M2.5)
     that work just as well for this task. See the [Cost Analysis](#-cost-analysis) section below.
   - Temperature: `0.3`
   - Max tokens: `1000`
4. Set the **Prompt Template** — see [WEBHOOK_PROMPT_TEMPLATES.md](WEBHOOK_PROMPT_TEMPLATES.md)
   for the current production template plus 7 alternatives (Minimal, Deep Technical,
   Beginner-Friendly, Opinionated Curation, Polish, Digest, and the retired legacy template).
5. Copy webhook URL and secret to GitHub Secrets

### Workflow Frequency

Edit `.github/workflows/python-scraper-hybrid.yml`:

```yaml
on:
  schedule:
    - cron: "0 */4 * * *"  # Every 4 hours
```

## 🎨 Customization

### Site Styling

Modify `site/style.css` to customize the appearance.

### Site Generator

Edit `generator/site_generator.py` to:
- Change HTML templates
- Modify article sorting
- Add new pages
- Customize RSS feed

## 📊 Features

### Article Enhancement

Each article is analyzed for:
- **AI Summary** - 200–250 word developer-focused overview (template-dependent)
- **Original Quote** - Verbatim 1–2 sentence quote with attribution
- **Category** - AI/ML, LLMs, DevOps, Cloud, etc.
- **Topics** - Specific technologies mentioned
- **Technical Level** - Beginner, Intermediate, Advanced
- **Key Insights** - Actionable takeaways
- **Recommendation** - Top 20% must-read articles

See [WEBHOOK_PROMPT_TEMPLATES.md](WEBHOOK_PROMPT_TEMPLATES.md) to customize or switch the AI analysis prompt.

### Supported Sources

- Anthropic Blog
- Google Cloud AI
- KiloCode Blog
- Windsurf AI
- Kiro Tech
- Zencoder
- HuggingFace Papers

## 🤖 AI Integration

This project uses **KiloCode Webhooks** for AI enhancement:

- Professional Claude API access
- Built-in rate limiting
- Cost controls ($50/month limit)
- Automatic retries
- Fallback handling

**Why Webhooks?**
- No API key management
- Simpler code (87% less than direct API)
- Professional monitoring
- Cost tracking dashboard

## 📈 Performance

- **Scraping:** ~5-7 minutes per run
- **AI Enhancement:** ~2-3 seconds per article
- **Site Generation:** ~1 minute
- **Total Runtime:** ~8-10 minutes per run
- **Frequency:** 6 runs per day (every 4 hours)
- **Monthly Articles:** ~120 articles processed

## 💰 Cost Analysis

### Current Implementation

| Component | Cost |
|-----------|------|
| GitHub Actions | $0 (unlimited for public repos) |
| GitHub Pages | $0 (100 GB bandwidth) |
| KiloCode Webhooks | Variable (see model options below) |

### Available Model Options in KiloCode

KiloCode provides access to **500+ models** with flexible pricing options. Here are some optimal choices for this project:

#### 🆓 Free & Promotional Models (Limited Time)

| Model | Input Cost | Output Cost | Status | Best For |
|-------|-----------|-------------|--------|----------|
| **GLM-5** | FREE | FREE | Limited time via [Kilo CLI](https://blog.kilo.ai/p/kilo-cli) | Matches Opus 4.5 performance at no cost |
| **MiniMax M2.5** | FREE | FREE | Free for first week ([details](https://blog.kilo.ai/p/minimax-m25-is-here-and-its-free)) | Ultra-fast (100 tokens/sec), 80.2% SWE-Bench |
| **Opus 4.6 (Slack)** | FREE | FREE | Via Kilo for Slack | Full flagship model at no cost |

#### 💎 Production Models (After Promotions End)

| Model | Input Cost | Cached Input | Output Cost | Use Case |
|-------|-----------|--------------|-------------|----------|
| **MiniMax M2.5** | $0.30/M tokens | $0.06/M tokens | Standard | Best price for always-on agents |
| **Claude Sonnet 4.5** | $3.00/M tokens | $0.30/M tokens | $15.00/M tokens | Current implementation (high quality) |
| **Claude Opus 4.6** | $15.00/M tokens | $1.50/M tokens | $75.00/M tokens | Maximum capability (adaptive thinking) |
| **GPT-5.3 Codex** | Varies | Varies | Varies | Specialized for coding tasks |

### Cost Optimization Strategies

This project implements several cost-saving techniques:

1. **Model Selection by Task**
   - Use free-tier models (GLM-5, MiniMax M2.5) during promotional periods
   - Switch to Claude Sonnet 4.5 for production balance of quality/cost
   - Reserve Opus 4.6 for complex analysis requiring adaptive thinking

2. **Caching Benefits**
   - KiloCode's prompt caching reduces costs by up to **90%** for repeated operations
   - MiniMax M2.5 with caching: **$0.06/M tokens** (vs $0.30/M tokens without)
   - Perfect for this project's repetitive article analysis pattern

3. **Batch Processing**
   - Process articles in concurrent batches (max 5 concurrent via webhooks)
   - Reduces total runtime and optimizes API usage
   - Limits: 256 KB payload, 20 concurrent requests per trigger

4. **GitHub Actions Free Tier**
   - Unlimited compute for public repositories
   - No infrastructure costs for scheduling, scraping, or site generation
   - Only pay for AI model inference

### Projected Monthly Costs

#### Scenario 1: Using Free Promotional Models

- 120 articles/month × $0/article = **$0/month** ✨
- (During GLM-5 or MiniMax M2.5 free periods)

#### Scenario 2: Using MiniMax M2.5 (Post-Promotion)

- 120 articles/month × ~500 tokens/article × $0.06/M tokens (cached)
- **~$3.60/month** 💰

#### Scenario 3: Using Claude Sonnet 4.5 (Current)

- 120 articles/month × ~500 tokens/article × $0.30/M tokens (cached)
- **~$18/month**

#### Scenario 4: Using Claude Opus 4.6 (Premium)

- 120 articles/month × ~500 tokens/article × $1.50/M tokens (cached)
- **~$90/month**

### Alternative Architectures

For even lower costs, consider:

1. **Kilo CLI Local Processing**
   - Use [Kilo CLI 1.0](https://blog.kilo.ai/p/kilo-cli) for local article enhancement
   - Access 500+ models without webhook overhead
   - Session sync across CLI, VS Code, and web

2. **Cloud Agents with Webhooks**
   - Current implementation using [Cloud Agents](https://kilo.ai/docs/code-with-ai/platforms/cloud-agent)
   - Compute is free during beta (only pay for model usage)
   - Automatic GitHub/GitLab integration
   - 15-minute timeout per execution

3. **Hybrid Approach** (Recommended)
   - Use free promotional models when available
   - Fall back to MiniMax M2.5 for best price/performance ratio
   - Reserve premium models for articles requiring deep analysis
   - Implement intelligent model routing based on article complexity

### Cost Controls

KiloCode provides built-in cost protection:
- ✅ Monthly spending limits (configurable)
- ✅ Per-request cost tracking
- ✅ Dashboard for monitoring usage
- ✅ Automatic retries with exponential backoff
- ✅ Rate limiting to prevent runaway costs

**Recommended for this project:** Start with free models, monitor quality, then optimize based on actual needs.

## 🛠️ Development

### Run Tests

```bash
# Test individual components
python test_scraper.py
python test_generator.py
```

### Debug Mode

Set environment variable:
```bash
export DEBUG=1
python scraper/scraper.py
```

### Local AI Enhancement

To test with AI enhancement locally:

```bash
export ENABLE_AI_ENHANCEMENT=true
export KILO_WEBHOOK_URL=https://webhook.kilo.ai/...
export KILO_WEBHOOK_SECRET=your-secret
python scraper/scraper.py
```

## 📚 Documentation

- **Deployment Tutorial:** [DEPLOYMENT_TUTORIAL.md](DEPLOYMENT_TUTORIAL.md) — step-by-step guide covering GitHub Actions, KiloCode webhooks, and GitHub Pages (including known gotchas like the `/site` folder limitation and the `/deployments` 404)
- **Webhook Prompt Templates:** [WEBHOOK_PROMPT_TEMPLATES.md](WEBHOOK_PROMPT_TEMPLATES.md) — current, legacy, and 7 alternative AI prompt templates with cost and model guidance
- **Copyright & Ethics:** [COPYRIGHT.md](COPYRIGHT.md) — scraping policy, source attribution, AI summary disclaimer
- **Architecture:** See workflow diagram above
- **Implementation:** Review code comments in `scraper/scraper.py`
- **Customization:** Modify `sources.json` and `site_generator.py`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Kilo League](https://blog.kilo.ai/p/kilo-league)** for inspiring this project through their competitive engineering challenges
- **Claude AI** by Anthropic for AI-powered content analysis
- **[KiloCode](https://kilo.ai/)** for webhook infrastructure and access to 500+ models
- **GitHub** for Actions and Pages hosting
- All the amazing AI/ML blogs this project aggregates

## 📚 Additional Resources

- [Kilo League Competition](https://blog.kilo.ai/p/kilo-league) - Year-long AI engineering competition
- [Kilo CLI Documentation](https://blog.kilo.ai/p/kilo-cli) - Command-line interface for agentic engineering
- [Cloud Agent Platform](https://kilo.ai/docs/code-with-ai/platforms/cloud-agent) - Run Kilo Code in the cloud
- [MiniMax M2.5 Announcement](https://blog.kilo.ai/p/minimax-m25-is-here-and-its-free) - Free high-performance model
- [GLM-5 Limited Offer](https://blog.kilo.ai/p/glm-5-free-limited-time) - Free access to GLM-5 model
- [Kilo Code Product Updates](https://blog.kilo.ai/p/kilo-code-weekly-product-roundup-155) - Weekly feature roundups

## 📧 Contact

**Jacek Mar** - [@jacek-mar](https://github.com/jacek-mar)

**Project Link:** https://github.com/jacek-mar/ai-dev-blog

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Built with ❤️ for the AI developer community**
