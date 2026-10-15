from lingualens_core import predict_sentiment

tests = [
    ("Super movie da, semma mass!", "Positive"),
    ("Romba worst padam, waste of money", "Negative"),
    ("Yeh movie bahut achi thi, loved it", "Positive"),
    ("Bakwaas film, time barbaad", "Negative"),
    ("Kollam nalla padam, ishtapettu", "Positive"),
    ("Nalla illa, bore adichu", "Negative"),
]
for text, expected in tests:
    r = predict_sentiment(text)[0]
    print(f"{expected:9} -> {r['label']:9} {r['scores']}  | {text}")