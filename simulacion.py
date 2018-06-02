from faker import Faker
from random import randint
import psycopg2
import sys
import pprint
import datetime

#VARIABLES DE CONECCION
connect_str = "dbname='chinook' user='rodrigo' host='localhost' password='Av99315peter'"
# use our connection values to establish a connection
conn = psycopg2.connect(connect_str)
# create a psycopg2 cursor that can execute queries
cursor = conn.cursor()

def cuenta(tabla):
    cursor.execute("SELECT COUNT(*) FROM "+tabla+";")
    rows = cursor.fetchone()
    return rows[0]

#ids actuales
nClientes = int(cuenta("customer"))
nVentas = int(cuenta("invoice"))
nLineas = int(cuenta("invoiceline"))
nArtistas = int(cuenta("artist"))
nCanciones = int(cuenta("track"))
nAlbumes = int(cuenta("album"))

#CLIENTE FALSO
def crearClienteFalso():
    fake = Faker('es_MX')
    fake.first_name()#primer nombre
    fake.last_name()#apellido
    fake.company()#compania
    fake.secondary_address()#direccion
    fake.city()#ciudad
    fake.state()#estado
    fake.country()#pais
    fake.postcode()#post code
    fake.phone_number()#telefono
    fake.phone_number()#fax
    fake.email()#email
    randint(0,1)#repid

def simular(dias):
    inicio = datetime.datetime.now()
    step = datetime.timedelta(days=1)
    for dia in range(dias):
        ventas = randint(20,60)
        for venta in range(ventas):
            factura(inicio.strftime("%Y-%m-%d"))
        inicio += step

def precio(id):
    cursor.execute("SELECT UnitPrice FROM track WHERE TrackId = %s", (id,))
    rows = cursor.fetchone()
    print("El precio es: "+ str(rows[0]))
    return rows[0]

def factura(fecha):
    global nVentas
    lineas = randint(1,20)
    cursor.execute("INSERT INTO invoice(InvoiceId, CustomerId, InvoiceDate, Total) VALUES (%s, %s, %s, %s) RETURNING InvoiceId", [str(nVentas), str(randint(1,nClientes)), fecha, "0"])
    idF = cursor.fetchone()[0]
    print("factura " + str(idF))
    for i in range(lineas):
        linea(idF)
    nVentas += 1

def linea(id_factura):
    global nLineas
    pista = randint(1,nCanciones)
    cantidad = randint(1,5)
    pre = precio(str(pista))
    print(pre)
    cursor.execute("INSERT INTO invoiceline VALUES (%s, %s, %s, %s, %s)", [str(nLineas), str(id_factura), str(pista), str(pre), str(cantidad)])
    nLineas += 1
    return int(pre) * cantidad

def main():
    try:
        print(cuenta("genre"))
        print(precio("1"))
        simular(2)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Uh oh, can't connect. Invalid dbname, user or password?")
        print(e)

if __name__ == "__main__":
    main()
