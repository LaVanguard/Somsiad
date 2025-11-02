# 🤖 AI Models Configuration - Somsiad Project

**Last Updated:** 2025-11-02
**Critical:** This file defines all AI models used in production

---

## 🎯 Current Production Models

### **Primary LLM: GPT-5 Mini**

**Model ID:** `gpt-5-mini`

**Release Date:** August 7, 2025 (OpenAI)

**Why GPT-5 Mini:**
- ✅ Latest generation model (successor to GPT-4o-mini)
- ✅ Cost-optimized for production use
- ✅ Improved reasoning capabilities vs GPT-4o-mini
- ✅ Lower latency than full GPT-5
- ✅ Better instruction following and safety tuning
- ✅ Supports verbosity parameter for answer length control
- ✅ Reduced latency with `reasoning_effort: minimal`

**Pricing (OpenAI API):**
- Input: ~$0.15-0.20 / 1M tokens (estimated, check latest pricing)
- Output: ~$0.60-0.80 / 1M tokens (estimated)

**Used In:**
- `knowledge/services/rag_service.py:39` - Main RAG answer generation
- `knowledge/services/summarizer.py:27` - Document summarization
- `accounts/views.py:321` - Conversation title generation

**Temperature Settings:**
- RAG answers: `0.3` (balanced creativity/precision)
- Summarization: `0.2` (more consistent, factual)
- Title generation: `0.3` (balanced)

---

### **Embeddings Model: text-embedding-3-small**

**Model ID:** `text-embedding-3-small`

**Dimensions:** 1536

**Why text-embedding-3-small:**
- ✅ Latest OpenAI embeddings model (2024)
- ✅ Better performance than ada-002
- ✅ More cost-effective
- ✅ Compatible with pgvector (Supabase)

**Pricing:**
- $0.02 / 1M tokens

**Used In:**
- `knowledge/services/rag_service.py:35` - Document embeddings
- Vector search in Supabase (1536-dimensional vectors)

---

## 📋 Model Migration History

| Date | From Model | To Model | Reason |
|------|------------|----------|--------|
| 2025-11-02 | gpt-4o-mini | **gpt-5-mini** | GPT-5 release - better performance, same cost tier |
| 2024-XX-XX | gpt-4o | gpt-4o-mini | Cost optimization |
| 2024-XX-XX | text-embedding-ada-002 | text-embedding-3-small | Better quality + lower cost |

---

## 🔧 How to Change Models in Future

### Change LLM Model (GPT-5 → GPT-6, etc.)

**Files to Update:**
1. `knowledge/services/rag_service.py` - Line 39
2. `knowledge/services/summarizer.py` - Line 27
3. `accounts/views.py` - Line 321
4. **This file** - Update documentation

**Code Pattern:**
```python
self.llm = ChatOpenAI(
    openai_api_key=settings.OPENAI_API_KEY,
    model="gpt-5-mini",  # ← Change this
    temperature=0.3
)
```

### Change Embeddings Model

**Files to Update:**
1. `knowledge/services/rag_service.py` - Line 35
2. Supabase vector dimension (if dimension changes)
3. **This file** - Update documentation

**⚠️ WARNING:** Changing embeddings model requires:
- Re-embedding all documents (434+ chunks)
- Updating Supabase vector dimension if different
- Migration script to reprocess all documents

---

## 💰 Current Cost Estimation (100 queries/day)

| Component | Model | Monthly Cost |
|-----------|-------|--------------|
| Query answering (100/day) | gpt-5-mini | ~$30-40 |
| Embeddings (one-time) | text-embedding-3-small | ~$0.50 |
| Document summaries (one-time) | gpt-5-mini | ~$5-10 |
| Title generation (100/day) | gpt-5-mini | ~$2-3 |
| **TOTAL** | | **~$37-53/month** |

*Note: Prices are estimates. Check OpenAI pricing for latest rates.*

---

## 🚀 Alternative Models (Future Consideration)

### If GPT-5 Full Model is Needed:
- **Model:** `gpt-5`
- **Use Case:** Complex legal reasoning, multi-document analysis
- **Cost:** ~5-10x more expensive than gpt-5-mini
- **When to use:** Premium tier, complex legal opinions

### If Even Cheaper Model is Needed:
- **Model:** `gpt-5-nano`
- **Use Case:** Simple queries, title generation only
- **Cost:** ~50% cheaper than gpt-5-mini
- **Trade-off:** Lower quality reasoning

### Embeddings Alternatives:
- **text-embedding-3-large** (3072 dim) - Better quality, 2x cost
- **Multilingual-e5-large** (1024 dim) - Open source, free
- **Cohere embed-multilingual-v3.0** - Better for non-English

---

## ⚙️ Model Configuration Best Practices

### Temperature Guidelines:
- **Factual answers:** 0.0 - 0.3 (RAG, legal advice)
- **Creative answers:** 0.5 - 0.7 (brainstorming, examples)
- **Title generation:** 0.3 - 0.5 (balanced)
- **Summaries:** 0.1 - 0.2 (consistent, factual)

### Token Limits:
- **gpt-5-mini:** 128K context window
- **Max output tokens:** 4096 (default)
- **Typical RAG response:** 500-1500 tokens

### Prompt Engineering:
- Always include system prompt with role definition
- Use few-shot examples for complex tasks
- Request structured output (JSON) when needed
- Add "think step-by-step" for reasoning

---

## 📊 Monitoring & Analytics

**Track These Metrics:**
- Average tokens per query (input + output)
- Response quality (user feedback)
- Latency (time to first token)
- Cost per query
- Error rate (API failures)

**Alerting Thresholds:**
- Cost > $100/day → Investigate
- Latency > 5s → Check API status
- Error rate > 5% → Switch to fallback

---

## 🔒 API Key Management

**Environment Variables:**
```bash
OPENAI_API_KEY=sk-...  # Never commit this!
```

**Security:**
- ✅ Stored in `.env` (gitignored)
- ✅ Separate keys for dev/staging/prod
- ✅ Rate limiting enabled (see `accounts/ratelimit_decorators.py`)
- ✅ Monthly spending limits set in OpenAI dashboard

---

## 📚 References

- [OpenAI GPT-5 Documentation](https://platform.openai.com/docs/models/gpt-5-mini)
- [GPT-5 Announcement](https://openai.com/index/introducing-gpt-5/)
- [Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Pricing Calculator](https://openai.com/pricing)

---

## ✅ Critical Reminder

**ALWAYS UPDATE THIS FILE WHEN CHANGING MODELS**

This ensures:
- Future developers know current config
- Cost estimations stay accurate
- Migration path is documented
- No accidental model downgrades

---

**Last Model Change:** 2025-11-02 - Migrated from gpt-4o-mini to gpt-5-mini
**Next Review:** 2025-12-01 - Check for GPT-5 full model viability
**Owner:** @LaVanguard
