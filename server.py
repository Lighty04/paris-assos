#!/usr/bin/env python3
"""
Paris Subventions API Server
Serves paginated data from the pre-processed data.json file
"""

import http.server
import json
import socketserver
import urllib.parse
import os
import sys

PORT = 8010
DATA_FILE = "/home/decisionhelper/website/data.json"
CACHE = None

def load_data():
    """Load and cache the data file"""
    global CACHE
    if CACHE is None:
        print(f"Loading data from {DATA_FILE}...")
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Data is already a list of associations
            CACHE = data
            print(f"Loaded {len(CACHE)} associations")
    return CACHE

def get_filters(data):
    """Get unique years and sectors for filters"""
    years = set()
    sectors = set()
    for assoc in data:
        for sub in assoc.get('subventions', []):
            year = sub.get('year', '')
            if year:
                years.add(year)
        for sector in assoc.get('sectors', []):
            if sector:
                sectors.add(sector)
    return {
        'years': sorted(list(years), reverse=True),
        'sectors': sorted(list(sectors))
    }

def filter_associations(data, search='', year='', sector=''):
    """Filter associations based on search criteria"""
    search_lower = search.lower()
    filtered = []
    
    for assoc in data:
        # Search filter (name, siret, sectors)
        matches_search = True
        if search_lower:
            name = assoc.get('name', '')
            siret = assoc.get('siret', '')
            sectors = assoc.get('sectors', [])
            matches_search = (
                search_lower in name.lower() or
                search_lower in siret or
                any(search_lower in str(s).lower() for s in sectors)
            )
        
        # Year filter
        matches_year = True
        if year:
            subventions = assoc.get('subventions', [])
            matches_year = any(sub.get('year') == year for sub in subventions)
        
        # Sector filter
        matches_sector = True
        if sector:
            matches_sector = sector in assoc.get('sectors', [])
        
        if matches_search and matches_year and matches_sector:
            filtered.append(assoc)
    
    return filtered

def get_last_year_info(assoc):
    """Get the year and amount from the most recent year with subvention data"""
    subventions = assoc.get('subventions', [])
    if not subventions:
        return {'year': None, 'amount': 0}
    
    # Group by year and sum amounts
    year_totals = {}
    for sub in subventions:
        year = sub.get('year', '')
        if year:
            if year not in year_totals:
                year_totals[year] = 0
            year_totals[year] += sub.get('amount', 0)
    
    if not year_totals:
        return {'year': None, 'amount': 0}
    
    # Get the most recent year
    last_year = max(year_totals.keys())
    return {'year': last_year, 'amount': year_totals[last_year]}

def sort_associations(data, sort_param=''):
    """Sort associations based on sort parameter"""
    if not sort_param:
        return data
    
    def get_last_year_amount(assoc):
        """Get the amount from the most recent year"""
        info = get_last_year_info(assoc)
        return info['amount']
    
    if sort_param == 'total_desc':
        return sorted(data, key=lambda x: x.get('totalAmount', 0), reverse=True)
    elif sort_param == 'total_asc':
        return sorted(data, key=lambda x: x.get('totalAmount', 0))
    elif sort_param == 'lastYear_desc':
        return sorted(data, key=get_last_year_amount, reverse=True)
    elif sort_param == 'lastYear_asc':
        return sorted(data, key=get_last_year_amount)
    elif sort_param == 'name_asc':
        return sorted(data, key=lambda x: x.get('name', '').lower())
    elif sort_param == 'name_desc':
        return sorted(data, key=lambda x: x.get('name', '').lower(), reverse=True)
    else:
        return data

def get_stats(data):
    """Calculate statistics"""
    total_assoc = len(data)
    total_subv = sum(len(a.get('subventions', [])) for a in data)
    total_amt = sum(a.get('totalAmount', 0) for a in data)
    
    years = set()
    for a in data:
        for s in a.get('subventions', []):
            year = s.get('year', '')
            if year:
                years.add(year)
    year_arr = sorted(list(years))
    
    return {
        'totalAssociations': total_assoc,
        'totalSubventions': total_subv,
        'totalAmount': total_amt,
        'yearRange': f"{year_arr[0]}-{year_arr[-1]}" if len(year_arr) > 1 else (year_arr[0] if year_arr else '-')
    }

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logs
        pass
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        
        # API endpoints
        if path == '/api/associations':
            data = load_data()
            
            # Get parameters
            page = int(query.get('page', ['1'])[0])
            per_page = int(query.get('per_page', ['100'])[0])  # Changed default to 100
            search = query.get('search', [''])[0]
            year = query.get('year', [''])[0]
            sector = query.get('sector', [''])[0]
            sort = query.get('sort', [''])[0]
            
            # Filter data
            filtered = filter_associations(data, search, year, sector)
            
            # Sort data
            filtered = sort_associations(filtered, sort)
            
            # Paginate
            total = len(filtered)
            start = (page - 1) * per_page
            end = start + per_page
            page_data = filtered[start:end]
            
            self.send_json({
                'associations': page_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': (total + per_page - 1) // per_page
                }
            })
            return
        
        # Search endpoint
        if path == '/api/associations/search':
            data = load_data()
            q = query.get('q', [''])[0]
            page = int(query.get('page', ['1'])[0])
            limit = int(query.get('limit', ['100'])[0])
            
            filtered = filter_associations(data, search=q)
            
            total = len(filtered)
            start = (page - 1) * limit
            end = start + limit
            page_data = filtered[start:end]
            
            self.send_json({
                'associations': page_data,
                'pagination': {
                    'page': page,
                    'per_page': limit,
                    'total': total,
                    'total_pages': (total + limit - 1) // limit
                }
            })
            return
        
        # Single association by ID (siret)
        if path.startswith('/api/associations/'):
            data = load_data()
            id_param = path.split('/')[-1]
            assoc = next((a for a in data if a.get('siret') == id_param), None)
            if assoc:
                self.send_json(assoc)
            else:
                self.send_response(404)
                self.end_headers()
            return
        
        if path == '/api/filters':
            data = load_data()
            self.send_json(get_filters(data))
            return
        
        if path == '/api/stats':
            data = load_data()
            search = query.get('search', [''])[0]
            year = query.get('year', [''])[0]
            sector = query.get('sector', [''])[0]
            filtered = filter_associations(data, search, year, sector)
            self.send_json(get_stats(filtered))
            return
        
        # Legacy: association lookup by siret query param
        if path == '/api/association':
            data = load_data()
            siret = query.get('siret', [''])[0]
            assoc = next((a for a in data if a.get('siret') == siret), None)
            if assoc:
                self.send_json(assoc)
            else:
                self.send_response(404)
                self.end_headers()
            return
        
        # Serve static files
        if path == '/':
            path = '/index.html'
        
        file_path = '/home/decisionhelper/website' + path
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return self.serve_file(file_path)
        
        self.send_response(404)
        self.end_headers()
    
    def serve_file(self, file_path):
        content_type = 'text/html'
        if file_path.endswith('.js'):
            content_type = 'application/javascript'
        elif file_path.endswith('.css'):
            content_type = 'text/css'
        elif file_path.endswith('.json'):
            content_type = 'application/json'
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_response(500)
            self.end_headers()

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    os.chdir('/home/decisionhelper/website')
    
    # Preload data
    try:
        load_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)
    
    with ReusableTCPServer(("", PORT), Handler) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            sys.exit(0)
