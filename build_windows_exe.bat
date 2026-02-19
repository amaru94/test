@echo off
setlocal

REM Build a standalone Windows .exe from the chatbot source.
REM Run from project root: build_windows_exe.bat

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

pyinstaller --noconfirm --onefile --name AutoFixChatBot autofix_chatbot.py

echo.
echo Build complete. EXE location:
echo %CD%\dist\AutoFixChatBot.exe
endlocal
