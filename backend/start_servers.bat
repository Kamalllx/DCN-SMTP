@echo off
echo Starting AI-Enhanced Email Server...
echo.
echo Starting MongoDB (if not running)...
start "MongoDB" mongod

echo.
echo Waiting for MongoDB to start...
timeout /t 5

echo.
echo Starting Flask Backend...
start "Flask Backend" email_server_env\Scripts\python app.py

echo.
echo Waiting for Flask to start...
timeout /t 5

echo.
echo Starting Streamlit Interface...
start "Streamlit Interface" email_server_env\Scripts\streamlit run streamlit_app.py

echo.
echo All services started!
echo.
echo Access URLs:
echo Flask Dashboard: http://localhost:5000
echo Streamlit Interface: http://localhost:8501
echo.
pause
