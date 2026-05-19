# Semester Project Ekren – NoSQL Database Queries
<hr>

## Project Goal

The goal of this project is to transform a relational SQL dataset from Kaggle into a document-based NoSQL data model using MongoDB.
The data is not imported 1:1 as raw CSV files. Instead, a Python script transforms the relational structure and stores the resulting documents in MongoDB.

<hr>

## Dataset Used

**Dataset:** Bike Store Relational Database / SQL Sample Database  
**Source:** Kaggle  
**Kaggle Link:** TODO: Insert link to the used Kaggle dataset

The dataset describes a bike store with customers, orders, products, brands, categories, staff members, stores, and stock information.

## Original Relational Structure

The original dataset consists of several relational tables, including:

- `customers`
- `orders`
- `order_items`
- `products`
- `categories`
- `brands`
- `stores`
- `staffs`
- `stocks`

Important relationships:

- One customer can have multiple orders.
- One order can contain multiple order items.
- One order item references one product.
- One product belongs to one category and one brand.
- One product can have stock quantities in multiple stores.

## Relational ER Diagram
<img src="docs/er_diagram_sql.png" alt="Relational ER Diagram" width="700">

<hr>

## MongoDB Data Model

For MongoDB, the relational structure is transformed into two main collections:

```text
Database: semesterproject_db2

Collections:
- orders
- products
```

### Collection `orders`


The `orders` collection is built from:

- `orders.csv`
- `order_items.csv`
- `customers.csv`
- `stores.csv`
- `staffs.csv`
- `products.csv`

Each order document contains all original columns from the `orders` table. The related customer, store, and staff records are embedded as full nested documents. The related order items are embedded as an array. Each order item preserves all original columns from the `order_items` table and additionally embeds the corresponding full product record.

Example structure:

```json
{
  "order_id": 1,
  "customer_id": 259,
  "order_status": 4,
  "order_date": "2016-01-01",
  "required_date": "2016-01-03",
  "shipped_date": "2016-01-03",
  "store_id": 1,
  "staff_id": 2,
  "customer": {
    "customer_id": 259,
    "first_name": "Example",
    "last_name": "Customer",
    "phone": null,
    "email": "customer@example.com",
    "street": "Example Street",
    "city": "Example City",
    "state": "NY",
    "zip_code": "12345"
  },
  "store": {
    "store_id": 1,
    "store_name": "Example Store",
    "phone": "123456789",
    "email": "store@example.com",
    "street": "Store Street",
    "city": "Store City",
    "state": "CA",
    "zip_code": "90001"
  },
  "staff": {
    "staff_id": 2,
    "first_name": "Example",
    "last_name": "Staff",
    "email": "staff@example.com",
    "phone": "123456789",
    "active": 1,
    "store_id": 1,
    "manager_id": 1
  },
  "items": [
    {
      "order_id": 1,
      "item_id": 1,
      "product_id": 20,
      "quantity": 1,
      "list_price": 599.99,
      "discount": 0.2,
      "product": {
        "product_id": 20,
        "product_name": "Example Product",
        "brand_id": 9,
        "category_id": 6,
        "model_year": 2016,
        "list_price": 599.99
      }
    }
  ]
}
```

### Collection `products`

The `products` collection is built from:

- `products.csv`
- `brands.csv`
- `categories.csv`
- `stocks.csv`

Each product document contains all original columns from the `products` table. Additionally, the related brand and category rows are embedded as full nested documents. Stock rows are embedded as an array.

Example structure:

```json
{
  "product_id": 1,
  "product_name": "Example Product",
  "brand_id": 9,
  "category_id": 6,
  "model_year": 2016,
  "list_price": 379.99,
  "brand": {
    "brand_id": 9,
    "brand_name": "Example Brand"
  },
  "category": {
    "category_id": 6,
    "category_name": "Example Category"
  },
  "stocks": [
    {
      "store_id": 1,
      "product_id": 1,
      "quantity": 27
    }
  ]
}
```

### Index Strategy

Indexes were created for fields that are frequently used in typical query patterns.  
The `product_id` and `order_id` fields are indexed uniquely because they represent the original primary keys.

Additional indexes support relationship-based queries, Top-N queries and aggregation queries:

- products by brand
- products by category
- products by store stock
- orders by customer
- orders by store
- orders by staff
- orders by status
- orders by date
- orders containing a specific product

Compound indexes were added for common combined filters, such as orders per store by date and orders per customer by date.

## Data Transformation

The relational tables are not stored as separate 1:1 MongoDB collections.

Instead, relationships are resolved during the import process and related data is embedded into documents:

- `order_items` is embedded into `orders.items[]`.
- `customers`, `stores`, and `staffs` are embedded into `orders`.
- `brands`, `categories`, and `stocks` are embedded into `products`.

This creates a document-based MongoDB model that supports typical queries without classical SQL joins.

<hr>

## Project Structure

```text
semesterprojekt_ekren/
├── code/
│   ├── queries
│   │   ├── mongodb
│   │   │   └── queries.mongodb
│   │   │
│   │   └── sql_legacydata
│   │       ├── db_relation_setup.sql
│   │       └── db_setup.sql
│   │
│   └── scripts/
│       ├── import_data.py
│       └── requirements.txt
│
├── data/
│   └── kaggle_tables/
│       ├── brands.csv
│       ├── categories.csv
│       ├── customers.csv
│       ├── order_items.csv
│       ├── orders.csv
│       ├── products.csv
│       ├── stocks.csv
│       ├── staffs.csv
│       └── stores.csv
│
├── docs/
│   └── er-diagram_sql.png
│
├── README.md
└── .gitignore
```

<hr>

## Requirements

- Python 3
- Local MongoDB installation
- Python packages from `requirements.txt`

MongoDB runs locally at:

```text
mongodb://localhost:27017
```

## Installation

Go to the scripts folder:

```bash
cd code/scripts
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Run the Import

```bash
python import_data.py
```

The script reads the CSV files from `data/kaggle_tables/`, transforms the relational data, and imports the resulting documents into MongoDB.

<hr>

## Queries

The MongoDB queries will be stored later in:

```text
code/queries/queries.mongodb
```

Planned queries:

1. Show orders with embedded order items
2. Show the top 10 orders by total value
3. Calculate revenue per store
4. Count sold products per category
5. Show products with stock quantities per store

The queries can be executed directly in MongoDB Compass or `mongosh`.
