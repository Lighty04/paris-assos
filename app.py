#!/usr/bin/env python3
"""
Paris Subventions API - Production Flask Application
Handles 100+ concurrent users with caching and optimizations
"""

import json
import os
import logging
import sys
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, Response
from flask_caching import Cache
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Import configuration
from config import get_config

# Initialize Flask app
app = Flask(__name__, static_folder=None)
config = get_config()
app.config.from_object(config)

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/app.log') if not config.DEBUG else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize cache
cache = Cache(app)

# Enable CORS
CORS(app, origins=config.CORS_ORIGINS.split(',') if ',' in config.CORS_ORIGINS else [config.CORS_ORIGINS])

# Handle proxy headers (for Render/Railway behind reverse proxy)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Global data cache (in-memory for fast access)
DATA_CACHE = None
DATA_TIMESTAMP = None

def load_data(force_reload=False):
    """Load and process association data from JSON file"""
    global DATA_CACHE, DATA_TIMESTAMP
    
    # Check if we need to reload
    if not force_reload and DATA_CACHE is not None:
        # Check if file has been modified
        try:
            mtime = os.path.getmtime(config.DATA_FILE)
            if DATA_TIMESTAMP and mtime <= DATA_TIMESTAMP:
                return DATA_CACHE
        except OSError:
            pass
    
    logger.info(f"Loading data from {config.DATA_FILE}...")
    start_time = datetime.now()
    
    try:
        with open(config.DATA_FILE, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Handle both formats: old flat array and new object with associations key
        if isinstance(raw_data, dict) and 'associations' in raw_data:
            raw_data = raw_data['associations']
            logger.info("Loaded data_net.json format (object with associations key)")
        elif isinstance(raw_data, list):
            logger.info("Loaded legacy data.json format (flat array)")
        else:
            raise ValueError(f"Unexpected data format: {type(raw_data)}")
        
        associations = {}
        for item in raw_data:
            siret = item.get('siret', '') or item.get('numero_siret', '')
            if not siret:
                continue
            
            if siret not in associations:
                associations[siret] = {
                    'name': item.get('name', 'Unknown'),
                    'siret': siret,
                    'mission': item.get('mission', 'Non spécifié'),
                    'sectors': item.get('sectors', []),
                    'subventions': [],
                    'totalAmount': 0,
                    'board_members': item.get('board_members', []),
                    'board_data_source': item.get('board_data_source', ''),
                    'board_coverage': item.get('board_coverage', 'none'),
                    # Add net subvention fields
                    'netSubventions': [],
                    'netTotalAmount': 0,
                    'netYearlyData': {}
                }
            
            # Add subventions (raw data)
            for sub in item.get('subventions', []):
                associations[siret]['subventions'].append({
                    'year': str(sub.get('year', '')),
                    'amount': float(sub.get('amount', 0)),
                    'object': sub.get('object', ''),
                    'nature': sub.get('nature', ''),
                    'direction': sub.get('direction', ''),
                    'collectivite': sub.get('collectivite', '')
                })
            
            # Add net subventions (processed data)
            for sub in item.get('netSubventions', []):
                associations[siret]['netSubventions'].append({
                    'year': str(sub.get('year', '')),
                    'net_amount': float(sub.get('net_amount', 0)),
                    'raw_amount': float(sub.get('raw_amount', 0)),
                    'object': sub.get('object', ''),
                    'adjustment_reason': sub.get('adjustment_reason', '')
                })
            
            # Use netTotalAmount if available, otherwise calculate from subventions
            associations[siret]['netTotalAmount'] = float(item.get('netTotalAmount', 0))
            associations[siret]['netYearlyData'] = item.get('netYearlyData', {})
            
            # Recalculate raw total for reference
            associations[siret]['totalAmount'] = sum(
                s['amount'] for s in associations[siret]['subventions']
            )
        
        # Sort by net total amount descending (primary display metric)
        DATA_CACHE = sorted(associations.values(), key=lambda x: x.get('netTotalAmount', x['totalAmount']), reverse=True)
        DATA_TIMESTAMP = os.path.getmtime(config.DATA_FILE)
        
        load_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Loaded {len(DATA_CACHE)} associations in {load_time:.2f}s")
        
        return DATA_CACHE
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        if DATA_CACHE is not None:
            logger.warning("Returning cached data due to error")
            return DATA_CACHE
        raise

def get_filters_data(data):
    """Extract unique years and sectors for filters"""
    years = set()
    sectors = set()
    
    for assoc in data:
        for sub in assoc['subventions']:
            if sub.get('year'):
                years.add(sub['year'])
        for sector in assoc.get('sectors', []):
            if sector:
                sectors.add(sector)
    
    return {
        'years': sorted(list(years), reverse=True),
        'sectors': sorted(list(sectors))
    }

def filter_associations(data, search='', year='', sector=''):
    """Filter associations based on search criteria"""
    if not search and not year and not sector:
        return data
    
    search_lower = search.lower()
    filtered = []
    
    for assoc in data:
        # Search filter
        matches_search = True
        if search_lower:
            matches_search = (
                search_lower in assoc['name'].lower() or
                search_lower in assoc['siret'] or
                any(search_lower in s.lower() for s in assoc.get('sectors', []))
            )
        
        # Year filter
        matches_year = True
        if year:
            matches_year = any(sub.get('year') == year for sub in assoc['subventions'])
        
        # Sector filter
        matches_sector = True
        if sector:
            matches_sector = sector in assoc.get('sectors', [])
        
        if matches_search and matches_year and matches_sector:
            filtered.append(assoc)
    
    return filtered

def calculate_stats(data):
    """Calculate statistics for the filtered data"""
    total_assoc = len(data)
    total_subv = sum(len(a['subventions']) for a in data)
    total_amt = sum(a['totalAmount'] for a in data)
    
    years = set()
    for a in data:
        for s in a['subventions']:
            if s.get('year'):
                years.add(s['year'])
    
    year_arr = sorted(list(years))
    year_range = f"{year_arr[0]}-{year_arr[-1]}" if len(year_arr) > 1 else (year_arr[0] if year_arr else '-')
    
    return {
        'totalAssociations': total_assoc,
        'totalSubventions': total_subv,
        'totalAmount': total_amt,
        'yearRange': year_range
    }

# Routes
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        data = load_data()
        return jsonify({
            'status': 'healthy',
            'associations_count': len(data),
            'timestamp': datetime.now().isoformat(),
            'cache_status': 'active' if DATA_CACHE else 'loading'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/api/associations')
@cache.cached(timeout=300, query_string=True)
def get_associations():
    """Get paginated list of associations with optional filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', config.DEFAULT_PER_PAGE, type=int), config.MAX_PER_PAGE)
        search = request.args.get('search', '', type=str)
        year = request.args.get('year', '', type=str)
        sector = request.args.get('sector', '', type=str)
        
        # Validate page
        if page < 1:
            page = 1
        
        # Load and filter data
        data = load_data()
        filtered = filter_associations(data, search, year, sector)
        
        # Paginate
        total = len(filtered)
        start = (page - 1) * per_page
        end = start + per_page
        page_data = filtered[start:end]
        
        return jsonify({
            'associations': page_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_associations: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/filters')
@cache.cached(timeout=600)  # Cache for 10 minutes (filters don't change often)
def get_filters():
    """Get available filter options (years and sectors)"""
    try:
        data = load_data()
        return jsonify(get_filters_data(data))
    except Exception as e:
        logger.error(f"Error in get_filters: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/stats')
@cache.cached(timeout=300, query_string=True)
def get_stats():
    """Get statistics for the current filter view"""
    try:
        search = request.args.get('search', '', type=str)
        year = request.args.get('year', '', type=str)
        sector = request.args.get('sector', '', type=str)
        
        data = load_data()
        filtered = filter_associations(data, search, year, sector)
        
        return jsonify(calculate_stats(filtered))
        
    except Exception as e:
        logger.error(f"Error in get_stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/association')
@cache.cached(timeout=300, query_string=True)
def get_association_detail():
    """Get detailed information for a specific association by SIRET"""
    try:
        siret = request.args.get('siret', '', type=str)
        if not siret:
            return jsonify({'error': 'SIRET parameter is required'}), 400
        
        data = load_data()
        assoc = next((a for a in data if a['siret'] == siret), None)
        
        if assoc:
            return jsonify(assoc)
        else:
            return jsonify({'error': 'Association not found'}), 404
            
    except Exception as e:
        logger.error(f"Error in get_association_detail: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/reload', methods=['POST'])
def reload_data():
    """Endpoint to force data reload (useful for data updates)"""
    try:
        # Clear cache
        cache.clear()
        
        # Reload data
        data = load_data(force_reload=True)
        
        return jsonify({
            'success': True,
            'associations_count': len(data),
            'message': 'Data reloaded successfully'
        })
    except Exception as e:
        logger.error(f"Error reloading data: {e}")
        return jsonify({'error': str(e)}), 500

# Static file serving (using WhiteNoise in production)
@app.route('/')
def serve_index():
    """Serve the main index.html"""
    static_folder = config.STATIC_FOLDER
    if os.path.exists(os.path.join(static_folder, 'index.html')):
        return send_from_directory(static_folder, 'index.html')
    return jsonify({'error': 'index.html not found'}), 404

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    static_folder = config.STATIC_FOLDER
    file_path = os.path.join(static_folder, filename)
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(static_folder, filename)
    
    # Return index.html for client-side routing (SPA)
    if os.path.exists(os.path.join(static_folder, 'index.html')):
        return send_from_directory(static_folder, 'index.html')
    
    return jsonify({'error': 'File not found'}), 404

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Preload data on startup
with app.app_context():
    try:
        load_data()
        logger.info("Data preloaded successfully")
    except Exception as e:
        logger.error(f"Failed to preload data: {e}")

if __name__ == '__main__':
    # Use this for development only
    # Production should use Gunicorn
    port = config.PORT
    host = config.HOST
    debug = config.DEBUG
    
    logger.info(f"Starting development server on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)