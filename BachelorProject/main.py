import uuid

from SET import *
from orderinfo import OrderInfo as OI
from paymentinfo import PaymentInfo as PI
from EMV import *


def app():
    products = ["TV", "Monitor"]
    price = [120, 300]
    command = -1
    order, payment = OI(), PI()
    while command != 4:
        print("Choose: \n1.Add product\n2.Remove product\n3.Display order\n4.Proceed to pay")
        command = int(input())
        if command == 1:
            print("Available products")
            print("Item price")
            for index in range(len(products)):
                print(index + 1, products[index], price[index])
            command2 = input("Enter item name to add:")
            found = False
            for index in range(len(products)):
                if command2 == products[index]:
                    order.addProduct(products[index], price[index])
                    found = True
            if not found:
                print("No product with that name exists")
        elif command == 2:
            order.display()
            command2 = input("Enter product name to remove:")
            order.removeProduct(command2)
        elif command == 3:
            order.display()
        elif command != 4:
            print("Invalid command. Try again!")
    order.display()
    command3 = "no"
    # ok = 0
    while command3 != "yes":
        # cardNumber, expiryDate, cvv = "", "", ""
        # while ok != 2:
        # cardNumber = input("Enter your card number:")
        # expiryDate = input("Enter expiry date in MM/YY format:")
        # cvv = input("Enter your cvv:")
        # if len(cardNumber)!=19 || len(cvv)!=3:
        # print("Your card details ")
        cardNumber = input("Enter your card number:")
        expiryDate = input("Enter expiry date in MM/YY format:")
        cvv = input("Enter your cvv:")
        payment.cardInfo(cardNumber, expiryDate, cvv)
        payment.setPay(order.getTotalPrice())
        payment.display()
        command3 = input("Are your details correct?(yes/no)")
        print(command3)
    dataFromDS = generateDualSignature(order.generateProducts(), payment.generatePaymentInfo())
    purchaseRequest(order.generateProducts(), payment.generatePaymentInfo(), dataFromDS[0], dataFromDS[1],
                    dataFromDS[2])
    verifyMerchant(order, dataFromDS[0], dataFromDS[2])
    verifyTerminal()
    RC = uuid.uuid4().hex
    TD = uuid.uuid4().hex
    signC = generateCardSign(payment.generateCardDataVerification(), RC, TD)
    confC = verifyCard(signC[0], signC[1])
    authOfTheClient()
    cryptogramKey = calculateCryptogramKey(payment.cardNumber, RC)
    authorizReq = generateARQC(cryptogramKey, RC, TD, confC, payment)
    verifyARQC(authorizReq, payment)


app()
