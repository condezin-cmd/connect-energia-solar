#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html as html_mod
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEPLOY_META_START = "<!-- DEPLOY META START -->"
DEPLOY_META_END = "<!-- DEPLOY META END -->"
DEPLOY_BODY_START = "<!-- DEPLOY BODY START -->"
DEPLOY_BODY_END = "<!-- DEPLOY BODY END -->"
DEFAULT_GA4_ID = "G-BSNY8GMP9G"
SOCIAL_IMAGE_PATH = "assets/images/solar-hero-rooftop.png"

ROOT_FILES = [
    "index.html",
    "blog.html",
    "styles.css",
    "script.js",
    "logo-connect-solar.svg",
    "logo-connect-solar-brand.svg",
    "logo-connect-solar-core.svg",
    "logo-connect-solar-stacked.svg",
    "logo-connect.png",
    "googlef56e1f346320f363.html",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a deployable static package.")
    parser.add_argument("--site-url", required=True, help="Public site URL, e.g. https://solar.exemplo.com.br")
    parser.add_argument("--out-dir", default="dist", help="Output directory")
    parser.add_argument("--ga4-id", default=os.environ.get("GA4_ID", DEFAULT_GA4_ID).strip())
    parser.add_argument("--gtm-id", default=os.environ.get("GTM_ID", "").strip())
    parser.add_argument("--gsc-token", default=os.environ.get("GSC_TOKEN", "").strip())
    return parser.parse_args()


def copy_static_files(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    for filename in ROOT_FILES:
      source = ROOT / filename
      if source.exists():
        shutil.copy2(source, out_dir / filename)

    assets_source = ROOT / "assets"
    if assets_source.exists():
        shutil.copytree(assets_source, out_dir / "assets", dirs_exist_ok=True)


def strip_managed_block(content: str, start_marker: str, end_marker: str) -> str:
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        flags=re.DOTALL,
    )
    return re.sub(pattern, "", content)


def strip_static_deploy_head(content: str) -> str:
    """Remove source-only meta blocks before writing the deploy package."""
    patterns = [
        r"\n\s*<!-- Google tag \(gtag\.js\) -->\s*"
        r"<script async src=\"https://www\.googletagmanager\.com/gtag/js\?id=[^\"]+\"></script>\s*"
        r"<script>.*?</script>\s*",
        r"\n\s*<!-- Open Graph / redes sociais -->.*?(?=\n\s*<!-- Dados estruturados|\n\s*<link rel=\"stylesheet\")",
        r"\n\s*<!-- Dados estruturados.*?-->\s*<script type=\"application/ld\+json\">.*?</script>\s*",
    ]

    for pattern in patterns:
        content = re.sub(pattern, "\n", content, flags=re.DOTALL | re.IGNORECASE)

    return content


def extract_title(content: str) -> str:
    match = re.search(r"<title>(.*?)</title>", content, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else "Connect Energia Solar Curitiba"


def extract_description(content: str) -> str:
    match = re.search(
        r'<meta\s+name="description"\s+content="(.*?)"\s*/?>',
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return match.group(1).strip() if match else ""


def clean_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/")
    if path in ("", "/"):
        return f"{base}/"
    return f"{base}/{path.lstrip('/')}"


def extract_faq_items(content: str) -> list[dict[str, str]]:
    """Extract FAQ question/answer pairs from <details> elements."""
    items: list[dict[str, str]] = []
    pattern = re.compile(
        r'<details\s+class="faq-item[^"]*"[^>]*>\s*'
        r'<summary>(.*?)</summary>\s*'
        r'<p>\s*(.*?)\s*</p>\s*'
        r'</details>',
        flags=re.DOTALL | re.IGNORECASE,
    )
    for match in pattern.finditer(content):
        question = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        answer = re.sub(r'<[^>]+>', '', match.group(2)).strip()
        answer = re.sub(r'\s+', ' ', answer)
        if question and answer:
            items.append({"question": question, "answer": html_mod.unescape(answer)})
    return items


def build_structured_data(page_type: str, page_url: str, title: str, description: str, site_url: str, faq_items: list[dict[str, str]] | None = None) -> str:
    """Build all structured data blocks for the page."""
    blocks: list[dict[str, object]] = []

    if page_type == "blog":
        blocks.append({
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": title,
            "description": description,
            "url": page_url,
            "isPartOf": {
                "@type": "WebSite",
                "name": "Connect Energia Solar Curitiba",
                "url": clean_url(site_url, "/"),
            },
        })
        # BreadcrumbList for blog
        blocks.append({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": clean_url(site_url, "/"),
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Blog",
                    "item": page_url,
                },
            ],
        })
    else:
        # WebSite
        blocks.append({
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Connect Energia Solar Curitiba",
            "description": description,
            "url": page_url,
            "sameAs": ["https://instagram.com/connectenergiasolarcuritiba"],
        })

        # LocalBusiness (full)
        blocks.append({
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "@id": f"{clean_url(site_url, '/')}#organization",
            "name": "Connect Energia Solar Curitiba",
            "alternateName": "Connect Energia Solar",
            "description": "Orçamentos e projetos de energia solar para casas, empresas e propriedades rurais no Paraná e em Santa Catarina. Visita técnica presencial, marcas como BYD, WEG, BelEnergy e JNG, e acompanhamento do orçamento à homologação.",
            "url": clean_url(site_url, "/"),
            "telephone": "+5541998641771",
            "image": clean_url(site_url, SOCIAL_IMAGE_PATH),
            "logo": clean_url(site_url, "logo-connect-solar-brand.svg"),
            "priceRange": "$$",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Curitiba",
                "addressRegion": "PR",
                "postalCode": "80000-000",
                "addressCountry": "BR",
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": -25.4284,
                "longitude": -49.2733,
            },
            "areaServed": [
                {"@type": "State", "name": "Paraná"},
                {"@type": "State", "name": "Santa Catarina"},
            ],
            "openingHoursSpecification": {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "08:00",
                "closes": "18:00",
            },
            "knowsAbout": ["energia solar", "painel solar", "sistema fotovoltaico", "energia solar residencial", "energia solar comercial", "energia solar rural"],
            "hasOfferCatalog": {
                "@type": "OfferCatalog",
                "name": "Serviços de Energia Solar",
                "itemListElement": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Energia Solar Residencial", "description": "Projeto e instalação de sistema fotovoltaico para residências."}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Energia Solar Comercial", "description": "Projeto e instalação de sistema fotovoltaico para empresas e comércios."}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Energia Solar Rural", "description": "Projeto e instalação de sistema fotovoltaico para propriedades rurais."}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Energia Solar Industrial", "description": "Projeto e instalação de sistema fotovoltaico para pequenas indústrias."}},
                ],
            },
            "sameAs": ["https://instagram.com/connectenergiasolarcuritiba"],
        })

        # FAQPage (if FAQ items found)
        if faq_items:
            blocks.append({
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": item["question"],
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": item["answer"],
                        },
                    }
                    for item in faq_items
                ],
            })

    return "\n".join(
        json.dumps(block, ensure_ascii=False, indent=2) for block in blocks
    )


def build_meta_block(
    *,
    page_url: str,
    page_type: str,
    title: str,
    description: str,
    gsc_token: str,
    ga4_id: str,
    gtm_id: str,
    image_url: str,
    site_url: str,
    faq_items: list[dict[str, str]] | None = None,
) -> str:
    tags = [
        DEPLOY_META_START,
        f'<link rel="canonical" href="{page_url}" />',
        '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />',
        '<meta name="googlebot" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1" />',
        f'<meta property="og:url" content="{page_url}" />',
        f'<meta property="og:type" content="{"website" if page_type == "home" else "article"}" />',
        f'<meta property="og:title" content="{title}" />',
        f'<meta property="og:description" content="{description}" />',
        f'<meta property="og:image" content="{image_url}" />',
        '<meta property="og:image:alt" content="Sistema de energia solar instalado em telhado residencial" />',
        '<meta property="og:image:width" content="1672" />',
        '<meta property="og:image:height" content="941" />',
        '<meta property="og:locale" content="pt_BR" />',
        '<meta property="og:site_name" content="Connect Energia Solar Curitiba" />',
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{title}" />',
        f'<meta name="twitter:description" content="{description}" />',
        f'<meta name="twitter:image" content="{image_url}" />',
        # Geo meta tags for local SEO
        '<meta name="geo.region" content="BR-PR" />',
        '<meta name="geo.placename" content="Curitiba" />',
        '<meta name="geo.position" content="-25.4284;-49.2733" />',
        '<meta name="ICBM" content="-25.4284, -49.2733" />',
    ]

    if gsc_token:
        tags.append(f'<meta name="google-site-verification" content="{gsc_token}" />')

    tags.append('<meta name="format-detection" content="telephone=no" />')
    tags.append('<link rel="manifest" href="site.webmanifest" />')

    # Structured data — may contain multiple JSON-LD blocks separated by newline
    sd_json = build_structured_data(page_type, page_url, title, description, site_url, faq_items)
    for block in sd_json.split('\n{\n  "@context'):  # split on block boundary
        block_text = block if block.startswith('{') else '{\n  "@context' + block
        tags.append(
            '<script type="application/ld+json">\n'
            f"{block_text}\n"
            "</script>"
        )

    if gtm_id:
        tags.append(
            "<script>\n"
            "(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':\n"
            "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],\n"
            "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=\n"
            "'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);\n"
            f"}})(window,document,'script','dataLayer','{gtm_id}');\n"
            "</script>"
        )
    elif ga4_id:
        tags.append(f'<script async src="https://www.googletagmanager.com/gtag/js?id={ga4_id}"></script>')
        tags.append(
            "<script>\n"
            "window.dataLayer = window.dataLayer || [];\n"
            "function gtag(){dataLayer.push(arguments);}\n"
            "gtag('js', new Date());\n"
            f"gtag('config', '{ga4_id}');\n"
            "</script>"
        )

    tags.append(DEPLOY_META_END)
    return "\n    ".join(tags)


def build_body_block(gtm_id: str) -> str:
    if not gtm_id:
        return ""

    return (
        DEPLOY_BODY_START
        + "\n    "
        + f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm_id}" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>'
        + "\n    "
        + DEPLOY_BODY_END
    )


def process_html(source_path: Path, out_path: Path, site_url: str, page_path: str, page_type: str, args: argparse.Namespace) -> None:
    content = source_path.read_text(encoding="utf-8")
    content = strip_managed_block(content, DEPLOY_META_START, DEPLOY_META_END)
    content = strip_managed_block(content, DEPLOY_BODY_START, DEPLOY_BODY_END)
    content = strip_static_deploy_head(content)

    title = extract_title(content)
    description = extract_description(content)
    page_url = clean_url(site_url, page_path)
    image_url = clean_url(site_url, SOCIAL_IMAGE_PATH)

    # Extract FAQ items for rich results
    faq_items = extract_faq_items(content) if page_type == "home" else None

    meta_block = build_meta_block(
        page_url=page_url,
        page_type=page_type,
        title=title,
        description=description,
        gsc_token=args.gsc_token,
        ga4_id=args.ga4_id,
        gtm_id=args.gtm_id,
        image_url=image_url,
        site_url=site_url,
        faq_items=faq_items,
    )
    content = content.replace("</head>", f"    {meta_block}\n  </head>", 1)

    body_block = build_body_block(args.gtm_id)
    if body_block:
        content = content.replace("<body>", f"<body>\n    {body_block}", 1)

    out_path.write_text(content, encoding="utf-8")


def write_robots(out_dir: Path, site_url: str) -> None:
    content = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {clean_url(site_url, '/sitemap.xml')}\n"
    )
    (out_dir / "robots.txt").write_text(content, encoding="utf-8")


def write_sitemap(out_dir: Path, site_url: str) -> None:
    urls = [
        clean_url(site_url, "/"),
        clean_url(site_url, "/blog.html"),
    ]
    lastmod = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    items = "\n".join(
        [
            "  <url>\n"
            f"    <loc>{url}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            "  </url>"
            for url in urls
        ]
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{items}\n"
        "</urlset>\n"
    )
    (out_dir / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def write_manifest(out_dir: Path) -> None:
    manifest = {
        "name": "Connect Energia Solar Curitiba",
        "short_name": "Connect Solar",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#fffdfb",
        "theme_color": "#ff6f1f",
        "icons": [
            {
                "src": "logo-connect.png",
                "sizes": "512x512",
                "type": "image/png",
            }
        ],
    }
    (out_dir / "site.webmanifest").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_404(out_dir: Path, site_url: str) -> None:
    page = f"""<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Página não encontrada | Connect Energia Solar Curitiba</title>
    <meta http-equiv="refresh" content="6;url={clean_url(site_url, '/')}" />
    <style>
      body {{
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        font-family: Manrope, Arial, sans-serif;
        background: linear-gradient(180deg, #fffdfb, #fff7ef);
        color: #1e2939;
      }}
      main {{
        width: min(92vw, 560px);
        padding: 36px;
        border-radius: 24px;
        background: #ffffff;
        border: 1px solid rgba(255, 111, 31, 0.14);
        box-shadow: 0 18px 42px rgba(176, 108, 56, 0.12);
      }}
      a {{
        color: #f76712;
        font-weight: 800;
        text-decoration: none;
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>Página não encontrada</h1>
      <p>Voltando para a home da Connect Energia Solar Curitiba.</p>
      <p><a href="{clean_url(site_url, '/')}">Ir para a página inicial</a></p>
    </main>
  </body>
</html>
"""
    (out_dir / "404.html").write_text(page, encoding="utf-8")


def main() -> None:
    args = parse_args()
    site_url = args.site_url.strip()
    out_dir = (ROOT / args.out_dir).resolve()

    if out_dir.exists():
        shutil.rmtree(out_dir)

    copy_static_files(out_dir)
    process_html(ROOT / "index.html", out_dir / "index.html", site_url, "/", "home", args)
    process_html(ROOT / "blog.html", out_dir / "blog.html", site_url, "/blog.html", "blog", args)
    write_robots(out_dir, site_url)
    write_sitemap(out_dir, site_url)
    write_manifest(out_dir)
    write_404(out_dir, site_url)

    print(f"Deploy package ready at: {out_dir}")


if __name__ == "__main__":
    main()
