import pymysql

# Konfigurasi koneksi
config = {
    'host': 'bnwhyiqbdwivwzitaygw-mysql.services.clever-cloud.com',  # Alamat server
    'user': 'ucof5wzkzblsdfcg',       # Username MySQL
    'password': 'gKJCYYJDlyeBCQkb8rPK',       # Password MySQL
    'database': 'bnwhyiqbdwivwzitaygw',  # Nama database
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