"""
Convert claude-code-cheatsheet.md to a styled two-column PDF using fpdf2.
Usage: python3 tools/make_pdf.py
"""

import re
import warnings
warnings.filterwarnings("ignore")
from fpdf import FPDF, XPos, YPos

MD_PATH = "claude-code-cheatsheet.md"
OUT_PATH = "claude-code-cheatsheet.pdf"

# ── Colour palette ──────────────────────────────────────────────────────────
INDIGO   = (99,  102, 241)   # headings / accents
DARK     = (15,  23,  42)    # h1, strong
MID      = (51,  65,  85)    # body text
LIGHT    = (100, 116, 136)   # muted / code comments
BG_CODE  = (15,  23,  42)    # code block bg
FG_CODE  = (165, 243, 252)   # code block text
BG_ROW   = (248, 250, 252)   # alternating table row
BG_TH    = (99,  102, 241)   # table header bg
WHITE    = (255, 255, 255)
BORDER   = (226, 232, 240)   # subtle rule

# ── Layout constants (mm) ───────────────────────────────────────────────────
PAGE_W, PAGE_H = 210, 297    # A4
MARGIN_X = 12
MARGIN_Y = 12
COL_GAP  = 6
COL_W    = (PAGE_W - 2 * MARGIN_X - COL_GAP) / 2   # ≈ 85 mm per column
FONT_BODY = 8.2
FONT_H1   = 18
FONT_H2   = 7.5
FONT_H3   = 8.5
FONT_CODE = 7.2

# ── Font paths ───────────────────────────────────────────────────────────────
FONTS = {
    'regular': '/System/Library/Fonts/Supplemental/Arial.ttf',
    'bold':    '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
    'italic':  '/System/Library/Fonts/Supplemental/Arial Italic.ttf',
    'mono':    '/System/Library/Fonts/Supplemental/Courier New.ttf',
}
LINE_H    = 4.2    # body line height
CODE_LINE = 3.8


def parse_inline(text: str):
    """Return list of (bold, code, content) tuples from an inline markdown string."""
    segments = []
    pattern = re.compile(r'(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|__[^_]+__|_[^_]+_)')
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            segments.append(('normal', text[pos:m.start()]))
        raw = m.group(0)
        if raw.startswith('`'):
            segments.append(('code', raw[1:-1]))
        elif raw.startswith('**') or raw.startswith('__'):
            segments.append(('bold', raw[2:-2]))
        else:
            segments.append(('em', raw[1:-1]))
        pos = m.end()
    if pos < len(text):
        segments.append(('normal', text[pos:]))
    return segments


class CheatSheet(FPDF):
    def __init__(self):
        super().__init__(format='A4')
        self.set_margins(MARGIN_X, MARGIN_Y, MARGIN_X)
        self.set_auto_page_break(False)
        # Register Unicode-capable fonts
        self.add_font('Arial', style='',  fname=FONTS['regular'], uni=True)
        self.add_font('Arial', style='B', fname=FONTS['bold'],    uni=True)
        self.add_font('Arial', style='I', fname=FONTS['italic'],  uni=True)
        self.add_font('Mono',  style='',  fname=FONTS['mono'],    uni=True)
        self.add_page()
        self.set_font('Arial', '', FONT_BODY)
        self._col = 0             # current column (0 or 1)
        self._col_y = [MARGIN_Y + 22, MARGIN_Y + 22]   # y-position per column
        self._in_col = False

    # ── Page footer ─────────────────────────────────────────────────────────
    def footer(self):
        self.set_y(-8)
        self.set_font('Arial', '', 7)
        self.set_text_color(*LIGHT)
        self.cell(0, 4, f'Claude Code Cheat Sheet  -  Page {self.page_no()} of {{nb}}', align='C')

    # ── Column helpers ───────────────────────────────────────────────────────
    def col_x(self):
        return MARGIN_X + self._col * (COL_W + COL_GAP)

    def cur_y(self):
        return self._col_y[self._col]

    def set_cur_y(self, y):
        self._col_y[self._col] = y

    def advance(self, h):
        self._col_y[self._col] += h
        if self._col_y[self._col] > PAGE_H - MARGIN_Y - 6:
            if self._col == 0:
                self._col = 1          # switch to right column
            else:
                self.add_page()
                self._col = 0
                self._col_y = [MARGIN_Y, MARGIN_Y]

    def remaining(self):
        return PAGE_H - MARGIN_Y - 6 - self.cur_y()

    # ── Drawing helpers ──────────────────────────────────────────────────────
    def draw_rule(self, color=BORDER, thickness=0.2):
        y = self.cur_y()
        self.set_draw_color(*color)
        self.set_line_width(thickness)
        self.line(self.col_x(), y, self.col_x() + COL_W, y)

    def write_line(self, segments, indent=0, h=LINE_H, align='L'):
        x = self.col_x() + indent
        y = self.cur_y()
        self.set_xy(x, y)
        w = COL_W - indent

        # Measure total width to handle alignment
        for style, text in segments:
            if style == 'bold':
                self.set_font('Arial', 'B', FONT_BODY)
                self.set_text_color(*DARK)
            elif style == 'code':
                self.set_font('Mono', '', FONT_CODE)
                self.set_text_color(*INDIGO)
                self.set_fill_color(241, 245, 249)
                # tiny inline bg
                tw = self.get_string_width(text) + 1.5
                self.rect(self.get_x(), y + 0.5, tw, h - 0.5, 'F')
            elif style == 'em':
                self.set_font('Arial', 'I', FONT_BODY)
                self.set_text_color(*LIGHT)
            else:
                self.set_font('Arial', '', FONT_BODY)
                self.set_text_color(*MID)
            self.set_xy(self.get_x(), y)
            self.cell(self.get_string_width(text), h, text)
        self.advance(h)

    def body_text(self, text, indent=0, h=LINE_H):
        """Render wrapped inline-markdown text."""
        if not text.strip():
            return
        segments = parse_inline(text)
        x0 = self.col_x() + indent
        max_w = COL_W - indent
        # Word-wrap approach: build word list per segment
        # Simple: use multi_cell with plain text, re-apply bold in passes
        # For simplicity: strip markdown and render with style emphasis
        plain = text
        for sym in ('**', '__', '*', '_', '`'):
            plain = plain.replace(sym, '')

        bold_ranges = [(m.start(), m.end(), m.group(1))
                       for m in re.finditer(r'\*\*(.+?)\*\*|__(.+?)__', text)]

        self.set_xy(x0, self.cur_y())
        self.set_font('Arial', '', FONT_BODY)
        self.set_text_color(*MID)
        before = self.get_y()
        self.multi_cell(max_w, h, plain, align='L')
        after = self.get_y()
        self.set_cur_y(after)

    def render_title(self):
        # Full-width title block
        self.set_fill_color(*INDIGO)
        self.rect(0, 0, PAGE_W, 18, 'F')
        self.set_xy(MARGIN_X, 4)
        self.set_font('Arial', 'B', FONT_H1)
        self.set_text_color(*WHITE)
        self.cell(0, 8, 'Claude Code  Cheat Sheet', align='L')
        self.set_xy(MARGIN_X, 11.5)
        self.set_font('Arial', '', 7.5)
        self.set_text_color(200, 210, 255)
        self.cell(0, 5, 'Beginner to Pro  |  WAT Framework | Context | MCP | Deployment | Agency', align='L')
        # Right-align source label
        self.set_xy(-55, 4)
        self.set_font('Arial', 'I', 7)
        self.set_text_color(180, 190, 255)
        self.cell(50, 8, 'youtube.com/watch?v=mpALXah_PBg', align='R')

    def h2(self, text):
        """Section header."""
        self.advance(1.5)
        y = self.cur_y()
        # Coloured left bar
        self.set_fill_color(*INDIGO)
        self.rect(self.col_x(), y, 1.5, 4.5, 'F')
        # Background pill
        self.set_fill_color(238, 240, 255)
        self.rect(self.col_x() + 1.5, y, COL_W - 1.5, 4.5, 'F')
        self.set_xy(self.col_x() + 3, y + 0.5)
        self.set_font('Arial', 'B', FONT_H2)
        self.set_text_color(*INDIGO)
        self.cell(COL_W - 4, 4, text.upper(), align='L')
        self.advance(4.5)
        self.advance(0.5)

    def h3(self, text):
        self.advance(1)
        self.set_xy(self.col_x(), self.cur_y())
        self.set_font('Arial', 'B', FONT_H3)
        self.set_text_color(*DARK)
        self.multi_cell(COL_W, LINE_H, text)
        self.set_cur_y(self.get_y())
        self.advance(0.3)

    def bullet(self, text, indent=3, marker='•'):
        plain = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        plain = re.sub(r'\*(.+?)\*', r'\1', plain)
        plain = re.sub(r'`(.+?)`', r'\1', plain)
        plain = re.sub(r'__(.+?)__', r'\1', plain)
        plain = re.sub(r'_(.+?)_', r'\1', plain)

        # Bold/code detection for inline highlight
        has_bold = bool(re.search(r'\*\*|__', text))
        x0 = self.col_x() + indent
        # Marker
        self.set_xy(self.col_x() + 1, self.cur_y())
        self.set_font('Arial', '', FONT_BODY)
        self.set_text_color(*INDIGO)
        self.cell(indent - 1, LINE_H, marker)
        # Text
        self.set_xy(x0, self.cur_y())
        self.set_font('Arial', '', FONT_BODY)
        self.set_text_color(*MID)
        before = self.get_y()
        self.multi_cell(COL_W - indent, LINE_H, plain)
        self.set_cur_y(self.get_y())

    def code_block(self, lines):
        pad = 2
        inner_h = len(lines) * CODE_LINE + pad * 2
        if inner_h > self.remaining() and self._col == 0:
            self._col = 1

        y = self.cur_y()
        self.set_fill_color(*BG_CODE)
        self.rect(self.col_x(), y, COL_W, inner_h, 'F')
        self.set_xy(self.col_x() + pad, y + pad)
        self.set_font('Mono', '', FONT_CODE)
        self.set_text_color(*FG_CODE)
        for line in lines:
            # Comments in lighter colour
            colour = (100, 160, 180) if line.strip().startswith('#') else FG_CODE
            self.set_text_color(*colour)
            self.set_xy(self.col_x() + pad, self.get_y())
            self.cell(COL_W - pad * 2, CODE_LINE, line)
            self.set_y(self.get_y() + CODE_LINE)
        self.set_cur_y(y + inner_h)
        self.advance(1.5)

    def table(self, headers, rows):
        col_n = len(headers)
        col_w = COL_W / col_n

        # Check space
        needed = 5 + len(rows) * 4.5 + 2
        if needed > self.remaining() and self._col == 0:
            self._col = 1

        y = self.cur_y()
        # Header row
        self.set_fill_color(*BG_TH)
        self.set_text_color(*WHITE)
        self.set_font('Arial', 'B', 6.8)
        for i, h in enumerate(headers):
            self.set_xy(self.col_x() + i * col_w, y)
            self.cell(col_w, 5, h.strip(), fill=True, border=0)
        self.advance(5)

        # Data rows
        self.set_font('Arial', '', FONT_CODE)
        for ri, row in enumerate(rows):
            fill = ri % 2 == 1
            y2 = self.cur_y()
            # Measure max height in this row
            row_h = 4.5
            for ci, cell in enumerate(row):
                plain = re.sub(r'\*\*(.+?)\*\*', r'\1', cell)
                plain = re.sub(r'`(.+?)`', r'\1', plain)
                plain = plain.strip()
                nw = self.get_string_width(plain)
                if nw > col_w - 2:
                    lines_needed = int(nw / (col_w - 2)) + 1
                    row_h = max(row_h, lines_needed * 4)

            if fill:
                self.set_fill_color(*BG_ROW)
                self.rect(self.col_x(), y2, COL_W, row_h, 'F')

            for ci, cell in enumerate(row):
                plain = re.sub(r'\*\*(.+?)\*\*', r'\1', cell)
                plain = re.sub(r'`(.+?)`', r'\1', plain)
                plain = plain.strip()
                self.set_text_color(*MID)
                if ci == 0:
                    self.set_font('Arial', 'B', FONT_CODE)
                    self.set_text_color(*DARK)
                else:
                    self.set_font('Arial', '', FONT_CODE)
                    self.set_text_color(*MID)
                self.set_xy(self.col_x() + ci * col_w + 1, y2)
                self.multi_cell(col_w - 1, 4, plain)

            # Bottom border
            self.set_draw_color(*BORDER)
            self.set_line_width(0.1)
            self.line(self.col_x(), y2 + row_h, self.col_x() + COL_W, y2 + row_h)
            self.set_cur_y(y2 + row_h)

        self.advance(2)


# ── Markdown parser → PDF calls ──────────────────────────────────────────────

def render(pdf: CheatSheet, md: str):
    lines = md.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # ── H1 (already rendered as title banner) ──
        if line.startswith('# ') and not line.startswith('## '):
            i += 1
            continue

        # ── H2 ──
        if line.startswith('## '):
            pdf.h2(line[3:].strip())
            i += 1
            continue

        # ── H3 ──
        if line.startswith('### '):
            pdf.h3(line[4:].strip())
            i += 1
            continue

        # ── HR ──
        if re.match(r'^-{3,}$', line.strip()):
            i += 1
            continue

        # ── Fenced code block ──
        if line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # closing ```
            # Remove trailing blank lines
            while code_lines and not code_lines[-1].strip():
                code_lines.pop()
            if code_lines:
                pdf.code_block(code_lines)
            continue

        # ── Table ──
        if '|' in line and i + 1 < len(lines) and re.match(r'^\|[-| :]+\|', lines[i + 1]):
            # Collect table rows
            table_lines = []
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            if len(table_lines) >= 2:
                headers = [c.strip() for c in table_lines[0].strip('|').split('|')]
                rows = []
                for tl in table_lines[2:]:   # skip separator row
                    if '|' in tl:
                        rows.append([c.strip() for c in tl.strip('|').split('|')])
                if rows:
                    pdf.table(headers, rows)
            continue

        # ── Bullet / task list ──
        if re.match(r'^(\s*)[-*+] ', line):
            indent_level = len(line) - len(line.lstrip())
            text = re.sub(r'^(\s*)[-*+] ', '', line)
            text = re.sub(r'^\[[ x]\] ', '', text)   # strip task checkbox
            pdf.bullet(text, indent=3 + indent_level * 2)
            i += 1
            continue

        # ── Numbered list ──
        if re.match(r'^\d+\. ', line):
            num = re.match(r'^(\d+)\. ', line).group(1)
            text = re.sub(r'^\d+\. ', '', line)
            pdf.bullet(text, indent=5, marker=f'{num}.')
            i += 1
            continue

        # ── Blank line ──
        if not line.strip():
            pdf.advance(1)
            i += 1
            continue

        # ── Paragraph / bold text ──
        plain = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
        plain = re.sub(r'\*(.+?)\*', r'\1', plain)
        plain = re.sub(r'`(.+?)`', r'\1', plain)
        plain = re.sub(r'__(.+?)__', r'\1', plain)
        plain = re.sub(r'_(.+?)_', r'\1', plain)
        plain = plain.strip()
        if plain:
            # Detect if the whole line is bold (tip/rule callout)
            if line.strip().startswith('**') and line.strip().endswith('**'):
                pdf.set_xy(pdf.col_x(), pdf.cur_y())
                pdf.set_font('Arial', 'B', FONT_BODY)
                pdf.set_text_color(*DARK)
                pdf.multi_cell(COL_W, LINE_H, plain)
                pdf.set_cur_y(pdf.get_y())
            else:
                pdf.set_xy(pdf.col_x(), pdf.cur_y())
                pdf.set_font('Arial', '', FONT_BODY)
                pdf.set_text_color(*MID)
                pdf.multi_cell(COL_W, LINE_H, plain)
                pdf.set_cur_y(pdf.get_y())
        i += 1


def main():
    with open(MD_PATH, encoding='utf-8') as f:
        md = f.read()

    pdf = CheatSheet()
    pdf.alias_nb_pages()
    pdf.render_title()
    render(pdf, md)
    pdf.output(OUT_PATH)
    print(f"Saved → {OUT_PATH}")


if __name__ == '__main__':
    main()
