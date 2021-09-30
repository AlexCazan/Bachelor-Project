import pickle
import socket
import uuid

from SET import *
from EMV import *

HOST = '127.0.0.1'
PORT = 2005

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
    client.connect((HOST, PORT))
    print("M-am conectat pentru protocoale")
    payment = pickle.loads(client.recv(4096))
    order = pickle.loads(client.recv(4096))
    dataFromDS = generateDualSignature(order.generateProducts(), payment.generatePaymentInfo())
    purchaseRequest(order.generateProducts(), payment.generatePaymentInfo(), dataFromDS[0], dataFromDS[1],
                    dataFromDS[2])

    verifyMerchant(order, dataFromDS[0], dataFromDS[2])
    verifyTerminal()
    print("Odata validat POMD-ul pe partea de terminal, se pregateste efectuarea tranzactiei.")
    RC = uuid.uuid4().hex
    TD = uuid.uuid4().hex
    print("Se genereaza doua coduri aleatorii RC: " + RC + " si TD: " + TD)
    print("Se pregateste identificarea cardului.")
    signC = generateCardSign(payment.generateCardDataVerification(), RC, TD)
    print("Se pregateste generarea confirmarii cardului ca este valid sau nu.")
    confC = verifyCard(signC[0], signC[1])
    client.send("6".encode())
    print("Se pregateste crearea cererii de autorizare pentru plata.")
    cryptogramKey = calculateCryptogramKey(payment.cardNumber, RC)
    print("Se genereaza autorizarea.")
    authorizReq = generateARQC(cryptogramKey, RC, TD, confC, payment)
    print("Se verifica autorizarea.")
    transaction = verifyARQC(authorizReq, payment)
    client.send(transaction.encode())
    while True:
        pass
