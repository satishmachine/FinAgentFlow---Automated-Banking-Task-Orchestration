"""
Generates Project_Documents/project_explained.pdf — a visual, slide-style
explainer of FinAgentFlow intended for an internship presentation.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mp
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path("Project_Documents/project_explained.pdf")

# Palette
C_BG      = "#f4f6fa"
C_PRIMARY = "#1f3a93"
C_ACCENT  = "#f39c12"
C_TEAL    = "#16a085"
C_DARK    = "#2c3e50"
C_MUTED   = "#7f8c8d"
C_SOFT    = "#ecf0f1"
C_RED     = "#c0392b"


def new_slide(title: str | None = None) -> tuple[plt.Figure, plt.Axes]:
    fig = plt.figure(figsize=(13.33, 7.5))  # 16:9 presentation size
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    # Background
    ax.add_patch(mp.Rectangle((0, 0), 100, 100, color=C_BG, zorder=0))
    # Top color band
    ax.add_patch(mp.Rectangle((0, 92), 100, 8, color=C_PRIMARY, zorder=1))
    if title:
        ax.text(
            3, 96, title,
            fontsize=22, color="white", weight="bold",
            ha="left", va="center", zorder=2,
        )
        ax.text(
            97, 96, "FinAgentFlow",
            fontsize=11, color="white", alpha=0.85,
            ha="right", va="center", zorder=2,
        )
    # Bottom footer strip
    ax.add_patch(mp.Rectangle((0, 0), 100, 3, color=C_DARK, zorder=1))
    ax.text(
        50, 1.5, "Automated Banking Task Orchestration  •  Internship Project",
        fontsize=8, color="white", ha="center", va="center", zorder=2,
    )
    return fig, ax


def box(ax, x, y, w, h, text, color=C_PRIMARY, text_color="white",
        fs=12, weight="bold", rounding=0.04):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={rounding}",
        facecolor=color, edgecolor="none", zorder=3,
    ))
    ax.text(x + w / 2, y + h / 2, text, color=text_color,
            fontsize=fs, ha="center", va="center",
            weight=weight, zorder=4, wrap=True)


def arrow(ax, x1, y1, x2, y2, color=C_DARK, lw=2.0):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=18,
        color=color, linewidth=lw, zorder=2,
    ))


def body_text(ax, x, y, text, fs=14, color=C_DARK, weight="normal",
              ha="left", va="top"):
    ax.text(x, y, text, fontsize=fs, color=color,
            weight=weight, ha=ha, va=va, zorder=3)


# ---------------------------------------------------------------------------
# Slide 1 — Title
# ---------------------------------------------------------------------------
def slide_title(pdf: PdfPages) -> None:
    fig = plt.figure(figsize=(13.33, 7.5))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    ax.add_patch(mp.Rectangle((0, 0), 100, 100, color=C_PRIMARY))
    ax.add_patch(mp.Rectangle((0, 0), 100, 10, color=C_ACCENT))
    ax.text(50, 70, "FinAgentFlow", fontsize=56, color="white",
            ha="center", va="center", weight="bold")
    ax.text(50, 60, "Automated Banking Task Orchestration",
            fontsize=22, color="white", alpha=0.9, ha="center", va="center")
    ax.text(50, 48, "An AI-powered assistant that runs routine bank work",
            fontsize=16, color="white", alpha=0.75, ha="center", va="center")
    # Icon row
    icons = [("$",  "Banking"), ("AI", "AI Agents"),
             ("⇄",  "Workflow"), ("■",  "Reports")]
    for i, (em, lbl) in enumerate(icons):
        cx = 20 + i * 20
        ax.add_patch(mp.Circle((cx, 30), 5.5, color=C_ACCENT, zorder=2))
        ax.text(cx, 30, em, fontsize=28, color="white", weight="bold",
                ha="center", va="center", zorder=3)
        ax.text(cx, 20, lbl, fontsize=13, color="white", ha="center", va="center")
    ax.text(50, 6, "Project Explainer  •  For Internship Presentation",
            fontsize=12, color="white", alpha=0.8, ha="center", va="center")
    pdf.savefig(fig); plt.close(fig)


# ---------------------------------------------------------------------------
# Slide 2 — What is it (plain English + analogy)
# ---------------------------------------------------------------------------
def slide_what(pdf: PdfPages) -> None:
    fig, ax = new_slide("What is FinAgentFlow?")
    body_text(ax, 5, 85,
              "A Python platform that turns a list of banking tasks into an\n"
              "automated workflow — with AI writing the summary at the end.",
              fs=18, weight="bold")
    # Analogy block
    ax.add_patch(FancyBboxPatch(
        (5, 45), 42, 32, boxstyle="round,pad=0.02,rounding_size=0.04",
        facecolor="white", edgecolor=C_MUTED, zorder=2))
    ax.text(26, 73, "Think of it as…", fontsize=15,
            color=C_PRIMARY, weight="bold", ha="center")
    ax.text(26, 60,
            "A diligent bank clerk who, every quarter:\n\n"
            "1. Matches the ledger against the bank statement\n"
            "2. Runs compliance checks on the results\n"
            "3. Drafts a customer letter about it\n\n"
            "FinAgentFlow does the same, automatically.",
            fontsize=13, color=C_DARK, ha="center", va="center")
    # Right panel: what it isn't
    ax.add_patch(FancyBboxPatch(
        (53, 45), 42, 32, boxstyle="round,pad=0.02,rounding_size=0.04",
        facecolor=C_SOFT, edgecolor=C_MUTED, zorder=2))
    ax.text(74, 73, "What it is NOT", fontsize=15,
            color=C_RED, weight="bold", ha="center")
    ax.text(74, 60,
            "✗ Not a real core-banking system\n"
            "✗ Not connected to live customer data\n"
            "✗ Not a replacement for human approval\n\n"
            "It is a proof-of-concept showing how\n"
            "agentic AI can orchestrate bank-style tasks.",
            fontsize=13, color=C_DARK, ha="center", va="center")
    # Bottom takeaway
    ax.add_patch(FancyBboxPatch(
        (5, 12), 90, 28, boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor=C_PRIMARY, edgecolor="none", zorder=2))
    ax.text(50, 32, "One-liner",
            fontsize=13, color="white", alpha=0.8, ha="center", weight="bold")
    ax.text(50, 22,
            '"Define banking tasks → the system runs them in order → AI writes the report."',
            fontsize=18, color="white", ha="center", va="center", style="italic")
    pdf.savefig(fig); plt.close(fig)


# ---------------------------------------------------------------------------
# Slide 3 — Real-world example: Quarterly banking review
# ---------------------------------------------------------------------------
def slide_example(pdf: PdfPages) -> None:
    fig, ax = new_slide("A Real-World Example")
    body_text(ax, 5, 86,
              "Scenario: a bank wants to close the books on Q1 2026.",
              fs=17, weight="bold")
    body_text(ax, 5, 80,
              "FinAgentFlow runs three connected tasks automatically:",
              fs=14, color=C_MUTED)

    # 3 step cards
    cards = [
        ("①  Reconcile", "Compare ledger\nvs. bank statement",
         "Input: 2 CSV/JSON files\nOutput: matched, unmatched,\ndiscrepancies", C_PRIMARY),
        ("②  Compliance", "Run AML / rule checks\non the reconciled data",
         "Input: step ① output\nOutput: pass/fail,\nviolations list", C_TEAL),
        ("③  Communication", "Draft a customer notice\nfor the quarter",
         "Input: step ② output\nOutput: letter text,\nsections", C_ACCENT),
    ]
    for i, (title, sub, io, col) in enumerate(cards):
        x = 5 + i * 32
        # Card
        ax.add_patch(FancyBboxPatch(
            (x, 28), 28, 46,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor="white", edgecolor=col, linewidth=2, zorder=2))
        # Header strip
        ax.add_patch(mp.Rectangle((x, 66), 28, 8, color=col, zorder=3))
        ax.text(x + 14, 70, title, fontsize=17, color="white",
                weight="bold", ha="center", va="center", zorder=4)
        ax.text(x + 14, 58, sub, fontsize=13, color=C_DARK,
                ha="center", va="center", weight="bold")
        ax.text(x + 14, 42, io, fontsize=11, color=C_MUTED,
                ha="center", va="center")
        # Arrow to next card
        if i < 2:
            arrow(ax, x + 28.5, 51, x + 31.5, 51, color=col, lw=3)

    # Final output block
    ax.add_patch(FancyBboxPatch(
        (5, 8), 90, 15, boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor=C_PRIMARY, edgecolor="none", zorder=2))
    ax.text(12, 15.5, "≡", fontsize=30, color=C_ACCENT,
            weight="bold", ha="center", va="center")
    ax.text(50, 18, "Final deliverable",
            fontsize=13, color="white", alpha=0.8, ha="center", weight="bold")
    ax.text(50, 12.5,
            "An AI-written executive summary PDF covering all three steps, saved as an artifact.",
            fontsize=13, color="white", ha="center", va="center")
    pdf.savefig(fig); plt.close(fig)


# ---------------------------------------------------------------------------
# Slide 4 — Architecture (the 6 HLD modules)
# ---------------------------------------------------------------------------
def slide_architecture(pdf: PdfPages) -> None:
    fig, ax = new_slide("How It Is Built  —  6 Layers")
    body_text(ax, 5, 86,
              "Each layer has a single responsibility. Data flows top-to-bottom.",
              fs=14, color=C_MUTED)

    layers = [
        ("1. User Interface",      "Streamlit web UI",              C_ACCENT),
        ("2. API Layer",           "FastAPI REST endpoints",        C_TEAL),
        ("3. Orchestration Engine","LangGraph workflow + deps",     C_PRIMARY),
        ("4. Task Agents",         "Reconcile • Compliance • Comm", C_PRIMARY),
        ("5. AI Generation",       "EuriAI (gpt-4.1-nano)",         C_TEAL),
        ("6. Storage & Logging",   "Artifacts (JSON/CSV) + audit",  C_DARK),
    ]
    y0, h = 78, 9
    for i, (name, desc, col) in enumerate(layers):
        y = y0 - (i + 1) * (h + 1.5)
        ax.add_patch(FancyBboxPatch(
            (15, y), 55, h,
            boxstyle="round,pad=0.02,rounding_size=0.04",
            facecolor=col, edgecolor="none", zorder=3))
        ax.text(17, y + h / 2, name, fontsize=14, color="white",
                weight="bold", ha="left", va="center")
        ax.text(68, y + h / 2, desc, fontsize=12, color="white",
                alpha=0.95, ha="right", va="center", style="italic")
        # Small arrow between layers
        if i < len(layers) - 1:
            arrow(ax, 42.5, y, 42.5, y - 1.5, color=C_MUTED, lw=1.5)

    # Side callouts
    ax.text(75, 65, "User types", fontsize=11, color=C_MUTED, weight="bold")
    ax.text(75, 60, "↑ clicks in\n   browser", fontsize=11, color=C_DARK)
    ax.text(75, 22, "Files on disk", fontsize=11, color=C_MUTED, weight="bold")
    ax.text(75, 17, "↓ reports &\n   audit logs", fontsize=11, color=C_DARK)
    pdf.savefig(fig); plt.close(fig)


# ---------------------------------------------------------------------------
# Slide 5 — The 3 banking agents
# ---------------------------------------------------------------------------
def slide_agents(pdf: PdfPages) -> None:
    fig, ax = new_slide("Meet the Banking Agents")
    body_text(ax, 5, 86,
              "Every task in a workflow is handled by one specialist agent.\n"
              "New agent types can be added without changing the core engine.",
              fs=14, color=C_MUTED)

    agents = [
        ("◉", "ReconcileAgent",
         "Matches transactions between two\nsources (e.g. ledger vs bank).\n\n"
         "Detects: matched, unmatched,\namount discrepancies.",
         C_PRIMARY),
        ("◆", "ComplianceAgent",
         "Runs rule-based AML and policy\nchecks on task input data.\n\n"
         "Outputs: pass/fail status,\nlist of violations.",
         C_TEAL),
        ("@", "CommunicationAgent",
         "Uses the AI generation layer to\ndraft customer-facing text.\n\n"
         "Outputs: letter text, subject,\nsection breakdown.",
         C_ACCENT),
    ]
    for i, (icon, name, body, col) in enumerate(agents):
        x = 5 + i * 32
        ax.add_patch(FancyBboxPatch(
            (x, 18), 28, 58,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor="white", edgecolor=col, linewidth=2, zorder=2))
        # Icon circle
        ax.add_patch(mp.Circle((x + 14, 64), 5.5, color=col, zorder=3))
        ax.text(x + 14, 64, icon, fontsize=30, color="white", weight="bold",
                ha="center", va="center", zorder=4)
        ax.text(x + 14, 52, name, fontsize=16, color=col, weight="bold",
                ha="center", va="center")
        ax.text(x + 14, 35, body, fontsize=12, color=C_DARK,
                ha="center", va="center")

    ax.text(50, 12,
            "All three inherit from a common TaskAgent base class "
            "(abstract execute + log_step).",
            fontsize=11, color=C_MUTED, ha="center", style="italic")
    pdf.savefig(fig); plt.close(fig)


# ---------------------------------------------------------------------------
# Slide 6 — Workflow as a DAG (dependency diagram)
# ---------------------------------------------------------------------------
def slide_dag(pdf: PdfPages) -> None:
    fig, ax = new_slide("A Workflow Is a Graph of Tasks")
    body_text(ax, 5, 86,
              "Each task declares its dependencies. The system figures out the order "
              "and runs them through LangGraph.",
              fs=13, color=C_MUTED)

    # Example DAG
    nodes = {
        "Reconcile":  (15, 55, C_PRIMARY),
        "Compliance": (40, 65, C_TEAL),
        "Fraud Scan": (40, 45, C_TEAL),
        "Draft Letter": (65, 55, C_ACCENT),
        "Archive":    (88, 55, C_DARK),
    }
    for name, (x, y, col) in nodes.items():
        ax.add_patch(mp.Circle((x, y), 6, color=col, zorder=3))
        ax.text(x, y, name, fontsize=10, color="white",
                weight="bold", ha="center", va="center", zorder=4)

    # Edges
    edges = [
        ("Reconcile", "Compliance"), ("Reconcile", "Fraud Scan"),
        ("Compliance", "Draft Letter"), ("Fraud Scan", "Draft Letter"),
        ("Draft Letter", "Archive"),
    ]
    for a, b in edges:
        x1, y1, _ = nodes[a]; x2, y2, _ = nodes[b]
        arrow(ax, x1 + 6, y1, x2 - 6, y2, color=C_MUTED, lw=2)

    # Side explanation
    ax.add_patch(FancyBboxPatch(
        (5, 12), 90, 20, boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor="white", edgecolor=C_MUTED, zorder=2))
    ax.text(8, 27, "Rules enforced automatically:",
            fontsize=13, color=C_PRIMARY, weight="bold")
    ax.text(8, 22,
            "✓ Topological sort (Kahn's algorithm) picks the execution order\n"
            "✓ Circular or self-dependencies are rejected at create-time\n"
            "✓ 'Continue on failure' mode is supported: one bad task does not kill the workflow",
            fontsize=12, color=C_DARK, va="top")
    pdf.savefig(fig); plt.close(fig)


# ---------------------------------------------------------------------------
# Slide 7 — Technology stack
# ---------------------------------------------------------------------------
def slide_tech(pdf: PdfPages) -> None:
    fig, ax = new_slide("Technology Stack")
    body_text(ax, 5, 86,
              "Everything is Python. No heavy infrastructure required to run locally.",
              fs=13, color=C_MUTED)

    tiles = [
        ("Py", "Python 3.10+",        "Language",              C_PRIMARY),
        ("⇄",  "LangGraph",           "Workflow engine",       C_PRIMARY),
        ("»",  "FastAPI",             "REST API + Swagger",    C_TEAL),
        ("♦",  "Streamlit",           "Web UI",                C_ACCENT),
        ("AI", "EuriAI  gpt-4.1-nano","AI text generation",    C_TEAL),
        ("▲",  "Pydantic v2",         "Data models + config",  C_PRIMARY),
        ("■",  "Local filesystem",    "Artifact storage",      C_DARK),
        ("≡",  "Python logging",      "Per-workflow audit",    C_DARK),
        ("✓",  "pytest  (27 tests)",  "Unit + integration",    C_TEAL),
    ]
    for i, (icon, name, desc, col) in enumerate(tiles):
        r, c = divmod(i, 3)
        x = 6 + c * 30
        y = 66 - r * 20
        ax.add_patch(FancyBboxPatch(
            (x, y), 28, 16,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor="white", edgecolor=col, linewidth=2, zorder=2))
        ax.add_patch(mp.Circle((x + 4.5, y + 8), 2.8, color=col, zorder=3))
        ax.text(x + 4.5, y + 8, icon, fontsize=13, color="white",
                weight="bold", ha="center", va="center", zorder=4)
        ax.text(x + 17, y + 11, name, fontsize=13, color=col,
                weight="bold", ha="left", va="center")
        ax.text(x + 17, y + 5, desc, fontsize=11, color=C_MUTED,
                ha="left", va="center")
    pdf.savefig(fig); plt.close(fig)


# ---------------------------------------------------------------------------
# Slide 8 — Core features (simplified FRs)
# ---------------------------------------------------------------------------
def slide_features(pdf: PdfPages) -> None:
    fig, ax = new_slide("What You Can Do With It")
    features = [
        ("≡", "Define your own workflow",
         "via a form in the browser or a REST call"),
        ("►", "Execute it end-to-end",
         "tasks run in dependency order on LangGraph"),
        ("AI", "Get an AI-written summary",
         "after every task and one final executive report"),
        ("□", "Download structured outputs",
         "JSON, CSV and report files per task"),
        ("≣", "See a full audit trail",
         "every step logged to a per-workflow log file"),
        ("+", "Plug in new task types",
         "subclass TaskAgent — no core code change needed"),
    ]
    for i, (icon, title, desc) in enumerate(features):
        r, c = divmod(i, 2)
        x = 5 + c * 46
        y = 70 - r * 20
        ax.add_patch(FancyBboxPatch(
            (x, y), 44, 16,
            boxstyle="round,pad=0.02,rounding_size=0.04",
            facecolor="white", edgecolor=C_PRIMARY, linewidth=1.5, zorder=2))
        ax.add_patch(mp.Circle((x + 5, y + 8), 3.2, color=C_PRIMARY, zorder=3))
        ax.text(x + 5, y + 8, icon, fontsize=14, color="white",
                weight="bold", ha="center", va="center", zorder=4)
        ax.text(x + 11, y + 11, title, fontsize=14, color=C_PRIMARY,
                weight="bold", ha="left", va="center")
        ax.text(x + 11, y + 5, desc, fontsize=11, color=C_DARK,
                ha="left", va="center")
    pdf.savefig(fig); plt.close(fig)


# ---------------------------------------------------------------------------
# Slide 9 — End-to-end data flow
# ---------------------------------------------------------------------------
def slide_flow(pdf: PdfPages) -> None:
    fig, ax = new_slide("End-to-End Data Flow")
    body_text(ax, 5, 86,
              "What happens, in order, when you hit “Execute Workflow”:",
              fs=14, color=C_MUTED)

    steps = [
        ("1", "User submits",   "workflow + input\n(UI / API)",        C_ACCENT),
        ("2", "Validate",       "dependency graph\n+ Pydantic schema", C_TEAL),
        ("3", "Build graph",    "LangGraph StateGraph\n(one node / task)", C_PRIMARY),
        ("4", "Run agents",     "each agent does\nits banking logic", C_PRIMARY),
        ("5", "AI summary",     "EuriAI generates\nper-task summary", C_TEAL),
        ("6", "Save artifacts", "JSON / CSV / report\nto disk",        C_DARK),
        ("7", "Final report",   "AI writes the\nexecutive summary",   C_ACCENT),
    ]
    n = len(steps)
    col_w = 90 / n
    for i, (num, title, desc, col) in enumerate(steps):
        cx = 5 + i * col_w + col_w / 2
        # Circle number
        ax.add_patch(mp.Circle((cx, 60), 5, color=col, zorder=3))
        ax.text(cx, 60, num, fontsize=18, color="white",
                weight="bold", ha="center", va="center", zorder=4)
        # Title + desc
        ax.text(cx, 50, title, fontsize=12, color=C_DARK,
                weight="bold", ha="center", va="center")
        ax.text(cx, 42, desc, fontsize=10, color=C_MUTED,
                ha="center", va="center")
        # Arrow to next
        if i < n - 1:
            arrow(ax, cx + 5, 60, cx + col_w - 5, 60, color=C_MUTED, lw=2)

    # Bottom emphasis
    ax.add_patch(FancyBboxPatch(
        (5, 12), 90, 20, boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor=C_PRIMARY, edgecolor="none", zorder=2))
    ax.text(8, 27, "Throughout the whole flow:",
            fontsize=13, color="white", weight="bold")
    ax.text(8, 22,
            "•  Every step is written to  logs/audit/workflow_<id>.log  for full auditability\n"
            "•  Failures either abort the workflow  OR  continue-on-failure (configurable per workflow)\n"
            "•  AI calls retry with exponential backoff; artifact writes retry + fall back to a safe directory",
            fontsize=11, color="white", va="top")
    pdf.savefig(fig); plt.close(fig)


# ---------------------------------------------------------------------------
# Slide 10 — What the user gets (outputs)
# ---------------------------------------------------------------------------
def slide_outputs(pdf: PdfPages) -> None:
    fig, ax = new_slide("What the User Gets Back")
    body_text(ax, 5, 86,
              "Everything is downloadable from the Streamlit UI and from the REST API.",
              fs=14, color=C_MUTED)

    outputs = [
        ("■",  "Structured data",
         "JSON / CSV per task:\nmatched / unmatched records,\ncompliance violations, letter JSON."),
        ("AI", "AI summaries",
         "Human-readable text produced by\nEuriAI for each task result."),
        ("≡",  "Final executive report",
         "One consolidated report covering\nall tasks, generated by AI at the end."),
        ("≣",  "Audit log",
         "Step-by-step timestamped log of the\nwhole execution — one file per run."),
    ]
    for i, (icon, title, desc) in enumerate(outputs):
        r, c = divmod(i, 2)
        x = 5 + c * 46
        y = 48 - r * 28
        ax.add_patch(FancyBboxPatch(
            (x, y), 44, 24,
            boxstyle="round,pad=0.02,rounding_size=0.04",
            facecolor="white", edgecolor=C_TEAL, linewidth=1.5, zorder=2))
        ax.add_patch(mp.Circle((x + 6, y + 16), 4.2, color=C_TEAL, zorder=3))
        ax.text(x + 6, y + 16, icon, fontsize=18, color="white",
                weight="bold", ha="center", va="center", zorder=4)
        ax.text(x + 12, y + 18, title, fontsize=15, color=C_TEAL,
                weight="bold", ha="left", va="center")
        ax.text(x + 12, y + 9, desc, fontsize=11, color=C_DARK,
                ha="left", va="top")

    # File path strip at bottom
    ax.add_patch(FancyBboxPatch(
        (5, 5), 90, 9, boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor=C_DARK, edgecolor="none", zorder=2))
    ax.text(8, 9.5, "On disk:", fontsize=11, color=C_ACCENT, weight="bold")
    ax.text(20, 9.5,
            "data/artifacts/<workflow_id>/<task_id>/*.json | *.csv   "
            "• data/logs/audit/workflow_<id>.log",
            fontsize=11, color="white", family="monospace", va="center")
    pdf.savefig(fig); plt.close(fig)


# ---------------------------------------------------------------------------
# Slide 11 — Takeaways
# ---------------------------------------------------------------------------
def slide_takeaways(pdf: PdfPages) -> None:
    fig, ax = new_slide("Takeaways for the Presentation")
    body_text(ax, 5, 86,
              "Three sentences you can open your demo with:",
              fs=14, color=C_MUTED)
    # Big quote
    ax.add_patch(FancyBboxPatch(
        (5, 58), 90, 22, boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor=C_PRIMARY, edgecolor="none", zorder=2))
    ax.text(10, 75, "“", fontsize=48, color=C_ACCENT, weight="bold",
            ha="left", va="top")
    ax.text(50, 69,
            "FinAgentFlow is an AI-driven Python platform that orchestrates\n"
            "routine banking tasks as a dependency-aware workflow\n"
            "and produces human-readable reports automatically.",
            fontsize=15, color="white", ha="center", va="center", style="italic")

    # Three-bullet summary
    bullets = [
        ("◆  Modular",
         "New task types plug in as\nsubclasses of TaskAgent."),
        ("★  AI-augmented",
         "Every task result carries a\ncontext-aware AI summary."),
        ("●  Auditable",
         "Per-workflow audit log is\nguaranteed — no silent runs."),
    ]
    for i, (t, d) in enumerate(bullets):
        x = 5 + i * 32
        ax.add_patch(FancyBboxPatch(
            (x, 18), 28, 34,
            boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor="white", edgecolor=C_PRIMARY, linewidth=1.5, zorder=2))
        ax.text(x + 14, 45, t, fontsize=16, color=C_PRIMARY,
                weight="bold", ha="center", va="center")
        ax.text(x + 14, 30, d, fontsize=12, color=C_DARK,
                ha="center", va="center")

    # Closing line
    ax.text(50, 9,
            "Aligned with the PRD, HLD and LLD  •  27/27 tests passing  •  "
            "UI + API fully wired",
            fontsize=11, color=C_MUTED, ha="center", style="italic")
    pdf.savefig(fig); plt.close(fig)


def add_all(pdf: PdfPages) -> None:
    slide_title(pdf)
    slide_what(pdf)
    slide_example(pdf)
    slide_architecture(pdf)
    slide_agents(pdf)
    slide_dag(pdf)
    slide_tech(pdf)
    slide_features(pdf)
    slide_flow(pdf)
    slide_outputs(pdf)
    slide_takeaways(pdf)


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(OUT) as pdf:
        add_all(pdf)
    print(f"wrote {OUT}")
