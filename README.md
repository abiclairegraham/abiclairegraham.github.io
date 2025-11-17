# abiclairegraham.github.io
My personal website. Here's how this repository is laid out:

## Repository Structure

```text
abiclairegraham.github.io/
├── index.html
├── styles.css
├── README.md
│
├── assets/
│   └── images/
│       ├── origami/
│       │   ├── insects/
│       │   ├── animals/
│       │   ├── tessellations/
│       │   ├── curved/
│       │   ├── modular/
│       │   └── general/
│       │
│       ├── powerlifting/
│       │   ├── 2020/
│       │   ├── 2021/
│       │   ├── 2022/
│       │   ├── 2023/
│       │   └── ...
│       │
│       ├── makeup/
│       ├── singing/
│       ├── activism/
│       └── general/
│
├── origami/
│   ├── index.html              # auto-generated gallery
│   └── posts/
│       └── <slug>.html         # auto-generated post pages
│
├── powerlifting/
│   ├── index.html
│   └── posts/
│       └── <slug>.html
│
├── makeup/
│   ├── index.html
│   └── posts/
│       └── <slug>.html
│
├── singing/
│   └── (future)
│
├── data-projects/
│   └── (future)
│
├── blog/
│   ├── index.html              # auto-generated blog homepage
│   └── posts/
│       └── <slug>.html         # blog articles
│
├── templates/
│   ├── origami_template.html
│   ├── powerlifting_template.html
│   ├── makeup_template.html
│   ├── blog_post_template.html
│   └── ...
│
└── scripts/
    ├── build_common.py         # shared config + helpers
    ├── build_origami_page.py
    ├── build_powerlifting_page.py
    ├── build_makeup_page.py
    ├── build_origami_posts.py
    ├── build_blog_index.py
    └── (future builders)
```
