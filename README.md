# CT Codex

Cocktails for all feelings. A free cocktail spec book: flip cards with a sketched glass on the front and the full spec on the back, plus house prep and batch recipes.

Open it on a phone and add it to your home screen (Safari: Share → Add to Home Screen) to use it like an app.

## Editing recipes

The recipes live in plain text files in `data/` (`recipes-1-classics.txt` and so on), one block per drink:

```
* Paper Plane | coupe | Shaken | | 
- 3/4 oz Bourbon
- 3/4 oz Aperol
- 3/4 oz Amaro Nonino
- 3/4 oz Lemon juice
> Shake with ice and double strain into a chilled coupe.
! A note shown on the card
~ An optional tip, shown in italics under the method
```

Glasses: coupe, wine, collins, dof, gibraltar, shot, bottle (for prep and batches). After editing, run `python3 tools/build_recipes.py` to rebuild `index.html`.
