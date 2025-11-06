import ibm_db
from app.config import DB2_DSN

def get_connection():
    try:
        conn = ibm_db.connect(DB2_DSN, "", "")
        return conn
    except Exception as e:
        raise Exception(f"Error al conectar con Db2: {e}")
