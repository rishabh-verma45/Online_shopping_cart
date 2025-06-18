# online_shopping_cart.py

import json

class Product:
    def __init__(self, product_id, name, price, quantity_available):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_available = quantity_available

    @property
    def product_id(self):
        return self._product_id

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @property
    def quantity_available(self):
        return self._quantity_available

    @quantity_available.setter
    def quantity_available(self, value):
        if value >= 0:
            self._quantity_available = value

    def decrease_quantity(self, amount):
        if 0 < amount <= self._quantity_available:
            self._quantity_available -= amount
            return True
        return False

    def increase_quantity(self, amount):
        if amount > 0:
            self._quantity_available += amount

    def display_details(self):
        return f"ID: {self._product_id}, Name: {self._name}, Price: ${self._price:.2f}, Available: {self._quantity_available}"

    def to_dict(self):
        return {
            'type': 'product',
            'product_id': self._product_id,
            'name': self._name,
            'price': self._price,
            'quantity_available': self._quantity_available
        }

class PhysicalProduct(Product):
    def __init__(self, product_id, name, price, quantity_available, weight):
        super().__init__(product_id, name, price, quantity_available)
        self._weight = weight

    @property
    def weight(self):
        return self._weight

    def display_details(self):
        return f"ID: {self.product_id}, Name: {self.name}, Price: ${self.price:.2f}, Available: {self.quantity_available}, Weight: {self.weight}kg"

    def to_dict(self):
        data = super().to_dict()
        data.update({'type': 'physical', 'weight': self._weight})
        return data

class DigitalProduct(Product):
    def __init__(self, product_id, name, price, quantity_available, download_link):
        super().__init__(product_id, name, price, quantity_available)
        self._download_link = download_link

    @property
    def download_link(self):
        return self._download_link

    def display_details(self):
        return f"ID: {self.product_id}, Name: {self.name}, Price: ${self.price:.2f}, Download Link: {self.download_link}"

    def to_dict(self):
        data = super().to_dict()
        data.update({'type': 'digital', 'download_link': self._download_link})
        return data

class CartItem:
    def __init__(self, product, quantity):
        self._product = product
        self._quantity = quantity if quantity > 0 else 1

    @property
    def product(self):
        return self._product

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if value >= 0:
            self._quantity = value

    def calculate_subtotal(self):
        return self._product.price * self._quantity

    def __str__(self):
        return f"Item: {self._product.name}, Quantity: {self._quantity}, Price: ${self._product.price:.2f}, Subtotal: ${self.calculate_subtotal():.2f}"

    def to_dict(self):
        return {'product_id': self._product.product_id, 'quantity': self._quantity}

class ShoppingCart:
    def __init__(self, product_catalog_file='products.json', cart_state_file='cart.json'):
        self._items = {}
        self._product_catalog_file = product_catalog_file
        self._cart_state_file = cart_state_file
        self._catalog = self._load_catalog()
        self._load_cart_state()

    def _load_catalog(self):
        try:
            with open(self._product_catalog_file, 'r') as f:
                data = json.load(f)
            catalog = {}
            for item in data:
                type_ = item.get('type')
                if type_ == 'physical':
                    product = PhysicalProduct(
                        item['product_id'], item['name'], item['price'],
                        item['quantity_available'], item['weight']
                    )
                elif type_ == 'digital':
                    product = DigitalProduct(
                        item['product_id'], item['name'], item['price'],
                        item['quantity_available'], item['download_link']
                    )
                else:
                    product = Product(
                        item['product_id'], item['name'], item['price'],
                        item['quantity_available']
                    )
                catalog[product.product_id] = product
            return catalog
        except FileNotFoundError:
            return {}

    def _load_cart_state(self):
        try:
            with open(self._cart_state_file, 'r') as f:
                data = json.load(f)
            for entry in data:
                product_id = entry['product_id']
                quantity = entry['quantity']
                if product_id in self._catalog:
                    self._items[product_id] = CartItem(self._catalog[product_id], quantity)
        except FileNotFoundError:
            pass

    def _save_catalog(self):
        with open(self._product_catalog_file, 'w') as f:
            json.dump([p.to_dict() for p in self._catalog.values()], f, indent=4)

    def _save_cart_state(self):
        with open(self._cart_state_file, 'w') as f:
            json.dump([item.to_dict() for item in self._items.values()], f, indent=4)

    def add_item(self, product_id, quantity):
        if product_id in self._catalog:
            product = self._catalog[product_id]
            if quantity <= 0:
                print("Quantity must be positive.")
                return False
            if product.decrease_quantity(quantity):
                if product_id in self._items:
                    self._items[product_id].quantity += quantity
                else:
                    self._items[product_id] = CartItem(product, quantity)
                self._save_cart_state()
                self._save_catalog()
                return True
            else:
                print("Not enough stock available.")
        else:
            print("Product not found.")
        return False

    def remove_item(self, product_id):
        if product_id in self._items:
            quantity = self._items[product_id].quantity
            self._catalog[product_id].increase_quantity(quantity)
            del self._items[product_id]
            self._save_cart_state()
            self._save_catalog()
            return True
        return False

    def update_quantity(self, product_id, new_quantity):
        if product_id in self._items:
            item = self._items[product_id]
            current_qty = item.quantity
            diff = new_quantity - current_qty
            if new_quantity < 0:
                print("Quantity cannot be negative.")
                return False
            if diff > 0:
                if self._catalog[product_id].decrease_quantity(diff):
                    item.quantity = new_quantity
                else:
                    print("Not enough stock available.")
                    return False
            elif diff < 0:
                self._catalog[product_id].increase_quantity(-diff)
                item.quantity = new_quantity
            self._save_cart_state()
            self._save_catalog()
            return True
        print("Item not found in cart.")
        return False

    def get_total(self):
        return sum(item.calculate_subtotal() for item in self._items.values())

    def display_cart(self):
        if not self._items:
            print("Your cart is empty.")
            return
        for item in self._items.values():
            print(item)
        print(f"Total: ${self.get_total():.2f}")

    def display_products(self):
        for product in self._catalog.values():
            print(product.display_details())

    def run(self):
        while True:
            print("\n1. View Products\n2. Add Item to Cart\n3. View Cart\n4. Update Quantity\n5. Remove Item\n6. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                self.display_products()
            elif choice == '2':
                pid = input("Enter product ID: ")
                try:
                    qty = int(input("Enter quantity: "))
                except ValueError:
                    print("Invalid quantity.")
                    continue
                if self.add_item(pid, qty):
                    print("Item added to cart.")
                else:
                    print("Failed to add item. Check availability.")
            elif choice == '3':
                self.display_cart()
            elif choice == '4':
                pid = input("Enter product ID: ")
                try:
                    qty = int(input("Enter new quantity: "))
                except ValueError:
                    print("Invalid quantity.")
                    continue
                if self.update_quantity(pid, qty):
                    print("Quantity updated.")
                else:
                    print("Update failed.")
            elif choice == '5':
                pid = input("Enter product ID to remove: ")
                if self.remove_item(pid):
                    print("Item removed.")
                else:
                    print("Item not found.")
            elif choice == '6':
                print("Goodbye!, Thank you for shopping with us.")
                break
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    cart = ShoppingCart()
    cart.run()