import os
os.system("set FLASK_APP=app.py")
os.system(f"flask run --port={os.getenv('PORT')} --host=0.0.0.0")

