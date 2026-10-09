#!/usr/bin/env python3
"""Build the RECIPES list in app/cocktail-codex.html from data/recipes-*.txt,
and write the standalone index.html for GitHub Pages.

Run from the repo root:  python3 tools/build_recipes.py
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "app", "cocktail-codex.html")
GLASSES = {"coupe", "wine", "collins", "dof", "gibraltar", "shot", "bottle"}
START = "const RECIPES = ["
END = "];\n/* ====================== END OF RECIPES"


def parse(path):
    recipes, section, cur = [], "", None
    for n, raw in enumerate(open(path, encoding="utf-8"), 1):
        line = raw.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        tag, rest = line[0], line[1:].strip()
        if tag == "@":
            section = rest
        elif tag == "*":
            parts = [p.strip() for p in rest.split("|")]
            if len(parts) != 5:
                sys.exit(f"{path}:{n}: expected 5 fields in '{line}'")
            name, glass, method, ice, garnish = parts
            if glass not in GLASSES:
                sys.exit(f"{path}:{n}: unknown glass '{glass}'")
            cur = {"name": name, "section": section, "glass": glass, "method": method,
                   "ice": ice, "garnish": garnish, "ingredients": [], "steps": [],
                   "notes": [], "checks": [], "tips": []}
            recipes.append(cur)
        elif cur is None:
            sys.exit(f"{path}:{n}: line before first recipe")
        elif tag == "-":
            cur["ingredients"].append(rest)
        elif tag == ">":
            cur["steps"].append(rest)
        elif tag == "!":
            cur["notes"].append(rest)
        elif tag == "?":
            cur["checks"].append(rest)
        elif tag == "~":
            cur["tips"].append(rest)
        else:
            sys.exit(f"{path}:{n}: unknown line '{line}'")
    return recipes


def js(recipes):
    out = []
    for r in recipes:
        r = dict(r, notes="\n".join(r["notes"]))
        lines = ["  {"]
        for k, v in r.items():
            if isinstance(v, list):
                if not v:
                    lines.append(f"    {k}: [],")
                else:
                    lines.append(f"    {k}: [")
                    lines += [f"      {json.dumps(x, ensure_ascii=False)}," for x in v]
                    lines.append("    ],")
            else:
                lines.append(f"    {k}: {json.dumps(v, ensure_ascii=False)},")
        lines.append("  },")
        out.append("\n".join(lines))
    return "\n".join(out) + "\n"


def main():
    recipes = []
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "recipes-*.txt"))):
        recipes += parse(path)
    # Recipes that share a name are versions of one drink, to compare during
    # review. The first one found is version A and sets the section.
    groups = {}
    for r in recipes:
        groups.setdefault(r["name"].lower(), []).append(r)
    for g in groups.values():
        for i, r in enumerate(g):
            r["section"] = g[0]["section"]
            if len(g) > 1:
                r["version"] = "ABCDEFGHIJ"[i]

    html = open(HTML, encoding="utf-8").read()
    a = html.index(START) + len(START)
    b = html.index(END)
    html = html[:a] + "\n" + js(recipes) + html[b:]
    open(HTML, "w", encoding="utf-8").write(html)

    # Standalone copy for GitHub Pages (the Claude viewer adds this skeleton itself).
    site = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1,viewport-fit=cover\">\n"
            "<meta name=\"theme-color\" content=\"#111312\">\n"
            "<meta name=\"apple-mobile-web-app-capable\" content=\"yes\">\n"
            "<meta name=\"mobile-web-app-capable\" content=\"yes\">\n"
            "<meta name=\"apple-mobile-web-app-status-bar-style\" content=\"black\">\n"
            "<meta name=\"apple-mobile-web-app-title\" content=\"CT Codex\">\n"
            "<link rel=\"apple-touch-icon\" sizes=\"180x180\" href=\"apple-touch-icon.png\">\n"
            "<link rel=\"apple-touch-icon-precomposed\" sizes=\"180x180\" href=\"apple-touch-icon-precomposed.png\">\n"
            "<link rel=\"icon\" type=\"image/png\" sizes=\"192x192\" href=\"icon-192.png\">\n"
            "<link rel=\"manifest\" href=\"manifest.webmanifest\">\n"
            "<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}"
            "body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n"
            "</head>\n<body>\n" + html + "\n</body>\n</html>\n")
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(site)

    flagged = [r for r in recipes if r["checks"]]

    secs = {}
    for r in recipes:
        secs[r["section"]] = secs.get(r["section"], 0) + 1
    print(f"{len(recipes)} recipes, {len(flagged)} flagged")
    for s, c in secs.items():
        print(f"  {c:3d}  {s}")


if __name__ == "__main__":
    main()
