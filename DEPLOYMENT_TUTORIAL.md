# Deployment Tutorial: AI Developers Blog Aggregator

> **Who this is for:** Anyone forking this project — from first-time GitHub Pages users
> to experienced engineers who just want to know the non-obvious gotchas.
>
> **What it covers:** Complete setup of the three-service stack:
> GitHub Actions (scheduling) + KiloCode Webhooks (AI) + GitHub Pages (hosting).
>
> **Time to complete:** 20–40 minutes depending on familiarity with GitHub.

---

## How the System Works

Before diving into steps, here is the full data flow:

```
Every 4 hours
─────────────────────────────────────────────────────────────────
GitHub Actions runner (free for public repos)
  │
  ├─ 1. Checkout repo + install Python deps
  │
  ├─ 2. python scraper/scraper.py
  │      │
  │      ├─ Fetch RSS feeds / HTML from blog sources
  │      ├─ Deduplicate against data/articles.json
  │      └─ For each new article → POST to KiloCode webhook
  │              │
  │              └─ KiloCode Cloud Agent (your webhook trigger)
  │                    │
  │                    └─ AI model analyzes article
  │                         Returns JSON: summary, quote, topics,
  │                         key_insights, technical_level, category
  │
  ├─ 3. python generator/site_generator.py
  │      Reads data/articles.json → generates site/ (HTML + CSS)
  │
  ├─ 4. git commit + push  (saves articles.json and posts/ to repo)
  │
  ├─ 5. actions/upload-pages-artifact  (packages site/ folder)
  │
  └─ 6. actions/deploy-pages  (publishes to GitHub Pages)
              │
              └─ https://your-username.github.io/ai-dev-blog/
```

---

## Prerequisites

You need accounts/tools at three services. All free tiers are sufficient.

| What | Where | Required |
|------|-------|----------|
| GitHub account | github.com | Yes |
| KiloCode account | kilo.ai | Yes (for AI analysis) |
| Git + Python 3.12+ | Local | For local testing only |

> **Beginner tip:** You can skip local Python setup entirely and let GitHub Actions
> do all the work. Local testing is optional but speeds up debugging.

---

## Part 1 — Fork and Configure the Repository

### Step 1.1 — Fork

1. Go to [github.com/jacek-mar/ai-dev-blog](https://github.com/jacek-mar/ai-dev-blog)
2. Click **Fork** (top right)
3. Choose your account as destination
4. Your copy is now at `https://github.com/YOUR-USERNAME/ai-dev-blog`

Throughout this guide, replace `YOUR-USERNAME` with your actual GitHub username.

---

### Step 1.2 — Enable GitHub Actions

1. Go to your fork: `https://github.com/YOUR-USERNAME/ai-dev-blog`
2. Click the **Actions** tab
3. If you see a yellow banner saying "Workflows aren't being run on this forked
   repository", click **"I understand my workflows, go ahead and enable them"**

> **Why this matters:** GitHub disables Actions on forks by default for security.
> Without this step, the scraper will never run automatically.

---

### Step 1.3 — Review `sources.json`

The file `sources.json` defines which blogs to aggregate. You can use the defaults or
customize them before your first run. Each source has:

```json
{
  "name": "Display name shown on site",
  "url": "Blog listing page URL",
  "rss": "RSS feed URL (if available)",
  "scrape_type": "html (if no RSS)",
  "max_articles": 10
}
```

No changes are required to proceed — the defaults point to real, live AI/ML blogs.

---

## Part 2 — KiloCode Webhook Setup

The AI analysis step runs through a KiloCode Cloud Agent webhook. This is what
transforms a raw scraped article into enriched content with a 200–250 word summary,
original quote, technical insights, and categories.

### Step 2.1 — Create a KiloCode Account

1. Go to [kilo.ai](https://kilo.ai) and sign up
2. You get access to the Cloud Agent platform on the free tier
3. No credit card required to start (free promotional models available)

---

### Step 2.2 — Create a Cloud Agent

1. Go to [app.kilo.ai/cloud](https://app.kilo.ai/cloud)
2. Click **"New Cloud Agent"** or equivalent button
3. Set:
   - **Name:** `ai-blog-enhancer` (or any name you prefer)
   - **Description:** "Analyzes AI/ML blog articles for the aggregator"
   - **Repository:** Not required — leave empty (the agent is stateless)

---

### Step 2.3 — Create a Webhook Trigger

This is the URL your scraper will call for each article.

1. Inside your Cloud Agent, find **Webhook Triggers** and click **"Add Trigger"**
2. Configure:
   - **Name:** `blog-article-enhancer`
   - **Method:** POST
   - **Authentication:** Enable webhook authentication
     - **Header name:** `Authorization`
     - **Shared secret:** Create a long random string, e.g. `kilo_blog_abc123xyz...`
     - **Copy this secret** — you'll need it in Step 3

3. **Set the Prompt Template** — paste this into the prompt field:

   ```
   You are an AI assistant that analyzes AI/ML blog posts for an automated blog aggregator targeting software developers.

   Incoming article data:
   - Title: {{bodyJson.title}}
   - Source: {{bodyJson.source}}
   - Link: {{bodyJson.link}}
   - Content: {{bodyJson.content}}

   Your tasks:
   1. Write a detailed summary of 200–250 words suitable for experienced developers.
      Cover the main argument, key technical points, and practical implications.
   2. Extract one original direct quote (1–2 sentences maximum) that best represents
      the author's voice or a key insight. Use exact wording from the content.
   3. Assign a category: "AI/ML" | "LLMs" | "DevOps" | "Cloud" | "Developer Tools" |
      "Research" | "Open Source" | "Security" | "Web Dev" | "Infrastructure"
   4. List 3–5 specific technical topics (short strings, e.g. "RAG", "fine-tuning").
   5. Assess technical level: "beginner" | "intermediate" | "advanced"
   6. List 3–5 key insights as bullet-point strings (what a developer should take away).
   7. Set recommended: true if the article offers practical value, false otherwise.

   Return ONLY this JSON, no markdown, no other text:
   {
     "summary": "<200–250 word developer-focused summary>",
     "quote": "<exact 1–2 sentence quote from the article>",
     "quote_attribution": "<Author Name, Source Name>",
     "category": "<category string>",
     "topics": ["topic1", "topic2", "topic3"],
     "technical_level": "intermediate",
     "key_insights": [
       "First actionable insight",
       "Second actionable insight",
       "Third actionable insight"
     ],
     "recommended": true
   }
   ```

   > **Model choice:** The template works with any capable model. Claude Sonnet 4.5
   > is a reliable default, but GLM-5 and MiniMax M2.5 are available on free/promotional
   > tiers and produce good results at $0/article. See [WEBHOOK_PROMPT_TEMPLATES.md](WEBHOOK_PROMPT_TEMPLATES.md)
   > for 7 alternative templates and a cost comparison table.

4. **Save the trigger**
5. **Copy the Webhook URL** — shown after saving, format:
   `https://app.kilo.ai/api/webhooks/[trigger-id]/...`

---

### Step 2.4 — Test the Webhook (Recommended)

Before wiring everything together, verify the webhook returns valid JSON:

```bash
curl -X POST "https://app.kilo.ai/api/webhooks/YOUR-TRIGGER-ID" \
  -H "Authorization: Bearer YOUR-SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Introduction to RAG with LangChain",
    "source": "Example Blog",
    "link": "https://example.com/rag-langchain",
    "content": "Retrieval-Augmented Generation (RAG) combines a retrieval system with a language model to answer questions using documents from a knowledge base. This tutorial shows how to build a RAG pipeline using LangChain and a local vector store..."
  }'
```

**Expected result:**
- HTTP status: `200 OK`
- Response body: a JSON object matching the schema above
- Response time: 10–30 seconds (AI processing)

**If it fails:**

| Status | Cause | Fix |
|--------|-------|-----|
| `401` | Wrong secret or header | Check `Authorization: Bearer YOUR-SECRET` |
| `413` | Payload too large (max 256 KB) | Trim `content` field |
| `415` | Wrong content type | Add `-H "Content-Type: application/json"` |
| `429` | Too many concurrent requests | Max 20 concurrent per trigger |
| `500` | Prompt error | Check the prompt template for syntax issues |

---

## Part 3 — GitHub Secrets

GitHub Actions needs your KiloCode credentials to call the webhook. Never hardcode
credentials in files — use GitHub Secrets instead.

### Step 3.1 — Add Secrets

1. Go to your fork: `https://github.com/YOUR-USERNAME/ai-dev-blog`
2. Navigate to **Settings → Secrets and variables → Actions**
3. Click **"New repository secret"** and add each of the following:

| Secret name | Value |
|-------------|-------|
| `KILO_WEBHOOK_URL` | The full webhook URL from Step 2.3 |
| `KILO_WEBHOOK_SECRET` | The shared secret from Step 2.3 |

> **Important:** The scraper prefixes the secret with `Bearer ` automatically
> (in `KiloAIEnhancer.__init__`). Store only the raw token in the secret,
> not `Bearer token` — unless your KiloCode trigger requires the full string.

---

### Step 3.2 — Verify Secrets Are Referenced in the Workflow

The workflow file `.github/workflows/python-scraper-hybrid.yml` already contains:

```yaml
- name: Run scraper with KiloCode AI enhancement
  env:
    ENABLE_AI_ENHANCEMENT: "true"
    KILO_WEBHOOK_URL: ${{ secrets.KILO_WEBHOOK_URL }}
    KILO_WEBHOOK_SECRET: ${{ secrets.KILO_WEBHOOK_SECRET }}
  run: python scraper/scraper.py
```

No changes needed — these variable names match exactly what `scraper.py` reads from
`os.environ`.

---

## Part 4 — GitHub Pages: The Tricky Part

> **Read this section carefully.** GitHub Pages configuration is where most forks
> get stuck. This project encountered these exact issues during initial setup.

### The Core Problem

The site generator outputs HTML to a folder called `site/`. GitHub Pages'
**branch-based deployment** only supports two folder options:

```
✅ /  (repository root)
✅ /docs
❌ /site  ← NOT available in the dropdown
```

If you go to **Settings → Pages** and try to select `/site` as the folder,
it simply does not appear in the list. This is a GitHub constraint, not a bug
in this project.

**Solution:** Use **GitHub Actions** as the Pages source instead of "Deploy from
a branch". The workflow already handles uploading `site/` and deploying it.

---

### Step 4.1 — Set Pages Source to GitHub Actions

1. Go to: `https://github.com/YOUR-USERNAME/ai-dev-blog/settings/pages`
2. Under **"Build and deployment"** → **"Source"**, open the dropdown
3. Select **"GitHub Actions"**

   ```
   ┌──────────────────────────────────┐
   │ Source                           │
   │ ┌──────────────────────────────┐ │
   │ │ GitHub Actions            ▼  │ │  ← Select this
   │ └──────────────────────────────┘ │
   └──────────────────────────────────┘

   NOT this:
   ┌──────────────────────────────────┐
   │ │ Deploy from a branch      ▼  │ │  ← Will NOT work with /site
   └──────────────────────────────────┘
   ```

4. Save if prompted (some repos auto-save)

> **If "GitHub Actions" is not visible in the dropdown:**
> Go to **Settings → Actions → General** and check that:
> - Actions are **enabled** (not disabled)
> - Workflow permissions are set to **"Read and write permissions"**
>
> Then go back to Pages settings — the option should now appear.

---

### Step 4.2 — Understand How Pages Deployment Works Here

Unlike branch-based Pages, the GitHub Actions approach uses two dedicated actions
in the workflow:

```yaml
- name: Upload site artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: 'site/'          # Packages the entire site/ folder

- name: Deploy to GitHub Pages
  id: deployment
  uses: actions/deploy-pages@v4   # Publishes it to gh-pages infrastructure
```

These require three permissions to be set in the workflow (already present):

```yaml
permissions:
  contents: write     # Push data/articles.json back to repo
  pages: write        # Upload pages artifact
  id-token: write     # Required by deploy-pages action (OIDC auth)
```

All three are already in the workflow file. You do not need to change anything here.

---

### Step 4.3 — The Deployments URL Confusion

> **Known gotcha:** `https://github.com/YOUR-USERNAME/ai-dev-blog/deployments`
> **returns a 404 page** even after a successful deployment.

This is a GitHub UI routing quirk. The URL `/deployments` is not a valid page
for most repositories — it returns 404 regardless of deployment status.

**How to actually check deployment status:**

| What | Where |
|------|-------|
| Active deployments | Sidebar widget on the repo homepage ("Deployments" section) |
| Deployment history | `https://github.com/YOUR-USERNAME/ai-dev-blog/deployments/activity_log?environments_filter=github-pages` |
| Workflow run logs | `https://github.com/YOUR-USERNAME/ai-dev-blog/actions` |
| Live site | `https://YOUR-USERNAME.github.io/ai-dev-blog/` |

The sidebar "Deployments" widget on the main repo page is the most reliable indicator
of deployment status. It appears after the first successful run.

---

## Part 5 — Running and Verifying

### Step 5.1 — Trigger Your First Run

The workflow runs automatically every 4 hours. To run it now:

1. Go to `https://github.com/YOUR-USERNAME/ai-dev-blog/actions`
2. Click **"AI Blog Scraper - Hybrid"** in the left sidebar
3. Click the **"Run workflow"** dropdown on the right
4. Click **"Run workflow"** (green button)

---

### Step 5.2 — Monitor the Run

Click on the running workflow. You should see 6 steps complete in order:

| Step | What happens | Typical duration |
|------|-------------|-----------------|
| Checkout repository | Clones your repo | 10–20s |
| Set up Python 3.12 | Installs Python (cached after first run) | 30s–2min |
| Install dependencies | `pip install -r requirements.txt` (cached) | 15–60s |
| Run scraper with KiloCode AI | Fetches articles, calls webhooks | 3–8 min |
| Generate static site | Builds HTML from articles.json | 10–30s |
| Commit and push changes | Saves new articles to repo | 10–20s |
| Upload site artifact | Packages site/ for Pages | 5–15s |
| Deploy to GitHub Pages | Publishes to GitHub Pages CDN | 30–60s |

First run total: approximately **8–12 minutes** (pip cache is cold).
Subsequent runs: approximately **5–8 minutes**.

---

### Step 5.3 — Verify the Site is Live

After the workflow completes:

1. Wait 1–2 minutes for Pages CDN propagation
2. Visit `https://YOUR-USERNAME.github.io/ai-dev-blog/`
3. You should see the dark-themed aggregator with a numbered article list

> **If you see a 404:** Wait another 2–3 minutes and hard-refresh (Ctrl+F5 / Cmd+Shift+R).
> CDN propagation can take a few minutes on the first deployment.

---

### Step 5.4 — Verify AI Enhancement Worked

On the site, click any article. If the webhook worked, you should see:

- A 200–250 word AI summary (not a short 2–3 line excerpt)
- A blockquote with a verbatim quote and author attribution
- A list of key insights
- Topic tags and technical level badge

If these are missing (only a short summary shown), the webhook may not have
returned valid JSON. Check the Actions run log for lines like:

```
✅ Enhanced: AI/ML | 4 topics
```

or error lines like:

```
Webhook error: ...
Invalid AI response, using fallback
```

---

## Part 6 — Customization

### Change the Article Sources

Edit `sources.json`. Each entry supports:

```json
{
  "name": "Source display name",
  "url": "https://example.com/blog",
  "rss": "https://example.com/feed.xml",   // Optional: use RSS if available
  "scrape_type": "html",                   // Required if no RSS
  "max_articles": 10                       // Limit articles per run
}
```

If a source has an RSS feed, use `"rss"`. If not, use `"scrape_type": "html"`.
The HTML scraper uses source-specific logic in `scraper/scraper.py` — you may need
to add a new `elif` block for sites with unusual layouts.

---

### Change the AI Prompt

The prompt template defines what the AI produces for each article. You can change
it at any time in KiloCode without touching any code — just edit the prompt in
the webhook trigger UI.

See [WEBHOOK_PROMPT_TEMPLATES.md](WEBHOOK_PROMPT_TEMPLATES.md) for:
- The current production template (200–250 word summary + quote)
- A minimal template (3–4 sentences, cheapest option)
- A deep technical template (for research-heavy sources)
- A beginner-friendly template (plain language, no jargon)
- An opinionated curation template (hype scores, editorial notes)
- A digest template (newsletter/Slack format)
- The retired legacy template (for historical reference)

Each template section explains the trade-offs in cost, output quality, and
which model works best.

---

### Change the Run Schedule

Edit `.github/workflows/python-scraper-hybrid.yml`:

```yaml
on:
  schedule:
    - cron: "0 */4 * * *"   # Every 4 hours — change this
```

Cron syntax: `minute hour day month weekday`

Examples:

```
"0 */6 * * *"    Every 6 hours (4×/day)
"0 8,20 * * *"   Twice a day at 08:00 and 20:00 UTC
"0 9 * * 1"      Every Monday at 09:00 UTC
```

> **Note:** GitHub may delay scheduled workflows by up to 15–30 minutes during
> high-load periods. This is normal behavior.

---

### Change the Site Appearance

The dark Hacker News-style theme is generated by `generator/site_generator.py`.
The `generate_css()` method creates `site/style.css` on each run — edits to a
manually placed `site/style.css` will be overwritten.

To change colors or layout, edit the CSS string inside `generate_css()` in
[generator/site_generator.py](generator/site_generator.py).

Key CSS variables:

```css
--bg-page:   #0a0a0a   /* Page background */
--bg-header: #1a0f00   /* Nav bar background */
--accent:    #ff6600   /* Orange accent (links, numbers) */
--link:      #ff9940   /* Body link color */
--width:     860px     /* Max column width */
```

---

## Part 7 — Cost Management

This project is designed to run within GitHub's free tier for public repos.
The only variable cost is AI model inference via KiloCode.

### Free Path (Recommended to Start)

KiloCode periodically offers free-tier models:
- **GLM-5** — free for a limited time via Kilo CLI
- **MiniMax M2.5** — free for the first week (80.2% SWE-Bench)
- **Opus 4.6 via Slack** — full flagship at no cost

Use one of these models in your Cloud Agent while they are available.

### Paid Path (After Promotions)

| Model | Input/M tokens | Output/M tokens | Cost per 100 articles* |
|-------|---------------|-----------------|----------------------|
| MiniMax M2.5 | $0.30 | Standard | ~$0.06 |
| Claude Sonnet 4.5 | $0.30 (cached) | $15.00 | ~$0.15 |
| Claude Opus 4.6 | $1.50 (cached) | $75.00 | ~$0.75 |

*Estimated at ~500 output tokens per article with cached input.

The default run processes up to ~20 articles per source per run, with 6 sources
and 6 runs per day. In practice, most runs produce 0–5 new articles (deduplication
eliminates previously seen articles).

### Built-in Cost Controls

The scraper already implements:
- **Deduplication:** articles are never processed twice
- **`max_articles` per source:** limits per-run article count (default 10–20)
- **KiloCode rate limiting:** max 20 concurrent webhook calls

---

## Troubleshooting Reference

These are real issues encountered during the development of this project.

---

### `/site` folder not available in GitHub Pages settings

**Symptom:** In Settings → Pages, the folder dropdown only shows `/` and `/docs`.

**Cause:** GitHub's branch-based deployment does not support custom folder names.

**Fix:** Set Pages source to **"GitHub Actions"** (see Part 4). Do not change the
generator output folder — GitHub Actions uploads `site/` directly.

---

### `https://github.com/.../deployments` returns 404

**Symptom:** After a successful deployment, visiting the `/deployments` URL gives a 404.

**Cause:** This URL is not a valid GitHub UI page for most repos. It is a routing
artifact, not a real deployment status page.

**Fix:** Check deployment status via the **sidebar widget** on the repo homepage or at:
`/deployments/activity_log?environments_filter=github-pages`

Your site may already be live at `https://YOUR-USERNAME.github.io/ai-dev-blog/`
even while `/deployments` shows 404.

---

### AI enhancement not running / articles have no summaries

**Symptom:** Articles show only a short excerpt instead of a 200-word AI summary.

**Possible causes and fixes:**

1. **`ENABLE_AI_ENHANCEMENT` not set**
   Verify the workflow has `ENABLE_AI_ENHANCEMENT: "true"` in the scraper step's `env:` block.

2. **Secrets not set or wrong**
   Go to Settings → Secrets → Actions. Verify `KILO_WEBHOOK_URL` and `KILO_WEBHOOK_SECRET`
   are present and match your KiloCode webhook configuration.

3. **Webhook returns invalid JSON**
   Test your webhook manually (see Step 2.4). The scraper requires these 6 fields:
   `summary`, `category`, `topics`, `technical_level`, `key_insights`, `recommended`.
   If any are missing, it falls back to a heuristic summary.

4. **Articles were already processed**
   The scraper only calls the webhook for articles that don't yet have `ai_enhanced_at`
   in `articles.json`. Already-processed articles skip the webhook call.

---

### Site deploys but is missing CSS (unstyled page)

**Symptom:** The site loads but looks unstyled (no dark background, no layout).

**Cause:** `site_generator.py` generates `site/style.css` dynamically. If only
`site/index.html` was generated but `style.css` was not, the HTML references a
missing file.

**Fix:** Run the generator locally to verify it completes without errors:
```bash
python generator/site_generator.py
ls site/style.css   # Should exist
```

---

### Workflow fails with "Permission denied" or "remote rejected"

**Symptom:** The "Commit and push changes" step fails.

**Cause:** Workflow doesn't have write access to the repository.

**Fix:**
1. Go to **Settings → Actions → General**
2. Under **"Workflow permissions"**, select **"Read and write permissions"**
3. Save and re-run the workflow

---

### `robots.txt` blocking article content fetch

**Symptom:** In the logs: `robots.txt disallows fetching: https://...`

**Cause:** The scraper (`can_fetch_url()`) checks `robots.txt` before fetching
each article page. Some sites disallow scraping in their `robots.txt`.

**Fix:** This is intentional and correct behavior — the scraper respects site terms.
The article will still appear in the database (from RSS metadata) but without
full-text content. The AI will summarize what's available.

If you believe the robots.txt is overly restrictive for your use case, check the
site's actual robots.txt manually: `https://example.com/robots.txt`.

---

### KiloCode webhook times out (>30 seconds)

**Symptom:** Log shows `Webhook timeout for: [article title]`

**Cause:** The AI model took longer than 30 seconds to process the article.

**Fix options:**
1. Switch to a faster model in your KiloCode Cloud Agent
2. Use Template 2 (Minimal) — shorter prompt, faster response
3. Trim the `content` field in the payload (already limited to 5000 chars in `scraper.py`)

---

## Local Development Setup

If you want to test changes locally before pushing:

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/ai-dev-blog.git
cd ai-dev-blog

# Install Python dependencies
pip install -r requirements.txt

# Run scraper WITHOUT AI (no KiloCode credentials needed)
python scraper/scraper.py

# Generate site
python generator/site_generator.py

# Preview locally
python -m http.server 8000 --directory site
# Open http://localhost:8000
```

To test WITH AI enhancement locally:

```bash
# Windows Command Prompt
set ENABLE_AI_ENHANCEMENT=true
set KILO_WEBHOOK_URL=https://app.kilo.ai/api/webhooks/YOUR-TRIGGER-ID
set KILO_WEBHOOK_SECRET=your-secret-here
python scraper/scraper.py

# Windows PowerShell
$env:ENABLE_AI_ENHANCEMENT="true"
$env:KILO_WEBHOOK_URL="https://app.kilo.ai/api/webhooks/YOUR-TRIGGER-ID"
$env:KILO_WEBHOOK_SECRET="your-secret-here"
python scraper/scraper.py

# Linux / macOS / Git Bash
export ENABLE_AI_ENHANCEMENT=true
export KILO_WEBHOOK_URL=https://app.kilo.ai/api/webhooks/YOUR-TRIGGER-ID
export KILO_WEBHOOK_SECRET=your-secret-here
python scraper/scraper.py
```

---

## Related Documentation

| Document | Contents |
|----------|----------|
| [README.md](README.md) | Project overview, quick start, architecture |
| [WEBHOOK_PROMPT_TEMPLATES.md](WEBHOOK_PROMPT_TEMPLATES.md) | 7 alternative AI prompt templates with cost analysis |
| [COPYRIGHT.md](COPYRIGHT.md) | Copyright notice, scraping policy, source attribution |
| `.github/workflows/python-scraper-hybrid.yml` | Full workflow file with all deployment steps |
| `scraper/scraper.py` | Scraper code — robots.txt handling, KiloCode client |
| `generator/site_generator.py` | Site generator — HTML templates, CSS, page structure |

---

*Having trouble with a step not covered here? Open an issue at
[github.com/jacek-mar/ai-dev-blog/issues](https://github.com/jacek-mar/ai-dev-blog/issues).*
