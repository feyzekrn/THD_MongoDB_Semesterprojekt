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


def build_product_documents(products, brands, categories, stocks):
    brands_by_id = brands.set_index("brand_id").to_dict("index")
    categories_by_id = categories.set_index("category_id").to_dict("index")

    product_documents = []

    for _, product in products.iterrows():
        product_id = product["product_id"]
        brand_id = product["brand_id"]
        category_id = product["category_id"]

        brand = brands_by_id.get(brand_id)
        category = categories_by_id.get(category_id)

        product_stocks = stocks[stocks["product_id"] == product_id]

        stock_documents = []

        for _, stock in product_stocks.iterrows():
            stock_documents.append(row_to_dict(stock))

        product_document = row_to_dict(product)
        product_document["brand"] = (
            row_to_dict(pd.Series(brand)) if brand is not None else None
        )
        product_document["category"] = (
            row_to_dict(pd.Series(category)) if category is not None else None
        )
        product_document["stocks"] = stock_documents

        product_documents.append(product_document)

    return product_documents


def build_order_documents(orders, order_items, customers, stores, staffs, products):
    customers_by_id = customers.set_index("customer_id").to_dict("index")
    stores_by_id = stores.set_index("store_id").to_dict("index")
    staffs_by_id = staffs.set_index("staff_id").to_dict("index")
    products_by_id = products.set_index("product_id").to_dict("index")

    order_documents = []

    for _, order in orders.iterrows():
        order_id = order["order_id"]

        customer = customers_by_id.get(order["customer_id"])
        store = stores_by_id.get(order["store_id"])
        staff = staffs_by_id.get(order["staff_id"])

        current_order_items = order_items[order_items["order_id"] == order_id]

        item_documents = []

        for _, item in current_order_items.iterrows():
            product = products_by_id.get(item["product_id"])
            item_document = row_to_dict(item)
            item_document["product"] = (
                row_to_dict(pd.Series(product)) if product is not None else None
            )

            item_documents.append(item_document)
        order_document = row_to_dict(order)
        order_document["customer"] = (
            row_to_dict(pd.Series(customer)) if customer is not None else None
        )
        order_document["store"] = (
            row_to_dict(pd.Series(store)) if store is not None else None
        )
        order_document["staff"] = (
            row_to_dict(pd.Series(staff)) if staff is not None else None
        )
        order_document["items"] = item_documents

        order_documents.append(order_document)

    return order_documents


def insert_documents(collection, documents):
    collection.delete_many({})

    if documents:
        collection.insert_many(documents)

    print(f"Inserted {len(documents)} documents into '{collection.name}'.")


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
        staffs=staffs,
        products=products
    )
    print(f"\nCreated order documents: {len(order_documents)}")

    print("\nConnecting to MongoDB...")
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]

    products_collection = db["products"]
    orders_collection = db["orders"]

    print("\nImporting documents into MongoDB...")
    insert_documents(products_collection, product_documents)
    insert_documents(orders_collection, order_documents)

    print("\nCreating indexes...")
    products_collection.create_index("product_id")
    products_collection.create_index("brand.brand_id")
    products_collection.create_index("category.category_id")

    orders_collection.create_index("order_id")
    orders_collection.create_index("customer.customer_id")
    orders_collection.create_index("store.store_id")
    orders_collection.create_index("staff.staff_id")
    orders_collection.create_index("items.product_id")

    client.close()

    print("\nMongoDB import completed.")


if __name__ == "__main__":
    main()