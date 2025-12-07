---
title: "Welcome — Cumstatística"
type: "home"
description: "Example Hugo homepage for cumstatistica.github.io"
slug: "/"
menu:
    main:
        identifier: home
        name: Home
        weight: 1
params:
    author: "Gonzalo"
    showHero: true
    heroImage: "images/hero.jpg"
---

Welcome to the Hugo example homepage for this site. This _index.md_ serves as the section (or home) page and demonstrates common front matter fields plus content sections.

<!--more-->

## Quick features

- Minimal front matter ready for a homepage
- Hugo shortcodes and internal links supported
- Summary (above) separated with <!--more-->

## Example usage

Run a local server to preview the site:

```bash
hugo server -D
```

Link to another section (use relref to keep links robust):

{{< relref "about/_index.md" >}}

## Content blocks

You can add image figures, code blocks, and shortcodes:

{{< figure src="/images/sample.png" alt="Sample" caption="A sample figure" >}}

## Notes

- Set `draft: true` while developing.
- Use `params` for theme-specific options (author, hero image, etc.).
- _index.md_ is used for section/home pages; plain `index.md` would create a regular page.

---
Author: Gonzalo