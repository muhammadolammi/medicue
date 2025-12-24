# ==========================================
# MEDICUE BACKEND - Flask + SQLAlchemy + MySQL
# Complete REST API Implementation
# ==========================================

from dotenv import load_dotenv
from db import init_database
from config import app
import os





# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == '__main__':
    # LOAD ENV
    load_dotenv()
    if os.getenv("DB_URL") =="" or os.getenv("DB_URL") is None:
        print("No DB_URL in env")
        os._exit(1)
    if os.getenv("JWT_SECRET_KEY") =="" or os.getenv("JWT_SECRET_KEY") is None:
        print("No JWT_SECRET_KEY in env")
        os._exit(1)

    init_database()
    app.run(debug=True, host='0.0.0.0', port=8080)