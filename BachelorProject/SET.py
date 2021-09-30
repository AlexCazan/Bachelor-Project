from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Hash import SHA3_256
from Crypto.Random import get_random_bytes
from Crypto.Signature import pss

from helperFunctions import *


def generateDualSignature(orderInformation, paymentInformation):
    generateKeysRSA("client")
    encoded_PI = paymentInformation.encode()
    encoded_OI = orderInformation.encode()
    print("Se genereaza semnatura duala de catre client")
    wait = input("Press Enter to move on.")
    print(f"Se aplica un hash asupra PI-ul : {paymentInformation}")
    print(f"Se aplica un hash asupra OI-ul : {orderInformation}")
    wait = input("Press Enter to move on.")
    OIMD = SHA3_256.new(encoded_OI)
    PIMD = SHA3_256.new(encoded_PI)
    print(f"Hash-ul rezultat pentru PI este PIMD: {PIMD.hexdigest()}")
    print(f"Hash-ul rezultat pentru OI este OIMD: {OIMD.hexdigest()}")
    wait = input("Press Enter to move on.")
    concat_msg = PIMD.hexdigest() + OIMD.hexdigest()
    POMD = SHA3_256.new(concat_msg.encode())
    print(f"S-a aplicat un alt hash peste PIMD+OIMD rezultand POMD: {POMD.hexdigest()}")
    print("Se pregateste cheia privata a clientului pentru generarea semnaturii")
    wait = input("Press Enter to move on.")
    clientSK = RSA.import_key(open("GeneratedFiles/SKclient").read(), passphrase="Mn6kGy9ytOuKom0N")

    signer = pss.new(clientSK)
    digitalSignature = signer.sign(POMD)
    print(f"S-a generat semnatura: {digitalSignature.hex()} \n cu ajutorul cheii {clientSK.exportKey(format='PEM').hex()} \n")
    wait = input("Press Enter to move on.")
    return PIMD, OIMD, digitalSignature


def purchaseRequest(OI, PI, PIMD, OIMD, digitalSignature):
    print("Se genereaza cererea de cumparare")
    wait = input("Press Enter to move on.")
    generateKeysRSA("bank")
    fileout = open("GeneratedFiles/encrypted_purchase_request.bin", "wb")
    key_AES = get_random_bytes(AES.block_size)
    msgForSplit = SHA3_256.new("AnaArePere".encode()).hexdigest().encode()
    data = PI.encode() + msgForSplit + OIMD.hexdigest().encode() + msgForSplit + digitalSignature

    bankPK = RSA.import_key(open("GeneratedFiles/PKbank").read())
    print(
        f"Se va cripta cheia simetrica: {key_AES.hex()} cu cheia publica a terminalului {bankPK.public_key().exportKey(format='PEM').hex()}")
    wait = input("Press Enter to move on.")
    print(f"Se va cripta mesajul format din PI+OIMD+DS cu cheia simetrica: {key_AES.hex()}")
    wait = input("Press Enter to move on.")
    cipherRSA = PKCS1_OAEP.new(bankPK)
    digitalEnvelope = cipherRSA.encrypt(key_AES)

    cipher = AES.new(key_AES, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    print(f"Cererea de cumparare este: {ciphertext.hex()} \n")
    [fileout.write(x) for x in (digitalEnvelope, cipher.nonce, tag, ciphertext)]
    fileout.close()
    wait = input("Press Enter to move on.")
    return PIMD, OI, digitalSignature


def verifyMerchant(OI, PIMD, DS):
    print("Se verifica daca POMD-ul este nealterat pe partea de comerciant")
    orderInfo = OI.generateProducts()
    encoded_OI = orderInfo.encode()
    f = open("GeneratedFiles/Price", "w")
    f.write(str(OI.totalPrice))
    f.close()
    print(f"Se aplica un hash asupra OI-ul : {orderInfo}")
    wait = input("Press Enter to move on.")
    OIMD = SHA3_256.new(encoded_OI)
    print(f"Hash-ul rezultat pentru OI este OIMD: {OIMD.hexdigest()}")
    wait = input("Press Enter to move on.")
    concat_msg = PIMD.hexdigest() + OIMD.hexdigest()
    POMD = SHA3_256.new(concat_msg.encode())
    print(
        f"Se genereaza POMD prin concatenarea PIMD-ul primit: {PIMD.hexdigest()} si a OIMD-ul generat: {OIMD.hexdigest()}")
    wait = input("Press Enter to move on.")
    print(f"POMD-ul este: {POMD.hexdigest()}")
    wait = input("Press Enter to move on.")
    certificate = RSA.import_key(open("GeneratedFiles/PKclient").read())
    print(f"Se obtine certificatul clientului {certificate.public_key().exportKey(format='PEM').hex()}")
    wait = input("Press Enter to move on.")
    verifier = pss.new(certificate)
    print("Se verifica daca POMD-ul este acelasi cu semnatura DS")
    wait = input("Press Enter to move on.")
    try:

        verifier.verify(POMD, DS)
        print("POMD valid pe partea de comerciant \n")
        wait = input("Press Enter to move on.")
        return OI
    except (ValueError, TypeError):
        print("POMD invalid pe partea de comerciant \n")


def verifyTerminal():
    print("Se verifica daca POMD-ul este nealterat pe partea de terminal")
    msgForSplit = SHA3_256.new("AnaArePere".encode())
    filein = open("GeneratedFiles/encrypted_purchase_request.bin", "rb")
    bankSK = RSA.import_key(open("GeneratedFiles/SKbank").read(), passphrase="8DTDc57vtTnFkJbu")
    digitalEnvelope, nonce, tag, ciphertext = [filein.read(x) for x in (bankSK.size_in_bytes(), 16, 16, -1)]

    cipherRSA = PKCS1_OAEP.new(bankSK)
    key_AES = cipherRSA.decrypt(digitalEnvelope)

    cipher = AES.new(key_AES, AES.MODE_EAX, nonce)
    purchaseReq = cipher.decrypt(ciphertext)

    info = purchaseReq.split(msgForSplit.hexdigest().encode(), 2)
    PI, OIMD, DS = info[0], info[1], info[2]
    print(f"Se aplica un hash asupra PI-ul : {PI.decode()}")
    wait = input("Press Enter to move on.")
    PIMD = SHA3_256.new(PI)
    print(f"Hash-ul rezultat pentru PI este PIMD: {PIMD.hexdigest()}")
    wait = input("Press Enter to move on.")
    POMD = SHA3_256.new((PIMD.hexdigest() + OIMD.decode()).encode())
    print(
        f"Se genereaza POMD prin concatenarea OIMD-ul primit: {OIMD.hex()} si a PIMD-ul generat: {PIMD.hexdigest()}")
    wait = input("Press Enter to move on.")
    print(f"POMD-ul este: {POMD.hexdigest()}")
    wait = input("Press Enter to move on.")
    certificate = RSA.import_key(open("GeneratedFiles/PKclient").read())
    verifier = pss.new(certificate)
    print("Se verifica daca POMD-ul este acelasi cu semnatura DS")
    wait = input("Press Enter to move on.")
    try:
        verifier.verify(POMD, DS)
        print("POMD valid pe partea de terminal \n")
        wait = input("Press Enter to move on.")
        return PI
    except (ValueError, TypeError):
        print("POMD invalid pe partea de comerciant \n")
