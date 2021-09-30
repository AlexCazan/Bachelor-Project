import pickle
import socket
from time import sleep

HOST = '127.0.0.1'
PORT = 2005



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))
    print("M-am conectat la comerciant!")
    print(client.recv(1024).decode())
    while True:
        requestForAction = input("Your command: ")
        client.send(requestForAction.encode())
        if requestForAction == '1':
            message = client.recv(1024).decode()
            print(message)
            productList = pickle.loads(client.recv(4096))
            for index in range(len(productList)):
                print(productList[index][0], productList[index][1], productList[index][2])
            requestForChoosingProduct = input("Enter product name to add: ")
            client.send(requestForChoosingProduct.encode())
            print(client.recv(4096).decode())
        elif requestForAction == '2':
            print(client.recv(4096).decode())
            productList = pickle.loads(client.recv(4096))
            for index in range(len(productList)):
                print(" " + str(productList[index][0]) + "  " + str(productList[index][1]) + " lei")
            requestForRemovingProduct = input("Enter product to remove from the list: ")
            client.send(requestForRemovingProduct.encode())
            print(client.recv(4096).decode())
        elif requestForAction == '3':
            print(client.recv(4096).decode())
            # data = []
            # while True:
            #     packet = client.recv(4096)
            #     print(type(packet))
            #     if packet is None:
            #         break
            #     data.append(packet)
            # print(data)
            productList = pickle.loads(client.recv(4096))
            for index in range(len(productList)):
                print(" " + str(productList[index][0]) + "  " + str(productList[index][1]) + " lei")
            print(" Total amount: " + client.recv(4096).decode() + " lei")
        elif requestForAction == '4':
            print(client.recv(4096).decode())
            productList = pickle.loads(client.recv(4096))
            for index in range(len(productList)):
                print(" " + str(productList[index][0]) + "  " + str(productList[index][1]) + " lei")
            print(" Total amount: " + client.recv(4096).decode() + " lei")
            correctDetails = 'no'
            while correctDetails != "yes":
                cardNumber = input("Enter your card number:")
                expiryDate = input("Enter expiry date in MM/YY format:")
                cvv = input("Enter your cvv:")
                message = cardNumber + ',' + expiryDate + ',' + cvv
                client.send(message.encode())
                totalPay = client.recv(4096).decode()
                print("Your card details are:")
                print("CardNumber:", cardNumber)
                print("Expiry:", expiryDate)
                print("Cvv:", cvv)
                print("Amount:", totalPay)
                correctDetails = input("Are your details correct?(yes/no)")
                client.send(correctDetails.encode())
                sleep(1)
                #client.send(b'monitor')
            if client.recv(1024).decode()=="6":

                while True:
                    PIN = str(input("Please enter your PIN's card: "))
                    client.send(PIN.encode())
                    validity = client.recv(4096).decode()
                    if validity == "Valid PIN!":
                        transaction = client.recv(4096).decode()
                        print(transaction)
                        break
                    elif 3 - int(validity) > 0:
                        print(f"Attempts remaining: {3 - int(validity)}")
                    else:
                        print("Transaction denied!")
                        break
        if requestForAction == '5':
            break
