#!/usr/bin/env python3
"""
Scraper for TradingEconomics Algeria Economic Indicators
Source: https://fr.tradingeconomics.com/algeria/indicators
Generates a comprehensive PDF preserving all KPIs and data.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
}

# Tab categories and their URL parameters
TABS = {
    'Vue d\'ensemble': '',
    'PIB': 'gdp',
    'Main-d\'œuvre': 'labour',
    'Tarifs': 'prices',
    'Argent': 'money',
    'Commerce': 'trade',
    'Gouvernement': 'government',
    'Entreprise': 'business',
    'Consommateur': 'consumer',
    'Énergie': 'energy',
}

BASE_URL = 'https://fr.tradingeconomics.com/algeria/indicators'

def fetch_tab(tab_key, tab_param):
    """Fetch data for a specific tab."""
    if tab_param:
        url = f'{BASE_URL}#{tab_param}'
    else:
        url = BASE_URL
    
    print(f"  Fetching: {url}")
    
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None

def parse_indicators_table(html_content):
    """Parse the main indicators table from the HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    all_data = {}
    
    # Find all tab panels/sections
    # TradingEconomics uses a specific table structure
    tables = soup.find_all('table', class_=re.compile(r'table', re.I))
    if not tables:
        # Try to find any table
        tables = soup.find_all('table')
    
    print(f"  Found {len(tables)} tables")
    
    # Find the main data table
    main_table = None
    for table in tables:
        rows = table.find_all('tr')
        if len(rows) > 5:  # Main table should have many rows
            main_table = table
            break
    
    if not main_table:
        return {}
    
    # Parse headers
    headers = []
    header_row = main_table.find('tr')
    if header_row:
        for th in header_row.find_all(['th', 'td']):
            headers.append(th.get_text(strip=True))
    
    # Parse data rows
    rows_data = []
    for row in main_table.find_all('tr')[1:]:
        cells = row.find_all(['td', 'th'])
        if cells:
            row_data = [cell.get_text(strip=True) for cell in cells]
            if any(row_data):  # Skip empty rows
                rows_data.append(row_data)
    
    return {'headers': headers, 'rows': rows_data}

def get_all_tab_data():
    """Get data by directly fetching the page and parsing all sections."""
    print("Fetching main page...")
    
    try:
        resp = requests.get(BASE_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"Error: {e}")
        return {}
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Save raw HTML for inspection
    with open('/tmp/te_algeria_raw.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("  Saved raw HTML to /tmp/te_algeria_raw.html")
    
    # Find all tab sections
    all_sections = {}
    
    # Find tab content divs
    tab_panels = soup.find_all('div', {'role': 'tabpanel'})
    print(f"  Found {len(tab_panels)} tab panels")
    
    # Try different approaches to find the data
    # Look for the indicators table
    tables = soup.find_all('table')
    print(f"  Found {len(tables)} tables total")
    
    for i, table in enumerate(tables):
        rows = table.find_all('tr')
        if len(rows) > 3:
            print(f"  Table {i}: {len(rows)} rows")
            # Get first row as sample
            first_row = rows[0]
            print(f"    First row: {first_row.get_text(strip=True)[:100]}")
    
    return html, soup

def extract_indicator_data(soup):
    """Extract all indicator data from the parsed HTML."""
    indicators = []
    
    # TradingEconomics renders data in a specific way
    # Look for rows with indicator names and values
    
    # Method 1: Look for specific CSS classes
    rows = soup.find_all('tr')
    print(f"  Total tr elements: {len(rows)}")
    
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) >= 3:
            cell_texts = [c.get_text(strip=True) for c in cells]
            if cell_texts[0] and not all(c == '' for c in cell_texts):
                indicators.append(cell_texts)
    
    return indicators

def main():
    print("=" * 60)
    print("TradingEconomics Algeria - Data Extraction")
    print("=" * 60)
    
    html, soup = get_all_tab_data()
    
    # Extract indicators
    print("\nExtracting indicator data...")
    data = extract_indicator_data(soup)
    
    print(f"\nFound {len(data)} data rows")
    for row in data[:5]:
        print(f"  {row}")
    
    return data, html, soup

if __name__ == '__main__':
    data, html, soup = main()
