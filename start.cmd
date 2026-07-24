@echo off
setlocal

if not exist venv (
  C:\Users\bueno\AppData\Local\Programs\Python\Python312\python.exe -m venv venv
)

call venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
