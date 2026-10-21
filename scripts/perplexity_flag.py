#!/usr/bin/env python3
"""perplexity_flag: rank a document's sentences by how predictable they are to GPT-2 (local, no upload).

Low perplexity = the sentence is what a language model would have written next. A flag, never a
verdict: detectors false-positive on dense formal prose, so the output is a rewrite list for a human,
not a gate on its own. Pairs with `slop_lint.py --structural` (banked 2026-10-21).

Runs from an isolated venv (deps: torch, transformers; model gpt2, ~500MB, cached locally):
  ~/.local/share/arcs-detector-venv/bin/python scripts/perplexity_flag.py <file.txt|.html> [--top 8]
"""
import math, re, sys

def sentences(text):
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>|&[a-zA-Z#0-9]+;", " ", text)
    parts = re.split(r"(?<=[.!?])\s+|\n\s*[•\-]\s+", text)
    return [re.sub(r"\s+", " ", p).strip() for p in parts if len(p.split()) >= 8]

def main(argv):
    top = int(argv[argv.index("--top") + 1]) if "--top" in argv else 8
    path = [a for a in argv if not a.startswith("--") and not a.isdigit()][0]
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained("gpt2"); model = AutoModelForCausalLM.from_pretrained("gpt2").eval()
    scored = []
    for s in sentences(open(path, encoding="utf-8", errors="replace").read()):
        ids = tok(s, return_tensors="pt").input_ids[:, :512]
        with torch.no_grad():
            loss = model(ids, labels=ids).loss.item()
        scored.append((math.exp(loss), s))
    if not scored:
        print("no sentences"); return 0
    ppl = sorted(p for p, _ in scored)
    print(f"{path}: {len(scored)} sentences, median perplexity {ppl[len(ppl)//2]:.0f} (lower = more machine-predictable)")
    for p, s in sorted(scored)[:top]:
        print(f"  {p:7.0f}  {s[:140]}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
