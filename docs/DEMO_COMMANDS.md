# TwinAgent AI Demo Commands

## Local demo

```cmd
python -m pytest
python scripts\run_full_pipeline.py
python scripts\launch_api.py
```

New terminal:

```cmd
python scripts\launch_dashboard.py
```

New terminal:

```cmd
python scripts\smoke_test_api.py
```

Open:

```text
http://localhost:8000/docs
http://localhost:8501
```

## Docker demo

```cmd
docker compose up
```

Open:

```text
http://localhost:8000/docs
http://localhost:8501
```

Smoke test:

```cmd
python scripts\smoke_test_api.py
```

## If Docker image is not built yet

```cmd
docker compose up --build
```

## If port 8000 is busy on Windows

```cmd
netstat -ano | findstr :8000
tasklist /FI "PID eq <PID>"
taskkill /PID <PID> /F
```

Or use a different API port locally:

```cmd
set TWINAGENT_API_PORT=8001
python scripts\launch_api.py
```

Then open:

```text
http://localhost:8001/docs
```
