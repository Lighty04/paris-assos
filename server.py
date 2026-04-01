#!/usr/bin/env python3
"""
Paris Subventions API Server
Serves paginated data from the pre-processed data_net.json file (net subventions)
"""

import http.server
import json
import socketserver
import urllib.parse
import os
import sys

PORT = 8010
# Use net data by default
DATA_FILE = "/home/decisionhelper/website/data_net.json"
RAW_DATA_FILE = "/home/decisionhelper/website/data.json"
CACHE = None
RAW_CACHE = None

def load_data(use_net=True):
    """Load and cache the data file"""
    global CACHE, RAW_CACHE
    
    if use_net and CACHE is not None:
        return CACHE.get('associations', [])
    
    if not use_net and RAW_CACHE is not None:
        return RAW_CACHE
    
    file_to_load = DATA_FILE if use_net else RAW_DATA_FILE
    print(f"Loading data from {file_to_load}...")
    
    try:
        with open(file_to_load, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if use_net:
            CACHE = data
            associations = data.get('associations', [])
            print(f"Loaded {len(associations)} associations (net subventions)")
            return associations
        else:
            RAW_CACHE = data
            print(f"Loaded {len(data)} associations (raw data)")
            return data
    except Exception as e:
        print(f"Error loading {file_to_load}: {e}")
        return []

def load_stats():
    """Load global statistics"""
    global CACHE
    if CACHE is None:
        load_data(use_net=True)
    return CACHE.get('stats', {})

def get_filters(data):
    """Get unique years and sectors for filters"""
    years = set()
    sectors = set()
    for assoc in data:
        # Use netSubventions for years
        for sub in assoc.get('netSubventions', []):
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
        
        # Year filter - use netSubventions
        matches_year = True
        if year:
            net_subs = assoc.get('netSubventions', [])
            matches_year = any(sub.get('year') == year for sub in net_subs)
        
        # Sector filter
        matches_sector = True
        if sector:
            matches_sector = sector in assoc.get('sectors', [])
        
        if matches_search and matches_year and matches_sector:
            filtered.append(assoc)
    
    return filtered

def get_last_year_info(assoc):
    """Get the year and net amount from the most recent year with subvention data"""
    net_subventions = assoc.get('netSubventions', [])
    if not net_subventions:
        return {'year': None, 'amount': 0}
    
    # Get the most recent year
    sorted_subs = sorted(net_subventions, key=lambda x: x.get('year', ''), reverse=True)
    if sorted_subs:
        return {
            'year': sorted_subs[0].get('year'),
            'amount': sorted_subs[0].get('net_amount', 0)
        }
    return {'year': None, 'amount': 0}

def sort_associations(data, sort_param=''):
    """Sort associations based on sort parameter"""
    if not sort_param:
        return data
    
    def get_last_year_amount(assoc):
        """Get the net amount from the most recent year"""
        info = get_last_year_info(assoc)
        return info['amount']
    
    if sort_param == 'total_desc':
        return sorted(data, key=lambda x: x.get('netTotalAmount', 0), reverse=True)
    elif sort_param == 'total_asc':
        return sorted(data, key=lambda x: x.get('netTotalAmount', 0))
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
    """Calculate statistics using net amounts"""
    total_assoc = len(data)
    total_subv = sum(len(a.get('netSubventions', [])) for a in data)
    total_amt = sum(a.get('netTotalAmount', 0) for a in data)
    
    years = set()
    for a in data:
        for s in a.get('netSubventions', []):
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
            data = load_data(use_net=True)
            
            # Get parameters
            page = int(query.get('page', ['1'])[0])
            per_page = int(query.get('per_page', ['100'])[0])
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
            data = load_data(use_net=True)
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
            data = load_data(use_net=True)
            id_param = path.split('/')[-1]
            assoc = next((a for a in data if a.get('siret') == id_param), None)
            if assoc:
                self.send_json(assoc)
            else:
                self.send_response(404)
                self.end_headers()
            return
        
        # Raw association data (for transparency)
        if path.startswith('/api/associations/raw/'):
            raw_data = load_data(use_net=False)
            id_param = path.split('/')[-1]
            assoc = next((a for a in raw_data if a.get('siret') == id_param), None)
            if assoc:
                self.send_json(assoc)
            else:
                self.send_response(404)
                self.end_headers()
            return
        
        # Raw associations list (for transparency)
        if path == '/api/associations/raw':
            raw_data = load_data(use_net=False)
            self.send_json({
                'associations': raw_data,
                'note': 'Raw data without net subvention calculation. Use /api/associations for net data.'
            })
            return
        
        if path == '/api/filters':
            data = load_data(use_net=True)
            self.send_json(get_filters(data))
            return
        
        if path == '/api/stats':
            data = load_data(use_net=True)
            search = query.get('search', [''])[0]
            year = query.get('year', [''])[0]
            sector = query.get('sector', [''])[0]
            filtered = filter_associations(data, search, year, sector)
            self.send_json(get_stats(filtered))
            return
        
        # Data quality stats endpoint
        if path == '/api/stats/quality':
            stats = load_stats()
            self.send_json({
                'dataQuality': stats.get('dataQuality', {}),
                'totals': {
                    'netAmount': stats.get('totalNetAmount', 0),
                    'rawAmount': stats.get('totalRawAmount', 0),
                    'difference': stats.get('difference', 0),
                    'reductionPercent': stats.get('reductionPercent', 0)
                }
            })
            return
        
        # Legacy: association lookup by siret query param
        if path == '/api/association':
            data = load_data(use_net=True)
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
        load_data(use_net=True)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)
    
    with ReusableTCPServer(("", PORT), Handler) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        print("Serving net subvention data from data_net.json")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            sys.exit(0)
