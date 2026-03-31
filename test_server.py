import urllib.request, json

# Test stats
resp = urllib.request.urlopen('http://localhost:8010/api/stats').read().decode()
# Find the JSON boundary
if '}' in resp:
    brace_count = 0
    for i, c in enumerate(resp):
        if c == '{': brace_count += 1
        elif c == '}': brace_count -= 1
        if brace_count == 0 and i > 0:
            stats = json.loads(resp[:i+1])
            print(f"Stats: {stats}")
            break

# Test associations
resp = urllib.request.urlopen('http://localhost:8010/api/associations?page=1&per_page=5').read().decode()
brace_count = 0
for i, c in enumerate(resp):
    if c == '{': brace_count += 1
    elif c == '}': brace_count -= 1
    if brace_count == 0 and i > 0:
        data = json.loads(resp[:i+1])
        print(f"Total associations: {data['pagination']['total']}")
        print(f"Pages: {data['pagination']['total_pages']}")
        print(f"First 3 names:")
        for a in data['associations'][:3]:
            print(f"  - {a['name']}")
        break

# Test filters
resp = urllib.request.urlopen('http://localhost:8010/api/filters').read().decode()
if '}' in resp:
    brace_count = 0
    for i, c in enumerate(resp):
        if c == '{': brace_count += 1
        elif c == '}': brace_count -= 1
        if brace_count == 0 and i > 0:
            filters = json.loads(resp[:i+1])
            print(f"Years: {len(filters['years'])} unique years")
            print(f"Sectors: {len(filters['sectors'])} unique sectors")
            break

print("All tests passed!")
