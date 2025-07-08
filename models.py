from sqlalchemy import Column, Integer, String
from database import Base

class CalonSiswa(Base):
    __tablename__ = "calon_siswa"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(64), nullable=False)
    alamat = Column(String(255), nullable=False)
    jenis_kelamin = Column(String(16), nullable=False)
    agama = Column(String(16), nullable=False)
    sekolah_asal = Column(String(64), nullable=False)
