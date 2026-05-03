from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# URL koneksi sesuai dengan yang Anda pakai di etl_pipeline.py
DATABASE_URL = "postgresql://postgres:root@localhost:5432/hse_db"

# Membuat 'Mesin' koneksi dengan Connection Pooling
# pool_size=5: Maksimal 5 koneksi standby
# max_overflow=10: Mengizinkan tambahan 10 koneksi jika sedang sangat sibuk
engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)

# Membuat pabrik sesi (Session Factory)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class untuk model tabel (jika nanti butuh ORM lanjutan)
Base = declarative_base()

# Dependency Injection: Fungsi untuk meminjam dan mengembalikan koneksi
def get_db():
    db = SessionLocal()
    try:
        yield db # Pinjamkan koneksi ke endpoint yang meminta
    finally:
        db.close() # WAJIB ditutup agar memory tidak bocor (Memory Leak)