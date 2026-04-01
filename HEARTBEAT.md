# Deployment Heartbeat

## Pre-Deployment Checklist

- [ ] Run `test_deployment.py` before marking deployment complete
- [ ] Verify gunicorn is running with 4 workers
- [ ] Check `/health` endpoint returns 200
- [ ] Check `/api/stats` returns valid data
- [ ] Verify homepage loads correctly
- [ ] Confirm associations API returns records with all fields

## Quick Health Check

```bash
python3 /home/openclaw/.openclaw/workspace/paris-assos-website/test_deployment.py
```
