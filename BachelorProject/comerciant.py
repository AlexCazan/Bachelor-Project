import pickle
import socket
import uuid
from time import sleep
from SET import *
from EMV import *
from orderinfo import OrderInfo as OI
from paymentinfo import PaymentInfo as PI

# def multi_threaded_client(connection):
#     while True:
#         message = connection.recv(1024).decode()
#         if message == "exit":
#             connection.send(b'Ups, ai tastat exit!')
#             print(f"Clientul cu threadul {threadCount} a iesit!")
#             break
#         else:
#             connection.send(b'Serverul a primit mesajul tau!')
#             print(message)
# threadCount = 0


HOST = '127.0.0.1'
PORT = 2005
products = ["TV", "Monitor"]
price = [120, 300]
order, payment = OI(), PI()


def hashDatabase(paymentOrder):
    f = open("Database", "w")
    f.write(SHA3_256.new("3333".encode()).hexdigest() + "\n")
    f.write(SHA3_256.new(paymentOrder.cardNumber.encode()).hexdigest() + "\n")
    f.write(SHA3_256.new(paymentOrder.expiryDate.encode()).hexdigest() + "\n")
    f.write("300")
    f.close()


def hashDatabaseWrongData():
    f = open("Database", "w")
    f.write(SHA3_256.new("3334".encode()).hexdigest() + "\n")
    f.write(SHA3_256.new("4242 4242 4242 4243".encode()).hexdigest() + "\n")
    f.write(SHA3_256.new("03/23".encode()).hexdigest() + "\n")
    f.write("300")
    f.close()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(2)
    print("Server comerciant pornit")
    conn, addr = s.accept()
    conn2, addr2 = s.accept()
    conn.send(
        b'Welcome to the store!\n Choose: \n1.Add product\n2.Remove product\n3.Display order\n4.Proceed to pay\n5.Exit')
    print("Connected by", addr)
    print("Connected by", addr2)
    while True:
        messageForAction = int(conn.recv(1024).decode())
        if messageForAction == 1:
            conn.send(b'Available products and product price\n ')
            productList = []
            for index in range(len(products)):
                productList.append((index + 1, products[index], price[index]))
            conn.send(pickle.dumps(productList))
            messageForSelectingProduct = conn.recv(1024).decode()
            found = False
            for index in range(len(products)):
                if messageForSelectingProduct == products[index]:
                    order.addProduct(products[index], price[index])
                    found = True
                    conn.send(b'Product added to your list')
            if not found:
                conn.send(b'No product with that name was found')
        elif messageForAction == 2:
            productList = []
            conn.send(b'\nOrder:\n')

            for index in range(len(order.productList)):
                productList.append((order.productList[index], order.priceList[index]))
            conn.send(pickle.dumps(productList))
            sleep(1)
            productToBeRemoved = conn.recv(4096).decode()
            removedProduct = order.removeProduct(productToBeRemoved)
            conn.send(removedProduct.encode())
        elif messageForAction == 3:
            productList = []
            conn.send(b'\nOrder:\n')

            for index in range(len(order.productList)):
                productList.append((order.productList[index], order.priceList[index]))
            conn.send(pickle.dumps(productList))
            sleep(2)
            conn.send(str(order.getTotalPrice()).encode())
        elif messageForAction == 4:
            ok = 'no'
            productList = []
            conn.send(b'\nOrder:\n')

            for index in range(len(order.productList)):
                productList.append((order.productList[index], order.priceList[index]))
            conn.send(pickle.dumps(productList))
            sleep(2)
            conn.send(str(order.getTotalPrice()).encode())
            while ok != 'yes':
                message = conn.recv(4096).decode()
                cardDetails = message.split(',')
                payment.cardInfo(cardDetails[0], cardDetails[1], cardDetails[2])
                payment.setPay(order.getTotalPrice())

                conn.send(str(payment.pay).encode())
                ok = conn.recv(4096).decode()
                sleep(1)
            hashDatabase(payment)
            dataPayment = pickle.dumps(payment)
            dataOrder = pickle.dumps(order)
            conn2.send(dataPayment)
            conn2.send(dataOrder)
            number=conn2.recv(1024).decode()
            conn.send(number.encode())
            attempts = 0
            if number == "6":
                while attempts != 3:
                    PIN = conn.recv(4096).decode()
                    validity = authOfTheClient2(PIN)
                    if validity == "Valid PIN!":
                        conn.send(validity.encode())
                        transaction = conn2.recv(4096)
                        conn.send(transaction)
                        attempts = 3
                    else:
                        attempts += 1
                        conn.send(str(attempts).encode())
            order, payment = OI(), PI()
        elif messageForAction == 5:
            print("Clientul  a iesit!")
            break
