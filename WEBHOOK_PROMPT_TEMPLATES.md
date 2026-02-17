# KiloCode Webhook Prompt Templates

> Community reference for customizing the AI analysis step of the AI Developers Blog aggregator.
> All templates plug into the [KiloCode Cloud Agent](https://kilo.ai/docs/code-with-ai/platforms/cloud-agent)
> webhook trigger — no code changes needed to switch between them.

---

## How It Works

The scraper sends one HTTP POST per article to your KiloCode webhook:

```json
{
  "title":   "Article title",
  "content": "Cleaned article text (up to ~5000 chars)",
  "source":  "Blog source name (e.g. Anthropic, Google Cloud)",
  "link":    "https://original-article-url"
}
```

In your KiloCode prompt template, these fields are accessed as:

```
{{bodyJson.title}}    {{bodyJson.source}}
{{bodyJson.content}}  {{bodyJson.link}}
```

The webhook must return a **JSON-only response** (no markdown, no prose). The scraper
validates six mandatory fields: `summary`, `category`, `topics`, `technical_level`,
`key_insights`, `recommended`. Any extra fields are stored automatically and displayed
by the site generator when present.

### Switching Templates

1. Go to [app.kilo.ai/cloud/webhooks](https://app.kilo.ai/cloud/webhooks)
2. Click your webhook trigger
3. Edit the **Prompt Template** field
4. Paste the new template and save

No repository changes required.

---

## Template History

### Legacy Template (v1 — initial prototype)

> **Status: Retired.** Used `ai_` prefixed field names in the response — which conflicted
> with the scraper's internal mapping. Included `ai_read_time` as an integer, but this
> was never rendered on the site. Replaced by Template 1 (below).
>
> **Why it was retired:** The field names (`ai_summary`, `ai_tags`, `ai_difficulty`, etc.)
> suggested the model should output scraper-internal fields. This caused confusion and
> inconsistency: the scraper maps response fields to `ai_*` keys internally, so the
> webhook output should use the unprefixed names (`summary`, `topics`, `technical_level`).
> The legacy template also generated only a 2–3 sentence summary, which was too short
> for reader value.

```text
You are an AI blog article analyzer. Process the incoming article and return a JSON response with analysis.

Article Details:
- Title: {{bodyJson.title}}
- Source: {{bodyJson.source}}
- Link: {{bodyJson.link}}
- Content Preview: {{bodyJson.content}}

Analyze this article and return ONLY valid JSON (no markdown, no explanations) in this exact format:

{
  "ai_summary": "2-3 sentence summary focusing on key technical insights",
  "ai_tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "ai_key_points": [
    "First key technical point",
    "Second key technical point",
    "Third key technical point"
  ],
  "ai_difficulty": "beginner|intermediate|advanced",
  "ai_read_time": 5,
  "ai_topics": ["Primary Topic", "Secondary Topic"],
  "ai_code_included": true,
  "ai_enhanced_at": "{{timestamp}}"
}
```

**Performance impact:** ~150–250 output tokens. Fast, cheap, but produces short summaries
and was incompatible with the scraper's field validation without extra mapping code.

---

## Current & Alternative Templates

All templates below use the correct field contract. Choose based on your audience,
budget, and the kind of content you're aggregating.

---

### Template 1: Current Production — Balanced (ACTIVE)

> **Status: Active default.**
> This is the template currently deployed on the live site.

**When to use:** General-purpose developer audience. Best balance of summary depth,
quote extraction, and token cost. Suitable for 90% of AI/ML blog content.

**Why the 200–250 word summary length?**
Short summaries (2–3 sentences) leave readers without enough context to decide whether
to click through to the original. 200–250 words gives enough detail to be genuinely
useful without replacing the original article. Longer summaries increase cost
proportionally with diminishing returns for comprehension.

**Why include the original quote?**
A verbatim quote anchors the summary in the author's actual voice and adds credibility.
It also signals to readers that this is a curated summary, not original writing.

**Performance impact:** ~600–800 output tokens per article. At Claude Sonnet 4.5 rates
(cached), approximately **$0.12–$0.15 per 100 articles**.

```text
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

---

### Template 2: Minimal — Fast & Cheap

**When to use:** High-volume ingestion, budget-constrained runs, or when you are
aggregating many short posts where deep analysis adds little value (e.g. changelog
entries, short release notes).

**Trade-offs:**
- **Pro:** ~65% cheaper than Template 1; noticeably faster per-article latency.
- **Con:** 3–4 sentence summary is thinner — less useful as a standalone read.
  Readers will need to click through more often to understand the article.

**Performance impact:** ~200–300 output tokens. Approximately **$0.03–$0.06 per 100 articles**
at Claude Sonnet 4.5 cached rates. Ideal with free-tier models (GLM-5, MiniMax M2.5).

```text
Analyze this AI/ML blog article and return JSON only.

Title: {{bodyJson.title}}
Source: {{bodyJson.source}}
Content: {{bodyJson.content}}

Return ONLY:
{
  "summary": "<3–4 sentence summary for developers>",
  "quote": "<one direct quote from the article, or empty string>",
  "quote_attribution": "<Author, Source or empty string>",
  "category": "<AI/ML | LLMs | DevOps | Cloud | Developer Tools | Research | Other>",
  "topics": ["topic1", "topic2"],
  "technical_level": "<beginner|intermediate|advanced>",
  "key_insights": ["insight1", "insight2"],
  "recommended": true
}
```

---

### Template 3: Deep Technical — Advanced Readers

**When to use:** Sources like Google Cloud, Anthropic, or HuggingFace that publish
long-form research-heavy posts with architecture diagrams, benchmarks, and deep
implementation details. Designed for an audience of senior engineers and researchers.

**Trade-offs:**
- **Pro:** Extracts 5–7 fine-grained technical topics and 5 precise insights.
  Includes `code_included` flag for filtering articles that have runnable examples.
- **Con:** ~40–50% more expensive than Template 1. Heavier prompts can occasionally
  cause models to produce longer-than-expected output. Works best with models that
  reliably follow JSON output constraints (Claude Sonnet 4.5 or better recommended).

**Performance impact:** ~900–1100 output tokens. Approximately **$0.17–$0.22 per 100 articles**
at Claude Sonnet 4.5 cached rates.

```text
You are a senior software engineer and technical writer analyzing a blog post for
an audience of professional AI/ML engineers and developers.

Article:
- Title: {{bodyJson.title}}
- Source: {{bodyJson.source}}
- URL: {{bodyJson.link}}
- Content: {{bodyJson.content}}

Produce a detailed analysis. Be specific and technical — avoid vague language.

Instructions:
1. Summary (200–250 words): Cover the technical approach, architecture decisions,
   benchmarks mentioned, and developer impact. Use precise technical language.
2. Original Quote: Extract the most technically significant 1–2 sentences verbatim.
3. Category: One of "AI/ML" | "LLMs" | "DevOps" | "Cloud" | "Developer Tools" |
   "Research" | "Open Source" | "Security" | "MLOps" | "Infrastructure"
4. Topics: 5–7 specific technical terms (e.g. "RLHF", "quantization", "LoRA").
5. Technical Level: "beginner" | "intermediate" | "advanced"
6. Key Insights: 5 precise technical takeaways a developer can act on.
7. Code Included: true if the article contains code examples/snippets.
8. Recommended: true if it provides concrete technical value.

Return ONLY valid JSON:
{
  "summary": "<200–250 word technical summary>",
  "quote": "<verbatim 1–2 sentence technical quote>",
  "quote_attribution": "<Author Name, Source>",
  "category": "<category>",
  "topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
  "technical_level": "advanced",
  "key_insights": [
    "Specific technical takeaway 1",
    "Specific technical takeaway 2",
    "Specific technical takeaway 3",
    "Specific technical takeaway 4",
    "Specific technical takeaway 5"
  ],
  "code_included": true,
  "recommended": true
}
```

---

### Template 4: Beginner-Friendly — Accessible Explanations

**When to use:** When your aggregator targets developers who are new to AI/ML — bootcamp
graduates, backend engineers exploring the AI space, or student readers. Adds an
`explain_quote` field that gives a plain-English gloss on the extracted quote.

**Trade-offs:**
- **Pro:** Summaries define jargon inline, making posts approachable. The
  `explain_quote` field can be rendered as a "What this means" tooltip.
- **Con:** The plain-language style reduces information density. Advanced readers
  may find it too basic. Token cost is similar to Template 1.

**Performance impact:** ~600–800 output tokens.

```text
You are a developer advocate writing about AI/ML topics for developers who are
beginning to explore the field. Explain things clearly without assuming deep prior knowledge.

Article:
- Title: {{bodyJson.title}}
- Source: {{bodyJson.source}}
- Content: {{bodyJson.content}}

Your tasks:
1. Write a summary of 200–250 words that:
   - Explains what the article is about in plain language
   - Defines any advanced terms used (briefly, inline)
   - States clearly why a developer might care about this
   - Avoids unexplained jargon
2. Find one quote (1–2 sentences) that explains the core idea well.
3. Add a plain-English explanation of the quote (1 sentence, "explain_quote" field).
4. Classify the article by category and difficulty.
5. List 3 key takeaways written for a beginner audience.

Return ONLY this JSON:
{
  "summary": "<200–250 word beginner-accessible summary>",
  "quote": "<1–2 sentence explanatory quote>",
  "quote_attribution": "<Author, Source>",
  "explain_quote": "<one sentence plain-English explanation of the quote>",
  "category": "<AI/ML | LLMs | DevOps | Cloud | Developer Tools | Research | Other>",
  "topics": ["topic1", "topic2", "topic3"],
  "technical_level": "beginner",
  "key_insights": [
    "Beginner-friendly takeaway 1",
    "Beginner-friendly takeaway 2",
    "Beginner-friendly takeaway 3"
  ],
  "recommended": true
}
```

---

### Template 5: Opinionated Curation — Editorial Voice

**When to use:** If your aggregator evolves to include an "Editor's Pick" or quality
scoring feature. This template adds `editorial_note` (honest 50–80 word take on whether
the article is hype or substance), `hype_score` (1–5), and `practical_score` (1–5).

**Trade-offs:**
- **Pro:** Gives the site a distinctive editorial perspective. The `hype_score` and
  `practical_score` can power sorting/filtering ("Show only practical_score ≥ 4").
- **Con:** Requires a capable model with strong reasoning to produce useful scores —
  cheaper models may output generic scores. The editorial voice is model-dependent
  and may feel inconsistent over time.
- **Model recommendation:** Claude Sonnet 4.5 or Opus 4.6. Avoid smaller models
  for this template.

**Performance impact:** ~700–900 output tokens.

```text
You are a senior developer and technical editor for an AI/ML news aggregator.
You have strong opinions about what is genuinely useful vs. hype.

Article:
- Title: {{bodyJson.title}}
- Source: {{bodyJson.source}}
- URL: {{bodyJson.link}}
- Content: {{bodyJson.content}}

Your tasks:
1. Factual Summary (150–200 words): What does the article actually say?
2. Editorial Note (50–80 words): Your honest take — is this genuinely useful,
   is it marketing, is it research for research's sake? Be direct.
3. Original Quote: The most memorable or representative 1–2 sentences.
4. Hype Score: Integer 1–5, where 1=pure hype, 5=grounded technical content.
5. Practical Score: Integer 1–5, where 1=academic only, 5=immediately applicable.
6. Topics, level, insights as usual.

Return ONLY this JSON:
{
  "summary": "<150–200 word factual summary>",
  "editorial_note": "<50–80 word editorial opinion>",
  "quote": "<1–2 sentence memorable quote>",
  "quote_attribution": "<Author, Source>",
  "hype_score": 3,
  "practical_score": 4,
  "category": "<category>",
  "topics": ["topic1", "topic2", "topic3"],
  "technical_level": "intermediate",
  "key_insights": ["insight1", "insight2", "insight3"],
  "recommended": true
}
```

---

### Template 6: Multilingual — Polish Summary

**When to use:** If your target audience is Polish-speaking developers. Technical terms
stay in English (as is standard in Polish technical writing); only prose is translated.
Adaptable to any target language by replacing Polish instructions with the desired language.

**Trade-offs:**
- **Pro:** Expands your reader base significantly. No code changes needed.
- **Con:** Translation quality depends on the model. Claude Sonnet 4.5 produces
  excellent Polish; smaller/cheaper models may produce awkward phrasing. Quote is
  kept in the original English (verbatim attribution is language-neutral).

**Performance impact:** ~700–900 output tokens (Polish prose is slightly more verbose
than English at the token level with some models).

```text
You are an AI assistant analyzing English-language AI/ML blog posts and summarizing
them in Polish for Polish software developers.

Article:
- Title: {{bodyJson.title}}
- Source: {{bodyJson.source}}
- Content: {{bodyJson.content}}

Tasks:
1. Write a Polish-language summary of 200–250 words. Use professional Polish
   technical writing style. Technical terms may remain in English where standard.
2. Keep the original English quote verbatim (do not translate quotes).
3. Provide category, topics, and key_insights in Polish.

Return ONLY this JSON:
{
  "summary": "<200–250 słów po polsku>",
  "quote": "<oryginalny cytat 1–2 zdania po angielsku>",
  "quote_attribution": "<Autor, Źródło>",
  "category": "<kategoria po polsku>",
  "topics": ["temat1", "temat2", "temat3"],
  "technical_level": "intermediate",
  "key_insights": [
    "Kluczowy wniosek po polsku 1",
    "Kluczowy wniosek po polsku 2",
    "Kluczowy wniosek po polsku 3"
  ],
  "recommended": true
}
```

---

### Template 7: Structured Digest — Newsletter Format

**When to use:** If you plan to generate a weekly email digest or Slack summary from
the same article database. Adds `headline` (punchy 10-word rewrite), `tldr` (25-word
one-liner), `why_it_matters`, and `action` fields.

**Trade-offs:**
- **Pro:** Output maps directly to newsletter components without further processing.
  The `action` field tells readers exactly what to do next.
- **Con:** The short `summary` (80–120 words) is less useful for the main site view.
  Best used as a **secondary** webhook run for digest generation, not as a replacement
  for Template 1 on the main aggregator.

**Performance impact:** ~500–600 output tokens.

```text
You are producing content for a weekly AI/ML developer digest newsletter.
Content must be scannable, tight, and actionable — developers read this in 60 seconds.

Article:
- Title: {{bodyJson.title}}
- Source: {{bodyJson.source}}
- URL: {{bodyJson.link}}
- Content: {{bodyJson.content}}

Format requirements:
1. "headline": A rewritten title as a punchy 10-word-max headline.
2. "tldr": One-sentence TL;DR (25 words max).
3. "summary": 3–4 sentence summary (80–120 words). Lead with the most important point.
4. "quote": Best 1-sentence quote from the article.
5. "quote_attribution": Author and source.
6. "why_it_matters": One sentence explaining developer impact.
7. "action": One concrete action a developer can take after reading (or "Read the full article").
8. Standard metadata: category, topics, technical_level, recommended.

Return ONLY this JSON:
{
  "headline": "<punchy rewritten headline>",
  "tldr": "<one-sentence TL;DR>",
  "summary": "<80–120 word digest summary>",
  "quote": "<best 1-sentence quote>",
  "quote_attribution": "<Author, Source>",
  "why_it_matters": "<one sentence developer impact>",
  "action": "<one concrete action>",
  "category": "<category>",
  "topics": ["topic1", "topic2"],
  "technical_level": "intermediate",
  "key_insights": ["insight1", "insight2"],
  "recommended": true
}
```

---

## Comparison Table

| Template | Output tokens (est.) | Cost / 100 articles* | Summary length | Extra fields | Best model fit |
|----------|---------------------|----------------------|----------------|--------------|----------------|
| Legacy (retired) | ~150–250 | ~$0.03 | 2–3 sentences | `ai_read_time`, `ai_code_included` | Any |
| **1. Current Production** | **~600–800** | **~$0.12–$0.15** | **200–250 words** | `quote`, `quote_attribution` | Any capable model |
| 2. Minimal | ~200–300 | ~$0.03–$0.06 | 3–4 sentences | `quote` (optional) | Any, inc. free tier |
| 3. Deep Technical | ~900–1100 | ~$0.17–$0.22 | 200–250 words | `code_included`, 5–7 topics | Sonnet 4.5+ |
| 4. Beginner-Friendly | ~600–800 | ~$0.12–$0.15 | 200–250 words | `explain_quote` | Any capable model |
| 5. Opinionated Curation | ~700–900 | ~$0.13–$0.18 | 150–200 words | `editorial_note`, `hype_score`, `practical_score` | Sonnet 4.5+ |
| 6. Polish | ~700–900 | ~$0.13–$0.18 | 200–250 words (PL) | Polish fields | Sonnet 4.5+ |
| 7. Digest | ~500–600 | ~$0.09–$0.12 | 80–120 words | `headline`, `tldr`, `why_it_matters`, `action` | Any capable model |

*Estimated at Claude Sonnet 4.5 cached input rate ($0.30/M tokens input + $15.00/M tokens output).
Actual cost depends on input article length and the model selected. With free-tier models
(GLM-5, MiniMax M2.5 during promotional periods) all templates run at **$0/article**.

---

## Model Recommendations by Template

| Template | Recommended model | Why |
|----------|------------------|-----|
| 1. Production | Any — Claude Sonnet 4.5 default | Reliable JSON + 200-word summaries |
| 2. Minimal | GLM-5 / MiniMax M2.5 (free tier) | Short output, any capable model works |
| 3. Deep Technical | Claude Sonnet 4.5 or Opus 4.6 | Needs strong reasoning for benchmark extraction |
| 4. Beginner | Any — Claude Sonnet 4.5 default | Consistent plain-language tone |
| 5. Opinionated | Claude Sonnet 4.5 or Opus 4.6 | Editorial scoring requires nuanced judgment |
| 6. Polish | Claude Sonnet 4.5+ | Best Polish prose quality |
| 7. Digest | Any — Claude Sonnet 4.5 default | Standard copywriting task |

See the [Cost Analysis section in README.md](README.md#-cost-analysis) for a full breakdown of
available models, pricing tiers, and cost optimization strategies.

---

## JSON Contract Reference

### Mandatory fields (all templates must return these)

| Field | Type | Values |
|-------|------|--------|
| `summary` | string | Developer-focused article summary |
| `category` | string | `"AI/ML"` \| `"LLMs"` \| `"DevOps"` \| `"Cloud"` \| `"Developer Tools"` \| `"Research"` \| `"Open Source"` \| `"Security"` \| `"Web Dev"` \| `"Infrastructure"` \| `"Other"` |
| `topics` | array of strings | 2–7 short technical tag strings |
| `technical_level` | string | `"beginner"` \| `"intermediate"` \| `"advanced"` |
| `key_insights` | array of strings | 2–5 actionable bullet-point strings |
| `recommended` | boolean | `true` if top ~20% value for developers |

### Optional fields (stored and displayed when present)

| Field | Template | Description |
|-------|----------|-------------|
| `quote` | 1–7 | Verbatim 1–2 sentence quote from the article |
| `quote_attribution` | 1–7 | `"Author Name, Source Name"` |
| `explain_quote` | 4 | Plain-English gloss on the quote |
| `code_included` | 3 | `true` if article has runnable code examples |
| `editorial_note` | 5 | 50–80 word honest editorial take |
| `hype_score` | 5 | Integer 1–5: 1=pure hype, 5=grounded technical |
| `practical_score` | 5 | Integer 1–5: 1=academic only, 5=immediately applicable |
| `headline` | 7 | Punchy 10-word rewritten headline |
| `tldr` | 7 | One-sentence TL;DR, 25 words max |
| `why_it_matters` | 7 | One sentence developer impact |
| `action` | 7 | One concrete next action for the reader |

> **Note on field names:** The scraper stores all response fields under `ai_*` keys
> internally (e.g. `summary` → `ai_summary`, `topics` → `ai_topics`). Your webhook
> response should use the **unprefixed** names shown above. Do not add `ai_` prefixes
> in the webhook output.

---

## Contributing Your Own Template

If you fork this project and develop a template that produces notably better results,
please share it via [GitHub Issues](https://github.com/jacek-mar/ai-dev-blog/issues)
or a Pull Request. Include:

- Template name and use case
- Estimated token count
- Sample output JSON
- Which model you tested it with
