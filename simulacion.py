from faker import Faker
from random import randint, uniform
import psycopg2
import sys
import pprint
import datetime
import csv

#ARRAYS PARA LOS CVS
canciones = [["TrackId", "Name", "AlbumId", "MediaTypeId", "GenreId", "Composer", "Milliseconds", "Bytes", "UnitPrice"]]
clientes = [["Id", "FirstName", "LastName", "Company", "Address", "City", "State", "Country", "PostalCode", "Phone", "Fax", "Email", "SupportRepId"]]
facturas = [["InvoiceId", "CustomerId", "InvoiceDate", "BillingAddress", "BillingCity", "BillingState", "BillingCountry", "BillingPostalCode", "Total"]]
lineasFactura = [["InvoiceLineId", "InvoiceId", "TrackId", "UnitPrice", "Quantity"]]

#VARIABLES DE CONECCION
connect_str = "dbname='chinook' user='postgres' host='localhost' password='123456'"
# Establecemos coneccion
conn = psycopg2.connect(connect_str)
# Cursor para hacer querys
cursor = conn.cursor()

#CUAL ES LA PROBABIBLIDAD DE UN CLIENTE NUEVO?
cln = 10
#CUAL ES LA PROBABIBLIDAD DE UNA CANCION NUEVA?
can = 1
#VENTAS MINIMAS Y MAXIMAS
vmin = 20
vmax = 60

#INICIALIZACION DE FAKER PARA CREACION DE CLIENTES, CANCIONES Y ALBUMES FALSOS
fake = Faker('es_MX')

#ARRAY CON PALABRAS COMUNES DE CANCIOENES PARA ALIMENTAR Faker
cancionGenerica = ["Love", "Friend", "Hearth", "Hate", "Look", "The", "And", "Generiquino", "Scream", "Orchestra", "LMAO", "Please", "Me", "You", "Him", "Her", "Party"]

#CUENTA LA CANTIDAD DE DATOS EN UNA TABLA
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
nGeneros = int(cuenta("genre"))

#CLIENTE FALSO
def crearClienteFalso():
    global nClientes
    global clientes
    nClientes += 1
    #*******************id**********Primer nombre******* apellido******** compania********* direccion************* ciudad***** estado********* pais******** postcode********* telefono************** Fax*********** email******* repid
    clienteFalso = [str(nClientes),fake.first_name(), fake.last_name(), fake.company(), fake.secondary_address(),fake.city(),fake.state(),fake.country(),fake.postcode(),fake.phone_number(),fake.phone_number(),fake.email(),str(randint(1,8))]
    cursor.execute("INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING CustomerId", clienteFalso)
    clientes.append(clienteFalso)
    return cursor.fetchone()[0]

def crearCancionFalsa():
    global nCanciones
    global canciones
    nCanciones += 1
    #***************id***********************************************Nombre************************************************************Album******************MediaTypeId************GenreId******************Composer***********Milliseconds******************************Bytes*************************Precio
    cancionFalsa = [str(nCanciones),fake.sentence(nb_words=randint(1,4), variable_nb_words=True, ext_word_list=cancionGenerica), str(randint(1,nAlbumes)), str(randint(1,4)), str(randint(1,nGeneros)), fake.first_name(), str(randint(300000,880000)), str(randint(7000000,50000000)), round(uniform(0.5,2), 2)]
    cursor.execute("INSERT INTO track VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING TrackId", cancionFalsa)
    canciones.append(cancionFalsa)
    return cursor.fetchone()[0]

#SIMULAR LA CANTIDAD DE DIAS QUE SE DESEEN*******************************************
def simular(dias):
    ventasT = 0
    gananciaT = 0
    inicio = datetime.datetime.now()
    step = datetime.timedelta(days=1)
    for dia in range(dias):
        ventas = randint(vmin,vmax)
        for venta in range(ventas):
            gananciaT += factura(inicio.strftime("%Y-%m-%d"))
            ventasT += 1
        inicio += step
    print("Se generaron $"+str(gananciaT)+" mediante: "+str(ventasT)+" ventas")
#*********************************************************************

#ENCONTRAR LA INFORMACION DE UN CLIENTE PARA EL BILLING
def getInfoCliente(id):
    cursor.execute("SELECT Address, City, State, Country, PostalCode FROM customer WHERE CustomerId = %s", (id, ))
    return cursor.fetchone()

#ENCONTRAR EL PRECIO DE UNA CANCION
def precio(id):
    cursor.execute("SELECT UnitPrice FROM track WHERE TrackId = %s", (id,))
    rows = cursor.fetchone()
    return rows[0]

#SIMULAR UNA VENTA
def factura(fecha):
    total = 0
    global nVentas
    global facturas
    lineas = randint(1,20)
    if randint(0,100)< cln:
        cliente = str(crearClienteFalso())
    else:
        cliente = str(randint(1,nClientes))
    billingInfo = getInfoCliente(cliente)
    factura = [str(nVentas), cliente, fecha, billingInfo[0], billingInfo[1],  billingInfo[2], billingInfo[3], billingInfo[4], "0"]
    cursor.execute("INSERT INTO invoice VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING InvoiceId", factura)
    idF = cursor.fetchone()[0]
    for i in range(lineas):
        total += linea(idF)
    nVentas += 1
    cursor.execute("UPDATE invoice SET total = %s WHERE InvoiceId = %s", (str(total), str(idF)))
    factura[len(factura)-1] = str(total)
    facturas.append(factura)
    return total

#SIMULAR UNA LINEA DE VENTA
def linea(id_factura):
    global nLineas
    global lineasFactura
    if randint(0,100)< cln:
        pista = crearCancionFalsa()
    else:
        pista = randint(1,nCanciones)
    cantidad = 1
    pre = precio(str(pista))
    linea = [str(nLineas), str(id_factura), str(pista), str(pre), str(cantidad)]
    cursor.execute("INSERT INTO invoiceline VALUES (%s, %s, %s, %s, %s)", linea)
    nLineas += 1
    lineasFactura.append(linea)
    return float(pre) * cantidad

#MAIN, PROBAR COSAS
def main():
    try:
        simular(2)
        conn.commit()
        cursor.close()
        conn.close()
        #ESCRIBIR TODO A LOS CSV
        clientesCSV = open('clientes.csv', 'w')
        with clientesCSV:
            writer = csv.writer(clientesCSV)
            writer.writerows(clientes)
        cancionesCSV = open('canciones.csv', 'w')
        with cancionesCSV:
            writer = csv.writer(cancionesCSV)
            writer.writerows(canciones)
        facturasCSV = open('facturas.csv', 'w')
        with facturasCSV:
            writer = csv.writer(facturasCSV)
            writer.writerows(facturas)
        lineasFacturaCSV = open('lineasFactura.csv', 'w')
        with lineasFacturaCSV:
            writer = csv.writer(lineasFacturaCSV)
            writer.writerows(lineasFactura)
    except Exception as e:
        print("Uh oh, can't connect. Invalid dbname, user or password?")
        print(e)

if __name__ == "__main__":
    main()
