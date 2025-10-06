@echo off
echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing required libraries...
pip install -r requirements.txt

echo Running the app...
streamlit run main-app.py
pause