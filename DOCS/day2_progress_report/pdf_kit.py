"""Pista-green PDF kit for the SIH26153 Day 2 progress report."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    CondPageBreak,
    Flowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

PAGE_W, PAGE_H = A4
LEFT = 16 * mm
RIGHT = 16 * mm
TOP = 20 * mm
BOTTOM = 16 * mm
CONTENT_W = PAGE_W - LEFT - RIGHT

# Soft pista / pistachio palette — not neon.
PISTA_PAGE = HexColor("#F7FBF2")
PISTA_BAND = HexColor("#DCECC8")
PISTA_SOFT = HexColor("#EAF4DC")
PISTA_CARD = HexColor("#F4F9EC")
PISTA_MID = HexColor("#B7D39A")
PISTA_ACCENT = HexColor("#7FA85A")
FOREST = HexColor("#2E5A32")
FOREST_DARK = HexColor("#1C3C22")
FOREST_HEAD = HexColor("#355E35")
INK = HexColor("#243028")
MUTED = HexColor("#4F5D52")
RULE = HexColor("#C5D6B0")
WHITE = white
WARN_BG = HexColor("#FBF6E4")
WARN_EDGE = HexColor("#C4A35A")
WARN_INK = HexColor("#6B4E10")
LIMIT_BG = HexColor("#F8EBEB")
LIMIT_EDGE = HexColor("#B85C5C")
LIMIT_INK = HexColor("#7A2A2A")
OK_BG = HexColor("#E7F3E1")
OK_EDGE = HexColor("#4E8B45")
OK_INK = HexColor("#245528")
DAY3_BG = HexColor("#E8F1EA")
DAY3_EDGE = HexColor("#4F7D5C")
FIND_BG = HexColor("#EEF5E6")
FIND_EDGE = HexColor("#6B8F4E")
TABLE_HEAD = HexColor("#3A6B3C")
TABLE_STRIPE = HexColor("#F3F8EC")
H500_ROW = HexColor("#F6E4E4")

FONT_DIR = Path(r"C:\Windows\Fonts")


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Calibri", str(FONT_DIR / "calibri.ttf")))
    pdfmetrics.registerFont(TTFont("Calibri-Bold", str(FONT_DIR / "calibrib.ttf")))
    pdfmetrics.registerFont(TTFont("Calibri-Italic", str(FONT_DIR / "calibrii.ttf")))
    pdfmetrics.registerFont(TTFont("Calibri-BoldItalic", str(FONT_DIR / "calibriz.ttf")))
    pdfmetrics.registerFont(TTFont("Georgia", str(FONT_DIR / "georgia.ttf")))
    pdfmetrics.registerFont(TTFont("Georgia-Bold", str(FONT_DIR / "georgiab.ttf")))
    pdfmetrics.registerFont(TTFont("Consolas", str(FONT_DIR / "consola.ttf")))
    pdfmetrics.registerFontFamily(
        "Calibri",
        normal="Calibri",
        bold="Calibri-Bold",
        italic="Calibri-Italic",
        boldItalic="Calibri-BoldItalic",
    )


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover_kicker": ParagraphStyle(
            "cover_kicker",
            parent=base["Normal"],
            fontName="Calibri-Bold",
            fontSize=10,
            textColor=FOREST,
            tracking=1.4,
            alignment=TA_LEFT,
            spaceAfter=6,
        ),
        "cover_title": ParagraphStyle(
            "cover_title",
            parent=base["Normal"],
            fontName="Georgia-Bold",
            fontSize=26,
            leading=32,
            textColor=FOREST_DARK,
            spaceAfter=8,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            parent=base["Normal"],
            fontName="Calibri",
            fontSize=12,
            leading=17,
            textColor=MUTED,
            spaceAfter=4,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Normal"],
            fontName="Georgia-Bold",
            fontSize=16,
            leading=21,
            textColor=FOREST_DARK,
            spaceBefore=4,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Normal"],
            fontName="Calibri-Bold",
            fontSize=12.5,
            leading=16,
            textColor=FOREST_HEAD,
            spaceBefore=10,
            spaceAfter=5,
        ),
        "h3": ParagraphStyle(
            "h3",
            parent=base["Normal"],
            fontName="Calibri-Bold",
            fontSize=11,
            leading=14,
            textColor=FOREST,
            spaceBefore=8,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="Calibri",
            fontSize=10,
            leading=14,
            textColor=INK,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "body_left": ParagraphStyle(
            "body_left",
            parent=base["Normal"],
            fontName="Calibri",
            fontSize=10,
            leading=14,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "small",
            parent=base["Normal"],
            fontName="Calibri",
            fontSize=8.5,
            leading=12,
            textColor=MUTED,
            spaceAfter=3,
        ),
        "toc": ParagraphStyle(
            "toc",
            parent=base["Normal"],
            fontName="Calibri",
            fontSize=10.5,
            leading=16,
            textColor=INK,
            leftIndent=4,
        ),
        "cell": ParagraphStyle(
            "cell",
            parent=base["Normal"],
            fontName="Calibri",
            fontSize=8,
            leading=11,
            textColor=INK,
        ),
        "cell_c": ParagraphStyle(
            "cell_c",
            parent=base["Normal"],
            fontName="Calibri",
            fontSize=8,
            leading=11,
            textColor=INK,
            alignment=TA_CENTER,
        ),
        "cell_head": ParagraphStyle(
            "cell_head",
            parent=base["Normal"],
            fontName="Calibri-Bold",
            fontSize=8,
            leading=11,
            textColor=WHITE,
            alignment=TA_CENTER,
        ),
        "cell_head_l": ParagraphStyle(
            "cell_head_l",
            parent=base["Normal"],
            fontName="Calibri-Bold",
            fontSize=8,
            leading=11,
            textColor=WHITE,
        ),
        "mono": ParagraphStyle(
            "mono",
            parent=base["Normal"],
            fontName="Consolas",
            fontSize=7.6,
            leading=10.5,
            textColor=FOREST_DARK,
        ),
        "callout_title": ParagraphStyle(
            "callout_title",
            parent=base["Normal"],
            fontName="Calibri-Bold",
            fontSize=9,
            leading=12,
            textColor=FOREST_DARK,
            spaceAfter=2,
        ),
        "callout_body": ParagraphStyle(
            "callout_body",
            parent=base["Normal"],
            fontName="Calibri",
            fontSize=9,
            leading=12.5,
            textColor=INK,
        ),
        "q": ParagraphStyle(
            "q",
            parent=base["Normal"],
            fontName="Calibri-Bold",
            fontSize=9.5,
            leading=13,
            textColor=FOREST,
            spaceAfter=1,
        ),
        "a": ParagraphStyle(
            "a",
            parent=base["Normal"],
            fontName="Calibri",
            fontSize=9.5,
            leading=13,
            textColor=INK,
            spaceAfter=7,
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            fontName="Calibri",
            fontSize=8,
            textColor=MUTED,
        ),
        "caption": ParagraphStyle(
            "caption",
            parent=base["Normal"],
            fontName="Calibri-Italic",
            fontSize=8,
            leading=11,
            textColor=MUTED,
            spaceBefore=2,
            spaceAfter=8,
        ),
        "member_role": ParagraphStyle(
            "member_role",
            parent=base["Normal"],
            fontName="Calibri",
            fontSize=11,
            leading=14,
            textColor=MUTED,
            spaceAfter=8,
        ),
    }


S = None  # filled after register_fonts()


def init_styles() -> dict[str, ParagraphStyle]:
    global S
    register_fonts()
    S = _styles()
    return S


def P(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, S[style])


def spacer(h: float = 6) -> Spacer:
    return Spacer(1, h)


class HLine(Flowable):
    def __init__(self, width: float = CONTENT_W, color: Color = RULE, thickness: float = 0.7):
        super().__init__()
        self.line_width = width
        self.color = color
        self.thickness = thickness
        self.height = 4

    def wrap(self, aw, ah):
        return self.line_width, self.height

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 2, self.line_width, 2)


class SectionMarker(Flowable):
    """Records the page number for TOC."""

    registry: dict[str, int] = {}

    def __init__(self, key: str):
        super().__init__()
        self.key = key

    def wrap(self, aw, ah):
        return 0, 0

    def draw(self):
        SectionMarker.registry[self.key] = int(self.canv.getPageNumber())


def heading(level: int, text: str, key: str | None = None) -> list:
    items = []
    if key:
        items.append(SectionMarker(key))
    if level == 1:
        items.append(CondPageBreak(48 * mm))
        items.append(P(text, "h1"))
        items.append(HLine(color=PISTA_ACCENT, thickness=1.4))
        items.append(spacer(6))
    elif level == 2:
        items.append(P(text, "h2"))
    else:
        items.append(P(text, "h3"))
    return items


CALLOUT_THEME = {
    "verified": ("Verified result", OK_BG, OK_EDGE, OK_INK),
    "warning": ("Warning / limitation", WARN_BG, WARN_EDGE, WARN_INK),
    "limitation": ("Limitation", LIMIT_BG, LIMIT_EDGE, LIMIT_INK),
    "finding": ("Important finding", FIND_BG, FIND_EDGE, FOREST_DARK),
    "day3": ("Day 3 priority", DAY3_BG, DAY3_EDGE, FOREST_DARK),
}


def callout(kind: str, body: str, title: str | None = None) -> Table:
    label, bg, edge, ink = CALLOUT_THEME[kind]
    use_title = title or label
    title_style = ParagraphStyle(
        f"callout_title_{kind}",
        parent=S["callout_title"],
        textColor=ink,
    )
    inner = [
        [Paragraph(use_title.upper(), title_style)],
        [Paragraph(body, S["callout_body"])],
    ]
    t = Table(inner, colWidths=[CONTENT_W - 8])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("BOX", (0, 0), (-1, -1), 0.6, edge),
                ("LINEBEFORE", (0, 0), (0, -1), 3.2, edge),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (0, 0), 7),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
                ("TOPPADDING", (0, 1), (-1, 1), 1),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return KeepTogether([t])


def bullets(items: list[str], style: str = "body_left") -> ListFlowable:
    lis = [
        ListItem(Paragraph(item, S[style]), leftIndent=12, value="•")
        for item in items
    ]
    return ListFlowable(
        lis,
        bulletType="bullet",
        start="•",
        leftIndent=16,
        bulletFontName="Calibri",
        bulletFontSize=10,
        bulletColor=FOREST,
        spaceAfter=6,
    )


def simple_table(
    headers: list[str],
    rows: list[list[str]],
    col_widths: list[float] | None = None,
    highlight_last: bool = False,
    header_left: bool = False,
) -> Table:
    head_style = "cell_head_l" if header_left else "cell_head"
    data = [[P(h, head_style) for h in headers]]
    for row in rows:
        styled = []
        for i, cell in enumerate(row):
            st = "cell" if i == 0 and header_left else "cell_c" if not header_left else "cell"
            if i == 0:
                st = "cell"
            styled.append(P(str(cell), st))
        data.append(styled)
    n = len(headers)
    if col_widths is None:
        col_widths = [CONTENT_W / n] * n
    t = Table(data, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEAD),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Calibri-Bold"),
        ("BACKGROUND", (0, 1), (-1, -1), WHITE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, TABLE_STRIPE]),
        ("GRID", (0, 0), (-1, -1), 0.35, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]
    if highlight_last and len(rows) > 0:
        cmds.append(("BACKGROUND", (0, len(rows)), (-1, len(rows)), H500_ROW))
    t.setStyle(TableStyle(cmds))
    return t


def kv_table(pairs: list[tuple[str, str]], key_w: float = 62 * mm) -> Table:
    data = [[P(f"<b>{k}</b>", "cell"), P(v, "cell")] for k, v in pairs]
    t = Table(data, colWidths=[key_w, CONTENT_W - key_w])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), PISTA_SOFT),
                ("BACKGROUND", (1, 0), (1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.5, RULE),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def qa_block(questions: list[tuple[str, str]]) -> list:
    blocks = []
    for i, (q, a) in enumerate(questions, start=1):
        blocks.append(P(f"Q{i}. {q}", "q"))
        blocks.append(P(f"A. {a}", "a"))
    return blocks


def member_banner(name: str, role: str, status: str) -> Table:
    inner = [
        [
            P(name, "h1"),
        ],
        [P(role, "member_role")],
        [P(f"<b>Day 2 status:</b> {status}", "body_left")],
    ]
    t = Table(inner, colWidths=[CONTENT_W])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PISTA_SOFT),
                ("BOX", (0, 0), (-1, -1), 0.7, PISTA_ACCENT),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (0, 0), 10),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 0),
            ]
        )
    )
    return t


def draw_header_footer(canvas, doc, is_cover: bool = False) -> None:
    canvas.saveState()
    canvas.setFillColor(PISTA_PAGE)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Top pista band
    canvas.setFillColor(PISTA_BAND)
    canvas.rect(0, PAGE_H - 11 * mm, PAGE_W, 11 * mm, fill=1, stroke=0)
    canvas.setFillColor(FOREST)
    canvas.rect(0, PAGE_H - 11.7 * mm, PAGE_W, 0.8 * mm, fill=1, stroke=0)

    # Bottom band
    canvas.setFillColor(FOREST_DARK)
    canvas.rect(0, 0, PAGE_W, 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(PISTA_MID)
    canvas.rect(0, 10 * mm, PAGE_W, 0.55 * mm, fill=1, stroke=0)

    canvas.setFillColor(FOREST_DARK)
    canvas.setFont("Calibri-Bold", 8)
    canvas.drawString(LEFT, PAGE_H - 7 * mm, "SIH26153  ·  Network Attack Forecasting")
    canvas.setFont("Calibri", 8)
    canvas.setFillColor(FOREST)
    canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 7 * mm, "Day 2 Progress Report  ·  Internal team handoff")

    canvas.setFillColor(WHITE)
    canvas.setFont("Calibri", 8)
    canvas.drawString(LEFT, 4.2 * mm, "SIH Team knowledge document  ·  03 Sep 2026")
    canvas.setFont("Calibri-Bold", 8)
    canvas.drawRightString(PAGE_W - RIGHT, 4.2 * mm, f"{doc.page}")
    canvas.restoreState()


def draw_cover(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(PISTA_PAGE)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Left forest strip
    canvas.setFillColor(FOREST_DARK)
    canvas.rect(0, 0, 14 * mm, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(PISTA_ACCENT)
    canvas.rect(14 * mm, 0, 2.2 * mm, PAGE_H, fill=1, stroke=0)

    # Top wash
    canvas.setFillColor(PISTA_BAND)
    canvas.rect(16.2 * mm, PAGE_H - 38 * mm, PAGE_W - 16.2 * mm, 38 * mm, fill=1, stroke=0)

    canvas.setFillColor(FOREST)
    canvas.setFont("Calibri-Bold", 10)
    canvas.drawString(28 * mm, PAGE_H - 18 * mm, "SMART INDIA HACKATHON 2026")
    canvas.setFont("Calibri", 9)
    canvas.drawString(28 * mm, PAGE_H - 24 * mm, "Problem ID  SIH26153")

    # Bottom forest bar
    canvas.setFillColor(FOREST_DARK)
    canvas.rect(16.2 * mm, 0, PAGE_W - 16.2 * mm, 22 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Calibri", 9)
    canvas.drawString(28 * mm, 12 * mm, "Internal team document  ·  Not a public SIH submission PDF")
    canvas.setFont("Calibri-Bold", 9)
    canvas.drawRightString(PAGE_W - 16 * mm, 12 * mm, "Branch: main")
    canvas.restoreState()
