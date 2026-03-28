#!/usr/bin/env python3
"""
TradingEconomics Algeria Economic Indicators - Comprehensive PDF Generator
Source: https://fr.tradingeconomics.com/algeria/indicators
Extracts ALL tabs and KPIs, generates a well-formatted PDF.
"""

import requests
from bs4 import BeautifulSoup
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
OUTPUT_PATH = '/Users/mac/Documents/GitHub/MiroFish-en/algeria-economy-com-extract/algeria-tradingeconomics-indicators.pdf'
SOURCE_URL  = 'https://fr.tradingeconomics.com/algeria/indicators'
EXTRACTED   = datetime.now().strftime('%d %B %Y à %H:%M')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
}

TAB_NAMES = {
    'overview':   "Vue d'ensemble",
    'gdp':        'PIB (GDP)',
    'labour':     "Main-d'œuvre",
    'prices':     'Tarifs & Prix',
    'money':      'Argent & Monnaie',
    'trade':      'Commerce',
    'government': 'Gouvernement',
    'business':   'Entreprise',
    'consumer':   'Consommateur',
    'energy':     'Énergie',
}

# ──────────────────────────────────────────────
# Colours
# ──────────────────────────────────────────────
DARK_GREEN   = colors.HexColor('#006633')
MID_GREEN    = colors.HexColor('#338855')
LIGHT_GREEN  = colors.HexColor('#E8F5EE')
HEADER_BG    = colors.HexColor('#1a3a5c')   # dark navy (TE brand)
HEADER_FG    = colors.white
ALT_ROW      = colors.HexColor('#F4F8FC')
BORDER_CLR   = colors.HexColor('#C8D8E8')
RED_VAL      = colors.HexColor('#CC0000')
TITLE_CLR    = colors.HexColor('#1a3a5c')
ACCENT_CLR   = colors.HexColor('#006633')

# ──────────────────────────────────────────────
# Fetch & Parse
# ──────────────────────────────────────────────
def fetch_html():
    """Fetch the TradingEconomics Algeria indicators page."""
    print(f"Fetching {SOURCE_URL} ...")
    resp = requests.get(SOURCE_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    print(f"  OK — {len(resp.text):,} chars")
    return resp.text


def parse_tab(panel, panel_id):
    """Extract all tables from a tab panel."""
    tables_data = []
    
    for table in panel.find_all('table'):
        rows = table.find_all('tr')
        if not rows:
            continue
        
        # Header row
        header_cells = rows[0].find_all(['th', 'td'])
        headers = [c.get_text(strip=True) for c in header_cells]
        
        # Data rows
        data_rows = []
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue
            row_data = []
            for cell in cells:
                text = cell.get_text(strip=True)
                row_data.append(text)
            if any(row_data):
                data_rows.append(row_data)
        
        if data_rows:
            tables_data.append({'headers': headers, 'rows': data_rows})
    
    return tables_data


def extract_all_data(html):
    """Parse all tab panels and extract indicator tables."""
    soup = BeautifulSoup(html, 'html.parser')
    all_tabs = {}
    
    panels = soup.find_all('div', {'role': 'tabpanel'})
    print(f"  Found {len(panels)} tab panels")
    
    for panel in panels:
        pid = panel.get('id', f'unknown_{len(all_tabs)}')
        tables_data = parse_tab(panel, pid)
        if tables_data:
            all_tabs[pid] = tables_data
            total_rows = sum(len(t['rows']) for t in tables_data)
            print(f"    Tab '{pid}': {len(tables_data)} table(s), {total_rows} indicator rows")
    
    return all_tabs

# ──────────────────────────────────────────────
# PDF Styles
# ──────────────────────────────────────────────
def get_styles():
    base = getSampleStyleSheet()
    
    styles = {
        'title': ParagraphStyle(
            'Title',
            fontSize=22,
            fontName='Helvetica-Bold',
            textColor=TITLE_CLR,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        'subtitle': ParagraphStyle(
            'Subtitle',
            fontSize=11,
            fontName='Helvetica',
            textColor=colors.HexColor('#555555'),
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        'source': ParagraphStyle(
            'Source',
            fontSize=9,
            fontName='Helvetica-Oblique',
            textColor=colors.HexColor('#777777'),
            alignment=TA_CENTER,
            spaceAfter=20,
        ),
        'section_header': ParagraphStyle(
            'SectionHeader',
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            backColor=HEADER_BG,
            alignment=TA_LEFT,
            spaceBefore=14,
            spaceAfter=4,
            leftIndent=8,
            rightIndent=8,
            leading=20,
        ),
        'col_header': ParagraphStyle(
            'ColHeader',
            fontSize=8,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        'cell_name': ParagraphStyle(
            'CellName',
            fontSize=8,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1a3a5c'),
            alignment=TA_LEFT,
        ),
        'cell': ParagraphStyle(
            'Cell',
            fontSize=8,
            fontName='Helvetica',
            textColor=colors.HexColor('#333333'),
            alignment=TA_CENTER,
        ),
        'cell_red': ParagraphStyle(
            'CellRed',
            fontSize=8,
            fontName='Helvetica-Bold',
            textColor=RED_VAL,
            alignment=TA_CENTER,
        ),
        'footer': ParagraphStyle(
            'Footer',
            fontSize=7,
            fontName='Helvetica-Oblique',
            textColor=colors.HexColor('#888888'),
            alignment=TA_CENTER,
        ),
        'note': ParagraphStyle(
            'Note',
            fontSize=8,
            fontName='Helvetica-Oblique',
            textColor=colors.HexColor('#555555'),
            alignment=TA_LEFT,
            spaceBefore=4,
            spaceAfter=4,
        ),
        'toc_item': ParagraphStyle(
            'TocItem',
            fontSize=10,
            fontName='Helvetica',
            textColor=TITLE_CLR,
            leftIndent=12,
            spaceAfter=2,
        ),
    }
    return styles


# ──────────────────────────────────────────────
# Table Builder
# ──────────────────────────────────────────────
def is_negative(val):
    """Return True if string represents a negative number."""
    try:
        return float(val.replace(',', '').replace(' ', '')) < 0
    except:
        return False


def build_indicator_table(table_data, styles, page_width):
    """Build a ReportLab Table from parsed indicator data."""
    headers = table_data['headers']
    rows    = table_data['rows']
    
    if not rows:
        return None
    
    # Normalize columns — ensure all rows have same # of cols as header
    n_cols = max(len(headers), max(len(r) for r in rows))
    
    # Pad headers if needed
    while len(headers) < n_cols:
        headers.append('')
    
    # Column widths — first col (indicator name) gets more space
    available = page_width - 2*cm
    if n_cols <= 1:
        col_widths = [available]
    elif n_cols == 7:
        # Standard: Name | Dernier | Précédent | Le plus élevé | Le Plus Bas | Unité | Date
        col_widths = [
            available * 0.30,  # Indicator name
            available * 0.10,  # Dernier
            available * 0.10,  # Précédent
            available * 0.12,  # Le plus élevé
            available * 0.10,  # Le Plus Bas
            available * 0.15,  # Unité
            available * 0.13,  # Date
        ]
    else:
        first_col = available * 0.35
        rest = (available - first_col) / max(n_cols - 1, 1)
        col_widths = [first_col] + [rest] * (n_cols - 1)
    
    # Ensure col_widths length matches n_cols
    if len(col_widths) < n_cols:
        leftover = available - sum(col_widths)
        col_widths += [leftover / (n_cols - len(col_widths))] * (n_cols - len(col_widths))
    col_widths = col_widths[:n_cols]
    
    # Build table content
    header_row = [Paragraph(h, styles['col_header']) for h in headers]
    table_content = [header_row]
    
    row_commands = []
    
    for ri, row in enumerate(rows):
        # Pad row
        while len(row) < n_cols:
            row.append('')
        row = row[:n_cols]
        
        formatted_row = []
        for ci, cell in enumerate(row):
            if ci == 0:
                # Indicator name — bold, left-aligned
                p = Paragraph(cell, styles['cell_name'])
            elif is_negative(cell):
                p = Paragraph(cell, styles['cell_red'])
            else:
                p = Paragraph(cell, styles['cell'])
            formatted_row.append(p)
        
        table_content.append(formatted_row)
        
        # Alternating row colour
        if ri % 2 == 0:
            row_commands.append(('BACKGROUND', (0, ri + 1), (-1, ri + 1), ALT_ROW))
    
    tbl = Table(table_content, colWidths=col_widths, repeatRows=1)
    
    tbl_style = TableStyle([
        # Header
        ('BACKGROUND',   (0, 0), (-1, 0), HEADER_BG),
        ('TEXTCOLOR',    (0, 0), (-1, 0), colors.white),
        ('FONTNAME',     (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, 0), 8),
        ('ALIGN',        (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN',       (0, 0), (-1, -1), 'MIDDLE'),
        # Grid
        ('GRID',         (0, 0), (-1, -1), 0.5, BORDER_CLR),
        ('LINEBELOW',    (0, 0), (-1, 0), 1.5, colors.white),
        # Padding
        ('TOPPADDING',   (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
        ('LEFTPADDING',  (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        # First column left-align
        ('ALIGN',        (0, 1), (0, -1), 'LEFT'),
        ('ALIGN',        (1, 1), (-1, -1), 'CENTER'),
    ] + row_commands)
    
    tbl.setStyle(tbl_style)
    return tbl


# ──────────────────────────────────────────────
# Page Template
# ──────────────────────────────────────────────
def on_first_page(canvas, doc):
    """Draw header/footer on first page."""
    _draw_footer(canvas, doc)


def on_later_pages(canvas, doc):
    """Draw header/footer on subsequent pages."""
    _draw_header_bar(canvas, doc)
    _draw_footer(canvas, doc)


def _draw_header_bar(canvas, doc):
    w, h = doc.pagesize
    canvas.saveState()
    canvas.setFillColor(HEADER_BG)
    canvas.rect(0, h - 28, w, 28, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(15, h - 18, 'ALGÉRIE — INDICATEURS ÉCONOMIQUES')
    canvas.setFont('Helvetica', 8)
    canvas.drawRightString(w - 15, h - 18, f'Source: fr.tradingeconomics.com  |  {EXTRACTED}')
    canvas.restoreState()


def _draw_footer(canvas, doc):
    w, h = doc.pagesize
    canvas.saveState()
    canvas.setStrokeColor(BORDER_CLR)
    canvas.setLineWidth(0.5)
    canvas.line(15, 28, w - 15, 28)
    canvas.setFillColor(colors.HexColor('#888888'))
    canvas.setFont('Helvetica', 7)
    canvas.drawString(15, 18, f'© Trading Economics  |  {SOURCE_URL}')
    canvas.drawRightString(w - 15, 18, f'Page {doc.page}')
    canvas.restoreState()


# ──────────────────────────────────────────────
# PDF Builder
# ──────────────────────────────────────────────
def build_pdf(all_tabs):
    """Build the complete PDF document."""
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=1.8*cm,
        title='Algérie — Indicateurs Économiques',
        author='Trading Economics',
        subject='Comprehensive Algeria Economic KPIs',
    )
    
    page_w = A4[0] - 3*cm  # usable width
    styles = get_styles()
    story  = []
    
    # ── Cover page content ──────────────────────────────
    story.append(Spacer(1, 1.5*cm))
    
    # Flag-colour accent bar
    flag_data = [['', '', '']]
    flag_tbl  = Table(flag_data, colWidths=[page_w/3]*3, rowHeights=[8])
    flag_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#006233')),  # green
        ('BACKGROUND', (1, 0), (1, 0), colors.white),
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#D21034')),  # red
        ('GRID', (0,0), (-1,-1), 0, colors.white),
    ]))
    story.append(flag_tbl)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph('ALGÉRIE', ParagraphStyle('ctry', fontSize=28,
        fontName='Helvetica-Bold', textColor=TITLE_CLR, alignment=TA_CENTER)))
    story.append(Paragraph('INDICATEURS ÉCONOMIQUES', ParagraphStyle('ind', fontSize=16,
        fontName='Helvetica', textColor=ACCENT_CLR, alignment=TA_CENTER, spaceAfter=6)))
    
    story.append(HRFlowable(width='100%', thickness=1.5, color=ACCENT_CLR, spaceAfter=10))
    
    story.append(Paragraph(
        f'Source : <a href="{SOURCE_URL}" color="blue">{SOURCE_URL}</a>',
        styles['source']
    ))
    story.append(Paragraph(f'Extraction : {EXTRACTED}', styles['source']))
    story.append(Spacer(1, 0.5*cm))
    
    # Summary box
    total_indicators = sum(
        sum(len(t['rows']) for t in tables)
        for tables in all_tabs.values()
    )
    summary_data = [
        ['Sections', 'Indicateurs', 'Période'],
        [str(len(all_tabs)), str(total_indicators), 'Données en temps réel'],
    ]
    summary_tbl = Table(summary_data, colWidths=[page_w/3]*3, rowHeights=[22, 22])
    summary_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), HEADER_BG),
        ('TEXTCOLOR',     (0,0), (-1,0), colors.white),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 10),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND',    (0,1), (-1,1), LIGHT_GREEN),
        ('FONTNAME',      (0,1), (-1,1), 'Helvetica-Bold'),
        ('TEXTCOLOR',     (0,1), (-1,1), TITLE_CLR),
        ('GRID',          (0,0), (-1,-1), 0.5, BORDER_CLR),
    ]))
    story.append(summary_tbl)
    story.append(Spacer(1, 0.8*cm))
    
    # Table of Contents
    story.append(Paragraph('TABLE DES MATIÈRES', ParagraphStyle('toch', fontSize=11,
        fontName='Helvetica-Bold', textColor=TITLE_CLR, spaceBefore=8, spaceAfter=6)))
    for pid, tab_name in TAB_NAMES.items():
        if pid in all_tabs:
            n = sum(len(t['rows']) for t in all_tabs[pid])
            story.append(Paragraph(f'• {tab_name}  ({n} indicateurs)', styles['toc_item']))
    
    story.append(PageBreak())
    
    # ── Data sections ──────────────────────────────────
    col_headers_map = {
        7: ['Indicateur', 'Dernier', 'Précédent', 'Le plus élevé', 'Le Plus Bas', 'Unité', 'Date'],
    }
    
    for pid, tab_name in TAB_NAMES.items():
        if pid not in all_tabs:
            continue
        
        tab_tables = all_tabs[pid]
        section_elements = []
        
        # Section heading
        section_elements.append(Spacer(1, 4))
        section_heading = Paragraph(f'  {tab_name.upper()}', styles['section_header'])
        section_elements.append(section_heading)
        section_elements.append(Spacer(1, 4))
        
        for ti, table_data in enumerate(tab_tables):
            tbl = build_indicator_table(table_data, styles, page_w)
            if tbl:
                section_elements.append(tbl)
                section_elements.append(Spacer(1, 6))
        
        story.extend(section_elements)
    
    # ── Metadata note at end ───────────────────────────
    story.append(PageBreak())
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph('NOTE MÉTHODOLOGIQUE', ParagraphStyle('meth', fontSize=12,
        fontName='Helvetica-Bold', textColor=TITLE_CLR, spaceBefore=6, spaceAfter=8)))
    notes = [
        'Les données proviennent de Trading Economics (fr.tradingeconomics.com), qui compile les statistiques officielles publiées par '
        'l\'Office National des Statistiques d\'Algérie (ONS), la Banque d\'Algérie, le Fonds Monétaire International (FMI), '
        'la Banque Mondiale et d\'autres organismes internationaux.',
        '',
        'Colonnes :',
        '  • Dernier — Valeur la plus récente disponible',
        '  • Précédent — Valeur de la période précédente',
        '  • Le plus élevé — Valeur historique maximale',
        '  • Le Plus Bas — Valeur historique minimale (en rouge si négatif)',
        '  • Unité — Unité de mesure (Pour Cent, Milliards USD, etc.)',
        '  • Date — Période de référence de la dernière valeur',
        '',
        f'Document généré le {EXTRACTED}.',
        f'Source : {SOURCE_URL}',
    ]
    for note in notes:
        story.append(Paragraph(note, styles['note']))
    
    # ── Build ──────────────────────────────────────────
    print(f"\nBuilding PDF → {OUTPUT_PATH}")
    doc.build(
        story,
        onFirstPage=on_first_page,
        onLaterPages=on_later_pages,
    )
    print(f"  Done — PDF saved.")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def main():
    print("=" * 60)
    print("Algeria TradingEconomics — PDF Generator")
    print("=" * 60)
    
    # Fetch & parse
    try:
        html = fetch_html()
    except Exception as e:
        print(f"Network error: {e}")
        print("Trying cached HTML...")
        try:
            with open('/tmp/te_algeria_raw.html', 'r', encoding='utf-8') as f:
                html = f.read()
            print("  Using cached HTML.")
        except:
            print("No cached HTML either. Exiting.")
            return
    
    print("\nParsing indicator tables...")
    all_tabs = extract_all_data(html)
    
    total = sum(sum(len(t['rows']) for t in tables) for tables in all_tabs.values())
    print(f"\n  Total: {len(all_tabs)} sections, {total} indicator rows")
    
    # Build PDF
    build_pdf(all_tabs)
    print(f"\n✓ PDF: {OUTPUT_PATH}")

# ── Import helpers from scraper ──────────────────
def extract_all_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    all_tabs = {}
    panels = soup.find_all('div', {'role': 'tabpanel'})
    for panel in panels:
        pid = panel.get('id', f'unknown_{len(all_tabs)}')
        tables_data = []
        for table in panel.find_all('table'):
            rows = table.find_all('tr')
            if not rows:
                continue
            header_cells = rows[0].find_all(['th', 'td'])
            headers = [c.get_text(strip=True) for c in header_cells]
            data_rows = []
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if not cells:
                    continue
                row_data = [c.get_text(strip=True) for c in cells]
                if any(row_data):
                    data_rows.append(row_data)
            if data_rows:
                tables_data.append({'headers': headers, 'rows': data_rows})
        if tables_data:
            all_tabs[pid] = tables_data
            total_rows = sum(len(t['rows']) for t in tables_data)
            print(f"  Tab '{TAB_NAMES.get(pid, pid)}': {len(tables_data)} table(s), {total_rows} rows")
    return all_tabs


if __name__ == '__main__':
    main()
