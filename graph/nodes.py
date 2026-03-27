from graph.state import AppState
from services.llm import safe_invoke


# ─── Router Node ───────────────────────────────────────────
def router(state: AppState):
    """Pass-through node; routing is handled by conditional edges."""
    return state


# ─── Idea Generator ────────────────────────────────────────
def generate_ideas(state: AppState):
    prompt = f"""
You are a YouTube content strategist.

Generate 10 viral YouTube video ideas for this niche:
{state['user_input']}

Rules:
- Make each idea engaging and clickable
- Include a mix of trending and evergreen topics
- Number each idea

Return only the numbered list.
"""
    result = safe_invoke(prompt)
    return {"response": result.content}


# ─── Title Generator ───────────────────────────────────────
def generate_titles(state: AppState):
    prompt = f"""
You are a YouTube title optimization expert.

Generate 10 highly clickable YouTube titles for:
{state['user_input']}

Rules:
- Use power words and emotional triggers
- Keep under 60 characters each
- Mix curiosity gaps, numbers, and urgency
- Number each title

Return only the numbered list.
"""
    result = safe_invoke(prompt)
    return {"response": result.content}


# ─── Script Generator ──────────────────────────────────────
def generate_script(state: AppState):
    prompt = f"""
You are a professional YouTube scriptwriter.

Write a complete YouTube video script for:
{state['user_input']}

Structure it exactly like this:

🎣 HOOK (first 5 seconds):
[Attention-grabbing opening line]

📢 INTRO (15-30 seconds):
[Brief context + what the viewer will learn]

📝 MAIN CONTENT:
[Detailed, engaging content with key points]

🎬 OUTRO (CTA):
[Call to action: like, subscribe, comment]

Make it conversational, engaging, and informative.
"""
    result = safe_invoke(prompt)
    return {"response": result.content}


# ─── SEO Generator ─────────────────────────────────────────
def generate_seo(state: AppState):
    prompt = f"""
You are a YouTube SEO specialist.

Generate complete YouTube SEO data for:
{state['user_input']}

Provide the following:

📌 TAGS (15-20 relevant tags):
[comma-separated tags]

📝 DESCRIPTION (SEO-optimized, 150-200 words):
[Engaging description with keywords and links placeholder]

🔑 KEYWORDS (10 primary keywords):
[comma-separated keywords]

📊 HASHTAGS (5-8 relevant hashtags):
[hashtags for the video]
"""
    result = safe_invoke(prompt)
    return {"response": result.content}
