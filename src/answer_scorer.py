from transformers import pipeline
import re

# ── Load NLP models ────────────────────────────────────────
print("Loading NLP models... (first time takes 2-3 mins)")

# Sentiment analysis — confidence detection
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

print("✅ NLP models loaded!")

# ── Weak vs strong words ───────────────────────────────────
WEAK_WORDS = [
    "maybe", "perhaps", "i think", "i guess",
    "sort of", "kind of", "not sure", "i don't know",
    "possibly", "might", "could be", "i feel like"
]

STRONG_WORDS = [
    "definitely", "certainly", "i am confident",
    "i have", "i did", "i achieved", "i led",
    "i built", "i created", "i solved", "successfully",
    "i demonstrated", "i improved", "i delivered"
]

# ── STAR method keywords ───────────────────────────────────
STAR_KEYWORDS = {
    "situation": ["when", "during", "at my", "in my", "while", "working at"],
    "task":      ["had to", "needed to", "responsible for", "my role", "tasked with"],
    "action":    ["i did", "i built", "i created", "i led", "i developed", "i implemented"],
    "result":    ["resulted in", "achieved", "improved", "increased", "reduced",
                  "successfully", "outcome was", "as a result"]
}


# ══════════════════════════════════════════════════════════
#  SCORING FUNCTIONS
# ══════════════════════════════════════════════════════════

def get_confidence_language_score(text):
    """
    Score based on word choice confidence
    Strong words = high score
    Weak words   = low score
    """
    text_lower = text.lower()
    score      = 50  # Start neutral

    weak_count   = sum(1 for w in WEAK_WORDS   if w in text_lower)
    strong_count = sum(1 for w in STRONG_WORDS if w in text_lower)

    score += strong_count * 10
    score -= weak_count   * 10

    return max(0, min(100, score)), weak_count, strong_count


def get_star_score(text):
    """
    Check if answer follows STAR structure
    Returns score and which components are present
    """
    text_lower  = text.lower()
    found_parts = {}

    for part, keywords in STAR_KEYWORDS.items():
        found = any(kw in text_lower for kw in keywords)
        found_parts[part] = found

    # Score based on how many STAR parts are present
    parts_count = sum(found_parts.values())
    score       = (parts_count / 4) * 100

    return round(score), found_parts


def get_clarity_score(text):
    """
    Score based on answer clarity
    - Good length (not too short, not too long)
    - Clear sentences
    - Not too many filler words
    """
    words     = text.split()
    sentences = text.split('.')
    score     = 100

    # Penalize too short answers
    if len(words) < 20:
        score -= 30

    # Penalize too long answers (rambling)
    if len(words) > 200:
        score -= 20

    # Reward good length
    if 50 <= len(words) <= 150:
        score += 10

    return max(0, min(100, score)), len(words)


def get_sentiment_score(text):
    """
    Use HuggingFace to detect overall sentiment
    Positive sentiment = confident answer
    """
    try:
        result = sentiment_analyzer(text[:512])[0]
        if result['label'] == 'POSITIVE':
            return round(result['score'] * 100), "Positive"
        else:
            return round((1 - result['score']) * 100), "Negative"
    except:
        return 50, "Neutral"


def get_overall_answer_score(confidence_score, star_score,
                              clarity_score, sentiment_score):
    """
    Weighted combination of all scores
    """
    score = (
        confidence_score * 0.30 +
        star_score       * 0.30 +
        clarity_score    * 0.25 +
        sentiment_score  * 0.15
    )
    return round(score)


def get_answer_feedback(confidence_score, star_score,
                         clarity_score, weak_count,
                         strong_count, found_parts, word_count):
    """Generate personalized feedback"""
    feedback = []

    # Confidence feedback
    if weak_count > 2:
        feedback.append("❌ Too many weak words — replace 'I think/maybe' with 'I did/I achieved'")
    elif strong_count > 2:
        feedback.append("✅ Good use of confident language")

    # STAR feedback
    missing = [p for p, found in found_parts.items() if not found]
    if missing:
        feedback.append(f"⚠️  Missing STAR components: {', '.join(missing).upper()}")
    else:
        feedback.append("✅ Good answer structure — covers all STAR components")

    # Clarity feedback
    if word_count < 20:
        feedback.append("❌ Answer too short — elaborate more")
    elif word_count > 200:
        feedback.append("⚠️  Answer too long — be more concise")
    else:
        feedback.append("✅ Good answer length")

    # Score based suggestion
    return feedback


def analyze_answer(question, answer):
    """Full answer analysis"""
    print("\n" + "="*50)
    print(f"❓ QUESTION: {question}")
    print(f"💬 ANSWER:   {answer}")
    print("="*50)

    confidence_score, weak_count, strong_count = get_confidence_language_score(answer)
    star_score, found_parts                    = get_star_score(answer)
    clarity_score, word_count                  = get_clarity_score(answer)
    sentiment_score, sentiment_label           = get_sentiment_score(answer)
    overall_score                              = get_overall_answer_score(
        confidence_score, star_score, clarity_score, sentiment_score
    )

    feedback = get_answer_feedback(
        confidence_score, star_score, clarity_score,
        weak_count, strong_count, found_parts, word_count
    )

    print(f"\n📊 SCORES:")
    print(f"   Confidence Language: {confidence_score}/100")
    print(f"   STAR Structure:      {star_score}/100")
    print(f"   Clarity:             {clarity_score}/100")
    print(f"   Sentiment:           {sentiment_score}/100 ({sentiment_label})")
    print(f"\n🎯 OVERALL ANSWER SCORE: {overall_score}/100")

    print(f"\n💡 FEEDBACK:")
    for f in feedback:
        print(f"   {f}")

    print(f"\n📋 STAR BREAKDOWN:")
    for part, found in found_parts.items():
        status = "✅" if found else "❌"
        print(f"   {status} {part.upper()}")

    print("="*50)

    return {
        "question":          question,
        "answer":            answer,
        "confidence_score":  confidence_score,
        "star_score":        star_score,
        "clarity_score":     clarity_score,
        "sentiment_score":   sentiment_score,
        "overall_score":     overall_score,
        "feedback":          feedback
    }


# ── Main — test it ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n🎯 PrepSense Answer Quality Scorer")
    print("="*50)

    # Test with sample interview answers
    test_cases = [
        {
            "question": "Tell me about a challenge you faced",
            "answer": "I think maybe I had some issues with a project once. I sort of tried to fix it but I'm not sure if it worked out well."
        },
        {
            "question": "Tell me about a challenge you faced",
            "answer": "During my second year project, I was responsible for building the backend API. I had to solve a critical performance issue where the system was processing requests too slowly. I implemented caching and optimized the database queries, which resulted in a 60% improvement in response time and successfully delivered the project on time."
        }
    ]

    for case in test_cases:
        result = analyze_answer(case["question"], case["answer"])
        print()