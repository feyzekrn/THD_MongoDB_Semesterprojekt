from pathlib import Path
import json

import pandas as pd
from pymongo import MongoClient


MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = "semesterproject_db2"

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data" / "kaggle_tables"


def read_csv(filename):
    path = DATA_DIR / filename
    print(f"\nReading: {path}")

    df = pd.read_csv(path, low_memory=False)

    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    return df


def clean_value(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


def row_to_dict(row):
    return {
        column: clean_value(row[column])
        for column in row.index
    }


def remove_keys(document, keys):
    for key in keys:
        document.pop(key, None)

    return document


def create_lookup(dataframe, key_column):
    lookup = {}

    for _, row in dataframe.iterrows():
        key = row[key_column]
        lookup[key] = row_to_dict(row)

    return lookup


def build_product_documents(products, brands, categories, stocks):
    brands_by_id = create_lookup(brands, "brand_id")
    categories_by_id = create_lookup(categories, "category_id")

    product_documents = []

    for _, product in products.iterrows():
        product_id = product["product_id"]

        product_document = row_to_dict(product)

        brand = brands_by_id.get(product["brand_id"])
        category = categories_by_id.get(product["category_id"])

        # brand_id and category_id are moved into embedded documents.
        remove_keys(product_document, ["brand_id", "category_id"])

        product_document["brand"] = brand
        product_document["category"] = category

        product_stocks = stocks[stocks["product_id"] == product_id]

        stock_documents = []

        for _, stock in product_stocks.iterrows():
            stock_document = row_to_dict(stock)

            # product_id is already represented by the parent product.
            remove_keys(stock_document, ["product_id"])

            stock_documents.append(stock_document)

        product_document["stocks"] = stock_documents

        product_documents.append(product_document)

    return product_documents


def build_order_documents(orders, order_items, customers, stores, staffs):
    customers_by_id = create_lookup(customers, "customer_id")
    stores_by_id = create_lookup(stores, "store_id")
    staffs_by_id = create_lookup(staffs, "staff_id")

    order_documents = []

    for _, order in orders.iterrows():
        order_id = order["order_id"]

        customer = customers_by_id.get(order["customer_id"])
        store = stores_by_id.get(order["store_id"])
        staff = staffs_by_id.get(order["staff_id"])

        order_document = row_to_dict(order)

        # Foreign keys are moved into embedded documents.
        remove_keys(order_document, ["customer_id", "store_id", "staff_id"])

        order_document["customer"] = customer
        order_document["store"] = store
        order_document["staff"] = staff

        current_order_items = order_items[order_items["order_id"] == order_id]

        item_documents = []

        for _, item in current_order_items.iterrows():
            item_document = row_to_dict(item)

            # order_id is already represented by the parent order.
            # product_id stays as reference to products.product_id.
            remove_keys(item_document, ["order_id"])

            item_documents.append(item_document)

        order_document["items"] = item_documents

        order_documents.append(order_document)

    return order_documents


def replace_collection(db, collection_name, documents):
    db.drop_collection(collection_name)

    collection = db[collection_name]

    if documents:
        collection.insert_many(documents)

    print(f"Inserted {len(documents)} documents into '{collection_name}'.")

    return collection


def create_indexes(products_collection, orders_collection):
    print("\nCreating indexes...")

    # Unique lookup by original SQL primary key
    products_collection.create_index(
        "product_id",
        unique=True,
        name="uq_products_product_id"
    )

    # Product filtering by category and brand
    products_collection.create_index(
        [("category.category_id", 1), ("brand.brand_id", 1)],
        name="idx_products_category_brand"
    )

    # Top-N query: most expensive products
    products_collection.create_index(
        "list_price",
        name="idx_products_list_price"
    )

    # Unique lookup by original SQL primary key
    orders_collection.create_index(
        "order_id",
        unique=True,
        name="uq_orders_order_id"
    )

    # Customer orders in a time range
    orders_collection.create_index(
        [("customer.customer_id", 1), ("order_date", 1)],
        name="idx_orders_customer_date"
    )

    # Store orders in a time range
    orders_collection.create_index(
        [("store.store_id", 1), ("order_date", 1)],
        name="idx_orders_store_date"
    )

    # Orders containing a specific product
    orders_collection.create_index(
        "items.product_id",
        name="idx_orders_items_product"
    )


def main():
    brands = read_csv("brands.csv")
    categories = read_csv("categories.csv")
    customers = read_csv("customers.csv")
    stores = read_csv("stores.csv")
    staffs = read_csv("staffs.csv")
    products = read_csv("products.csv")
    orders = read_csv("orders.csv")
    order_items = read_csv("order_items.csv")
    stocks = read_csv("stocks.csv")

    print("\nBuilding product documents...")

    product_documents = build_product_documents(
        products=products,
        brands=brands,
        categories=categories,
        stocks=stocks
    )

    print(f"\nCreated product documents: {len(product_documents)}")
    print("\nBuilding order documents...")

    order_documents = build_order_documents(
        orders=orders,
        order_items=order_items,
        customers=customers,
        stores=stores,
        staffs=staffs
    )

    print(f"\nCreated order documents: {len(order_documents)}")
    print("\nConnecting to MongoDB...")

    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]

    print("\nImporting documents into MongoDB...")

    products_collection = replace_collection(
        db=db,
        collection_name="products",
        documents=product_documents
    )

    orders_collection = replace_collection(
        db=db,
        collection_name="orders",
        documents=order_documents
    )

    create_indexes(
        products_collection=products_collection,
        orders_collection=orders_collection
    )

    client.close()
    print("\nMongoDB import completed.")

if __name__ == "__main__":
    main()