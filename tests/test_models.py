# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_update_product(self):
    """It should update an existing product"""
    product = ProductFactory()
    product.create()

    updated_product = Product.query.get(product.id)
    updated_product.name = "Updated Fedora"
    updated_product.description = "A stylish red hat"
    updated_product.price = 15.00
    updated_product.available = False
    updated_product.update()

    # Fetch the updated product and assert that the changes were made
    fetched_product = Product.query.get(product.id)
    self.assertEqual(fetched_product.name, "Updated Fedora")
    self.assertEqual(fetched_product.description, "A stylish red hat")
    self.assertEqual(Decimal(fetched_product.price), 15.00)
    self.assertEqual(fetched_product.available, False)

def test_delete_product(self):
    """It should delete an existing product"""
    product = ProductFactory()
    product.create()

    product_id = product.id
    product.delete()

    # Try to fetch the deleted product and assert that it does not exist
    deleted_product = Product.query.get(product_id)
    self.assertIsNone(deleted_product)
def test_list_all_products(self):
    """It should list all products"""
    products = Product.all()
    self.assertEqual(len(products), 0)
    product = ProductFactory()
    product.create()
    products = Product.all()
    self.assertEqual(len(products), 1)
def test_find_product_by_name(self):
    """It should find a product by name"""
    product_name = "Fedora"
    product = ProductFactory(name=product_name)
    product.create()
    product_found = Product.find_by_name(product_name)
    self.assertEqual(product_found, product)
def test_find_product_by_category(self):
    """It should find a product by category"""
    category = Category.CLOTHS
    product = ProductFactory(category=category)
    product.create()
    products_found = Product.find_by_category(category)
    self.assertEqual(products_found[0], product)
def test_find_product_by_availability(self):
    """It should find a product by availability"""
    availability = True
    product = ProductFactory(available=availability)
    product.create()
    products_found = Product.find_by_availability(availability)
    self.assertEqual(products_found[0], product)

# Test the READ endpoint
def test_read_product(self):
    """It should read a product from the database"""
    product = ProductFactory()
    product.create()

    # Read the product from the database
    retrieved_product = Product.query.get(product.id)

    # Check the retrieved product data
    self.assertEqual(retrieved_product.id, product.id)
    self.assertEqual(retrieved_product.name, product.name)
    self.assertEqual(retrieved_product.description, product.description)
    self.assertEqual(retrieved_product.price, product.price)
    self.assertEqual(retrieved_product.available, product.available)
    self.assertEqual(retrieved_product.category, product.category)
