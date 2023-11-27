######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
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

# spell: ignore Rofrano jsonify restx dbname
"""
Product Store Service with UI
"""
from flask import jsonify, request, abort
from flask import url_for  # noqa: F401 pylint: disable=unused-import
from service.models import Product
from service.common import status  # HTTP Status Codes
from . import app


######################################################################
# H E A L T H   C H E C K
######################################################################
@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# H O M E   P A G E
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# C R E A T E   A   N E W   P R O D U C T
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to Create a Product...")
    check_content_type("application/json")

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    product = Product()
    product.deserialize(data)
    product.create()
    app.logger.info("Product with new id [%s] saved!", product.id)

    message = product.serialize()

    #
    # Uncomment this line of code once you implement READ A PRODUCT
    #
    # location_url = url_for("get_products", product_id=product.id, _external=True)
    location_url = "/"  # delete once READ is implemented
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# L I S T   A L L   P R O D U C T S
######################################################################
@app.route("/products", methods=["GET"])
def get_products():
    """
    Lists all products
    This endpoint will return a list of all products.
    """
    products = []  # Placeholder for listing all products
    return jsonify(products)


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """
    Retrieves a specific product by ID
    This endpoint will return the details of a product based on its ID.
    """

    product = Product.query.get(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND)
    return jsonify(product.serialize())

## UPDATE
```python
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """
    Updates a specific product by ID
    This endpoint will update the details of a product based on its ID.
    """

    check_content_type("application/json")
    data = request.get_json()

    product = Product.query.get(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND)

    product.deserialize(data)
    product.update()

    return jsonify(product.serialize())



@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """
    Deletes a specific product by ID
    This endpoint will delete a product based on its ID.
    """

    product = Product.query.get(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND)

    product.delete()

    return jsonify(status="Product deleted")
@app.route("/products", methods=["GET"])
def get_products():
    """
    Lists all products
    This endpoint will return a list of all products.
    """

    products = Product.query.all()
    return jsonify([product.serialize() for product in products])
@app.route("/products/name/<string:name>", methods=["GET"])
def get_products_by_name(name):
    """
    Lists all products by name
    This endpoint will return a list of all products that match the given name.
    """

    products = Product.query.filter_by(name=name).all()
    return jsonify([product.serialize() for product in products])
@app.route("/products/category/<string:category>", methods=["GET"])
def get_products_by_category(category):
    """
    Lists all products by category
    This endpoint will return a list of all products that match the given category.
    """

    products = Product.query.filter_by(category=category).all()
    return jsonify([product.serialize() for product in products])
@app.route("/products/availability/<bool:availability>", methods=["GET"])
def get_products_by_availability(availability):
    """
    Lists all products by availability
    This endpoint will return a list of all products that match the given availability.
    """

    products = Product.query.filter_by(available=availability).all()
    return jsonify([product.serialize() for product in products])
