class OrderInfo:
    def __init__(self):
        self.productList = []
        self.priceList = []
        self.totalPrice = 0

    def calculatePrice(self):
        totalPrice = 0
        for price in self.priceList:
            totalPrice += price
        self.totalPrice = totalPrice

    def addProduct(self, product, price):
        self.productList.append(product)
        print("Product added to the client list")
        self.priceList.append(price)
        self.calculatePrice()

    def searchProduct(self, product):
        for index in range(len(self.productList)):
            if self.productList[index] == product:
                return index
        return -1

    def numberOfProductOfSameType(self, product):
        count = 0
        for index in range(len(self.productList)):
            if self.productList[index] == product:
                count += 1
        return count

    def removeProduct(self, product):
        productIndex = self.searchProduct(product)
        if productIndex != -1:
            del self.productList[productIndex]
            del self.priceList[productIndex]
            self.calculatePrice()
            return f"Product deleted with index {productIndex}"
        else:
            return "Product not found"

    def getTotalPrice(self):
        return self.totalPrice

    def display(self):
        print("\n Your order is:")
        print("Item  Price")
        for index in range(len(self.productList)):
            print(self.productList[index], "    ", self.priceList[index])
        print("Total amount: ", self.totalPrice)

    def generateProducts(self):
        products = "---Order Information---\nProducts:\n"
        for index in range(len(self.productList)):
            products += self.productList[index] + "    " + str(self.priceList[index]) + "\n"
        products += "Total price: " + str(self.totalPrice)
        return products
