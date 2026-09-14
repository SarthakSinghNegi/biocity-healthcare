#!/usr/bin/env python3
"""Generate BLOOD_TEST_CATALOG_KNOWLEDGE.md from v3/assets/data/catalog.json.

Single source of truth = the JSON exported from Blood_Test_Packages_Completed.xlsx.
Re-run this whenever catalog.json changes so the knowledge bank stays exact.
"""
import collections
import datetime
import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "v3", "assets", "data", "catalog.json")
OUT = os.path.join(HERE, "BLOOD_TEST_CATALOG_KNOWLEDGE.md")

c = json.load(open(DATA, encoding="utf-8"))
sections = c["sections"]
tests = c["tests"]
a = c["analytics"]


def flo(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


mrp = [flo(t.get("mrp")) for t in tests]
mrp = [x for x in mrp if x]
off = [flo(t.get("offer_price")) for t in tests]
off = [x for x in off if x]
disc = [flo(t.get("discount")) for t in tests if flo(t.get("discount")) is not None]
pkg_prices = [p["offer_price"] for s in sections for p in s["packages"] if p["offer_price"]]

# most-reused component panels across packages
comp = collections.Counter()
comp_params = {}
for s in sections:
    for p in s["packages"]:
        for x in p["components"]:
            base = x["test"].split("(")[0].strip()
            comp[base] += 1
            if x["params"]:
                comp_params[base] = x["params"]

L = []
w = L.append

w("# Biocity — Blood Test Packages & Catalog Knowledge Bank")
w("")
w("> **Domain knowledge bank** for the Biocity diagnostics catalog: every health")
w("> **package**, every **test** in the master menu, and the category-wise structure")
w("> that powers the website's package recommender, comparison and booking flows.")
w("> Built to be *integrated* — the machine-readable twin lives at")
w("> [`v3/assets/data/catalog.json`](../v3/assets/data/catalog.json).")
w("")
w(f"- **Last updated:** {datetime.date.today().isoformat()}")
w("- **Source of truth:** `Blood_Test_Packages_Completed.xlsx` → `catalog.json`")
w("- **Regenerate:** `python3 docs/gen_catalog_kb.py` (never hand-edit the tables)")
w("")
w("---")
w("")
w("## 1. TL;DR — the catalog at a glance")
w("")
w(f"- **{a['packages']['count']} packages** organised into **{a['packages']['sections']} categories** "
  f"(sections), priced **₹{a['packages']['price_min']:,}–₹{a['packages']['price_max']:,}** "
  f"(median ₹{a['packages']['price_median']:,}).")
w(f"- **{a['tests']['count']} individual tests** in the master menu across "
  f"**{len(a['by_department'])} lab departments**.")
w(f"- Fulfilment split: **{a['by_processing'].get('In-house','?')} in-house** vs "
  f"**{a['by_processing'].get('Outsource','?')} outsourced** (vendor *Accuprobe*); "
  f"**{a['by_nabl'].get('Yes','?')} tests carry NABL scope**.")
w(f"- Per-test economics: MRP median **₹{int(st.median(mrp)):,}**, offer median "
  f"**₹{int(st.median(off)):,}**, mean discount **{st.mean(disc)*100:.0f}%**.")
w(f"- Packages are assembled from **{len(comp)} reusable panel building-blocks** "
  f"(CBC, Lipid, KFT, LFT, Diabetes, Thyroid, Vitamin, Bone… reused across dozens of packages).")
w("")
w("---")
w("")
w("## 2. Two-sheet source model")
w("")
w("The workbook has two sheets that join on **panel/test names**:")
w("")
w("| Sheet | Rows | Grain | What it holds |")
w("|---|---|---|---|")
w(f"| `Package List` | 678 | section → package → component line | The **retail catalog**: {a['packages']['count']} sellable packages grouped in {a['packages']['sections']} sections, each with an offer price and its constituent panels (+param counts). |")
w(f"| `Test Details` | 490 | one test | The **operational master**: {a['tests']['count']} tests with department, sample, fasting, TAT, processing/vendor, full cost stack, MRP/offer/discount, NABL scope, machine and profile mapping. |")
w("")
w("### Test-master schema (22 columns)")
w("")
w("`category` · `code` · `name` · `department` · `sample` · `fasting` · `special` (instruction) · "
  "`tat` · `processing` (In-house/Outsource) · `vendor` · **cost stack** (`lab_cost`, `consumable_cost`, "
  "`phlebo_cost`, `processing_cost`, `total_cost`) · `mrp` · `offer_price` · `discount` · `status` · "
  "`profile` (panel mapping) · `machine` · `nabl` (scope Y/N).")
w("")
w("---")
w("")
w("## 3. Package taxonomy — the 9 categories (mind map)")
w("")
w("```mermaid")
w("mindmap")
w("  root((Biocity<br/>Packages))")
for s in sections:
    title = s["title"] or s["section"]
    w(f"    {title.replace('(', '').replace(')', '')}")
    for p in s["packages"][:6]:
        w(f"      {p['name']} ₹{p['offer_price']}")
    if len(s["packages"]) > 6:
        w(f"      +{len(s['packages'])-6} more…")
w("```")
w("")
w("> The recommender maps a user's **age / gender / organ / disease / lifestyle** answer")
w("> onto one of these branches. See [§9 Recommender map](#9-recommender-decision-map).")
w("")
w("---")
w("")
w("## 4. Full package directory (all 85, category-wise)")
w("")
w("> Prices are the **offer price in ₹**. \"Claimed tests\" is the marketing count printed")
w("> in the sheet; \"key components\" are the panel building-blocks (parameter count in brackets).")
for s in sections:
    w("")
    w(f"### {s['section']}")
    w("")
    pr = [p["offer_price"] for p in s["packages"] if p["offer_price"]]
    w(f"*{len(s['packages'])} packages · ₹{min(pr):,}–₹{max(pr):,}*")
    w("")
    w("| # | Package | Claimed | ₹ Offer | Key components (params) |")
    w("|---|---|---|---|---|")
    for p in s["packages"]:
        comps = ", ".join(
            (x["test"].split("(")[0].strip() + (f" ({x['params']})" if x["params"] else ""))
            for x in p["components"][:6]
        )
        if len(p["components"]) > 6:
            comps += ", …"
        w(f"| {p['num']} | **{p['name']}** | {p['claimed_tests']} | {p['offer_price'] or '—'} | {comps or '—'} |")
w("")
w("---")
w("")
w("## 5. Reusable panel building-blocks (mind map)")
w("")
w("Packages are not bespoke — they are **compositions of a small set of core panels**.")
w("These are the most-reused components across all 85 packages:")
w("")
w("```mermaid")
w("mindmap")
w("  root((Core<br/>Panels))")
for base, n in comp.most_common(14):
    pp = f" · {comp_params[base]}p" if base in comp_params else ""
    short = base if len(base) < 46 else base[:44] + "…"
    w(f"    {short} (x{n}{pp})")
w("```")
w("")
w("| Panel building-block | Reused in # packages | Typical params |")
w("|---|---|---|")
for base, n in comp.most_common(20):
    w(f"| {base} | {n} | {comp_params.get(base,'—')} |")
w("")
w(f"> **101 distinct** component lines exist in total; the tail is package-specific add-ons "
  f"(cancer markers, hormones, allergy panels, etc.).")
w("")
w("---")
w("")
w("## 6. Test master — category-wise breakdowns")


def tbl(title, d, note=""):
    w("")
    w(f"### {title}")
    if note:
        w("")
        w(note)
    w("")
    w("| Value | Count |")
    w("|---|---|")
    for k, v in sorted(d.items(), key=lambda kv: -kv[1]):
        w(f"| {k} | {v} |")


tbl("By lab department", a["by_department"],
    "Where the test is physically run. Biochemistry + Immunology dominate the menu.")
tbl("By processing & vendor", a["by_processing"],
    "*In-house* = run at Biocity's own lab; *Outsource* = sent to partner **Accuprobe**. "
    "In-house tests are the fast, same-day, NABL-scoped core.")
tbl("By turnaround time (TAT)", a["by_tat"])
tbl("By NABL scope", a["by_nabl"],
    "NABL-accredited scope tests are the marketable trust signal — all are in-house, same-day.")
tbl("By fasting requirement", a["by_fasting"])
tbl("By machine / technology", a["by_machine"])
w("")
w("### Top sample types")
w("")
w("| Sample | Count |")
w("|---|---|")
for k, v in a["by_sample"].items():
    w(f"| {k} | {v} |")
w("")
w("> **Serum (1 ml)** is the workhorse specimen (~67% of the menu); a single serum draw")
w("> unlocks most biochemistry + immunology tests — key for the home-collection model.")
w("")
w("---")
w("")
w("## 7. Profile / panel mapping catalog")
w("")
w("`profile` groups raw tests into the named panels used in packages & reports:")
w("")
w("| Profile / panel | # member tests |")
w("|---|---|")
for k, v in a["by_profile"].items():
    if k != "—":
        w(f"| {k} | {v} |")
w("")
w("---")
w("")
w("## 8. Pricing & unit economics")
w("")
w("```mermaid")
w("flowchart LR")
w('  LC["Lab cost"] --> TC["Total cost"]')
w('  CC["Consumable"] --> TC')
w('  PC["Phlebo cost"] --> TC')
w('  PR["Processing"] --> TC')
w('  TC --> MRP["MRP"]')
w('  MRP -->|"~50% avg discount"| OFF["Offer price"]')
w("```")
w("")
w("- **Per-test:** MRP ₹{:,.0f}–₹{:,.0f} (median ₹{:,.0f}); offer ₹{:,.0f}–₹{:,.0f} "
  "(median ₹{:,.0f}); discount mean **{:.0f}%** (max {:.0f}%).".format(
      min(mrp), max(mrp), st.median(mrp), min(off), max(off), st.median(off),
      st.mean(disc) * 100, max(disc) * 100))
w("- **Cost stack** per test = `lab_cost + consumable_cost + phlebo_cost + processing_cost = total_cost`. "
  "The phlebo (home-collection) cost is a flat loading on every test — amortised across a package it's negligible, "
  "which is *why packages are the profitable unit*, not single tests.")
w("- **Package pricing** ladder (offer ₹): "
  + " · ".join(f"₹{p:,}" for p in sorted(set(pkg_prices))[:1])
  + f" (cheapest, *Eye Health*) → ₹{max(pkg_prices):,} (*Platinum*).")
w("")
w("---")
w("")
w("## 9. Recommender decision map")
w("")
w("How a website visitor's inputs should resolve to a package category:")
w("")
w("```mermaid")
w("flowchart TD")
w('  Q{"What is the user telling us?"}')
w('  Q -->|"Just a routine check"| S1["Preventive → Full Body / Comprehensive"]')
w('  Q -->|"Age (kid/teen/senior)"| S3["Age Based → Kids…Super Senior"]')
w('  Q -->|"Gender / reproductive"| S2["Gender Specific → Women/Men/PCOS/Fertility"]')
w('  Q -->|"Named disease"| S4["Disease Specific → Diabetes/Heart/Thyroid/Kidney…"]')
w('  Q -->|"An organ"| S5["Organ Wise → Heart/Liver/Kidney/Brain…"]')
w('  Q -->|"Job / habit"| S6["Lifestyle → IT/Corporate/Smoker/Gym…"]')
w('  Q -->|"Whole family"| S7["Family → Couple/Parents/Festival"]')
w('  Q -->|"Employer / bulk"| S8["Corporate → Employee/Executive/Factory"]')
w('  Q -->|"Cancer/cardiac/hormone/allergy"| S9["Specialized → screening panels"]')
w("```")
w("")
w("**Integration signals available in `catalog.json`** for ranking within a branch:")
w("`offer_price` (budget), component `params` (comprehensiveness), `claimed_tests`, and the")
w("panel building-blocks (match user concern → package that contains that panel).")
w("")
w("---")
w("")
w("## 10. Sample → department → fulfilment flow")
w("")
w("```mermaid")
w("flowchart LR")
w('  Home["Home collection<br/>(phlebotomist)"] --> Serum["Serum draw<br/>(~67% of tests)"]')
w('  Home --> Other["EDTA / Urine / Stool / Swab"]')
w('  Serum --> Bio["Clinical Biochemistry"]')
w('  Serum --> Imm["Immunology & Serology"]')
w('  Other --> Hem["Hematology"]')
w('  Other --> Micro["Microbiology / Molecular"]')
w('  Bio --> InH["In-house · same-day · NABL"]')
w('  Imm --> Out["Outsource → Accuprobe · 24-48h"]')
w("```")
w("")
w("---")
w("")
w("## 11. Data-quality caveats (read before integrating)")
w("")
w("- **Claimed vs actual counts:** the \"85+ Test\" style label is a *marketing* count and")
w("  doesn't always equal the sum of component params — display the label, but rank on real params.")
w("- **Spelling in source:** component names contain typos (e.g. *\"Funtion\"*, *\"Diabeties\"*,")
w("  *\"Testostrone\"*). Keep a normalisation map before showing on the site.")
w("- **One `Inactive` test** exists in the master (488 Active / 1 Inactive) — filter on `status`.")
w("- **Discount anomaly:** discount ranges from **-24%** (a few tests priced *above* MRP) to 75%.")
w("  Clamp/validate before rendering a \"% off\" badge.")
w("- **Profile mapping is sparse:** 274/489 tests have no `profile` — treat blank as \"standalone test\".")
w("")
w("---")
w("")
w("## 12. Integration guide (site ↔ data)")
w("")
w("| Site surface | Data to use |")
w("|---|---|")
w("| Packages grid / comparison | `sections[].packages[]` → name, `offer_price`, `claimed_tests`, `components[]` |")
w("| Recommender (age/disease/organ) | section branch (§9) + filter packages by component panel |")
w("| Individual test pages / search | `tests[]` → `name`, `department`, `sample`, `fasting`, `tat`, `mrp`, `offer_price` |")
w("| Trust badges | `nabl == \"Yes\"`, `processing == \"In-house\"`, same-day `tat` |")
w("| \"% off\" badges | `discount` (validate 0–0.75) |")
w("")
w("Load once, cache client-side:")
w("")
w("```js")
w("const cat = await fetch('assets/data/catalog.json').then(r => r.json());")
w("// cat.sections[].packages[] , cat.tests[] , cat.analytics")
w("```")
w("")
w("---")
w("")
w("## 13. Maintenance protocol")
w("")
w("1. Update `Blood_Test_Packages_Completed.xlsx` → re-export → overwrite `v3/assets/data/catalog.json`.")
w("2. Run `python3 docs/gen_catalog_kb.py` to regenerate this file.")
w("3. Commit the xlsx-derived JSON **and** this doc in the same commit.")

open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("WROTE", OUT, "lines:", len(L))
