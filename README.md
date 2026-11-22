# Marginalia

Essays related to computer science by [tavro.se](https://tavro.se).

## Build

Python 3 standard library only, no dependencies.

```
python3 build.py
cd site && python3 -m http.server 8000
```

Then open http://localhost:8000/.

- `src/essays/<slug>.html`: one essay per file, a `key: value` header between `---` lines, then body HTML, then `=== sources ===`.
- `static/`: stylesheet, script, fonts and icons, copied into `site/` as is.
- `build.py`: writes the static site to `site/`.
- `tools/make_icons.py`: regenerates the icons in `static/icons/`.

## Deploy

Every push to `main` builds the site and publishes it to GitHub Pages through `.github/workflows/pages.yml`.

## Fonts

EB Garamond and UnifrakturMaguntia are under the SIL Open Font License 1.1.
