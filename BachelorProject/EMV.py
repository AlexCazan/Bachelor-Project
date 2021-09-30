import sys

from Crypto.Cipher import AES
from Crypto.Hash import SHA3_256, HMAC, SHA256
from Crypto.Random import get_random_bytes
from Crypto.Signature import pss

from helperFunctions import *


def generateCertIB():
    issuerPK = RSA.import_key(open("GeneratedFiles/PKissuer").read()).public_key().export_key(format='PEM')
    paymentSchemeSK = RSA.import_key(open("GeneratedFiles/SKpaymentS").read(), passphrase="lHeV78RNWJF1v5tf")
    signer = pss.new(paymentSchemeSK)
    certIB = signer.sign(SHA3_256.new(issuerPK))
    return certIB


def generateCertC():
    cardPK = RSA.import_key(open("GeneratedFiles/PKcard").read()).public_key().exportKey(format='PEM')
    issuerSK = RSA.import_key(open("GeneratedFiles/SKissuer").read(), passphrase="8xzIerIQNffrdNlj")
    signer = pss.new(issuerSK)
    certC = signer.sign(SHA3_256.new(cardPK))
    return certC


def generateCardSign(cardVerificationInfo, RC, TD):
    print("Se genereaza cheile pentru banca emitenta, card si schema de plata.")
    generateKeysRSA("card")
    generateKeysRSA("IB")
    generateKeysRSA("PS")
    wait = input("Press Enter to move on.")
    cardInfo = cardVerificationInfo.split("\n")
    dataToBeHashed = (RC + "," + TD + "," + cardInfo[0] + "," + cardInfo[1]).encode()
    print(
        f"Se aplica un hash peste RC+TD+numarul cardului ({cardInfo[0]})+data de expirare a cardului ({cardInfo[1]}).")
    wait = input("Press Enter to move on.")
    print(f"Hash-ul rezultat este {SHA3_256.new(dataToBeHashed).hexdigest()}")
    cardSK = RSA.import_key(open("GeneratedFiles/SKcard").read(), passphrase="Y2MRzsULvxtf6pbR")
    print(f"Se genereaza semnatura cardului folosind cheia privata a acestuia: {cardSK.exportKey(format='PEM').hex()}")
    wait = input("Press Enter to move on.")
    signer = pss.new(cardSK)
    signC = signer.sign(SHA3_256.new(dataToBeHashed))
    print(f"Semnatura cardului este {signC.hex()}")
    return signC, dataToBeHashed


def verifyCard(signC, dataHashed):
    wait = input("Press Enter to move on.")
    print("Se genereaza certificatele semnate de catre schema de plata pentru banca emitenta si card.")
    certIB = generateCertIB()
    certC = generateCertC()
    wait = input("Press Enter to move on.")
    print(f"Semnatura pentru certificatul bancii este {certIB.hex()} iar a cardului {certC.hex()}")
    wait = input("Press Enter to move on.")
    print("Se verifica certificatele.")
    paymentSchemePK = RSA.import_key(open("GeneratedFiles/PKpaymentS").read())
    issuerPK = RSA.import_key(open("GeneratedFiles/PKissuer").read())
    cardPK = RSA.import_key(open("GeneratedFiles/PKcard").read())
    verifierCertIB = pss.new(paymentSchemePK)
    verifierCertC = pss.new(issuerPK)
    verifierSignC = pss.new(cardPK)
    try:
        verifierCertIB.verify(
            SHA3_256.new(RSA.import_key(open("GeneratedFiles/PKissuer").read()).public_key().exportKey(format='PEM')),
            certIB)
        print("Certificatul bancii valid!")
        verifierCertC.verify(SHA3_256.new(RSA.import_key(open(
            "GeneratedFiles/PKcard").read()).public_key().exportKey(format='PEM')),
                             certC)
        print("Certificaatul cardului valid!")
        verifierSignC.verify(SHA3_256.new(dataHashed), signC)
        print("Semnatura cardului valida!")
        return "Valid"
    except (ValueError, TypeError):
        sys.exit("Invalid data!")


def generateKeyAESByIssuerBank():
    IMK_AC = get_random_bytes(AES.block_size)
    return IMK_AC


# def authOfTheClient(PIN):
#     with open('Database') as f:
#         first_line = f.readline()
#     attempts = 0
#     while attempts != 3:
#         if first_line[:(len(first_line) - 1)] == PIN:
#             return "Valid PIN!"
#         else:
#             attempts += 1
#             print(f"Attempts remaining: {3 - attempts}")
#     sys.exit("Too many attempts on the PIN's card!")


def authOfTheClient2(PIN):
    with open('Database') as f:
        first_line = f.readline()
        if first_line[:(len(first_line) - 1)] == SHA3_256.new(PIN.encode()).hexdigest():
            return "Valid PIN!"
        else:
            return "Invalid PIN!"


def calculateCryptogramKey(PAN, RC):
    print("Se genereaza cheia simterica pentru autorizare")
    key_AES = generateKeyAESByIssuerBank()
    wait = input("Press Enter to move on.")
    cipher = AES.new(key_AES, AES.MODE_EAX)
    CK_AC, tag = cipher.encrypt_and_digest(PAN.encode())
    msg = CK_AC + b"," + RC.encode()
    print(f"Cheia finala este {msg}")
    cryptogramKey = SHA3_256.new(msg)
    wait = input("Press Enter to move on.")
    print(f"Hash-ul cheii este {cryptogramKey.hexdigest()}")
    f = open("GeneratedFiles/StoredCK", "w")
    f.write(bin2hex(CK_AC).decode())
    f.close()
    wait = input("Press Enter to move on.")
    return cryptogramKey.hexdigest().encode()


def generateARQC(cryptogramKey, RC, TD, ConfC, cardInfo):
    print("Se aplica un HMAC peste cheia precedenta.")
    Hmac = HMAC.new(cryptogramKey, digestmod=SHA256)
    msg = (RC + "," + TD + "," + cardInfo.cardNumber + "," + cardInfo.expiryDate + "," + ConfC).encode()
    print(f"Se hash-uieste mesajul format din {RC, TD, cardInfo.cardNumber, cardInfo.expiryDate, ConfC}")
    wait = input("Press Enter to move on.")
    Hmac.update(msg)
    print(f"Mesajul final este {Hmac.hexdigest()}")
    wait = input("Press Enter to move on.")
    authorizReq = msg.decode() + "," + Hmac.hexdigest()
    print(f"Cererea de autorizare este {authorizReq}")
    wait = input("Press Enter to move on.")
    return authorizReq


# def secureMessageBetweenTerminalAndAcquirer(TD, RC, authorizReq):
#     key_AES = os.urandom(16)
#     cipher = AES.new(key_AES, AES.MODE_EAX)
#     msg = (TD + "," + RC + "," + authorizReq).encode()
#     ciphertext, tag = cipher.encrypt_and_digest(msg)
#     return ciphertext, tag
#
#
# def secureMessageBetweenAcquirerAndIssuer(TD, RC, authorizReq):
#     key_AES = os.urandom(16)
#     RAB=uuid.uuid4().hex
#     cipher = AES.new(key_AES, AES.MODE_EAX)
#     msg = (RAB+","+TD + "," + RC + "," + authorizReq).encode()
#     ciphertext, tag = cipher.encrypt_and_digest(msg)
#     return ciphertext, tag

def verifyARQC(authorizReq, cardInfo):
    getInfo = authorizReq.split(",")
    RC, TD, cardNumber, cardExpiryDate, ConfC = getInfo[0], getInfo[1], getInfo[2], getInfo[3], getInfo[4]
    f = open("Database", "rb")
    f.readline()
    second_line = f.readline()
    third_line = f.readline()
    balance = f.readline().decode()
    f1 = open("GeneratedFiles/StoredCK", "rb")
    fourth_line = f1.readline()
    f2 = open("GeneratedFiles/Price", "r")
    price = f2.readline()
    print("Se verifica cardul pentru validare")
    if ConfC == "Valid":
        print("Cardul este valid!")
        wait = input("Press Enter to move on.")
        if second_line[:(len(second_line) - 2)].decode() == SHA3_256.new(
                cardNumber.encode()).hexdigest() and third_line[:(
                len(third_line) - 2)].decode() == SHA3_256.new(cardExpiryDate.encode()).hexdigest():
            print("Se genereaza un nou ARQC cu datele primite.")
            CK_AC = hex2bin(fourth_line.decode().encode())
            msg = CK_AC + b"," + getInfo[0].encode()
            cryptogramKey = SHA3_256.new(msg)
            print(f"Noua cheie este {cryptogramKey.hexdigest()}")
            wait = input("Press Enter to move on.")
            ARQC2 = generateARQC(cryptogramKey.hexdigest().encode(), RC, TD, ConfC, cardInfo).split(",")[5]
            print(f"Noul ARQC este {ARQC2}")
            wait = input("Press Enter to move on.")
            print("Se verifica daca cele doua ARQC-uri coincid.")
            wait = input("Press Enter to move on.")
            if getInfo[5] == ARQC2:
                print("ARQC-urile coincid. Se verifica balanta contului bancar al clientului.")
                if int(balance) >= int(price):
                    print("Balanta este in regula, se efectueaza tranzactia.")
                    balance = int(balance) - int(price)
                    replace_line("Database", 3, str(balance))
                    return "Transaction accepted!"
                else:
                    # print("al patrulea if")
                    return "Transaction denied!"
            else:
                # print("al treilea if")
                return "Transaction denied!"
        else:
            # print("al doilea if")
            return "Transaction denied!"
    else:
        # print("primu if")
        return "Transaction denied!"
