#!/usr/bin/env python3
"""Writes a simple, ready-to-post caption (feed or reel) to a temp file and
prints its path. No AI generation -- a small set of static templates in
GM Hamburgueria's established voice (see the Canva stories built for this
client: playful, informal, food-craving language, light emoji use), picked
at random so consecutive posts don't read identically. Swap this for an
AI-generated version later if the static set feels repetitive.

Usage: make_caption.py <feed|reel>
Prints: path to the temp file containing the caption.
"""
import random
import sys
import tempfile

FOOTER = (
    "\n\n📍 GM Hamburgueria Artesanal\n"
    "⏰ Delivery: todos os dias — das 11h às 01h\n"
    "👉 Peça já o seu!"
)

FEED_TEMPLATES = [
    "Óia que coisa mais linda! 🍔 Um prato caprichado, feito na hora, especialmente pra você.",
    "Reparou no capricho? Cada detalhe pensado pra você sentir o sabor de verdade.",
    "Sabor que não erra, do jeito que só a GM faz. Bora matar essa vontade?",
    "Aqui não tem meio-termo: é sabor de verdade, sempre fresquinho.",
]

REEL_TEMPLATES = [
    "Direto da chapa pra sua tela! 🔥 Vem ver o capricho que a GM coloca em cada pedido.",
    "Bastidores da GM: é assim que a gente prepara o seu favorito, com muito carinho.",
    "Água na boca só de ver! Passa aqui pra conferir de perto o que está saindo agora.",
]

TEMPLATES = {"feed": FEED_TEMPLATES, "reel": REEL_TEMPLATES}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in TEMPLATES:
        print("Uso: make_caption.py <feed|reel>", file=sys.stderr)
        raise SystemExit(1)
    kind = sys.argv[1]
    body = random.choice(TEMPLATES[kind])
    caption = body + FOOTER
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(caption)
        path = f.name
    print(path)


if __name__ == "__main__":
    main()
