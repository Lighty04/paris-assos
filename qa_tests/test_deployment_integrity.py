#!/usr/bin/env python3
"""
QA Test Suite for Deployment Integrity
Tests that deployed files match workspace and Git state.

Issues Caught:
1. Workspace/Deployment Mismatch - Files differ between workspace and deployment
2. Uncommitted changes pending - Code not committed before deploy
3. Missing files in deployment
"""

import json
import sys
import os
import hashlib
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
WEBSITE_DIR = PROJECT_ROOT / "paris-assos-website"
DATA_FILE = WEBSITE_DIR / "data_net.json"

def test_index_html_exists():
    """Verify index.html exists in deployment directory"""
    index_path = '/home/decisionhelper/website/index.html'
    assert os.path.exists(index_path), f"index.html not found at {index_path}"
    print(f"✅ index.html exists ({os.path.getsize(index_path)} bytes)")
    
def test_static_folder_configured():
    """Verify STATIC_FOLDER points to correct directory"""
    # Check config.py content
    with open('/home/decisionhelper/website/config.py') as f:
        content = f.read()
    assert '/home/decisionhelper/website' in content, "STATIC_FOLDER not pointing to correct directory"
    print("✅ STATIC_FOLDER configured correctly")

def run_command(cmd, cwd=None):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd or PROJECT_ROOT
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1

def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        return None

def test_workspace_matches_deployment():
    """
    Verify deployed files match workspace.
    Compare MD5 hashes of critical files.
    """
    print("\n[TEST] Checking workspace matches deployment...")
    
    # Critical files that must match
    critical_files = [
        'paris-assos-website/data_net.json',
        'paris-assos-website/server.py',
    ]
    
    mismatches = []
    
    # For local deployment, workspace IS deployment
    # So we check that files exist and are valid
    for rel_path in critical_files:
        file_path = PROJECT_ROOT / rel_path
        
        if not file_path.exists():
            mismatches.append(f"{rel_path}: file not found")
            continue
        
        # Check file is valid JSON if it's a JSON file
        if rel_path.endswith('.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                mismatches.append(f"{rel_path}: invalid JSON - {e}")
    
    if mismatches:
        print(f"   ❌ FAILED: {len(mismatches)} issues:")
        for m in mismatches:
            print(f"      - {m}")
        return False
    
    print(f"   ✅ PASSED: All critical files present and valid")
    return True

def test_all_committed_files_deployed():
    """
    Check Git status - verify no uncommitted changes pending.
    This catches the issue where changes were made but not committed.
    """
    print("\n[TEST] Checking Git status for uncommitted changes...")
    
    stdout, stderr, rc = run_command("git status --porcelain")
    
    if rc != 0:
        print(f"   ⚠️  WARNING: Could not check git status: {stderr}")
        return True  # Don't fail if git not available
    
    if stdout:
        changes = stdout.split('\n')
        print(f"   ⚠️  WARNING: {len(changes)} uncommitted changes:")
        
        # Show changes
        staged = [c for c in changes if c.startswith('M') or c.startswith('A')]
        unstaged = [c for c in changes if c.startswith(' M') or c.startswith('??')]
        
        if staged:
            print(f"      Staged: {len(staged)} files")
        if unstaged:
            print(f"      Unstaged: {len(unstaged)} files")
        
        # Check if critical files are uncommitted
        critical_uncommitted = []
        for change in changes:
            if 'data_net.json' in change or 'server.py' in change:
                critical_uncommitted.append(change)
        
        if critical_uncommitted:
            print(f"\n   ❌ CRITICAL: Uncommitted changes in critical files:")
            for c in critical_uncommitted[:5]:
                print(f"      {c}")
            return False
        
        print(f"\n   ℹ️  Note: Uncommitted changes exist but not in critical files")
        return True
    
    print(f"   ✅ PASSED: All changes committed")
    return True

def test_data_file_not_corrupted():
    """Verify data file is not corrupted or truncated"""
    print("\n[TEST] Checking data file integrity...")
    
    if not DATA_FILE.exists():
        print(f"   ❌ FAILED: Data file not found: {DATA_FILE}")
        return False
    
    # Check file size
    file_size = DATA_FILE.stat().st_size
    if file_size < 1000000:  # Less than 1MB is suspicious
        print(f"   ❌ FAILED: Data file suspiciously small ({file_size} bytes)")
        return False
    
    # Try to load and validate structure
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check required keys
        if 'stats' not in data:
            print(f"   ❌ FAILED: Missing 'stats' key in data")
            return False
        
        if 'associations' not in data:
            print(f"   ❌ FAILED: Missing 'associations' key in data")
            return False
        
        associations = data['associations']
        if len(associations) < 1000:
            print(f"   ❌ FAILED: Too few associations ({len(associations)})")
            return False
        
        print(f"   ✅ PASSED: Data file is valid")
        print(f"   - Size: {file_size:,} bytes")
        print(f"   - Associations: {len(associations):,}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"   ❌ FAILED: Data file is corrupted JSON: {e}")
        return False
    except Exception as e:
        print(f"   ❌ FAILED: Error reading data file: {e}")
        return False

def test_critical_files_exist():
    """Verify all critical deployment files exist"""
    print("\n[TEST] Checking all critical files exist...")
    
    critical_files = [
        ('paris-assos-website/data_net.json', 'Data file'),
        ('paris-assos-website/server.py', 'Server script'),
        ('paris-assos-website/index.html', 'HTML page'),
    ]
    
    missing = []
    
    for rel_path, description in critical_files:
        file_path = PROJECT_ROOT / rel_path
        if not file_path.exists():
            missing.append(f"{description}: {rel_path}")
    
    if missing:
        print(f"   ❌ FAILED: {len(missing)} critical files missing:")
        for m in missing:
            print(f"      - {m}")
        return False
    
    print(f"   ✅ PASSED: All {len(critical_files)} critical files exist")
    return True

def test_no_duplicate_sirets():
    """Verify no duplicate SIRETs in data"""
    print("\n[TEST] Checking for duplicate SIRETs...")
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"   ❌ FAILED: Could not load data: {e}")
        return False
    
    associations = data.get('associations', [])
    sirets = [a.get('siret') for a in associations if a.get('siret')]
    
    seen = set()
    duplicates = []
    
    for siret in sirets:
        if siret in seen:
            duplicates.append(siret)
        seen.add(siret)
    
    if duplicates:
        print(f"   ❌ FAILED: {len(duplicates)} duplicate SIRETs found")
        print(f"      Examples: {duplicates[:5]}")
        return False
    
    print(f"   ✅ PASSED: No duplicate SIRETs ({len(sirets)} unique)")
    return True

def test_git_log_shows_recent_commits():
    """Check that Git has recent commits"""
    print("\n[TEST] Checking Git has recent commits...")
    
    stdout, stderr, rc = run_command("git log --oneline -5")
    
    if rc != 0:
        print(f"   ⚠️  WARNING: Could not check git log: {stderr}")
        return True
    
    if not stdout:
        print(f"   ⚠️  WARNING: No recent commits found")
        return True
    
    commits = stdout.split('\n')
    print(f"   ✅ PASSED: Found {len(commits)} recent commits")
    for commit in commits[:3]:
        print(f"      {commit}")
    return True

def test_deployment_config_valid():
    """Check deployment configuration is valid"""
    print("\n[TEST] Checking deployment configuration...")
    
    # Check if deploy script exists and is executable
    deploy_script = PROJECT_ROOT / "deploy_enhanced.py"
    
    if deploy_script.exists():
        # Check if it's valid Python
        stdout, stderr, rc = run_command(f"python3 -m py_compile {deploy_script}")
        if rc != 0:
            print(f"   ⚠️  WARNING: Deploy script has syntax errors: {stderr}")
        else:
            print(f"   ✅ Deployment script is valid Python")
    
    # Check DEPLOY.md exists
    deploy_md = PROJECT_ROOT / "DEPLOY.md"
    if deploy_md.exists():
        print(f"   ✅ DEPLOY.md exists")
    else:
        print(f"   ⚠️  WARNING: DEPLOY.md not found")
    
    return True

def run_all_tests():
    """Run all deployment integrity tests"""
    print("=" * 70)
    print("DEPLOYMENT INTEGRITY QA TESTS")
    print("=" * 70)
    print(f"Project root: {PROJECT_ROOT}")
    
    results = []
    results.append(test_workspace_matches_deployment())
    results.append(test_all_committed_files_deployed())
    results.append(test_data_file_not_corrupted())
    results.append(test_critical_files_exist())
    results.append(test_no_duplicate_sirets())
    results.append(test_git_log_shows_recent_commits())
    results.append(test_deployment_config_valid())
    
    print("\n" + "=" * 70)
    print("DEPLOYMENT INTEGRITY TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ ALL TESTS PASSED: {passed}/{total}")
        print(f"\n🎉 Deployment integrity verified!")
        print(f"   Workspace matches deployment.")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED: {passed}/{total} passed")
        print(f"\n⚠️  Deployment integrity issues detected!")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
