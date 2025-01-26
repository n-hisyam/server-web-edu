import pymysql
import bcrypt
from connectdb import config

# def create_user_table():
#     try:
#         # Koneksi ke database menggunakan konfigurasi dari config
#         connection = pymysql.connect(
#             host=config["host"],
#             user=config["user"],
#             password=config["password"],
#             database=config["database"]
#         )
        
#         with connection.cursor() as cursor:
#             # Query untuk membuat tabel user
#             create_table_query = """
#             CREATE TABLE IF NOT EXISTS user (
#                 id INT AUTO_INCREMENT PRIMARY KEY,
#                 username VARCHAR(50) NOT NULL,
#                 email VARCHAR(100) NOT NULL UNIQUE,
#                 password_hash VARCHAR(255) NOT NULL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             );
#             """
#             cursor.execute(create_table_query)
#             print("Tabel 'user' berhasil dibuat.")
        
#         # Commit perubahan ke database
#         connection.commit()
    
#     except pymysql.MySQLError as e:
#         print(f"Error saat membuat tabel: {e}")
    
#     finally:
#         # Pastikan koneksi ditutup
#         if connection:
#             connection.close()
#             print("Koneksi ke database ditutup.")

# def add_user(username, email, password):
#     try:
#         # Hash password menggunakan bcrypt
#         password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
#         # Koneksi ke database
#         connection = pymysql.connect(
#             host=config["host"],
#             user=config["user"],
#             password=config["password"],
#             database=config["database"]
#         )
        
#         with connection.cursor() as cursor:
#             # Query untuk menambahkan data ke tabel user
#             insert_query = """
#             INSERT INTO user (username, email, password_hash)
#             VALUES (%s, %s, %s);
#             """
#             cursor.execute(insert_query, (username, email, password_hash))
#             print(f"User '{username}' berhasil ditambahkan.")
        
#         # Commit perubahan ke database
#         connection.commit()
    
#     except pymysql.MySQLError as e:
#         print(f"Error saat menambahkan user: {e}")
    
#     finally:
#         # Pastikan koneksi ditutup
#         if connection:
#             connection.close()
#             print("Koneksi ke database ditutup.")

# # Eksekusi fungsi untuk membuat tabel dan menambahkan data
# create_user_table()

# # Contoh penambahan user
# add_user("admin", "admin@gmail.com", "Password123")


import pymysql
from connectdb import config

def create_kelas_table():
    try:
        # Koneksi ke database menggunakan konfigurasi dari config
        connection = pymysql.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"]
        )
        
        with connection.cursor() as cursor:
            # Query untuk membuat tabel kelas
            create_table_query = """
            CREATE TABLE IF NOT EXISTS video (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_kelas INT NOT NULL,
                id_semester INT NOT NULL,
                id_bab INT NOT NULL,
                id_materi INT NOT NULL,
                judul VARCHAR(255) NOT NULL,
                link VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_kelas) REFERENCES kelas(id),
                FOREIGN KEY (id_semester) REFERENCES semester(id),
                FOREIGN KEY (id_bab) REFERENCES bab(id)
                FOREIGN KEY (id_materi) REFERENCES materi(id)

                );
            """
            cursor.execute(create_table_query)
            print("Tabel 'kelas' berhasil dibuat.")
        
        # Commit perubahan ke database
        connection.commit()
    
    except pymysql.MySQLError as e:
        print(f"Error saat membuat tabel: {e}")
    
    finally:
        # Pastikan koneksi ditutup
        if connection:
            connection.close()
            print("Koneksi ke database ditutup.")

# def add_kelas(gambar, judul, deskripsi):
#     try:
#         # Koneksi ke database
#         connection = pymysql.connect(
#             host=config["host"],
#             user=config["user"],
#             password=config["password"],
#             database=config["database"]
#         )
        
#         with connection.cursor() as cursor:
#             # Query untuk menambahkan data ke tabel kelas
#             insert_query = """
#             INSERT INTO kelas (gambar, judul, deskripsi)
#             VALUES (%s, %s, %s);
#             """
#             cursor.execute(insert_query, (gambar, judul, deskripsi))
#             print(f"Kelas '{judul}' berhasil ditambahkan.")
        
#         # Commit perubahan ke database
#         connection.commit()
    
#     except pymysql.MySQLError as e:
#         print(f"Error saat menambahkan kelas: {e}")
    
#     finally:
#         # Pastikan koneksi ditutup
#         if connection:
#             connection.close()
#             print("Koneksi ke database ditutup.")



# # Eksekusi fungsi untuk membuat tabel kelas dan menambahkan data
create_kelas_table()

# Contoh penambahan kelas
# add_kelas("/images/kelas8.jpg", "Siswa Dasar Kelas 1 (satu)", "Siswa diharapkan memilih kelas yang sesuai")
# add_kelas("/images/kelas8.jpg", "Siswa Dasar Kelas 2 (dua)", "Siswa diharapkan memilih kelas yang sesuai")
# add_kelas("/images/kelas8.jpg", "Siswa Dasar Kelas 3 (tiga)", "Siswa diharapkan memilih kelas yang sesuai")
# add_kelas("/images/kelas8.jpg", "Siswa Dasar Kelas 4 (empat)", "Siswa diharapkan memilih kelas yang sesuai")
# add_kelas("/images/kelas8.jpg", "Siswa Dasar Kelas 5 (lima)", "Siswa diharapkan memilih kelas yang sesuai")
# add_kelas("/images/kelas8.jpg", "Siswa Dasar Kelas 6 (enam)", "Siswa diharapkan memilih kelas yang sesuai")
