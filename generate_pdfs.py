#!/usr/bin/env python3
import os, subprocess, glob, tempfile, shutil

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE   = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE, "pdf")
os.makedirs(PDF_DIR, exist_ok=True)

INJECT_STYLE = """
<style id="pdf-override">
/* ── Hide chrome, images, ALL icons ─── */
.site-nav, .nav-drawer, footer, .cta-band,
.hero-actions, .btn-primary, .btn-outline-light, .btn-mat,
.mat-card-cta, .breadcrumb-nav,
img, .mat-card-image, .hero-image-panel, .page-hero-bg, .hero-logo-stamp,
.why-card-icon, .about-owner-photo-icon, .about-value-icon,
.guide-rule-icon, .mat-prop-icon, .service-card-icon,
.industry-card-icon, svg { display: none !important; }

* { background-image: none !important; box-shadow: none !important; }

/* ── Force reveal elements visible ─── */
[data-reveal], [data-reveal="left"], [data-reveal="right"] {
  opacity: 1 !important; transform: none !important;
  transition: none !important;
}

/* ── Global: all text solid black, no backgrounds ─── */
* { color: #111 !important; background-color: transparent !important; }

/* ── White base ─── */
body, html {
  background: #fff !important;
  padding-top: 0 !important;
  font-size: 13px !important;
  line-height: 1.55 !important;
}

/* ── Compact sections ─── */
section, .mat-intro, .contact-card, .mat-specs-section,
.fournisseurs-section, .about-section, .guide-section,
.services-section, .industries-section, .why {
  padding-top: 28px !important;
  padding-bottom: 28px !important;
}

/* ── Tighten headings ─── */
h1 { font-size: 26px !important; margin-bottom: 10px !important; }
h2 { font-size: 20px !important; margin-bottom: 8px !important; }
h3 { font-size: 16px !important; margin-bottom: 6px !important; }
p  { margin-bottom: 8px !important; }

/* ── Keep green on accents ─── */
.section-eyebrow, .mat-badge { color: #2B5C3A !important; }
.accent { color: #2B5C3A !important; }

/* ── Hero band ─── */
.hero { min-height: 0 !important; display: block !important; }
.hero-content {
  background: #111814 !important;
  padding: 28px 40px !important;
}
.hero-content * { color: #fff !important; }
.hero-content .accent { color: #5aab78 !important; }

/* ── Page hero ─── */
.page-hero { background: #111814 !important; padding: 28px 40px !important; }
.page-hero * { color: #fff !important; }
.page-hero .accent { color: #5aab78 !important; }

/* ── Cards & grids: stack cleanly ─── */
.why-cards, .service-cards, .industries-grid,
.mat-grid, .mat-cards { display: block !important; }
.why-card, .service-card, .industry-card, .mat-card {
  margin-bottom: 12px !important;
  padding: 12px 16px !important;
  border: 1px solid #ccc !important;
  border-radius: 4px !important;
  page-break-inside: avoid !important;
}

/* ── Why inner: strip green bg ─── */
.why-inner {
  background: #fff !important;
  border: 1px solid #ccc !important;
  padding: 20px !important;
}
.why-headline { color: #111 !important; }

/* ── Forms ─── */
.form-input, .form-textarea, .form-select {
  border: 1px solid #bbb !important;
  color: #111 !important;
}
.form-label { font-weight: 600 !important; }

/* ── Tables ─── */
.mat-specs-table td, .mat-specs-table th {
  border: 1px solid #ccc !important;
  padding: 6px 10px !important;
}

/* ── Remove decorative gaps ─── */
.mat-divider, .section-divider, .hero-image-panel,
.about-owner-photo { display: none !important; }

section, .mat-intro { page-break-inside: avoid; }
a { text-decoration: none; }
</style>
"""

html_files = sorted(glob.glob(os.path.join(BASE, "*.html")))
tmp_dir = tempfile.mkdtemp()

try:
    for html_path in html_files:
        name = os.path.splitext(os.path.basename(html_path))[0]
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Inject before </head>
        if "</head>" in content:
            content = content.replace("</head>", INJECT_STYLE + "\n</head>", 1)
        else:
            content = INJECT_STYLE + content

        tmp_file = os.path.join(tmp_dir, f"{name}.html")
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write(content)

        out_pdf = os.path.join(PDF_DIR, f"{name}.pdf")

        # Retry up to 3 times for flaky pages
        for attempt in range(3):
            subprocess.run([
                CHROME,
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--print-to-pdf=" + out_pdf,
                "--no-pdf-header-footer",
                "file://" + tmp_file,
            ], capture_output=True)
            size = os.path.getsize(out_pdf) if os.path.exists(out_pdf) else 0
            if size > 10000:
                break

        size_kb = os.path.getsize(out_pdf) // 1024 if os.path.exists(out_pdf) else 0
        status = "OK" if size_kb > 10 else "TINY"
        print(f"{status:4s}  {name}.pdf  ({size_kb} KB)")
finally:
    shutil.rmtree(tmp_dir)

print("\nDone.")
