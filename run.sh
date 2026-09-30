#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export ADMIN_USER="ibuuuu_19"
export ADMIN_PASS="passer1234"
python -m streamlit run app.py