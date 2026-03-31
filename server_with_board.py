#!/usr/bin/env python3
import http.server, json, socketserver, urllib.parse, os, sys
PORT = 8010
DATA_FILE = '/home/decisionhelper/website/data.json'
CACHE = None

def load_data():
    global CACHE
    if CACHE is None:
        with open(DATA_FILE, 'r') as f:
            raw_data = json.load(f)
        associations = {}
        for item in raw_data:
            siret = item.get('siret', '')
            if not siret: continue
            if siret not in associations:
                associations[siret] = {
                    'name': item.get('name', 'Unknown'),
                    'siret': siret,
                    'mission': item.get('mission', ''),
                    'sectors': item.get('sectors', []),
                    'subventions': [],
                    'totalAmount': 0,
                    'board_members': item.get('board_members', []),
                    'board_data_source': item.get('board_data_source', ''),
                    'board_coverage': item.get('board_coverage', 'none')
                }
            associations[siret]['subventions'].extend(item.get('subventions', []))
            associations[siret]['totalAmount'] = sum(s['amount'] for s in associations[siret]['subventions'])
            # Keep board_members if they exist
            if item.get('board_members') and len(item.get('board_members')) > 0 and not associations[siret]['board_members']:
                associations[siret]['board_members'] = item.get('board_members')
                associations[siret]['board_data_source'] = item.get('board_data_source', '')
                associations[siret]['board_coverage'] = item.get('board_coverage', 'none')
        CACHE = sorted(associations.values(), key=lambda x: x['totalAmount'], reverse=True)
        print(f"Loaded {len(CACHE)} associations")
    return CACHE

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if path == '/api/associations':
            data = load_data()
            page = int(query.get('page', ['1'])[0])
            per_page = int(query.get('per_page', ['50'])[0])
            search = query.get('search', [''])[0].lower()
            year = query.get('year', [''])[0]
            sector = query.get('sector', [''])[0]
            filtered = data
            if search:
                filtered = [a for a in filtered if search in a['name'].lower() or search in a['siret'] or any(search in s.lower() for s in a['sectors'])]
            if year:
                filtered = [a for a in filtered if any(s['year'] == year for s in a['subventions'])]
            if sector:
                filtered = [a for a in filtered if sector in a['sectors']]
            total = len(filtered)
            start = (page-1)*per_page
            page_data = filtered[start:start+per_page]
            self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({'associations': page_data, 'pagination': {'page': page, 'per_page': per_page, 'total': total, 'total_pages': (total+per_page-1)//per_page}}).encode())
        elif path == '/api/stats':
            data = load_data()
            search = query.get('search', [''])[0].lower()
            year = query.get('year', [''])[0]
            sector = query.get('sector', [''])[0]
            filtered = data
            if search:
                filtered = [a for a in filtered if search in a['name'].lower() or search in a['siret'] or any(search in s.lower() for s in a['sectors'])]
            if year:
                filtered = [a for a in filtered if any(s['year'] == year for s in a['subventions'])]
            if sector:
                filtered = [a for a in filtered if sector in a['sectors']]
            total = len(filtered); subv = sum(len(a['subventions']) for a in filtered); amt = sum(a['totalAmount'] for a in filtered)
            years = sorted(set(s['year'] for a in filtered for s in a['subventions'] if s.get('year')))
            yearRange = f"{years[0]}-{years[-1]}" if len(years) > 1 else (years[0] if years else '-')
            self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({'totalAssociations': total, 'totalSubventions': subv, 'totalAmount': amt, 'yearRange': yearRange}).encode())
        elif path == '/api/filters':
            data = load_data()
            years = sorted(set(s['year'] for a in data for s in a['subventions'] if s.get('year')), reverse=True)
            sectors = sorted(set(s for a in data for s in a['sectors']))
            self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers()
            self.wfile.write(json.dumps({'years': years, 'sectors': sectors}).encode())
        elif path == '/api/association':
            data = load_data(); siret = query.get('siret', [''])[0]
            assoc = next((a for a in data if a['siret'] == siret), None)
            if assoc:
                self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers()
                self.wfile.write(json.dumps(assoc).encode())
            else: self.send_response(404); self.end_headers()
        elif path == '/': path = '/index.html'
        file_path = '/home/decisionhelper/website' + path
        if os.path.exists(file_path) and os.path.isfile(file_path):
            content_type = 'text/html' if file_path.endswith('.html') else 'application/javascript' if file_path.endswith('.js') else 'application/json' if file_path.endswith('.json') else 'text/plain'
            with open(file_path, 'rb') as f: content = f.read()
            self.send_response(200); self.send_header('Content-Type', content_type); self.send_header('Content-Length', len(content)); self.end_headers()
            self.wfile.write(content)
        else: self.send_response(404); self.end_headers()

load_data()
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(('', PORT), Handler) as httpd:
    print(f'Server running on port {PORT}')
    httpd.serve_forever()
