import pymysql

# Konfigurasi koneksi
config = {
    'host': 'sql202.infinityfree.com',  # Alamat server
    'user': 'if0_38181432',       # Username MySQL
    'password': 'et77P245WRGM00 ',       # Password MySQL
    'database': 'if0_38181432_web_pkn',  # Nama database
}

try:
    # Membuat koneksi
    connection = pymysql.connect(**config)
    print("Berhasil terhubung ke MySQL!")

    # Membuat cursor untuk eksekusi query
    cursor = connection.cursor()

    # # Contoh query
    # query = "SELECT * FROM nama_tabel;"
    # cursor.execute(query)

    # # Ambil hasil query
    # results = cursor.fetchall()
    # for row in results:
    #     print(row)

except pymysql.MySQLError as err:
    print(f"Error: {err}")
finally:
    # Tutup koneksi
    if connection:
        cursor.close()
        connection.close()
        print("Koneksi MySQL ditutup.")