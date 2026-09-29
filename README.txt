CASELINK local academic prototype
1. Extract the ZIP and open the CASELINK_READY folder in VS Code.
2. Activate your existing venv if you have one: .\venv\Scripts\Activate.ps1
3. Install dependencies: pip install -r requirements.txt
4. Run: python app.py
5. Open http://127.0.0.1:5000

If activation is blocked, run .\venv\Scripts\python.exe app.py after installing dependencies with that same interpreter.
Back up your current caselink.db before replacing files if you want to keep your existing records.
Smart matching tries Sentence-BERT and falls back to basic text similarity if unavailable.
Statement analysis is a simple review aid, not lie detection. Graph lines mean only that records belong to a case.
