from bottle import Bottle, request, response, run, static_file
import pymysql
import bcrypt
import os
from connectdb import config
import logging
import requests
import json
from datetime import datetime


from pymysql.cursors import DictCursor



app = Bottle()

# Fungsi kustom untuk mengonversi objek datetime menjadi string
def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Mengubah datetime ke format string ISO
    raise TypeError("Type not serializable")


UPLOAD_DIR = './uploads/'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Tidak akan error jika direktori sudah ada

# Tambahkan hook untuk mengatur CORS
@app.hook('after_request')
def enable_cors():
    response.set_header('Access-Control-Allow-Origin', '*')
    response.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
# Tangani permintaan OPTIONS
@app.route('/login', method='OPTIONS')
def handle_options():
    return {}

@app.route('/delete_data_kelas/<kelas_id>', method='OPTIONS')
def handle_options():
    return {}

def get_db_connection():
    """Membuat koneksi ke database."""
    return pymysql.connect(
        host=config["host"],
        user=config["user"],
        password=config["password"],
        database=config["database"]
    )

@app.post('/login')
def login():
    """Fungsi login untuk memvalidasi pengguna."""
    try:
        # Ambil data JSON dari request
        data = request.json
        if not data or 'email' not in data or 'password' not in data:
            response.status = 400
            return {"error": "Email dan password wajib diisi."}
        
        email = data['email']
        password = data['password']
        
        # Koneksi ke database
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Query untuk mendapatkan data user berdasarkan email
            select_query = "SELECT id, username, password_hash FROM user WHERE email = %s;"
            cursor.execute(select_query, (email,))
            user = cursor.fetchone()
        
        if not user:
            response.status = 401
            return {"error": "Email atau password salah."}
        
        user_id, username, password_hash = user
        
        # Verifikasi password
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            response.status = 401
            return {"error": "Email atau password salah."}
        
        # Autentikasi berhasil
        return {
            "message": "Login berhasil.",
            "user": {
                "id": user_id,
                "username": username,
                "email": email
            }
        }
    
    except pymysql.MySQLError as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}
    
    finally:
        # Tutup koneksi database
        if 'connection' in locals() and connection:
            connection.close()

@app.post('/create_data_kelas')
def create_kelas():
    try:
        judul = request.forms.get('judul')
        deskripsi = request.forms.get('deskripsi')
        gambar = request.files.get('gambar')

        if not judul or not deskripsi or not gambar:
            response.status = 400
            return {"error": "Semua data wajib diisi!"}

        # Tentukan direktori untuk menyimpan gambar
        upload_dir = 'uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        gambar_filename = gambar.filename
        gambar_path = os.path.join(upload_dir, gambar_filename)
        gambar.save(gambar_path)

        connection = get_db_connection()
        with connection.cursor() as cursor:
            insert_query = """
                INSERT INTO kelas (gambar, judul, deskripsi)
                VALUES (%s, %s, %s);
            """
            cursor.execute(insert_query, (gambar_filename, judul, deskripsi))
            connection.commit()

        # URL untuk mengakses gambar yang disimpan
        image_url = f"http://localhost:8080/uploads/{gambar_filename}"
        return {"message": "Kelas berhasil dibuat!", "gambar_url": image_url}
    
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}


@app.route('/edit_data_kelas/<kelas_id>', method=['OPTIONS'])
def handle_options(kelas_id):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return {}
# Endpoint untuk mengedit data kelas
@app.post('/edit_data_kelas/<kelas_id>')
def edit_kelas(kelas_id):
    try:
        # Debugging request data
        print("Request Headers:", request.headers)
        print("Request JSON:", request.json)

        # Pastikan backend menangkap data JSON yang dikirim
        data = request.json
        if not data:
            response.status = 400
            return {"error": "Tidak ada data yang dikirim."}

        # Ambil data dari JSON
        judul = data.get("judul", "")
        deskripsi = data.get("deskripsi", "")

        # Debugging nilai-nilai yang diterima
        print(f"Judul: {judul}")
        print(f"Deskripsi: {deskripsi}")

        # Logika penyimpanan atau pengolahan data
        # (misal: simpan ke database)

        return {
            "message": f"Kelas dengan ID {kelas_id} berhasil diupdate.",
            "success": True,
        }

    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {str(e)}"}




@app.get('/get_kelas/<id>')
def get_kelas(id):
    try:
        connection = get_db_connection()
        with connection.cursor(DictCursor) as cursor:  # Menggunakan DictCursor
            select_query = "SELECT * FROM kelas WHERE id = %s;"
            cursor.execute(select_query, (id,))
            kelas = cursor.fetchone()

        if not kelas:
            response.status = 404
            return {"error": "Kelas tidak ditemukan!"}

        # URL untuk gambar
        gambar_url = f"http://localhost:8080/uploads/{kelas['gambar']}"

        return {
            "id": kelas["id"],
            "judul": kelas["judul"],
            "deskripsi": kelas["deskripsi"],
            "gambar_url": gambar_url
        }
    
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}

@app.route('/delete_data_kelas', method='OPTIONS')
def handle_options():
    return {}

@app.post('/delete_data_kelas')
def delete_data_kelas():
    try:
        # Ambil parameter id dari request body dalam format JSON
        request_data = request.json
        kelas_id = request_data.get('id') if request_data else None

        if not kelas_id:
            response.status = 400
            return {"error": "ID kelas wajib diisi!"}

        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Ambil nama file gambar dari database
            select_query = "SELECT gambar FROM kelas WHERE id = %s;"
            cursor.execute(select_query, (kelas_id,))
            kelas = cursor.fetchone()

            if not kelas:
                response.status = 404
                return {"error": "Kelas tidak ditemukan!"}

            gambar_filename = kelas[0]
            gambar_path = os.path.join('uploads', gambar_filename)

            # Hapus data kelas dari database
            delete_query = "DELETE FROM kelas WHERE id = %s;"
            cursor.execute(delete_query, (kelas_id,))
            connection.commit()

            # Hapus file gambar dari direktori
            if os.path.exists(gambar_path):
                os.remove(gambar_path)

        return {"message": "Kelas berhasil dihapus!"}

    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}



@app.put('/edit_data_kelas/<kelas_id>')
def edit_kelas(kelas_id):
    try:
        judul = request.forms.get('judul')
        deskripsi = request.forms.get('deskripsi')
        gambar = request.files.get('gambar')

        if not judul or not deskripsi:
            response.status = 400
            return {"error": "Judul dan deskripsi wajib!"}

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Periksa apakah kelas ada
                select_query = "SELECT gambar FROM kelas WHERE id = %s;"
                cursor.execute(select_query, (kelas_id,))
                kelas = cursor.fetchone()
                print(kelas)  # Mengganti `f(kelas)` dengan `print(kelas)`
                if not kelas:
                    response.status = 404
                    return {"error": "Kelas tidak ditemukan."}

                gambar_lama = kelas[0]  # Asumsikan kolom gambar ada di indeks pertama

                # Proses gambar baru jika ada
                if gambar and gambar.filename:
                    # Buat nama file unik
                    gambar_filename = f"{kelas_id}_{gambar.filename}"
                    gambar_path = os.path.join('uploads', gambar_filename)

                    # Pastikan direktori uploads ada
                    if not os.path.exists('uploads'):
                        os.makedirs('uploads')

                    # Simpan file baru
                    gambar.save(gambar_path)
                    gambar_baru = gambar_filename

                    # Hapus file lama jika ada dan berbeda dari file baru
                    if gambar_lama and gambar_lama != gambar_baru:
                        gambar_lama_path = os.path.join('uploads', gambar_lama)
                        if os.path.exists(gambar_lama_path):
                            os.remove(gambar_lama_path)
                else:
                    gambar_baru = gambar_lama

                # Perbarui data kelas
                update_query = """
                    UPDATE kelas 
                    SET judul = %s, deskripsi = %s, gambar = %s
                    WHERE id = %s;
                """
                cursor.execute(update_query, (judul, deskripsi, gambar_baru, kelas_id))
                connection.commit()

            image_url = f"http://localhost:8080/uploads/{gambar_baru}"

            return {"message": "Kelas berhasil diperbarui!", "gambar_url": image_url}

        finally:
            connection.close()
    
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}

@app.route('/uploads/<filename>')
def serve_image(filename):
    return static_file(filename, root='./uploads')

@app.get('/edit-kelas/<id>')
def get_kelas(id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            select_query = "SELECT id, judul, deskripsi, gambar FROM kelas WHERE id = %s"
            cursor.execute(select_query, (id,))
            kelas = cursor.fetchone()

            if kelas:
                return {
                    "id": id[0],
                    "judul": kelas[1],
                    "deskripsi": kelas[2],
                    "gambar": kelas[3],

                }
            else:
                response.status = 404
                return {"error": "Kelas tidak ditemukan"}
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {str(e)}"}
    finally:
        if 'connection' in locals() and connection:
            connection.close()

# Fungsi untuk mengambil semua data kelas
@app.get('/get_all_data_kelas')
def get_all_kelas():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Query untuk mengambil semua data kelas
            select_query = "SELECT id, judul, deskripsi, gambar FROM kelas;"
            cursor.execute(select_query)
            kelas_list = cursor.fetchall()

            if not kelas_list:
                response.status = 404
                return {"error": "Tidak ada kelas ditemukan."}

            # Membuat list untuk semua kelas dengan URL gambar
            all_kelas = []
            for kelas in kelas_list:
                kelas_id, judul, deskripsi, gambar = kelas
                image_url = f"http://localhost:8080/uploads/{gambar}"

                all_kelas.append({
                    "id": kelas_id,
                    "judul": judul,
                    "deskripsi": deskripsi,
                    "gambar_url": image_url
                })

            return {"kelas": all_kelas}
    
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}


    finally:
        if 'connection' in locals() and connection:
            connection.close()



@app.delete('/delete_data_kelas/<kelas_id>')
def delete_kelas(kelas_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Ambil informasi gambar yang akan dihapus dari database
            select_query = "SELECT gambar FROM kelas WHERE id = %s"
            cursor.execute(select_query, (kelas_id,))
            kelas = cursor.fetchone()

            if not kelas:
                response.status = 404
                return {"error": "Kelas tidak ditemukan!"}

            gambar_filename = kelas[0]
            gambar_path = os.path.join('uploads', gambar_filename)

            # Hapus file gambar dari server
            if os.path.exists(gambar_path):
                os.remove(gambar_path)

            # Hapus data kelas dari database
            delete_query = "DELETE FROM kelas WHERE id = %s"
            cursor.execute(delete_query, (kelas_id,))
            connection.commit()

        return {"message": "Kelas berhasil dihapus!"}
    
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}


# semester
@app.post('/create_data_semester')
def create_data_semester():
    try:
        judul = request.forms.get("judul")
        deskripsi = request.forms.get("deskripsi")
        id_kelas = request.forms.get("id_kelas")
        gambar = request.files.get("gambar")

        if not judul or not deskripsi or not gambar or not id_kelas:
            response.status = 400
            return {"message": "Semua data wajib diisi!"}

        # Save uploaded file
        
        gambar_filename = gambar.filename
        file_path = os.path.join(UPLOAD_DIR, gambar.filename)
        gambar.save(file_path)

        # Save data to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO semester (judul, deskripsi, gambar, id_kelas) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (judul, deskripsi, gambar.filename, id_kelas))
        conn.commit()
        cursor.close()
        conn.close()

        image_url = f"http://localhost:8080/semesters/{gambar_filename}"


        return {"message": "Semester berhasil dibuat!", "gambar_url": image_url}

    except Exception as e:
        response.status = 500
        return {"message": f"Terjadi kesalahan: {str(e)}"}

@app.post('/edit_data_semester/<semester_id>')
def edit_data_semester(semester_id):
    try:
        judul = request.forms.get("judul")
        deskripsi = request.forms.get("deskripsi")
        id_kelas = request.forms.get("id_kelas")
        gambar = request.files.get("gambar")

        if not judul or not deskripsi or not id_kelas:
            response.status = 400
            return {"message": "Judul, deskripsi, dan ID kelas wajib diisi!"}

        # Cek apakah gambar diupload
        if gambar:
            gambar_filename = gambar.filename
            file_path = os.path.join(UPLOAD_DIR, gambar.filename)
            gambar.save(file_path)

            # Update gambar di database jika ada
            image_url = f"http://localhost:8080/semesters/{gambar_filename}"

            # Update data semester di database
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = """
                UPDATE semester 
                SET judul = %s, deskripsi = %s, gambar = %s, id_kelas = %s 
                WHERE id = %s
            """
            cursor.execute(sql, (judul, deskripsi, gambar.filename, id_kelas, semester_id))
            conn.commit()
            cursor.close()
            conn.close()

            return {"message": f"Semester dengan ID {semester_id} berhasil diperbarui!", "gambar_url": image_url}

        else:
            # Update tanpa gambar
            conn = get_db_connection()
            cursor = conn.cursor()
            sql = """
                UPDATE semester 
                SET judul = %s, deskripsi = %s, id_kelas = %s
                WHERE id = %s
            """
            cursor.execute(sql, (judul, deskripsi, id_kelas, semester_id))
            conn.commit()
            cursor.close()
            conn.close()

            return {"message": f"Semester dengan ID {semester_id} berhasil diperbarui tanpa gambar."}

    except Exception as e:
        response.status = 500
        return {"message": f"Terjadi kesalahan: {str(e)}"}


@app.get('/get_all_semester')
def get_all_semester():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Query untuk mengambil data semester beserta data kelas yang terkait
            select_query = """
                SELECT 
                    semester.id AS semester_id, 
                    semester.judul AS semester_judul, 
                    semester.deskripsi AS semester_deskripsi, 
                    semester.gambar AS semester_gambar,
                    kelas.id AS kelas_id, 
                    kelas.judul AS kelas_judul, 
                    kelas.deskripsi AS kelas_deskripsi
                FROM semester
                LEFT JOIN kelas ON semester.id_kelas = kelas.id;
            """
            cursor.execute(select_query)
            semester_list = cursor.fetchall()

            if not semester_list:
                response.status = 404
                return {"error": "Tidak ada semester ditemukan."}

            # Membuat list untuk semua semester dengan data kelas yang terkait
            all_semester = []
            for semester in semester_list:
                semester_id, semester_judul, semester_deskripsi, semester_gambar, kelas_id, kelas_judul, kelas_deskripsi = semester
                semester_data = {
                    "id": semester_id,
                    "judul": semester_judul,
                    "deskripsi": semester_deskripsi,
                    "gambar_url": f"http://localhost:8080/uploads/{semester_gambar}",
                    "kelas": {
                        "id": kelas_id,
                        "judul": kelas_judul,
                        "deskripsi": kelas_deskripsi
                    } if kelas_id else None  # Handle jika tidak ada kelas terkait
                }
                all_semester.append(semester_data)

            return {"semesters": all_semester}
    
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}

@app.route('/delete_data_semester', method='OPTIONS')
def handle_options():
    return {}

@app.post('/delete_data_semester')
def delete_data_semester():
    try:
        # Ambil parameter id dari request body dalam format JSON
        request_data = request.json
        kelas_id = request_data.get('id') if request_data else None

        if not kelas_id:
            response.status = 400
            return {"error": "ID kelas wajib diisi!"}

        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Ambil nama file gambar dari database
            select_query = "SELECT gambar FROM semester WHERE id = %s;"
            cursor.execute(select_query, (kelas_id,))
            kelas = cursor.fetchone()

            if not kelas:
                response.status = 404
                return {"error": "Kelas tidak ditemukan!"}

            gambar_filename = kelas[0]
            gambar_path = os.path.join('uploads', gambar_filename)

            # Hapus data kelas dari database
            delete_query = "DELETE FROM semester WHERE id = %s;"
            cursor.execute(delete_query, (kelas_id,))
            connection.commit()

            # Hapus file gambar dari direktori
            if os.path.exists(gambar_path):
                os.remove(gambar_path)

        return {"message": "Kelas berhasil dihapus!"}

    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}




@app.get('/get_semester_by_kelas/<kelas_id>')
def get_semester_by_kelas(kelas_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            query = """
SELECT s.id, s.judul, s.gambar, s.deskripsi, s.id_kelas
                FROM semester s
                WHERE s.id_kelas = %s;
            """
            cursor.execute(query, (kelas_id,))
            semesters = cursor.fetchall()
            
            # Debugging: print data yang diterima untuk pengecekan
            print("Semesters fetched:", semesters)
        
        # Mengembalikan data semester yang benar
        return {"semesters": [{"id": s[0], "judul": s[1], "gambar": f"http://localhost:8080/uploads/{s[2]}", "deskripsi": s[3], "id_kelas": s[4]} for s in semesters], }
    
    except Exception as e:
        # Mengatur status respons dan mengembalikan pesan error
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {str(e)}"}
    
    finally:
        # Menutup koneksi ke database
        if 'connection' in locals() and connection:
            connection.close()
@app.delete('/delete_semester/<kelas_id>')
def delete_semester(kelas_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Ambil informasi gambar yang akan dihapus dari database
            select_query = "SELECT gambar FROM semester WHERE id = %s"
            cursor.execute(select_query, (kelas_id,))
            kelas = cursor.fetchone()

            if not kelas:
                response.status = 404
                return {"error": "Kelas tidak ditemukan!"}

            gambar_filename = kelas[0]
            gambar_path = os.path.join('uploads', gambar_filename)

            # Hapus file gambar dari server
            if os.path.exists(gambar_path):
                os.remove(gambar_path)

            # Hapus data kelas dari database
            delete_query = "DELETE FROM semester WHERE id = %s"
            cursor.execute(delete_query, (kelas_id,))
            connection.commit()

        return {"message": "Kelas berhasil dihapus!"}
    
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}



@app.post('/create_data_bab')
def create_data_bab():
    try:
        # Validasi file gambar
        upload = request.files.get('gambar')
        if not upload:
            response.status = 400
            return {"error": "Gambar wajib diunggah."}

        # Simpan file gambar
        gambar_filename = upload.filename
        image_url = f"http://localhost:8080/{gambar_filename}"
        gambar_path = f"./uploads/{upload.filename}"
        upload.save(gambar_path)

        # Ambil data lainnya
        judul = request.forms.get('judul')
        deskripsi = request.forms.get('deskripsi')
        id_kelas = request.forms.get('id_kelas')
        id_semester = request.forms.get('id_semester')

        # Validasi data input
        if not judul or not id_kelas or not id_semester:
            response.status = 400
            return {"error": "Judul, Kelas, dan Semester wajib diisi."}

        # Simpan data ke database
        connection = get_db_connection()
        with connection.cursor() as cursor:
            insert_query = """
                INSERT INTO bab (judul, deskripsi, gambar, id_kelas, id_semester)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(insert_query, (judul, deskripsi, upload.filename, id_kelas, id_semester))
            connection.commit()

        return {"message": "BAB berhasil dibuat.", "gambar_url": image_url}
    
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan: {e}"}

@app.get('/get_all_bab')
def get_all_bab():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            query = """
                SELECT b.id, b.judul, b.deskripsi, b.gambar, k.judul AS kelas, s.judul AS semester
                FROM bab b
                JOIN kelas k ON b.id_kelas = k.id
                JOIN semester s ON b.id_semester = s.id;
            """
            cursor.execute(query)
            bab_data = cursor.fetchall()
        return {
            "bab": [
                {
                    "id": b[0],
                    "judul": b[1],
                    "deskripsi": b[2],
                    "gambar_url": f"http://localhost:8080/uploads/{b[3]}",
                    "kelas": {"judul": b[4]},
                    "semester": {"judul": b[5]},
                }
                for b in bab_data
            ]
        }
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}

@app.route('/delete_data_bab', method='OPTIONS')
def handle_options():
    return {}

@app.post('/delete_data_bab')
def delete_data_bab():
    try:
        # Ambil parameter id dari request body dalam format JSON
        request_data = request.json
        kelas_id = request_data.get('id') if request_data else None

        if not kelas_id:
            response.status = 400
            return {"error": "ID kelas wajib diisi!"}

        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Ambil nama file gambar dari database
            select_query = "SELECT gambar FROM bab WHERE id = %s;"
            cursor.execute(select_query, (kelas_id,))
            kelas = cursor.fetchone()

            if not kelas:
                response.status = 404
                return {"error": "Kelas tidak ditemukan!"}

            gambar_filename = kelas[0]
            gambar_path = os.path.join('uploads', gambar_filename)

            # Hapus data kelas dari database
            delete_query = "DELETE FROM bab WHERE id = %s;"
            cursor.execute(delete_query, (kelas_id,))
            connection.commit()

            # Hapus file gambar dari direktori
            if os.path.exists(gambar_path):
                os.remove(gambar_path)

        return {"message": "Kelas berhasil dihapus!"}

    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}



@app.get('/get_bab_by_semester/<id_kelas>/<id_semester>')
def get_semester_by_kelas(id_kelas, id_semester):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            query = """
                SELECT s.id, s.judul, s.deskripsi, s.gambar, s.id_kelas, s.id_semester 
                FROM bab s
                WHERE s.id_kelas = %s
                AND s.id_semester = %s;
            """
            # Pastikan dua parameter disediakan: id_kelas dan id_semester
            cursor.execute(query, (id_kelas, id_semester))
            semesters = cursor.fetchall()
        return {"semesters": [{"id": s[0], "judul": s[1], "deskripsi": s[2], "gambar": f"http://localhost:8080/uploads/{s[3]}", "id_kelas": s[4], "id_semester": s[5]} for s in semesters]}
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}





@app.delete('/delete_bab/<kelas_id>')
def delete_bab(kelas_id):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Ambil informasi gambar yang akan dihapus dari database
            select_query = "SELECT gambar FROM bab WHERE id = %s"
            cursor.execute(select_query, (kelas_id,))
            kelas = cursor.fetchone()

            if not kelas:
                response.status = 404
                return {"error": "Kelas tidak ditemukan!"}

            gambar_filename = kelas[0]
            gambar_path = os.path.join('uploads', gambar_filename)

            # Hapus file gambar dari server
            if os.path.exists(gambar_path):
                os.remove(gambar_path)

            # Hapus data kelas dari database
            delete_query = "DELETE FROM bab WHERE id = %s"
            cursor.execute(delete_query, (kelas_id,))
            connection.commit()

        return {"message": "Kelas berhasil dihapus!"}
    
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}



# API untuk create data materi
@app.post('/create_materi')
def create_data_materi():
    try:
        # Ambil data dari form
        judul = request.forms.get("judul")
        deskripsi = request.forms.get("deskripsi")
        id_kelas = request.forms.get("id_kelas")
        id_semester = request.forms.get("id_semester")
        id_bab = request.forms.get("id_bab")

        # Cek apakah ada gambar yang di-upload
        upload = request.files.get("gambar")
        if not upload:
            return {"error": "Gambar diperlukan"}

        # Tentukan path untuk menyimpan gambar
        file_path = f"./uploads/{upload.filename}"
        gambar_filename = upload.filename
        # image_url = f"http://localhost:8080/{gambar_filename}"

        # Simpan gambar
        upload.save(file_path)

        # Koneksi ke database
        connection = get_db_connection()
        with connection.cursor() as cursor:
            query = """
                INSERT INTO materi (judul, deskripsi, id_kelas, id_semester, id_bab, gambar)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (judul, deskripsi, id_kelas, id_semester, id_bab, gambar_filename))
        # Commit perubahan ke database
        connection.commit()
        
        # Respon sukses
        return {"message": "Materi berhasil dibuat"}
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}


# Encoder kustom untuk mengonversi datetime
@app.get('/get_all_materi')
def get_all_materi_with_details():
    try:
        # Koneksi ke database
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Query untuk mengambil data materi lengkap dengan judul kelas, semester, dan bab
            query = """
                SELECT 
                    m.id, 
                    m.judul, 
                    m.deskripsi, 
                    k.judul AS judul_kelas, 
                    s.judul AS judul_semester, 
                    b.judul AS judul_bab, 
                    m.gambar
                FROM 
                    materi m
                LEFT JOIN 
                    kelas k ON m.id_kelas = k.id
                LEFT JOIN 
                    semester s ON m.id_semester = s.id
                LEFT JOIN 
                    bab b ON m.id_bab = b.id
            """
            cursor.execute(query)
            materi_list = cursor.fetchall()

        # Format data hasil query menjadi list of dict
        result = []
        for materi in materi_list:
            result.append({
                "id": materi[0],
                "judul": materi[1],
                "deskripsi": materi[2],
                "judul_kelas": materi[3],
                "judul_semester": materi[4],
                "judul_bab": materi[5],
                "gambar": f"http://localhost:8080/uploads/{materi[6]}",
            })

        # Respon sukses
        return {"materi": result}
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}


@app.route('/delete_data_materi', method='OPTIONS')
def handle_options():
    return {}

@app.post('/delete_data_materi')
def delete_data_materi():
    try:
        # Ambil parameter id dari request body dalam format JSON
        request_data = request.json
        kelas_id = request_data.get('id') if request_data else None

        if not kelas_id:
            response.status = 400
            return {"error": "ID kelas wajib diisi!"}

        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Ambil nama file gambar dari database
            select_query = "SELECT gambar FROM materi WHERE id = %s;"
            cursor.execute(select_query, (kelas_id,))
            kelas = cursor.fetchone()

            if not kelas:
                response.status = 404
                return {"error": "Kelas tidak ditemukan!"}

            gambar_filename = kelas[0]
            gambar_path = os.path.join('uploads', gambar_filename)

            # Hapus data kelas dari database
            delete_query = "DELETE FROM materi WHERE id = %s;"
            cursor.execute(delete_query, (kelas_id,))
            connection.commit()

            # Hapus file gambar dari direktori
            if os.path.exists(gambar_path):
                os.remove(gambar_path)

        return {"message": "Kelas berhasil dihapus!"}

    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}



@app.route('/get_materi_by_bab/<id_kelas>/<id_semester>/<id_bab>', method='GET')
def get_materi_by_bab(id_kelas, id_semester, id_bab):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            query = """
                SELECT s.id, s.judul, s.deskripsi, s.gambar, s.id_kelas, s.id_semester, s.id_bab
                FROM materi s
                WHERE s.id_kelas = %s
                AND s.id_semester = %s
                AND s.id_bab = %s;
            """
            cursor.execute(query, (id_kelas, id_semester, id_bab))
            materi = cursor.fetchall()

        return {"materi": [{"id": m[0], "judul": m[1], "deskripsi": m[2], "gambar": f"http://localhost:8080/uploads/{m[3]}", "id_kelas": m[4], "id_semester": m[5], "id_bab": m[6]} for m in materi]}
    except Exception as e:
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}

@app.get('/get_data_by_kelas_id/<id_kelas>')
def get_data_by_kelas_id(id_kelas):
    try:
        # Membuka koneksi ke database dengan DictCursor
        connection = get_db_connection()
        with connection.cursor(DictCursor) as cursor:  # Menggunakan DictCursor
            # Query untuk mengambil data berdasarkan id_kelas
            query = """
                SELECT 
                    kelas.judul AS kelas_judul, 
                    semester.judul AS semester_judul, 
                    semester.id AS semester_id,
                    semester.deskripsi AS semester_deskripsi,
                    semester.gambar AS semester_gambar,
                    bab.id AS bab_id,
                    bab.judul AS bab_judul, 
                    bab.deskripsi AS bab_deskripsi,
                    bab.gambar AS bab_gambar,
                    materi.id AS materi_id,
                    materi.judul AS materi_judul,
                    materi.deskripsi AS materi_deskripsi,
                    materi.gambar AS materi_gambar,
                    materi.vidio AS materi_vidio
                FROM 
                    materi
                JOIN 
                    kelas ON materi.id_kelas = kelas.id
                JOIN 
                    semester ON materi.id_semester = semester.id
                JOIN 
                    bab ON materi.id_bab = bab.id
                WHERE 
                    kelas.id = %s;  # Filter berdasarkan id_kelas
            """
            cursor.execute(query, (id_kelas,))
            result = cursor.fetchall()

            # Jika tidak ada data
            if not result:
                response.status = 404
                return {"error": "Data tidak ditemukan!"}

            # Format hasil query
            data = []
            for row in result:
                # Memasukkan data dalam format yang benar
                data.append({
                    "kelas_judul": row['kelas_judul'],
                    "semester": {
                        "id": row['semester_id'],
                        "judul": row['semester_judul'],
                        "deskripsi": row['semester_deskripsi'],
                        "gambar": f"http://localhost:8080/uploads/{row['semester_gambar']}",
                        "bab": {
                            "id": row['bab_id'],
                            "judul": row['bab_judul'],
                            "deskripsi": row['bab_deskripsi'],
                            "gambar": f"http://localhost:8080/uploads/{row['bab_gambar']}",
                            "materi": {
                                "id": row['materi_id'],
                                "judul": row['materi_judul'],
                                "deskripsi": row['materi_deskripsi'],
                                "gambar": f"http://localhost:8080/uploads/{row['materi_gambar']}",
                                "vidio": row['materi_vidio']
                            }
                        },
                    },


                })

        # Kembalikan data dalam format JSON
        response.content_type = 'application/json'
        return {"message": "Data berhasil diambil!", "data": data}

    except Exception as e:
        # Tangani error dengan memberikan respons yang sesuai
        response.status = 500
        return {"error": f"Terjadi kesalahan pada server: {e}"}


@app.route('/create_video', method='POST')
def create_video():
    try:
        # Ambil data dari request body
        id_kelas = request.forms.get('id_kelas')
        id_semester = request.forms.get('id_semester')
        id_bab = request.forms.get('id_bab')
        id_materi = request.forms.get('id_materi')
        judul = request.forms.get('judul')
        link = request.forms.get('link')

        # Validasi data
        if not (id_kelas and id_semester and id_bab and id_materi and judul and link):
            response.status = 400
            return {"error": "Semua field wajib diisi"}

        # Buat koneksi ke database
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Query untuk menambahkan data
            sql = """
                INSERT INTO video (id_kelas, id_semester, id_bab, id_materi, judul, link)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (id_kelas, id_semester, id_bab, id_materi, judul, link))
            connection.commit()

        # Berikan respon sukses
        return {"message": "Video berhasil ditambahkan"}
    except Exception as e:
        response.status = 500
        return {"error": str(e)}


@app.route('/delete_video', method='OPTIONS')
def handle_options():
    return {}

# Fungsi untuk menghapus video berdasarkan videoId
@app.route('/delete_video', method='POST')
def delete_video():
    # Mendapatkan videoId dari body request (dalam format JSON)
    data = request.json
    videoId = data.get('videoId')

    if not videoId:
        return json.dumps({'error': 'ID video wajib diisi'}), 400

    # Membuka koneksi ke database MySQL
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Menghapus video berdasarkan videoId
        sql = "DELETE FROM video WHERE id = %s"
        cursor.execute(sql, (videoId,))
        connection.commit()

        # Mengecek apakah ada video yang dihapus
        if cursor.rowcount > 0:
            return json.dumps({'message': 'Video berhasil dihapus'})
        else:
            return json.dumps({'error': 'Video tidak ditemukan'}), 404
    except Exception as e:
        # Jika terjadi error saat penghapusan
        return json.dumps({'error': str(e)}), 500



class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Mengonversi datetime menjadi string
        return super().default(obj)


@app.route('/get_all_videos', method='GET')
def get_all_videos():
    try:
        # Buat koneksi ke database
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Query untuk mengambil semua video
            sql = "SELECT * FROM video"
            cursor.execute(sql)
            result = cursor.fetchall()

        # Kirim hasil menggunakan encoder kustom
        response.content_type = 'application/json'
        return json.dumps({"videos": result}, cls=DateTimeEncoder)

    except Exception as e:
        response.status = 500
        return json.dumps({"error": str(e)})

@app.get('/get_data_by_kelas_id/<id_kelas>/<id_semester>/<id_bab>/<id_materi>')
def get_video_by_kelas(id_kelas, id_semester, id_bab, id_materi):
    try:
        connection = get_db_connection()

        with connection.cursor(pymysql.cursors.DictCursor) as cursor:  # Menggunakan DictCursor
            
            # Query untuk mengambil data berdasarkan id_kelas, id_semester, id_bab, dan id_materi
            query = """
            SELECT * FROM video
            WHERE id_kelas = %s AND id_semester = %s AND id_bab = %s AND id_materi = %s
            """
            
            # Eksekusi query
            cursor.execute(query, (id_kelas, id_semester, id_bab, id_materi))
            result = cursor.fetchall()
            
            if result:
                # Mengembalikan hasil sebagai JSON
                response.content_type = 'application/json'
                return json.dumps(result, default=json_serial)  # Gunakan json_serial untuk menangani datetime
            else:
                response.status = 404
                return {"error": "Data not found"}
    
    except pymysql.MySQLError as err:
        print(f"Error: {err}")
        response.status = 500
        return {"error": "Internal Server Error"}





# Configure YouTube API key
YOUTUBE_API_KEY = "AIzaSyCbYbv16hd6GGxQJjtSqIMbBU88O_1L8Lc"  # Ganti dengan API Key Anda

@app.route('/api/search', method='GET')
def search_youtube():
    query = request.query.get('query')
    if not query:
        return {"error": "Query parameter is required"}

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 10,
        "key": YOUTUBE_API_KEY  # API Key disisipkan di sini
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()  # Raise error jika status HTTP bukan 200
        return res.json()
    except requests.exceptions.RequestException as e:
        return {"error": "Failed to fetch data from YouTube API", "details": str(e)}


run(app, host='localhost', port=8080, debug=True, reloader=True)

