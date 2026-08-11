$env:PYTHONPATH = "..\work\.python-packages"
& "C:\Users\19551\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m uvicorn app.main:app --reload --port 8000
