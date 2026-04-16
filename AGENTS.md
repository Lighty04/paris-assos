# AGENTS.md - Paris Associations Website Rules

## Archived Research Data

**Historical research files have been archived:**
- Location: `workspace/archive/research/`
- Includes: batch_* research JSONs, conflict analysis, data files
- Recovery: If needed, copy from archive/ back to workspace

## QA & Deployment

**Full QA + Deploy is delegated to devclaw agent.**

### Deployment Workflow

1. **Main agent spawns devclaw** with context
2. **Devclaw executes:**
   - Run `qa_tests/run_all_qa_tests.py`
   - Deploy to decisionhelper@192.168.0.16:~/paris-assos-website/
   - Verify at http://192.168.0.16:8010
   - Report results

### QA Test Suite

**Comprehensive:**
```bash
cd qa_tests
python3 run_all_qa_tests.py
```

**Legacy (still valid):**
```bash
python3 test_data_integrity.py
python3 test_api_response.py
python3 test_frontend_display.py
```
