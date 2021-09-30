class PaymentInfo:
    def __init__(self):
        self.cardNumber = ""
        self.expiryDate = ""
        self.cvv = ""
        self.pay = 0
        self.totalMoney = 300
        self.auth = "CDA"

    def cardInfo(self, cardNumber, expiryDate, cvv):
        self.cardNumber = cardNumber
        self.expiryDate = expiryDate
        self.cvv = cvv

    def generateCardDataVerification(self):
        msg = self.cardNumber + "\n" + self.expiryDate
        return msg

    def display(self):
        print("Your card details are:")
        print("CardNumber:", self.cardNumber)
        print("Expiry:", self.expiryDate)
        print("Cvv:", self.cvv)
        print("Amount:", self.pay)

    def setPay(self, amount):
        self.pay = amount

    def generatePaymentInfo(self):
        msg = "---Payment Information---\nCard Number:" + self.cardNumber + "\nExpiry Date:" + self.expiryDate + "\nCvv Number:" + self.cvv + "\nPayment Amount:" + str(
            self.pay)
        return msg
