"""Spike 002: three style directions for the landing page, built from the same content.

Writes option-a.html (Terminal Paper), option-b.html (Hardware Console) and option-c.html
(Blueprint Sketchbook) next to this file. Content and copy are the current landing page's; only
the style differs. Run from the repository root: python3 docs/spikes/002-landing-style/build.py
"""
from __future__ import annotations

import html
from pathlib import Path

HERE = Path(__file__).resolve().parent
UP = '../../../'  # from this folder to the repository root

TITLE = 'Medet.ink - HTML Pentest Report Template'
HEADLINE = 'Beautiful HTML Cybersecurity Presentations and Reports'
LEAD = ('A highly professional, easily modifiable deliverable format designed for cybersecurity '
        'consultancies, internal red teams, and enterprise security professionals. Prints to a perfect '
        'pixel 11x8.5 landscape PDF.')
GALLERY_NOTE = 'Click any preview below to load the actual interactive HTML slide. All 16 slides are included.'
SLIDES = [
    ('01', 'Cover Page', '01-Slide-Cover.html'),
    ('02', 'Table of Contents', '02-Slide-Table-of-Content.html'),
    ('03', 'Executive Summary', '03-Slide-Executive-Summary.html'),
    ('04', 'Cybersecurity Maturity', '04-Slide-Cybersecurity-Maturity.html'),
    ('05', 'Scope', '05-Slide-Scope.html'),
    ('06', 'Risk Matrix', '06-Slide-Risk-Matrix.html'),
    ('07', 'Testing Phases', '07-Slide-Testing-Phases.html'),
    ('08', 'Findings Overview', '08-Slide-Findings-Overview.html'),
    ('09', 'Technical Details', '09-Slide-Technical-Details.html'),
    ('10', 'Proof of Concept', '10-Slide-Proof-of-Concept.html'),
    ('11', 'The Team', '11-Slide-Team.html'),
    ('12', 'Capability Statement', '12-Slide-Capability-Statement.html'),
    ('13', 'Vulnerabilities Overview', '13-Slide-Vulnerabilities-Overview.html'),
    ('14', 'Exploitability Overview', '14-Slide-Exploitability-Overview.html'),
    ('15', 'Appendix A', '15-Slide-Appendix-A.html'),
    ('16', 'Company Overview', '16-Slide-Company-Overview.html'),
]
FEATURES = [
    ('Executive-Ready', 'Communicates complex findings effectively to both technical stakeholders and executive leadership.'),
    ('Pixel-Perfect PDF', 'Rigorous @media print CSS ensures a 1:1 translation from the browser to a paginated landscape PDF.'),
    ('Zero-Friction', 'Pure HTML/CSS architecture requires no complex build pipelines or proprietary software.'),
    ('Teams & Zoom Ready', 'The 11x8.5 aspect ratio naturally fits 16:9 widescreen formats perfectly, making it ideal for digital screen sharing.'),
]
FOOTER = '&copy; 2026 Manteiga Foundation. Released under the MIT License.'
REPORT, PDF, GITHUB, MANTEIGA = (UP + 'reports/combined_report.html', UP + 'reports/final_report.pdf',
                                 'https://github.com/manteiga-foundation/medet.ink', 'https://manteiga.org')
e = lambda s: html.escape(s, quote=False)


def page(fonts: str, css: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{TITLE}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?{fonts}&display=swap" rel="stylesheet">
    <style>
{css}
    </style>
</head>
<body>
{body}
</body>
</html>
"""


# ---------------------------------------------------------------- A. Terminal Paper
A_CSS = """
:root {
    --paper: #F2EFE6; --paper-deep: #E8E3D5; --ink: #2B2B2B; --ink-soft: #5B5850; --grid: rgba(43, 43, 43, 0.055);
    --sage: #8FB3A8; --peach: #D9A877; --lavender: #A99BC2; --led: #3E9B4F;
    --shadow: 4px 4px 0 var(--ink); --head: 'Space Grotesk', sans-serif; --mono: 'IBM Plex Mono', monospace;
}
* { box-sizing: border-box; }
html { background: var(--paper); }
body {
    margin: 0; color: var(--ink); font-family: var(--head); font-size: 16px; line-height: 1.6;
    background-image: linear-gradient(var(--grid) 1px, transparent 1px), linear-gradient(90deg, var(--grid) 1px, transparent 1px);
    background-size: 24px 24px;
}
a { color: inherit; }
:focus-visible { outline: 3px solid var(--lavender); outline-offset: 3px; }
.wrap { max-width: 1240px; margin: 0 auto; padding: 0 32px; }
.mono { font-family: var(--mono); }

/* Slim navigation band with status read-outs */
.band { border-bottom: 2px solid var(--ink); background: var(--paper); position: sticky; top: 0; z-index: 10; }
.band .wrap { display: flex; align-items: center; gap: 28px; height: 52px; font-family: var(--mono); font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; }
.wordmark { font-weight: 600; font-size: 14px; letter-spacing: 0.12em; text-decoration: none; }
.band .by { color: var(--ink-soft); text-decoration: none; }
.band .by:hover, .band nav a:hover { text-decoration: underline; text-underline-offset: 4px; }
.status { display: flex; gap: 18px; margin-left: auto; color: var(--ink-soft); }
.status span { display: inline-flex; align-items: center; gap: 7px; }
.led { width: 8px; height: 8px; border-radius: 50%; background: var(--led); box-shadow: 0 0 0 2px rgba(62, 155, 79, 0.2); }
.band nav a { text-decoration: none; font-weight: 600; }

/* Hero */
.hero { padding: 72px 0 88px; }
.hero .wrap { display: grid; grid-template-columns: 1fr 1.05fr; gap: 64px; align-items: center; }
.label { font-family: var(--mono); font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-soft); }
.label b { color: var(--ink); font-weight: 600; }
h1 { font-size: clamp(38px, 4.6vw, 60px); line-height: 1.02; letter-spacing: -0.02em; text-transform: uppercase; margin: 18px 0 22px; font-weight: 700; text-wrap: balance; }
.lead { font-size: 18px; color: var(--ink-soft); max-width: 34em; margin: 0 0 34px; }
.actions { display: flex; flex-wrap: wrap; gap: 14px; }
.btn {
    display: inline-flex; align-items: center; min-height: 48px; padding: 0 22px; border: 2px solid var(--ink);
    box-shadow: var(--shadow); font-family: var(--mono); font-weight: 600; font-size: 13px; letter-spacing: 0.08em;
    text-transform: uppercase; text-decoration: none; background: var(--paper); transition: transform 0.12s, box-shadow 0.12s;
}
.btn:hover { transform: translate(-2px, -2px); box-shadow: 6px 6px 0 var(--ink); }
.btn:active { transform: translate(2px, 2px); box-shadow: 1px 1px 0 var(--ink); }
.btn.primary { background: var(--sage); }
.btn.secondary { background: var(--peach); }
.window { border: 2px solid var(--ink); box-shadow: 8px 8px 0 var(--ink); background: #FFFFFF; }
.window .bar { display: flex; align-items: center; gap: 8px; height: 34px; padding: 0 12px; border-bottom: 2px solid var(--ink); background: var(--paper-deep); font-family: var(--mono); font-size: 12px; }
.window .bar i { width: 11px; height: 11px; border: 2px solid var(--ink); display: inline-block; }
.window .bar span { margin-left: auto; color: var(--ink-soft); letter-spacing: 0.06em; }
.window img { display: block; width: 100%; height: auto; }

/* Sections */
section { padding: 72px 0; border-top: 2px solid var(--ink); }
.section-head { display: grid; grid-template-columns: 220px 1fr; gap: 32px; align-items: baseline; margin-bottom: 40px; }
h2 { font-size: 34px; line-height: 1.1; text-transform: uppercase; letter-spacing: -0.01em; margin: 0; }
.section-head p { margin: 10px 0 0; color: var(--ink-soft); }

/* Gallery */
.gallery { display: grid; grid-template-columns: repeat(4, 1fr); gap: 26px; }
.card { display: block; border: 2px solid var(--ink); background: #FFFFFF; box-shadow: var(--shadow); text-decoration: none; transition: transform 0.12s, box-shadow 0.12s; }
.card:hover { transform: translate(-2px, -2px); box-shadow: 6px 6px 0 var(--ink); }
.card .shot { aspect-ratio: 11 / 8.5; overflow: hidden; border-bottom: 2px solid var(--ink); background: var(--paper-deep); }
.card img { width: 100%; height: 100%; object-fit: cover; display: block; }
.card .name { display: flex; gap: 10px; padding: 10px 12px; font-family: var(--mono); font-size: 12px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; }
.card .name b { color: var(--ink-soft); font-weight: 500; }

/* Spec sheet */
.spec { border: 2px solid var(--ink); background: var(--paper); }
.spec-row { display: grid; grid-template-columns: 90px 260px 1fr; gap: 24px; padding: 20px 24px; align-items: baseline; }
.spec-row + .spec-row { border-top: 1px solid var(--ink); }
.spec-row .no { font-family: var(--mono); font-size: 12px; color: var(--ink-soft); letter-spacing: 0.1em; }
.spec-row h3 { margin: 0; font-size: 18px; text-transform: uppercase; letter-spacing: 0.01em; }
.spec-row p { margin: 0; color: var(--ink-soft); }

footer { border-top: 2px solid var(--ink); background: var(--ink); color: var(--paper); }
footer .wrap { display: flex; justify-content: space-between; gap: 20px; padding-top: 22px; padding-bottom: 22px; font-family: var(--mono); font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; }

@media (max-width: 980px) {
    .hero .wrap, .section-head { grid-template-columns: 1fr; gap: 40px; }
    .gallery { grid-template-columns: repeat(2, 1fr); }
    .spec-row { grid-template-columns: 60px 1fr; }
    .spec-row p { grid-column: 2; }
    .status { display: none; }
}
@media (max-width: 560px) {
    .wrap { padding: 0 18px; }
    .band .wrap { gap: 14px; }
    .band .by { display: none; }
    .gallery { gap: 16px; }
    footer .wrap { flex-direction: column; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
"""


def a_body() -> str:
    cards = '\n'.join(f"""                <a href="{UP}archetypes/{f}" class="card">
                    <div class="shot"><img src="{UP}assets/slide_{n}.png" alt="{e(name)}" loading="lazy"></div>
                    <div class="name"><b>{n}</b>{e(name)}</div>
                </a>""" for n, name, f in SLIDES)
    specs = '\n'.join(f"""            <div class="spec-row"><span class="no">SPEC {i:02d}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>"""
                      for i, (t, d) in enumerate(FEATURES, 1))
    return f"""    <header class="band">
        <div class="wrap">
            <a class="wordmark" href="#">medet.ink</a>
            <a class="by" href="{MANTEIGA}" target="_blank" rel="noopener">Manteiga Foundation</a>
            <div class="status"><span><i class="led"></i>Ready</span><span>16 archetypes</span><span>PDF 16 pp</span></div>
            <nav><a href="{GITHUB}" target="_blank" rel="noopener">GitHub</a></nav>
        </div>
    </header>
    <main>
        <div class="hero">
            <div class="wrap">
                <div>
                    <div class="label"><b>HTML pentest report template</b> / 11 x 8.5 in landscape</div>
                    <h1>{e(HEADLINE)}</h1>
                    <p class="lead">{e(LEAD)}</p>
                    <div class="actions">
                        <a class="btn primary" href="{REPORT}">View Full Report</a>
                        <a class="btn secondary" href="{PDF}" download>Download PDF</a>
                        <a class="btn" href="{GITHUB}" target="_blank" rel="noopener">GitHub</a>
                    </div>
                </div>
                <div class="window">
                    <div class="bar"><i></i><i></i><i></i><span>report preview</span></div>
                    <img src="{UP}assets/demo.gif" alt="Report Demo">
                </div>
            </div>
        </div>
        <section>
            <div class="wrap">
                <div class="section-head"><div class="label">01 / Gallery</div><div><h2>Template Gallery</h2><p>{e(GALLERY_NOTE)}</p></div></div>
                <div class="gallery">
{cards}
                </div>
            </div>
        </section>
        <section>
            <div class="wrap">
                <div class="section-head"><div class="label">02 / Features</div><div><h2>Enterprise Features</h2></div></div>
                <div class="spec">
{specs}
                </div>
            </div>
        </section>
    </main>
    <footer><div class="wrap"><span>{FOOTER}</span><span>medet.ink</span></div></footer>"""


# ---------------------------------------------------------------- B. Hardware Console
B_CSS = """
:root {
    --chassis: #E6E2D6; --panel: #D8D3C4; --panel-hi: #F3F0E7; --panel-lo: #A9A393; --bezel: #34342F;
    --ink: #2C2C2A; --ink-soft: #5E5A50; --lcd: #A3BDA9; --lcd-ink: #1F3328;
    --sage: #8FB3A8; --peach: #D9A877; --lavender: #A99BC2; --mustard: #E2C27F;
    --green: #47A15A; --amber: #E0A23A; --head: 'Space Grotesk', sans-serif; --mono: 'IBM Plex Mono', monospace; --lcdfont: 'VT323', monospace;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--chassis); color: var(--ink); font-family: var(--head); line-height: 1.55; }
a { color: inherit; }
:focus-visible { outline: 3px solid var(--amber); outline-offset: 3px; }
.wrap { max-width: 1240px; margin: 0 auto; padding: 0 28px; }

/* Panels: bevelled, screwed */
.panel {
    position: relative; background: var(--panel); border-radius: 10px; border: 1px solid var(--panel-lo);
    box-shadow: inset 2px 2px 0 var(--panel-hi), inset -2px -2px 0 var(--panel-lo), 0 2px 0 rgba(0, 0, 0, 0.12);
}
.screw { position: absolute; width: 11px; height: 11px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #F7F5EE, #9C9686 70%); border: 1px solid #8A8476; }
.screw::after { content: ''; position: absolute; left: 2px; right: 2px; top: 4px; height: 1.5px; background: #6F6A5E; transform: rotate(-35deg); }
.screw.tl { top: 10px; left: 10px; } .screw.tr { top: 10px; right: 10px; } .screw.bl { bottom: 10px; left: 10px; } .screw.br { bottom: 10px; right: 10px; }
.silk { font-family: var(--mono); font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--ink-soft); }

/* Instrument bar */
.bar { padding: 14px 0; }
.bar .panel { display: flex; align-items: center; gap: 26px; padding: 12px 34px; min-height: 56px; }
.wordmark { font-weight: 700; font-size: 18px; letter-spacing: 0.14em; text-transform: uppercase; text-decoration: none; text-shadow: 1px 1px 0 var(--panel-hi); }
.leds { display: flex; gap: 20px; margin-left: auto; }
.led { display: inline-flex; align-items: center; gap: 8px; font-family: var(--mono); font-size: 11px; letter-spacing: 0.14em; color: var(--ink-soft); }
.led i { width: 10px; height: 10px; border-radius: 50%; background: var(--green); box-shadow: 0 0 6px rgba(71, 161, 90, 0.7), inset 0 -2px 2px rgba(0, 0, 0, 0.25); }
.led.amber i { background: var(--amber); box-shadow: 0 0 6px rgba(224, 162, 58, 0.7), inset 0 -2px 2px rgba(0, 0, 0, 0.25); }
.key {
    display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 0 18px; border-radius: 6px;
    font-family: var(--mono); font-weight: 600; font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; text-decoration: none;
    background: var(--panel); border: 1px solid #7F7969;
    box-shadow: inset 2px 2px 0 rgba(255, 255, 255, 0.55), inset -2px -3px 0 rgba(0, 0, 0, 0.22), 0 3px 0 #7F7969;
    transition: transform 0.08s, box-shadow 0.08s;
}
.key:hover { filter: brightness(1.04); }
.key:active { transform: translateY(3px); box-shadow: inset 2px 2px 3px rgba(0, 0, 0, 0.25), 0 0 0 #7F7969; }
.key.sage { background: var(--sage); } .key.peach { background: var(--peach); } .key.lavender { background: var(--lavender); }

/* Hero console */
.hero { padding: 10px 0 30px; }
.hero .panel { display: grid; grid-template-columns: 1fr 1.15fr; gap: 44px; padding: 48px 48px 44px; align-items: center; }
h1 { font-size: clamp(34px, 4.2vw, 54px); line-height: 1.04; letter-spacing: -0.015em; text-transform: uppercase; margin: 14px 0 20px; text-wrap: balance; }
.lead { color: var(--ink-soft); font-size: 17px; margin: 0 0 30px; max-width: 33em; }
.keys { display: flex; flex-wrap: wrap; gap: 14px; }
.readout { margin-top: 28px; display: inline-flex; gap: 22px; padding: 8px 16px; background: var(--lcd); color: var(--lcd-ink); font-family: var(--lcdfont); font-size: 22px; letter-spacing: 0.06em; border-radius: 4px; box-shadow: inset 2px 2px 4px rgba(0, 0, 0, 0.35); }
.monitor { background: var(--bezel); padding: 18px 18px 30px; border-radius: 14px; box-shadow: inset 0 2px 0 #55554E, 0 6px 0 #22221F; position: relative; }
.monitor::after { content: 'PREVIEW'; position: absolute; bottom: 8px; left: 22px; font-family: var(--mono); font-size: 10px; letter-spacing: 0.2em; color: #9A9888; }
.screen { position: relative; border-radius: 6px; overflow: hidden; background: var(--lcd); box-shadow: inset 0 0 0 3px #1E1E1B; }
.screen img { display: block; width: 100%; height: auto; filter: sepia(0.12) saturate(0.9); }
.screen::after { content: ''; position: absolute; inset: 0; pointer-events: none; background: repeating-linear-gradient(0deg, rgba(0, 0, 0, 0.06) 0 1px, transparent 1px 3px); }

/* Modules */
.module { margin: 0 0 30px; padding: 40px 44px 44px; }
.module-head { display: flex; align-items: baseline; justify-content: space-between; gap: 24px; margin-bottom: 30px; flex-wrap: wrap; }
h2 { font-size: 30px; text-transform: uppercase; margin: 6px 0 0; letter-spacing: 0.01em; }
.module-head p { margin: 0; color: var(--ink-soft); max-width: 36em; }
.bank { display: grid; grid-template-columns: repeat(4, 1fr); gap: 22px; }
.unit { display: block; min-width: 0; text-decoration: none; background: var(--bezel); border-radius: 9px; padding: 9px 9px 0; box-shadow: 0 4px 0 #22221F; transition: transform 0.1s; }
.unit:hover { transform: translateY(-3px); }
.unit .shot { aspect-ratio: 11 / 8.5; border-radius: 4px; overflow: hidden; background: var(--lcd); box-shadow: inset 0 0 0 2px #1E1E1B; }
.unit img { display: block; width: 100%; height: 100%; object-fit: cover; }
.unit .tag { display: flex; gap: 10px; padding: 7px 4px 9px; font-family: var(--lcdfont); font-size: 20px; color: #CFE0D2; letter-spacing: 0.04em; text-transform: uppercase; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.unit .tag b { color: var(--mustard); font-weight: 400; }
.mods { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.mod { padding: 26px 24px 28px; background: var(--chassis); border-radius: 8px; border: 1px solid var(--panel-lo); box-shadow: inset 1px 1px 0 var(--panel-hi); }
.mod .led { margin-bottom: 16px; }
.mod h3 { margin: 0 0 8px; font-size: 18px; text-transform: uppercase; }
.mod p { margin: 0; color: var(--ink-soft); font-size: 15px; }
footer { padding: 6px 0 30px; }
footer .panel { display: flex; justify-content: space-between; gap: 20px; padding: 16px 34px; font-family: var(--mono); font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ink-soft); }

@media (max-width: 980px) {
    .hero .panel { grid-template-columns: 1fr; padding: 40px 28px; }
    .bank, .mods { grid-template-columns: repeat(2, 1fr); }
    .leds { display: none; }
    .module { padding: 34px 24px; }
}
@media (max-width: 560px) {
    .wrap { padding: 0 12px; }
    .bar .panel { padding: 10px 22px; gap: 12px; }
    .bar .key { display: none; }
    .bank { gap: 14px; }
    .mods { grid-template-columns: 1fr; }
    .readout { font-size: 18px; gap: 12px; }
    footer .panel { flex-direction: column; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
"""


def screws() -> str:
    return '<i class="screw tl"></i><i class="screw tr"></i><i class="screw bl"></i><i class="screw br"></i>'


def b_body() -> str:
    units = '\n'.join(f"""                    <a href="{UP}archetypes/{f}" class="unit">
                        <div class="shot"><img src="{UP}assets/slide_{n}.png" alt="{e(name)}" loading="lazy"></div>
                        <div class="tag"><b>{n}</b>{e(name)}</div>
                    </a>""" for n, name, f in SLIDES)
    leds = ['', 'amber', '', 'amber']
    mods = '\n'.join(f"""                    <div class="mod"><span class="led {leds[i]}"><i></i>Module {i + 1:02d}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>"""
                     for i, (t, d) in enumerate(FEATURES))
    return f"""    <header class="bar">
        <div class="wrap">
            <div class="panel">{screws()}
                <a class="wordmark" href="#">medet.ink</a>
                <span class="silk">by <a href="{MANTEIGA}" target="_blank" rel="noopener">Manteiga Foundation</a></span>
                <div class="leds"><span class="led"><i></i>PWR</span><span class="led amber"><i></i>DATA</span><span class="led"><i></i>READY</span></div>
                <a class="key" href="{GITHUB}" target="_blank" rel="noopener">GitHub</a>
            </div>
        </div>
    </header>
    <main>
        <div class="hero">
            <div class="wrap">
                <div class="panel">{screws()}
                    <div>
                        <div class="silk">HTML pentest report template</div>
                        <h1>{e(HEADLINE)}</h1>
                        <p class="lead">{e(LEAD)}</p>
                        <div class="keys">
                            <a class="key sage" href="{REPORT}">View Full Report</a>
                            <a class="key peach" href="{PDF}" download>Download PDF</a>
                            <a class="key lavender" href="{GITHUB}" target="_blank" rel="noopener">GitHub</a>
                        </div>
                        <div class="readout"><span>16 PAGES</span><span>11 x 8.5 IN</span><span>READY</span></div>
                    </div>
                    <div class="monitor"><div class="screen"><img src="{UP}assets/demo.gif" alt="Report Demo"></div></div>
                </div>
            </div>
        </div>
        <div class="wrap">
            <section class="panel module">{screws()}
                <div class="module-head"><div><div class="silk">Slide bank</div><h2>Template Gallery</h2></div><p>{e(GALLERY_NOTE)}</p></div>
                <div class="bank">
{units}
                </div>
            </section>
            <section class="panel module">{screws()}
                <div class="module-head"><div><div class="silk">Modules</div><h2>Enterprise Features</h2></div></div>
                <div class="mods">
{mods}
                </div>
            </section>
        </div>
    </main>
    <footer><div class="wrap"><div class="panel">{screws()}<span>{FOOTER}</span><span>medet.ink</span></div></div></footer>"""


# ---------------------------------------------------------------- C. Blueprint Sketchbook
C_CSS = """
:root {
    --paper: #F4F1EA; --ink: #2D2D2D; --ink-soft: #5D5A52;
    --lavender: #9B8FB8; --teal: #7FB3B5; --peach: #D4B483;
    --head: 'Big Shoulders Display', sans-serif; --type: 'Courier Prime', monospace;
}
* { box-sizing: border-box; }
body {
    margin: 0; color: var(--ink); font-family: var(--type); font-size: 16px; line-height: 1.6; background-color: var(--paper);
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.25 0 0 0 0 0.22 0 0 0 0 0.18 0 0 0 0.09 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
a { color: inherit; }
:focus-visible { outline: 3px dashed var(--lavender); outline-offset: 4px; }
.wrap { max-width: 1200px; margin: 0 auto; padding: 0 32px; }
.svg-defs { position: absolute; width: 0; height: 0; }

/* Ink-drawn boxes: the border is drawn on a pseudo-element through a roughening filter. */
.ink { position: relative; }
.ink::before { content: ''; position: absolute; inset: 0; border: 2.2px solid var(--ink); border-radius: 3px; filter: url(#rough); pointer-events: none; }

.band { padding: 22px 0 0; }
.band .wrap { display: flex; align-items: center; gap: 26px; padding-bottom: 18px; position: relative; }
.band .wrap::after { content: ''; position: absolute; left: 32px; right: 32px; bottom: 0; height: 2.5px; background: var(--ink); filter: url(#rough-line); }
.wordmark { font-family: var(--head); font-weight: 800; font-size: 34px; letter-spacing: 0.02em; text-transform: uppercase; line-height: 1; text-decoration: none; }
.wordmark small { display: block; font-family: var(--type); font-weight: 700; font-size: 11px; letter-spacing: 0.22em; margin-top: 4px; }
.band nav { margin-left: auto; display: flex; gap: 22px; font-size: 14px; }
.band nav a { text-decoration: underline; text-decoration-style: wavy; text-decoration-color: var(--lavender); text-underline-offset: 5px; }

.hero { padding: 64px 0 80px; }
.hero .wrap { display: grid; grid-template-columns: 1fr 1.05fr; gap: 64px; align-items: center; }
.note { font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-soft); }
h1 { position: relative; font-family: var(--head); font-weight: 800; font-size: clamp(48px, 6vw, 82px); line-height: 0.95; text-transform: uppercase; letter-spacing: 0.005em; margin: 14px 0 26px; text-wrap: balance; isolation: isolate; }
h1::before { content: ''; position: absolute; z-index: -1; left: -4%; top: 18%; width: 78%; height: 70%; background: radial-gradient(ellipse at 40% 50%, rgba(127, 179, 181, 0.55), rgba(127, 179, 181, 0.15) 60%, transparent 72%); filter: url(#wash); }
.lead { font-size: 17px; color: var(--ink-soft); max-width: 33em; margin: 0 0 34px; }
.actions { display: flex; flex-wrap: wrap; gap: 16px; }
.btn { display: inline-flex; align-items: center; min-height: 48px; padding: 0 22px; font-family: var(--type); font-weight: 700; font-size: 15px; text-decoration: none; background: var(--paper); box-shadow: 4px 4px 0 var(--ink); transition: transform 0.12s, box-shadow 0.12s; }
.btn:hover { transform: translate(-2px, -2px); box-shadow: 6px 6px 0 var(--ink); }
.btn.teal { background: rgba(127, 179, 181, 0.55); } .btn.peach { background: rgba(212, 180, 131, 0.6); }
.taped { position: relative; transform: rotate(-1.2deg); background: #FFFFFF; padding: 12px; box-shadow: 0 10px 24px rgba(45, 45, 45, 0.15); }
.taped img { display: block; width: 100%; height: auto; }
.taped::before, .taped::after { content: ''; position: absolute; width: 110px; height: 30px; background: rgba(212, 180, 131, 0.55); top: -14px; }
.taped::before { left: 18px; transform: rotate(-6deg); } .taped::after { right: 18px; transform: rotate(5deg); }
.taped figcaption { font-size: 12px; color: var(--ink-soft); padding-top: 8px; letter-spacing: 0.06em; }

section { padding: 56px 0 72px; }
.section-head { margin-bottom: 40px; max-width: 760px; }
h2 { position: relative; display: inline-block; font-family: var(--head); font-weight: 800; font-size: 46px; line-height: 1; text-transform: uppercase; margin: 6px 0 14px; isolation: isolate; }
h2::after { content: ''; position: absolute; z-index: -1; left: -6px; right: -10px; bottom: 2px; height: 16px; background: rgba(155, 143, 184, 0.45); filter: url(#wash); }
.section-head p { margin: 0; color: var(--ink-soft); }

/* Postage stamps */
.stamps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 34px 28px; }
.stamp {
    display: block; text-decoration: none; background: #FFFFFF; padding: 12px 12px 10px; transition: transform 0.15s;
    -webkit-mask: radial-gradient(circle 5px at 5px 5px, transparent 98%, #000) -5px -5px / 14px 14px;
            mask: radial-gradient(circle 5px at 5px 5px, transparent 98%, #000) -5px -5px / 14px 14px;
    filter: drop-shadow(0 3px 4px rgba(45, 45, 45, 0.16));
}
.stamp:nth-child(odd) { transform: rotate(-0.8deg); } .stamp:nth-child(even) { transform: rotate(0.7deg); }
.stamp:hover { transform: rotate(0deg) translateY(-4px); }
.stamp .shot { aspect-ratio: 11 / 8.5; overflow: hidden; outline: 1.5px solid var(--ink); }
.stamp img { display: block; width: 100%; height: 100%; object-fit: cover; }
.stamp .name { display: flex; justify-content: space-between; gap: 8px; padding-top: 8px; font-size: 13px; font-weight: 700; }
.stamp .name b { font-family: var(--head); font-size: 18px; line-height: 1; color: var(--lavender); }

.figs { display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px 40px; }
.fig { padding: 26px 28px 28px; background: rgba(255, 255, 255, 0.5); }
.fig .no { font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--ink-soft); }
.fig h3 { font-family: var(--head); font-weight: 800; font-size: 28px; text-transform: uppercase; margin: 4px 0 8px; line-height: 1.05; }
.fig p { margin: 0; color: var(--ink-soft); }

footer .wrap { display: flex; justify-content: space-between; gap: 20px; padding-top: 22px; padding-bottom: 34px; font-size: 13px; position: relative; }
footer .wrap::before { content: ''; position: absolute; left: 32px; right: 32px; top: 0; height: 2.5px; background: var(--ink); filter: url(#rough-line); }

@media (max-width: 980px) {
    .hero .wrap { grid-template-columns: 1fr; gap: 48px; }
    .stamps { grid-template-columns: repeat(2, 1fr); }
    .figs { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
    .wrap { padding: 0 18px; }
    .band .wrap::after, footer .wrap::before { left: 18px; right: 18px; }
    .wordmark { font-size: 28px; }
    .stamps { gap: 22px 16px; }
    footer .wrap { flex-direction: column; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
"""


def c_body() -> str:
    stamps = '\n'.join(f"""                <a href="{UP}archetypes/{f}" class="stamp">
                    <div class="shot"><img src="{UP}assets/slide_{n}.png" alt="{e(name)}" loading="lazy"></div>
                    <div class="name"><span>{e(name)}</span><b>{n}</b></div>
                </a>""" for n, name, f in SLIDES)
    figs = '\n'.join(f"""                <div class="fig ink"><div class="no">Fig. {i}</div><h3>{e(t)}</h3><p>{e(d)}</p></div>"""
                     for i, (t, d) in enumerate(FEATURES, 1))
    return f"""    <svg class="svg-defs" aria-hidden="true">
        <filter id="rough"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="3.2"/></filter>
        <filter id="rough-line"><feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="1" seed="5"/><feDisplacementMap in="SourceGraphic" scale="1.4"/></filter>
        <filter id="wash"><feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="3" seed="8"/><feDisplacementMap in="SourceGraphic" scale="14"/></filter>
    </svg>
    <header class="band">
        <div class="wrap">
            <a class="wordmark" href="#">medet.ink<small>Report templates</small></a>
            <nav><a href="{MANTEIGA}" target="_blank" rel="noopener">Manteiga Foundation</a><a href="{GITHUB}" target="_blank" rel="noopener">GitHub</a></nav>
        </div>
    </header>
    <main>
        <div class="hero">
            <div class="wrap">
                <div>
                    <div class="note">HTML pentest report template</div>
                    <h1>{e(HEADLINE)}</h1>
                    <p class="lead">{e(LEAD)}</p>
                    <div class="actions">
                        <a class="btn ink teal" href="{REPORT}">View Full Report</a>
                        <a class="btn ink peach" href="{PDF}" download>Download PDF</a>
                        <a class="btn ink" href="{GITHUB}" target="_blank" rel="noopener">GitHub</a>
                    </div>
                </div>
                <figure class="taped"><img src="{UP}assets/demo.gif" alt="Report Demo"><figcaption>Sixteen archetypes, 11 x 8.5 in landscape.</figcaption></figure>
            </div>
        </div>
        <section>
            <div class="wrap">
                <div class="section-head"><h2>Template Gallery</h2><p>{e(GALLERY_NOTE)}</p></div>
                <div class="stamps">
{stamps}
                </div>
            </div>
        </section>
        <section>
            <div class="wrap">
                <div class="section-head"><h2>Enterprise Features</h2></div>
                <div class="figs">
{figs}
                </div>
            </div>
        </section>
    </main>
    <footer><div class="wrap"><span>{FOOTER}</span><span>medet.ink</span></div></footer>"""


OPTIONS = {
    'option-a.html': ('family=IBM+Plex+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;700', A_CSS, a_body),
    'option-b.html': ('family=IBM+Plex+Mono:wght@400;600&family=Space+Grotesk:wght@400;500;700&family=VT323', B_CSS, b_body),
    'option-c.html': ('family=Big+Shoulders+Display:wght@700;800&family=Courier+Prime:wght@400;700', C_CSS, c_body),
}

if __name__ == '__main__':
    for name, (fonts, css, body) in OPTIONS.items():
        (HERE / name).write_text(page(fonts, css, body()), encoding='utf-8')
        print('wrote', HERE / name)
