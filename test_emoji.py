from lingualens_core import predict_sentiment

tests = [
    "My first crush arvind🤍",                      # raw emoji
    "My first crush arvind white heart",            # emoji as words
    "My first crush arvind",                        # no emoji
    "💯 suppar my song",
    "hundred points suppar my song",
    "suppar my song",
    "🤍🤍🤍",
    "white heart",
]
for t in tests:
    r = predict_sentiment(t)
    r = r[0] if isinstance(r, list) else r
    print(f"{t!r:45} -> {r['label']:9} {r['scores']}")