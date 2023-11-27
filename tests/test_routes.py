######################################################################
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
######################################################################
"""
Product API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_service.py:TestProductService
"""
import os
import logging
from decimal import Decimal
from unittest import TestCase
from service import app
from service.common import status
from service.models import db, init_db, Product
from tests.factories import ProductFactory

# Disable all but critical errors during normal test run
# uncomment for debugging failing tests
# logging.disable(logging.CRITICAL)

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/products"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductRoutes(TestCase):
    """Product Service tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    ############################################################
    # Utility function to bulk create products
    ############################################################
    def _create_products(self, count: int = 1) -> list:
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(BASE_URL, json=test_product.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test product"
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ############################################################
    #  T E S T   C A S E S
    ############################################################
    def test_index(self):
        """It should return the index page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Product Catalog Administration", response.data)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data['message'], 'OK')
   
    def test_read_product(self):
        """It should retrieve a product by its ID"""
        product = self._create_products()[0]
    
        # Get the product by ID
        response = self.client.get(f"{BASE_URL}/{product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        # Check the returned product data
        retrieved_product = response.get_json()
        self.assertEqual(retrieved_product["id"], product.id)
        self.assertEqual(retrieved_product["name"], product.name)
        self.assertEqual(retrieved_product["description"], product.description)
        self.assertEqual(retrieved_product["price"], product.price)
        self.assertEqual(retrieved_product["available"], product.available)
        self.assertEqual(retrieved_product["category"], product.category.name)
      # Test the UPDATE endpoint
      def test_update_product(self):
          """It should update an existing product"""
          product = self._create_products()[0]
      
          # Update the product data
          new_product_data = {
              "name": "Updated Product",
              "description": "A much better product",
              "price": 99.99,
              "available": False,
          }
      
          # Update the product
          response = self.client.put(f"{BASE_URL}/{product.id}", json=new_product_data)
          self.assertEqual(response.status_code, status.HTTP_200_OK)
      
          # Get the updated product
          retrieved_product = response.get_json()
      
          # Check the updated product data
          self.assertEqual(retrieved_product["id"], product.id)
          self.assertEqual(retrieved_product["name"], "Updated Product")
          self.assertEqual(retrieved_product["description"], "A much better product")
          self.assertEqual(retrieved_product["price"], 99.99)
          self.assertEqual(retrieved_product["available"], False)
      # Test the DELETE endpoint
      def test_delete_product(self):
          """It should delete an existing product"""
          product = self._create_products()[0]
      
          # Delete the product
          response = self.client.delete(f"{BASE_URL}/{product.id}")
          self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
      
          # Try to get the deleted product
          response = self.client.get(f"{BASE_URL}/{product.id}")
          self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
      # Test the LIST ALL endpoint
      def test_list_all_products(self):
          """It should retrieve a list of all products"""
          # Create some test products
          products = self._create_products(count=3)
      
          # Get the list of all products
          response = self.client.get(BASE_URL)
          self.assertEqual(response.status_code, status.HTTP_200_OK)
      
          # Check that all products are returned
          product_list = response.get_json()
          self.assertEqual(len(product_list), 3)
      
          # Check that the returned product names match the created ones
          for i, product in enumerate(products):
              self.assertEqual(product_list[i]["name"], product.name)

    
    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_product(self):
        """It should Create a new Product"""
        test_product = ProductFactory()
        logging.debug("Test Product: %s", test_product.serialize())
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(Decimal(new_product["price"]), test_product.price)
        self.assertEqual(new_product["available"], test_product.available)
        self.assertEqual(new_product["category"], test_product.category.name)

        #
        # Uncomment this code once READ is implemented
        #

        # # Check that the location header was correct
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_product = response.get_json()
        # self.assertEqual(new_product["name"], test_product.name)
        # self.assertEqual(new_product["description"], test_product.description)
        # self.assertEqual(Decimal(new_product["price"]), test_product.price)
        # self.assertEqual(new_product["available"], test_product.available)
        # self.assertEqual(new_product["category"], test_product.category.name)

    def test_create_product_with_no_name(self):
        """It should not Create a Product without a name"""
        product = self._create_products()[0]
        new_product = product.serialize()
        del new_product["name"]
        logging.debug("Product no name: %s", new_product)
        response = self.client.post(BASE_URL, json=new_product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        """It should not Create a Product with no Content-Type"""
        response = self.client.post(BASE_URL, data="bad data")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_wrong_content_type(self):
        """It should not Create a Product with wrong Content-Type"""
        response = self.client.post(BASE_URL, data={}, content_type="plain/text")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_get_all_products(self):
        """It should retrieve a list of all products"""
        # Create some test products
        products = self._create_products(count=3)

        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product_list = response.get_json()
        self.assertEqual(len(product_list), 3)  # Ensure all products are returned
        # Check that the returned product names match the created ones
        for i, product in enumerate(products):
            self.assertEqual(product_list[i]["name"], product.name)

    def test_get_product_by_id(self):
        """It should retrieve a product by its ID"""
        product = self._create_products()[0]
        product_id = product.id

        response = self.client.get(f"{BASE_URL}/{product_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        retrieved_product = response.get_json()
        self.assertEqual(retrieved_product["id"], product_id)
        self.assertEqual(retrieved_product["name"], product.name)

    def test_get_product_by_id_not_found(self):
        """It should return a 404 status when trying to retrieve a non-existent product"""
        response = self.client.get(f"{BASE_URL}/1000")  # Assuming product with ID 1000 does not exist
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    # Utility functions
    ######################################################################

    def get_product_count(self):
        """save the current number of products"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        # logging.debug("data = %s", data)
        return len(data)
    
