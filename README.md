# Semester Project Ekren – NoSQL Database Queries

## Project Goal

The goal of this project is to transform a relational SQL dataset from Kaggle into a document-based NoSQL data model using MongoDB.
The data is not imported 1:1 as raw CSV files. Instead, a Python script transforms the relational structure and stores the resulting documents in MongoDB.

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
[Relational ER Diagram](docs/er_diagram_sql.png)

## Project Structure

```text
semesterprojekt_ekren/
├── code/
│   ├── scripts/
│   │   ├── import_data.py
│   │   └── requirements.txt
│   │
│   └── queries/
│       └── queries.mongodb
│
├── data/
│   └── kaggle_tables/
│       ├── customers.csv
│       ├── orders.csv
│       ├── order_items.csv
│       ├── products.csv
│       ├── categories.csv
│       ├── brands.csv
│       ├── stores.csv
│       ├── staffs.csv
│       └── stocks.csv
│
├── docs/
│   └── er-diagram_sql.png
│
├── README.md
└── .gitignore
```

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
