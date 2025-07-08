from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
import io

from database import SessionLocal, engine
from models import Base, CalonSiswa

app = FastAPI(title="Sistem Pendaftaran Calon Siswa", description="Aplikasi CRUD untuk mengelola data pendaftaran calon siswa")

templates = Jinja2Templates(directory="templates")
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    siswa_list = db.query(CalonSiswa).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "siswa_list": siswa_list, 
        "mode": "tambah"
    })

@app.post("/tambah-siswa")
def tambah_siswa(
    nama: str = Form(...), 
    alamat: str = Form(...), 
    jenis_kelamin: str = Form(...),
    agama: str = Form(...),
    sekolah_asal: str = Form(...),
    db: Session = Depends(get_db)
):
    calon_siswa = CalonSiswa(
        nama=nama, 
        alamat=alamat, 
        jenis_kelamin=jenis_kelamin,
        agama=agama,
        sekolah_asal=sekolah_asal
    )
    db.add(calon_siswa)
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/edit-siswa/{siswa_id}")
def form_edit_siswa(request: Request, siswa_id: int, db: Session = Depends(get_db)):
    siswa = db.query(CalonSiswa).filter(CalonSiswa.id == siswa_id).first()
    siswa_list = db.query(CalonSiswa).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "siswa_list": siswa_list, 
        "siswa_edit": siswa, 
        "mode": "edit"
    })

@app.post("/edit-siswa/{siswa_id}")
def update_siswa(
    siswa_id: int,
    nama: str = Form(...), 
    alamat: str = Form(...), 
    jenis_kelamin: str = Form(...),
    agama: str = Form(...),
    sekolah_asal: str = Form(...),
    db: Session = Depends(get_db)
):
    siswa = db.query(CalonSiswa).filter(CalonSiswa.id == siswa_id).first()
    siswa.nama = nama
    siswa.alamat = alamat
    siswa.jenis_kelamin = jenis_kelamin
    siswa.agama = agama
    siswa.sekolah_asal = sekolah_asal
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/hapus-siswa/{siswa_id}")
def hapus_siswa(siswa_id: int, db: Session = Depends(get_db)):
    siswa = db.query(CalonSiswa).filter(CalonSiswa.id == siswa_id).first()
    db.delete(siswa)
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/export-pdf")
def export_pdf(db: Session = Depends(get_db)):
    # Get all student data
    siswa_list = db.query(CalonSiswa).all()
    
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Set title
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Laporan Data Calon Siswa', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.cell(0, 10, 'SMK Digital', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    
    # Add date
    pdf.set_font('Helvetica', '', 10)
    current_date = datetime.now().strftime('%d %B %Y')
    pdf.cell(0, 10, f'Tanggal: {current_date}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)
    
    # Table header
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(10, 10, 'No', border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.cell(40, 10, 'Nama Lengkap', border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.cell(50, 10, 'Alamat', border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.cell(25, 10, 'Jenis Kelamin', border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.cell(20, 10, 'Agama', border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.cell(45, 10, 'Sekolah Asal', border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    
    # Table content
    pdf.set_font('Helvetica', '', 8)
    for index, siswa in enumerate(siswa_list, 1):
        # Handle text that might be too long
        nama = siswa.nama[:18] + '...' if len(siswa.nama) > 18 else siswa.nama
        alamat = siswa.alamat[:25] + '...' if len(siswa.alamat) > 25 else siswa.alamat
        sekolah = siswa.sekolah_asal[:20] + '...' if len(siswa.sekolah_asal) > 20 else siswa.sekolah_asal
        
        pdf.cell(10, 8, str(index), border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        pdf.cell(40, 8, nama, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='L')
        pdf.cell(50, 8, alamat, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='L')
        pdf.cell(25, 8, siswa.jenis_kelamin, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        pdf.cell(20, 8, siswa.agama, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
        pdf.cell(45, 8, sekolah, border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    
    # Add summary
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(0, 10, f'Total Calon Siswa: {len(siswa_list)} orang', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    
    # Add footer
    pdf.ln(20)
    pdf.set_font('Helvetica', 'I', 8)
    pdf.cell(0, 10, 'Dokumen ini dibuat secara otomatis oleh Sistem Pendaftaran Calon Siswa', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    
    # Generate PDF binary data
    pdf_output = bytes(pdf.output())
    
    # Return PDF as response
    headers = {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename="laporan_calon_siswa_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    }
    
    return Response(content=pdf_output, headers=headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
