from django.conf import settings
from courses.models import Course
from decimal import Decimal




class Cart(object):
    def __init__(self, request):
        """
        Initialize the cart 
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            #save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
            'price': str(product.price)}

        if update_quantity:
            self.cart[product_id]['quantity'] = quantity

        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()


    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        
        self.session.modified = True










# mark the session as "modified" to make sure it is saved
#update the session cart


    def remove(self,product):
        """
        Remove a product from the cart
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()


    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database
        """
        product_ids = self.cart.keys()
        # get the products objects and add them to the cart
        products = Course.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item


    def __next__(self):
        if self.index == 0:
            raise StopIteration
        self.index = self.index - 1
        return self.data[self.index]

    def __len__(self):
        """
        Count all items in class
        """
        return sum(item['quantity'] for item in self.cart.values())

    def total_price(self):
        return (Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in 
        self.cart.values())


    def clear(self): #remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def total_price(self):
        return (item['price'] * item['quantity'] for item in self.cart.values())
        





