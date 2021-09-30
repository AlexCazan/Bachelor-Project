import binascii
import os

from Crypto.PublicKey import RSA


def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


def bin2hex(binStr):
    return binascii.hexlify(binStr)


def hex2bin(hexStr):
    return binascii.unhexlify(hexStr)


def generateKeysRSA(participant):
    save_path = './GeneratedFiles/'

    if participant == "client":
        filename1, filename2 = os.path.join(save_path, "SKclient"), os.path.join(save_path, "PKclient")
        secure = "Mn6kGy9ytOuKom0N"
    elif participant == "card":
        filename1, filename2 =os.path.join(save_path, "SKcard"), os.path.join(save_path, "PKcard")
        secure = "Y2MRzsULvxtf6pbR"
    elif participant == "IB":
        filename1, filename2 = os.path.join(save_path, "SKissuer"), os.path.join(save_path, "PKissuer")
        secure = "8xzIerIQNffrdNlj"
    elif participant == "PS":
        filename1, filename2 = os.path.join(save_path, "SKpaymentS"), os.path.join(save_path, "PKpaymentS")
        secure = "lHeV78RNWJF1v5tf"
    else:
        filename1, filename2 = os.path.join(save_path, "SKbank"), os.path.join(save_path, "PKbank")
        secure = "8DTDc57vtTnFkJbu"
    key = RSA.generate(2048)
    private_key = key.exportKey(passphrase=secure)
    outputSK = open(filename1, "wb")
    outputSK.write(private_key)
    outputSK.close()

    public_key = key.public_key().exportKey()
    outputPK = open(filename2, "wb")
    outputPK.write(public_key)
    outputPK.close()
