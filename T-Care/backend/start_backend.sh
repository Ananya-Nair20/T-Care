#!/bin/sh
echo " Starting T-Care Backend at http://localhost:8000"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
