"""
Tensai SecureBank AIR — Extensible Agentic Ops Platform PPT (15 slides)
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

OUTPUT = r"c:\Users\KulkarS4.EU\Documents\portfolio-web\BOS_BAU\Tensai_SecureBank_AIR_Phase1_Scoped.pptx"

NAVY   = RGBColor(0x0B, 0x1F, 0x3A)
TEAL   = RGBColor(0x00, 0x96, 0x88)
SLATE  = RGBColor(0x45, 0x55, 0x64)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT  = RGBColor(0xF1, 0xF5, 0xF9)
ACCENT = RGBColor(0x1E, 0x40, 0xAF)
GREEN  = RGBColor(0x05, 0x96, 0x69)
AMBER  = RGBColor(0xD9, 0x77, 0x06)
BORDER = RGBColor(0xE2, 0xE8, 0xF0)


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def bg(slide, color=LIGHT):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def bar(slide, title, sub=None):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(10), Inches(1.0))
    r.fill.solid(); r.fill.fore_color.rgb = NAVY; r.line.fill.background()
    t = slide.shapes.add_textbox(Inches(0.45), Inches(0.15), Inches(9.1), Inches(0.55))
    p = t.text_frame.paragraphs[0]
    p.text = title; p.font.size = Pt(24); p.font.bold = True; p.font.color.rgb = WHITE
    if sub:
        s = slide.shapes.add_textbox(Inches(0.45), Inches(0.58), Inches(9.1), Inches(0.35))
        sp = s.text_frame.paragraphs[0]
        sp.text = sub; sp.font.size = Pt(11); sp.font.color.rgb = RGBColor(0xBF, 0xDB, 0xFE)


def bullets(slide, items, left=0.5, top=1.2, w=9.0, h=5.9, sz=14, col=SLATE, gap=8):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item if item[:1] in "•→" else f"• {item}"
        p.font.size = Pt(sz); p.font.color.rgb = col; p.space_after = Pt(gap)


def cols(slide, lt, li, rt, ri, top=1.2):
    for title, items, left in [(lt, li, 0.5), (rt, ri, 5.1)]:
        tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(4.4), Inches(0.35))
        p = tb.text_frame.paragraphs[0]
        p.text = title; p.font.bold = True; p.font.size = Pt(16); p.font.color.rgb = ACCENT
        bullets(slide, items, left=left, top=top + 0.42, w=4.4, h=5.5, sz=13)


def box(slide, text, l, t, w=1.6, h=0.5, fill=NAVY, fsize=10, bold=True):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = fill; s.line.color.rgb = fill
    tf = s.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = text
    p.font.size = Pt(fsize); p.font.bold = bold; p.font.color.rgb = WHITE
    p.alignment = PP_ALIGN.CENTER; tf.vertical_anchor = MSO_ANCHOR.MIDDLE


def arrow(slide, l, t):
    a = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(l), Inches(t), Inches(0.3), Inches(0.18))
    a.fill.solid(); a.fill.fore_color.rgb = TEAL; a.line.fill.background()


def down_arrow(slide, l, t):
    a = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(l), Inches(t), Inches(0.22), Inches(0.28))
    a.fill.solid(); a.fill.fore_color.rgb = TEAL; a.line.fill.background()


def layer_diagram(slide):
    """Simple 5-layer platform diagram"""
    layers = [
        (ACCENT,  "Experience Layer",      "Ops Command Portal  |  Executive Dashboard  |  Approval Console"),
        (TEAL,    "Intelligence Layer",    "Multi-Agent Engine  |  Correlation  |  Decision Policies  |  Learning"),
        (NAVY,    "Orchestration Layer",   "Workflow Engine  |  Event Router  |  Runbook Registry  |  Tool Connectors"),
        (RGBColor(0x37,0x47,0x5A), "Integration Layer", "ELK  |  ServiceNow  |  Azure  |  Teams  |  + Future Adapters"),
        (RGBColor(0x64,0x74,0x8B), "Data & Systems",    "SecureBank App  |  Infra  |  Security Tools  |  CMDB  |  Knowledge Base"),
    ]
    y = 1.25
    for color, name, desc in layers:
        box(slide, name, 0.5, y, w=2.0, h=0.48, fill=color, fsize=9)
        tb = slide.shapes.add_textbox(Inches(2.65), Inches(y + 0.04), Inches(6.85), Inches(0.42))
        p = tb.text_frame.paragraphs[0]
        p.text = desc; p.font.size = Pt(11); p.font.color.rgb = SLATE
        if y < 5.0:
            down_arrow(slide, 1.38, y + 0.5)
        y += 0.78


def hub_diagram(slide):
    """Hub-and-spoke integration diagram"""
    cx, cy = 5.0, 3.55
    # center hub
    hub = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - 0.85), Inches(cy - 0.55), Inches(1.7), Inches(1.1))
    hub.fill.solid(); hub.fill.fore_color.rgb = NAVY; hub.line.color.rgb = TEAL
    ht = slide.shapes.add_textbox(Inches(cx - 0.75), Inches(cy - 0.22), Inches(1.5), Inches(0.55))
    hp = ht.text_frame.paragraphs[0]
    hp.text = "AIR\nPlatform"; hp.font.size = Pt(11); hp.font.bold = True
    hp.font.color.rgb = WHITE; hp.alignment = PP_ALIGN.CENTER

    spokes = [
        (1.0,  1.5,  "Elasticsearch\nKibana",        ACCENT),
        (7.8,  1.5,  "ServiceNow\nITSM / CMDB",      ACCENT),
        (1.0,  5.2,  "Azure\nAKS / AI / Monitor",    TEAL),
        (7.8,  5.2,  "Microsoft\nTeams / Email",     TEAL),
        (4.35, 5.55, "SecureBank\nMicroservices",    GREEN),
        (4.35, 1.15, "Future:\nDatadog / Splunk\nPagerDuty / Jira", AMBER),
    ]
    for sx, sy, label, color in spokes:
        box(slide, label.replace("\n", " "), sx, sy, w=1.55, h=0.72 if "\n" in label else 0.55, fill=color, fsize=8)
        # connector line (simple rectangle as line)
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(min(sx+0.75, cx)-0.01), Inches(min(sy+0.3, cy)), Inches(0.02), Inches(0.02))
        line.fill.solid(); line.fill.fore_color.rgb = BORDER; line.line.fill.background()


def flow_diagram(slide):
    steps = ["Signal\nDetected", "Agent\nTriage", "Enriched\nTicket", "Smart\nAction", "Recovery\n& Audit"]
    for i, s in enumerate(steps):
        box(slide, s, 0.45 + i * 1.85, 1.35, w=1.55, h=0.72, fill=NAVY if i % 2 == 0 else TEAL, fsize=9)
        if i < len(steps) - 1:
            arrow(slide, 1.95 + i * 1.85, 1.62)
    bullets(slide, [
        "Works the same way for ANY connected system — not hard-coded to one alert type or one tool.",
        "New problem? Add a rule + agent playbook. New system? Plug in an adapter. No rebuild needed.",
    ], top=2.35, sz=13)


def impact_cards(slide):
    cards = [
        ("Time Saved", "60–80%\nMTTR reduction", GREEN),
        ("Cost Saved", "30–45%\nOps toil cut", TEAL),
        ("Availability", "99.95%+\ncritical paths", ACCENT),
        ("Scale", "1 platform\nmany use cases", NAVY),
    ]
    for i, (title, val, color) in enumerate(cards):
        l = 0.5 + i * 2.35
        c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(1.25), Inches(2.15), Inches(1.15))
        c.fill.solid(); c.fill.fore_color.rgb = WHITE; c.line.color.rgb = BORDER
        tb = slide.shapes.add_textbox(Inches(l + 0.12), Inches(1.32), Inches(1.9), Inches(1.0))
        tf = tb.text_frame
        p1 = tf.paragraphs[0]; p1.text = title; p1.font.size = Pt(11); p1.font.color.rgb = SLATE
        p2 = tf.add_paragraph(); p2.text = val; p2.font.size = Pt(20); p2.font.bold = True; p2.font.color.rgb = color


def roadmap_diagram(slide):
    phases = [
        ("Now", "Incident Response\nSNOW + ELK + Azure", ACCENT),
        ("Next", "Change Intelligence\nCapacity & Cost Ops", TEAL),
        ("Future", "SecOps Fusion\nCompliance Automation\nMulti-cloud adapters", NAVY),
    ]
    for i, (tag, desc, color) in enumerate(phases):
        l = 0.55 + i * 3.1
        box(slide, tag, l, 1.35, w=0.9, h=0.45, fill=color, fsize=10)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(1.9), Inches(2.75), Inches(1.5))
        card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = BORDER
        tb = slide.shapes.add_textbox(Inches(l + 0.15), Inches(2.05), Inches(2.45), Inches(1.2))
        p = tb.text_frame.paragraphs[0]
        p.text = desc; p.font.size = Pt(12); p.font.color.rgb = SLATE
        if i < 2:
            arrow(slide, l + 2.85, 2.35)


def main():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # ── SLIDE 1: Title ──────────────────────────────────────────────
    s = blank(prs); bg(s, NAVY)
    t = s.shapes.add_textbox(Inches(0.65), Inches(1.6), Inches(8.7), Inches(1.1))
    p = t.text_frame.paragraphs[0]
    p.text = "TENSAI SECUREBANK AIR"; p.font.size = Pt(38); p.font.bold = True; p.font.color.rgb = WHITE
    sub = s.shapes.add_textbox(Inches(0.65), Inches(2.75), Inches(8.7), Inches(0.7))
    sp = sub.text_frame.paragraphs[0]
    sp.text = "Extensible Agentic Operations Platform on Azure"
    sp.font.size = Pt(22); sp.font.color.rgb = RGBColor(0x93, 0xC5, 0xFD)
    tag = s.shapes.add_textbox(Inches(0.65), Inches(3.8), Inches(8.7), Inches(1.5))
    tp = tag.text_frame.paragraphs[0]
    tp.text = (
        "One platform  •  Many problems  •  Many systems  •  Measurable savings\n"
        "ELK  |  ServiceNow  |  Azure  |  SecureBank  |  Future-ready integrations"
    )
    tp.font.size = Pt(13); tp.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)

    # ── SLIDE 2: Vision ─────────────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "1. Vision — A Platform, Not a Point Fix")
    bullets(s, [
        "AIR is an extensible Agentic Operations Platform — not a one-time fix for two incidents.",
        "It sits on top of your existing tools (ELK, ServiceNow, Azure) and connects them through a smart automation layer.",
        "Today it resolves incidents faster. Tomorrow it can handle change risk, capacity, security, and compliance — same platform.",
        "Think of it as an 'automation fabric': plug in a new system, define a playbook, and the agents take care of the rest.",
        "Built for banking: safe telemetry, human approval where needed, and full audit for regulators.",
        "Goal: save time, cut manual cost, and keep digital banking services always available.",
    ], sz=15)

    # ── SLIDE 3: Problem Statement (extensive) ──────────────────────
    s = blank(prs); bg(s); bar(s, "2. Problem Statement — What Hurts Banks Today", "Multiple pain areas — one common root cause: tools don't talk to each other")
    cols(s,
        "Operational Problems",
        [
            "Incidents detected in ELK but resolved manually in ServiceNow — slow handoffs.",
            "Same failures repeat: DB pool full, API latency, cache miss, pod crash.",
            "Engineers jump between 5–8 tools per incident — high MTTR (45–120 min).",
            "Runbooks live in documents; knowledge leaves when people leave.",
            "Night/weekend pages for issues that could auto-heal safely.",
        ],
        "Business & Other Problems",
        [
            "Downtime on transfer/payment flows = SLA fines + customer churn.",
            "Security spikes (login fraud) need AppOps + SecOps — no shared workflow.",
            "Change deployments cause 60%+ of outages — no auto link to observability.",
            "Compliance needs proof of every action — manual reports take days.",
            "Each new tool (Datadog, PagerDuty, Jira) adds cost but not connected value.",
        ])

    # ── SLIDE 4: Why current approach fails ─────────────────────────
    s = blank(prs); bg(s); bar(s, "3. Why Current Tools Alone Are Not Enough")
    bullets(s, [
        "ELK/Kibana is excellent at SEEING problems — logs, metrics, traces, synthetics, AIOps correlation.",
        "ServiceNow is excellent at TRACKING work — incidents, changes, CMDB, approvals.",
        "Azure runs the application — but neither ELK nor SNOW can safely ACT on the infrastructure.",
        "Gap: Detection → Investigation → Ticket → Manual fix → Audit = hours of delay and cost.",
        "Point automation scripts break when systems change — they are not reusable or governed.",
        "What is missing: a central, extensible brain that connects all systems and acts with control.",
    ], sz=14)

    # ── SLIDE 5: Solution Overview ──────────────────────────────────
    s = blank(prs); bg(s); bar(s, "4. Solution — SecureBank AIR Platform", "Extensible by design: new problems and systems plug in without rebuilding")
    bullets(s, [
        "AIR = Agentic Intelligence & Response — an Azure-hosted platform with multi-agent automation.",
        "Pluggable Integration Hub: connect ELK, ServiceNow, Azure, Teams today; add Splunk, PagerDuty, Jira tomorrow.",
        "Problem Catalog: pre-built playbooks for incidents, security, performance, change — add custom ones easily.",
        "Multi-Agent Engine: Triage → Correlate → Decide → Act → Audit — same flow for every problem type.",
        "Operations Command Portal: one formal UI for NOC, SRE, SOC, and management — approvals, reasoning, reports.",
        "Policy Engine: auto-fix low-risk issues; require human approval for high-risk; everything logged.",
    ], sz=14)

    # ── SLIDE 6: Platform Architecture Diagram ───────────────────────
    s = blank(prs); bg(s); bar(s, "5. Platform Architecture — Layered & Extensible")
    layer_diagram(s)
    bullets(s, [
        "Each layer is independent — upgrade agents, add integrations, or extend UI without touching other layers.",
    ], top=5.55, sz=12)

    # ── SLIDE 7: Integration Hub Diagram ────────────────────────────
    s = blank(prs); bg(s); bar(s, "6. Multi-System Integration Hub", "Works with what you have — extensible to what you add")
    hub_diagram(s)
    bullets(s, [
        "Adapter pattern: each system connects via API/webhook. New system = new adapter, not a new project.",
        "SecureBank app, ELK observability, SNOW ITSM, Azure infra — all orchestrated from one hub.",
    ], top=6.05, sz=11)

    # ── SLIDE 8: Phase 1 Scope (3 problems only) ────────────────────
    s = blank(prs); bg(s); bar(s, "7. Phase 1 Scope — 3 Problems We Build First", "Feasible, real, and doable — same platform grows in Phase 2")
    cols(s,
        "Phase 1 — Build & Prove (3 Problems)",
        [
            "Problem 1: Transfer Service Failure — 5xx errors + DB pool full (from reference RCA scenario).",
            "Problem 2: Failed Login Spike — unusual failed logins / suspicious access (from reference security alerts).",
            "Problem 3: Service Down — auth or API unavailable (from reference critical alert).",
            "For each: ELK detects → agent finds cause → SNOW ticket auto-created → fix with approval.",
            "Uses existing SecureBank + ELK alerts — no new monitoring setup needed.",
        ],
        "Phase 2 — Extend Later (Same Platform)",
        [
            "P95 latency / performance tuning alerts.",
            "Change deployment ↔ incident linking.",
            "Capacity forecasting and cloud cost savings.",
            "Compliance report automation.",
            "More tools: PagerDuty, Jira, Splunk, Datadog adapters.",
            "Advanced dashboards — only after Phase 1 is stable.",
        ])

    # ── SLIDE 9: Multi-Agent Engine ─────────────────────────────────
    s = blank(prs); bg(s); bar(s, "8. Multi-Agent Engine — One Brain, Many Jobs")
    agents = ["Triage\nAgent", "Correlation\nAgent", "Decision\nAgent", "Remediation\nAgent", "Compliance\nAgent"]
    for i, a in enumerate(agents):
        box(s, a, 0.4 + i * 1.85, 1.3, w=1.55, h=0.75, fill=NAVY if i % 2 == 0 else TEAL, fsize=9)
        if i < len(agents) - 1:
            arrow(s, 1.9 + i * 1.85, 1.58)
    bullets(s, [
        "Agents share a Tool Registry: query ELK, create SNOW ticket, restart AKS pod, send Teams alert, search runbooks.",
        "New problem domain = new agent skill + playbook — the engine stays the same.",
        "Human-in-the-loop: agents recommend; humans approve high-risk actions; low-risk runs automatically.",
        "Every agent decision is explainable in plain English for NOC and audit teams.",
    ], top=2.35, sz=13)

    # ── SLIDE 10: End-to-End Flow Diagram ───────────────────────────
    s = blank(prs); bg(s); bar(s, "9. How It Works — Universal Flow for Any Problem")
    flow_diagram(s)
    cols(s,
        "Example: Transfer API Down",
        [
            "ELK alert: 5xx rate high + DB pool 98%.",
            "Agents correlate → root cause: connection pool.",
            "SNOW SEV-2 created with full context.",
            "Pool scaled + pods restarted → recovered in ~12 min.",
        ],
        "Example: Login Fraud Spike",
        [
            "ELK security event: failed logins 10x normal.",
            "Agents correlate IP + geo + device signals.",
            "Rate-limit applied + SecOps SNOW task opened.",
            "Sessions revoked for flagged accounts → contained in ~5 min.",
        ], top=3.1)

    # ── SLIDE 11: Simple UI (Phase 1 — 3 screens only) ──────────────
    s = blank(prs); bg(s); bar(s, "10. Simple UI for Phase 1 — 3 Screens Only", "Clean, formal, easy — no complex admin panels in v1")
    screens = [
        ("Screen 1\nIncident List", "Open | In Progress | Resolved\nSeverity + Service + Time", ACCENT),
        ("Screen 2\nIncident Detail", "What happened\nRoot cause (plain English)\nWhat agent recommends", TEAL),
        ("Screen 3\nApprove Action", "Approve  |  Deny\nOne-click fix\nAudit log auto-saved", GREEN),
    ]
    for i, (title, desc, color) in enumerate(screens):
        l = 0.55 + i * 3.1
        box(s, title, l, 1.3, w=2.75, h=0.85, fill=color, fsize=10)
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(2.25), Inches(2.75), Inches(1.35))
        card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = BORDER
        tb = s.shapes.add_textbox(Inches(l + 0.12), Inches(2.38), Inches(2.5), Inches(1.1))
        p = tb.text_frame.paragraphs[0]; p.text = desc; p.font.size = Pt(11); p.font.color.rgb = SLATE
        if i < 2:
            arrow(s, l + 2.85, 1.55)
    bullets(s, [
        "No complex menus, no admin config screens, no executive dashboards in Phase 1.",
        "Engineers open the portal → see incidents → read cause → click Approve. That is it.",
        "Kibana stays the deep-dive tool; this portal is the action and tracking layer.",
        "Phase 2 adds: KPI dashboard, playbook editor, multi-system views.",
    ], top=3.85, sz=12)

    # ── SLIDE 12: Business Impact & ROI ─────────────────────────────
    s = blank(prs); bg(s); bar(s, "11. Business Impact — Time & Money Saved", "Quantifiable value for operations and business leadership")
    impact_cards(s)
    bullets(s, [
        "MTTR: from 60–90 min manual → 10–20 min agent-assisted = 60–80% faster recovery.",
        "Manual toil: 40% fewer L1/L2 tickets through auto-enrichment and auto-resolution of repeat issues.",
        "On-call load: 50% reduction in night/weekend pages for known, auto-healable problems.",
        "Tool ROI: unlock full value from existing ELK + SNOW + Azure spend — no rip-and-replace.",
        "Downtime cost: even 1 hour/month saved on payment APIs can mean $500K+ for a mid-size bank.",
        "Compliance: audit reports in minutes, not days — reduces regulatory risk and audit prep cost.",
        "Extensibility: each new use case added at low marginal cost — platform pays back faster over time.",
    ], top=2.65, sz=12)

    # ── SLIDE 13: Security & Governance ─────────────────────────────
    s = blank(prs); bg(s); bar(s, "12. Security, Compliance & Governance")
    cols(s,
        "Banking-Grade Controls",
        [
            "No PII, account numbers, or payment data in ELK or agent logs.",
            "Azure Entra ID RBAC — role-based views and approval rights.",
            "Key Vault for secrets; managed identities for all service calls.",
            "Policy engine: whitelist auto-actions vs approval-required actions.",
            "Immutable audit log — every agent action stored 7+ years.",
        ],
        "Trust & Transparency",
        [
            "Agents explain every decision in plain language — no black box.",
            "Human override always available — automation assists, never replaces control.",
            "Rollback built into every remediation playbook.",
            "Regulator-ready export: incident timeline, actions, approvers, evidence.",
            "Secure telemetry only: counts, masked IDs, latency, status codes.",
        ])

    # ── SLIDE 14: Future Roadmap ────────────────────────────────────
    s = blank(prs); bg(s); bar(s, "13. Future Scope & Enhancements", "Same platform grows with your needs — no new silos")
    roadmap_diagram(s)
    bullets(s, [
        "Phase 1 (Now): 3 problems — transfer failure, login spike, service down. ELK + SNOW + Azure + simple UI.",
        "Phase 2 (Next): Add latency alerts, change intelligence, capacity ops, richer dashboards.",
        "Phase 3 (Future): Compliance automation, multi-vendor adapters, customer-impact scoring.",
        "Same platform code — each phase adds playbooks and UI screens, not a rebuild.",
    ], top=3.65, sz=12)

    # ── SLIDE 15: Implementation & Outcome ──────────────────────────
    s = blank(prs); bg(s); bar(s, "14. Phase 1 Implementation — Realistic & Doable")
    steps = [
        ("Wk 1-2", "SecureBank\non Azure AKS"),
        ("Wk 3-4", "ELK alerts\n→ webhook"),
        ("Wk 5-6", "ServiceNow\n+ 3 playbooks"),
        ("Wk 7-8", "Simple UI\n+ demo"),
    ]
    for i, (ph, desc) in enumerate(steps):
        box(s, ph, 0.55 + i * 2.25, 1.25, w=0.95, h=0.42, fill=ACCENT, fsize=9)
        card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.55 + i * 2.25), Inches(1.75), Inches(1.85), Inches(0.85))
        card.fill.solid(); card.fill.fore_color.rgb = WHITE; card.line.color.rgb = BORDER
        tb = s.shapes.add_textbox(Inches(0.65 + i * 2.25), Inches(1.88), Inches(1.65), Inches(0.65))
        p = tb.text_frame.paragraphs[0]; p.text = desc; p.font.size = Pt(10); p.font.color.rgb = SLATE; p.alignment = PP_ALIGN.CENTER
        if i < 3:
            arrow(s, 2.35 + i * 2.25, 2.0)

    bullets(s, [
        "Phase 1 deliverable: working demo of 3 problems end-to-end in ~8 weeks.",
        "Stack: SecureBank (AKS) + ELK (existing) + ServiceNow (REST API) + Azure Functions + simple React UI.",
        "Outcome: Detect → ticket → fix → audit — proven for 3 cases, ready to extend in Phase 2.",
    ], top=2.85, sz=14)

    # Fix slide count: user asked max 15. We have 15 content areas but labeled 14 on last - that's 15 slides total (1 title + 14 numbered = 15). Good.

    prs.save(OUTPUT)
    print(f"Saved: {OUTPUT}  ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
