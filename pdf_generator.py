"""
BrainyNotes AI — PDF Generator Core
"""
import os, io
from reportlab.platypus import (
    SimpleDocTemplate, Spacer, PageBreak,
    Paragraph, Flowable, HRFlowable
)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

BASE       = os.path.dirname(os.path.abspath(__file__))
FONT_DIR   = os.path.join(BASE, "fonts")
LOGO_LIGHT = os.path.join(BASE, "static", "brainynotes-logo-light.png")
LOGO_DARK  = os.path.join(BASE, "static", "brainynotes-logo-dark.png")
QR_PATH    = os.path.join(BASE, "static", "qr_brainynotes.png")

pdfmetrics.registerFont(TTFont("Inter",        os.path.join(FONT_DIR, "Inter-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Inter-Bold",   os.path.join(FONT_DIR, "Inter-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Inter-Italic", os.path.join(FONT_DIR, "Inter-Italic.ttf")))

C_ORANGE    = colors.HexColor("#F97316")
C_ORANGE_DK = colors.HexColor("#C2410C")
C_NAVY      = colors.HexColor("#0F172A")
C_RULE      = colors.HexColor("#D1B99A")
C_MUTED     = colors.HexColor("#6B7280")
C_AMBER_BG  = colors.HexColor("#FFFBEB")
C_AMBER_RL  = colors.HexColor("#FCD34D")
C_WHITE     = colors.white
W, H = A4
ML = 52; MR_PT = W - 52; DOC_W = W - 104

S_H1 = ParagraphStyle("H1", fontName="Inter-Bold", fontSize=17, leading=24, textColor=C_ORANGE, spaceAfter=6, spaceBefore=18)
S_H2 = ParagraphStyle("H2", fontName="Inter-Bold", fontSize=13, leading=19, textColor=C_ORANGE_DK, spaceAfter=4, spaceBefore=14)
S_H3 = ParagraphStyle("H3", fontName="Inter-Italic", fontSize=9, leading=13, textColor=C_MUTED, spaceAfter=6, spaceBefore=2)
S_BODY = ParagraphStyle("Body", fontName="Inter", fontSize=10.5, leading=18, textColor=C_NAVY, spaceAfter=8, alignment=TA_JUSTIFY)
S_NUM_TITLE = ParagraphStyle("NumTitle", fontName="Inter-Bold", fontSize=10.5, leading=17, textColor=C_NAVY, spaceAfter=0, spaceBefore=0, leftIndent=18, firstLineIndent=-18)
S_NUM_DESC = ParagraphStyle("NumDesc", fontName="Inter", fontSize=10.5, leading=16, textColor=C_MUTED, spaceAfter=9, spaceBefore=1, leftIndent=18)
S_QUOTE = ParagraphStyle("Quote", fontName="Inter-Italic", fontSize=9.5, leading=16, textColor=colors.HexColor("#1E3A5F"), leftIndent=14, rightIndent=10, spaceAfter=0, spaceBefore=0)
S_KW = ParagraphStyle("KW", fontName="Inter-Bold", fontSize=9, leading=13, textColor=colors.HexColor("#92400E"))
S_KD = ParagraphStyle("KD", fontName="Inter", fontSize=9, leading=13, textColor=C_NAVY)

class DefinitionBox(Flowable):
    def __init__(self, text, width):
        Flowable.__init__(self)
        self.width = width
        self.para = Paragraph(text, S_QUOTE)
        _, h = self.para.wrap(width - 32, 2000)
        self.height = h + 20
    def wrap(self, aw, ah): return self.width, self.height
    def draw(self):
        c = self.canv; c.saveState()
        c.setFillColor(colors.HexColor("#EFF6FF")); c.setStrokeColor(colors.HexColor("#BFDBFE")); c.setLineWidth(0.6)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#3B82F6")); c.rect(0, 0, 4, self.height, fill=1, stroke=0)
        self.para.drawOn(c, 18, 10); c.restoreState()

class QuickRecall(Flowable):
    def __init__(self, title, items, width):
        Flowable.__init__(self)
        self.title = title; self.width = width; self.pad = 10; self.kw_w = 120; self.row_gap = 3
        self.rows = []
        def_w = width - self.kw_w - self.pad * 3
        for kw, defn in items:
            kp = Paragraph(kw, S_KW); dp = Paragraph(defn, S_KD)
            _, kh = kp.wrap(self.kw_w, 2000); _, dh = dp.wrap(def_w, 2000)
            self.rows.append((kp, dp, max(kh, dh) + self.row_gap + 4))
        self.height = sum(r[2] for r in self.rows) + self.pad * 2 + 22
    def wrap(self, aw, ah): return self.width, self.height
    def draw(self):
        c = self.canv; c.saveState()
        c.setFillColor(C_AMBER_BG); c.setStrokeColor(C_AMBER_RL); c.setLineWidth(0.7)
        c.roundRect(0, 0, self.width, self.height, 8, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#F59E0B")); c.rect(0, 0, 4, self.height, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#92400E")); c.setFont("Inter-Bold", 8)
        c.drawString(14, self.height - 15, f"  {self.title.upper()}")
        c.setStrokeColor(C_AMBER_RL); c.setLineWidth(0.5)
        c.line(12, self.height - 19, self.width - 10, self.height - 19)
        def_w = self.width - self.kw_w - self.pad * 3
        y = self.height - 22
        for i, (kp, dp, rh) in enumerate(self.rows):
            if i % 2 == 0:
                c.setFillColor(colors.Color(0.984, 0.941, 0.8, alpha=0.6))
                c.rect(12, y - rh + 3, self.width - 18, rh, fill=1, stroke=0)
            kp.drawOn(c, 14, y - kp.wrap(self.kw_w, 2000)[1])
            c.setStrokeColor(C_AMBER_RL); c.setLineWidth(0.4)
            c.line(14 + self.kw_w + 4, y - rh + 4, 14 + self.kw_w + 4, y + 2)
            dp.drawOn(c, 14 + self.kw_w + 12, y - dp.wrap(def_w, 2000)[1])
            y -= rh
        c.restoreState()

class PremiumTOC(Flowable):
    def __init__(self, width, items):
        Flowable.__init__(self); self.width = width; self.items = items
        self.height = len(items) * 20 + 8
    def wrap(self, aw, ah): return self.width, self.height
    def draw(self):
        c = self.canv; c.saveState(); y = self.height - 4; row_h = 20
        for topic, pg, is_group in self.items:
            if is_group:
                c.setFillColor(colors.HexColor("#F1F5F9"))
                c.rect(0, y - row_h + 3, self.width, row_h - 2, fill=1, stroke=0)
                c.setFillColor(C_MUTED); c.setFont("Inter-Bold", 7.5)
                c.drawString(4, y - 13, topic.upper())
            else:
                c.setFillColor(C_NAVY); c.setFont("Inter", 10)
                tw = c.stringWidth(topic, "Inter", 10); pw = c.stringWidth(pg, "Inter-Bold", 10)
                c.drawString(12, y - 14, topic)
                dx = 12 + tw + 4; dx2 = self.width - pw - 6
                c.setFillColor(C_MUTED)
                while dx < dx2 - 3:
                    c.circle(dx, y - 10, 0.65, fill=1, stroke=0); dx += 4.5
                c.setFillColor(C_ORANGE); c.setFont("Inter-Bold", 10)
                c.drawRightString(self.width, y - 14, pg)
                c.setStrokeColor(colors.HexColor("#F3F4F6")); c.setLineWidth(0.4)
                c.line(0, y - row_h + 3, self.width, y - row_h + 3)
            y -= row_h
        c.restoreState()

class EndPage(Flowable):
    def __init__(self): Flowable.__init__(self); self.width = self.height = 1
    def wrap(self, aw, ah): self.width = aw; self.height = ah; return aw, ah
    def draw(self):
        c = self.canv; Wc = self.width; Hc = self.height; cx = Wc / 2
        c.saveState()
        c.setFillColor(colors.HexColor("#F9FAFB")); c.rect(0, 0, Wc, Hc, fill=1, stroke=0)
        c.setFillColor(C_ORANGE); c.rect(0, Hc - 4, Wc, 4, fill=1, stroke=0)
        cw = 340; ch = 390; card_x = (Wc - cw) / 2; card_y = (Hc - ch) / 2 - 5
        c.setFillColor(C_WHITE); c.setStrokeColor(colors.HexColor("#E5E7EB")); c.setLineWidth(1)
        c.roundRect(card_x, card_y, cw, ch, 16, fill=1, stroke=1)
        ls = 26
        if os.path.exists(LOGO_LIGHT):
            c.drawImage(LOGO_LIGHT, cx - ls/2, card_y + ch - 42, width=ls, height=ls, preserveAspectRatio=True, mask="auto")
        c.setFillColor(C_ORANGE); c.setFont("Inter-Bold", 7.5)
        c.drawCentredString(cx, card_y + ch - 52, "B R A I N Y N O T E S  A I")
        c.setFillColor(C_NAVY); c.setFont("Inter-Bold", 20)
        c.drawCentredString(cx, card_y + ch - 80, "Thank you for reading")
        c.setFillColor(C_MUTED); c.setFont("Inter", 9)
        c.drawCentredString(cx, card_y + ch - 98, "Get more notes, quizzes & flashcards")
        c.drawCentredString(cx, card_y + ch - 112, "to study smarter and score higher.")
        c.setStrokeColor(colors.HexColor("#E5E7EB")); c.setLineWidth(0.6)
        c.line(card_x + 30, card_y + ch - 124, card_x + cw - 30, card_y + ch - 124)
        qs = 100; qx = cx - qs/2; qy = card_y + ch - 248
        c.setFillColor(colors.HexColor("#F8FAFC")); c.setStrokeColor(colors.HexColor("#E5E7EB")); c.setLineWidth(0.6)
        c.roundRect(qx - 8, qy - 8, qs + 16, qs + 16, 10, fill=1, stroke=1)
        if os.path.exists(QR_PATH):
            c.drawImage(QR_PATH, qx, qy, width=qs, height=qs, preserveAspectRatio=True, mask="auto")
        c.setFillColor(C_MUTED); c.setFont("Inter-Bold", 7)
        c.drawCentredString(cx, qy - 18, "S C A N  T O  V I S I T")
        url = "brainynotesai.com"; uw = c.stringWidth(url, "Inter-Bold", 11)
        ux = cx - uw/2; uy = qy - 34
        c.setFillColor(C_ORANGE); c.setFont("Inter-Bold", 11)
        c.drawString(ux, uy, url)
        c.linkURL(f"https://{url}", (ux, uy - 2, ux + uw, uy + 11), relative=0)
        feats = ["AI Doubt Solver", "Summary", "Flashcards", "Quiz"]
        c.setFont("Inter-Bold", 7); ph = 18; pr = 9; ppad = 9; pgap = 5
        pws = [c.stringWidth(f, "Inter-Bold", 7) + ppad*2 for f in feats]
        total = sum(pws) + pgap*(len(feats)-1); px = cx - total/2; py = card_y + 22
        for feat, pw in zip(feats, pws):
            c.setFillColor(colors.HexColor("#FFF7ED")); c.setStrokeColor(colors.HexColor("#FED7AA")); c.setLineWidth(0.5)
            c.roundRect(px, py, pw, ph, pr, fill=1, stroke=1)
            c.setFillColor(C_ORANGE_DK); c.drawString(px + ppad, py + 5.5, feat); px += pw + pgap
        c.setFillColor(C_MUTED); c.setFont("Inter", 7.5)
        c.drawCentredString(cx, 16, "BrainyNotes AI  ·  brainynotesai.com  ·  Free FYUGP Study Material")
        c.restoreState()

class BrainyCanvas(canvas.Canvas):
    def __init__(self, *args, course=None, **kwargs):
        super().__init__(*args, **kwargs); self.course = course or {}
    def showPage(self):
        self._draw_chrome(); canvas.Canvas.showPage(self)
    def _draw_chrome(self):
        pg = self.getPageNumber(); self.saveState(); course = self.course
        if pg == 1:
            self.setFillColor(C_ORANGE); self.rect(0, 0, W, H, fill=1, stroke=0)
            self.setStrokeColor(colors.Color(1,1,1,alpha=0.10)); self.setLineWidth(0.6)
            for i in range(30):
                x1 = W - 200 + i*16; y1 = H; x2 = W; y2 = H - 200 + i*16
                self.line(max(x1, W-220), y1, x2, max(y2, H-220))
            self.setStrokeColor(colors.Color(1,1,1,alpha=0.07)); self.setLineWidth(38)
            self.arc(-60, -60, 220, 220, startAng=0, extent=90)
            logo_size = 34; logo_y = H - 60
            if os.path.exists(LOGO_DARK):
                self.drawImage(LOGO_DARK, ML, logo_y - logo_size + 10, width=logo_size, height=logo_size, preserveAspectRatio=True, mask="auto")
            self.setFillColor(C_WHITE); self.setFont("Inter-Bold", 20)
            self.drawString(ML + logo_size + 8, logo_y - 10, "BrainyNotes AI")
            pill_w = 108; pill_h = 24
            self.setFillColor(colors.Color(0,0,0,alpha=0.20))
            self.roundRect(ML, H-250, pill_w, pill_h, 12, fill=1, stroke=0)
            self.setFillColor(C_WHITE); self.setFont("Inter-Bold", 9)
            self.drawCentredString(ML + pill_w/2, H-242, course.get("note_type","SHORT NOTES"))
            self.setFont("Inter", 11); self.drawString(ML, H-278, course.get("subject",""))
            self.setFont("Inter-Bold", 40)
            self.drawString(ML, H-326, course.get("title1",""))
            self.drawString(ML, H-374, course.get("title2",""))
            self.setFont("Inter", 11); self.drawString(ML, H-408, course.get("module",""))
            meta = [course.get("program",""), course.get("code",""), course.get("semester",""), course.get("credits","")]
            self.setFont("Inter-Bold", 7.5); px2 = ML; py2 = H-440
            for m in meta:
                if not m: continue
                pw2 = self.stringWidth(m, "Inter-Bold", 7.5) + 24
                self.setFillColor(colors.Color(1,1,1,alpha=0.15)); self.setStrokeColor(colors.Color(1,1,1,alpha=0.45)); self.setLineWidth(0.7)
                self.roundRect(px2, py2, pw2, 20, 10, fill=1, stroke=1)
                self.setFillColor(C_WHITE); self.drawString(px2+12, py2+6.5, m); px2 += pw2 + 7
            self.setFillColor(colors.HexColor("#0F172A")); self.rect(0, 0, W, 58, fill=1, stroke=0)
            if os.path.exists(LOGO_DARK):
                self.drawImage(LOGO_DARK, ML, 14, width=28, height=28, preserveAspectRatio=True, mask="auto")
            self.setFillColor(C_WHITE); self.setFont("Inter-Bold", 10)
            self.drawString(ML+34, 36, "BrainyNotes AI")
            self.setFillColor(colors.Color(1,1,1,alpha=0.65)); self.setFont("Inter", 8)
            self.drawString(ML+34, 11, "brainynotesai.com")
        else:
            hdr_logo = 15
            if os.path.exists(LOGO_LIGHT):
                self.drawImage(LOGO_LIGHT, ML, H-36, width=hdr_logo, height=hdr_logo, preserveAspectRatio=True, mask="auto")
            self.setFont("Inter", 8); self.setFillColor(C_MUTED)
            self.drawString(ML+hdr_logo+4, H-28, course.get("subject","").upper())
            self.drawRightString(MR_PT, H-28, f"{course.get('code','')}  |  {course.get('module','')}")
            self.setStrokeColor(C_RULE); self.setLineWidth(0.9)
            self.line(ML, H-33, MR_PT, H-33); self.line(ML, 36, MR_PT, 36)
            self.setFont("Inter", 7.5); self.setFillColor(C_MUTED)
            self.drawString(ML, 24, "BrainyNotes AI")
            url = "brainynotesai.com"; uw = self.stringWidth(url, "Inter", 7.5)
            ux = W/2 - uw/2; self.setFillColor(C_ORANGE); self.drawString(ux, 24, url)
            self.linkURL(f"https://{url}", (ux,20,ux+uw,32), relative=0)
            self.setFillColor(C_NAVY); self.setFont("Inter-Bold", 7.5)
            self.drawRightString(MR_PT, 24, str(pg))
        self.restoreState()

def sp(pts=10): return Spacer(1, pts)
def h1(t): return Paragraph(t, S_H1)
def h2(t): return Paragraph(t, S_H2)
def h3(t): return Paragraph(t, S_H3)
def body(t): return Paragraph(t, S_BODY)
def defbox(t): return DefinitionBox(t, DOC_W)
def rule(): return HRFlowable(width="100%", thickness=0.8, color=C_RULE)
def numbered(n, term, desc):
    return [Paragraph(f"<b>{n}.  {term}</b>", S_NUM_TITLE), Paragraph(desc, S_NUM_DESC)]

def generate_pdf(course: dict, sections: list) -> bytes:
    buf = io.BytesIO()
    def canvas_maker(*args, **kwargs): return BrainyCanvas(*args, course=course, **kwargs)
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=52, bottomMargin=52, leftMargin=ML, rightMargin=W-MR_PT)
    story = [sp(1), PageBreak(), sp(8)]
    story.append(Paragraph("Contents", ParagraphStyle("TOCHead", fontName="Inter-Bold", fontSize=28, leading=34, textColor=C_NAVY)))
    story.append(sp(6))
    story.append(HRFlowable(width="100%", thickness=2.5, color=C_ORANGE, spaceAfter=16))
    toc_items = []; page_num = 3
    for sec in sections:
        if sec.get("h1"): toc_items.append((sec["h1"], str(page_num), False))
        for sub in sec.get("subsections",[]): toc_items.append((sub.get("h2",""), str(page_num), False))
        page_num += 1
    if toc_items: story.append(PremiumTOC(DOC_W, toc_items))
    story.append(PageBreak())
    for sec in sections:
        if sec.get("h1"): story.append(h1(sec["h1"]))
        if sec.get("body"): story.append(body(sec["body"]))
        if sec.get("definition"): story.append(defbox(sec["definition"])); story.append(sp(8))
        if sec.get("numbered_list"):
            story.append(sp(4))
            for i, item in enumerate(sec["numbered_list"], 1):
                for el in numbered(i, item.get("title",""), item.get("desc","")): story.append(el)
        for sub in sec.get("subsections",[]):
            story.append(sp(14))
            if sub.get("h2"): story.append(h2(sub["h2"]))
            if sub.get("body"): story.append(body(sub["body"]))
            if sub.get("definition"): story.append(defbox(sub["definition"])); story.append(sp(8))
            if sub.get("numbered_list"):
                story.append(sp(4))
                for i, item in enumerate(sub["numbered_list"], 1):
                    for el in numbered(i, item.get("title",""), item.get("desc","")): story.append(el)
        if sec.get("recall_items"):
            story.append(sp(16))
            story.append(QuickRecall("Quick Recall", [(r.get("keyword",""), r.get("definition","")) for r in sec["recall_items"]], DOC_W))
        story.append(PageBreak())
    story.append(EndPage())
    doc.build(story, canvasmaker=canvas_maker)
    buf.seek(0); return buf.read()
