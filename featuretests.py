import unittest
import os
import sys
from server import app
from model import connect_to_db, db, example_data, Product
import json

current = os.getcwd()
current = current.split("/")
current = "/".join(current[:-1])
sys.path.append(current)


class FlaskTests(unittest.TestCase):

    def setUp(self):
        """Before tests."""

        self.client = app.test_client()
        app.config['TESTING'] = True
        # Connect to test database
        connect_to_db(app)

        # Create tables and add sample data
        db.create_all()
        example_data()
        self.cart = Product.query.filter(Product.product_id.in_([1])).all()

    def tearDown(self):
        """For after test."""

        db.session.close()
        db.drop_all()

    def test_register(self):
        """Register test user"""

        result = self.client.post("/register",
                                  data={"first_name": "Jane",
                                        "last_name": "Doe",
                                        "email": "jane@gmail.com",
                                        "password": "123"},
                                  follow_redirects=True)
        self.assertIn(b"Registration successful!", result.data)

        result = self.client.get('/register')
        self.assertIn(b'register_img', result.data)

    def test_login(self):
        """Test login functionality"""

        login = self.client.post("/login",
                                 data={"email": "Jane@jane.com", "password": "password"},
                                 follow_redirects=True)
        self.assertIn(b"Success", login.data)

        logged_in = self.client.get("/products")
        self.assertIn(b"Account", logged_in.data)
        self.assertIn(b"Log Out", logged_in.data)

        result = self.client.get('/account')
        self.assertIn(b'Jane Doe', result.data)

        logout = self.client.get("/logout", follow_redirects=True)
        self.assertNotIn(b"Account", logout.data)
        self.assertIn(b"Login", logout.data)

    def test_frontpage(self):
        """Test static frontpage"""

        result = self.client.get("/")

        self.assertIn(b"Farm", result.data)

    def test_all_products(self):
        """Test products listings"""

        result = self.client.get("/products")

        self.assertIn(b"Add to Cart</button>", result.data)

    def test_product_page(self):
        """Test individual product page"""

        result = self.client.get("/products/1")

        self.assertIn(b"Blackberries", result.data)

        result = self.client.post('/products/1', data={'productId': '1'}, follow_redirects=True)
        self.assertIn(b'Blackberries', result.data)

    def test_cart_page(self):
        """Test cart page"""

        result = self.client.get("/cart")

        self.assertIn(b"Shopping Cart", result.data)

        result = self.client.post('/cart',
                                  data=json.dumps({'delivery': 'delivery',
                                                   'address': {'street': '1234 Main Street',
                                                               'zipcode': '31626'}}),
                                  follow_redirects=True)
        self.assertIn(b'Success', result.data)

    def test_locations(self):
        """Test locations page"""

        result = self.client.get("/locations")

        self.assertIn(b'<div id="map">', result.data)

    def test_search(self):
        """Test search functionality"""

        result = self.client.get("/search?terms=black")

        self.assertIn(b"Organic Blackberries", result.data)

    def test_save_recipe(self):
        result = self.client.post('/save-recipe',
                                  data=json.dumps({'url': 'http://foodandstyle.com/2012/12/20/persimmon-cosmopolitan/'}),
                                  follow_redirects=True)
        self.assertIn(b'Success', result.data)

    def test_update_cart(self):
        result = self.client.post('/add-item', data=json.dumps({'product_id': 1}), follow_redirects=True)
        self.assertIn(b'Success!', result.data)

        result = self.client.post('/update-cart', data=json.dumps({'product_id': 1, 'qty': 3}), follow_redirects=True)
        self.assertIn(b'Success', result.data)

    def test_checkout(self):
        result = self.client.get('/checkout')
        self.assertIn(b'Thank you', result.data)

        result = self.client.post('/checkout')
        self.assertIn(b'Your order has been placed!', result.data)


if __name__ == "__main__":
    log_file = 'log_file.txt'
    with open(log_file, "w") as f:
        runner = unittest.TextTestRunner(f)
        unittest.main(testRunner=runner)