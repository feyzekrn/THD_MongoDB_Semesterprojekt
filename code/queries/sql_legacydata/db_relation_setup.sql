-- check amount of rows in each table
SELECT 'brands' AS table_name, COUNT(*) AS row_count FROM brands
UNION ALL
SELECT 'categories', COUNT(*) FROM categories
UNION ALL
SELECT 'customers', COUNT(*) FROM customers
UNION ALL
SELECT 'stores', COUNT(*) FROM stores
UNION ALL
SELECT 'staffs', COUNT(*) FROM staffs
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL
SELECT 'stocks', COUNT(*) FROM stocks;

-- check if foreign keys are existing
SELECT
    TABLE_NAME,
    CONSTRAINT_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'semesterproject_db2'
  AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY TABLE_NAME, CONSTRAINT_NAME;

-- create relations
ALTER TABLE staffs
ADD CONSTRAINT fk_staffs_store
FOREIGN KEY (store_id) REFERENCES stores(store_id);

ALTER TABLE staffs
ADD CONSTRAINT fk_staffs_manager
FOREIGN KEY (manager_id) REFERENCES staffs(staff_id);

ALTER TABLE orders
ADD CONSTRAINT fk_orders_customer
FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

ALTER TABLE orders
ADD CONSTRAINT fk_orders_store
FOREIGN KEY (store_id) REFERENCES stores(store_id);

ALTER TABLE orders
ADD CONSTRAINT fk_orders_staff
FOREIGN KEY (staff_id) REFERENCES staffs(staff_id);

ALTER TABLE order_items
ADD CONSTRAINT fk_order_items_order
FOREIGN KEY (order_id) REFERENCES orders(order_id);

ALTER TABLE order_items
ADD CONSTRAINT fk_order_items_product
FOREIGN KEY (product_id) REFERENCES products(product_id);

ALTER TABLE stocks
ADD CONSTRAINT fk_stocks_store
FOREIGN KEY (store_id) REFERENCES stores(store_id);

ALTER TABLE stocks
ADD CONSTRAINT fk_stocks_product
FOREIGN KEY (product_id) REFERENCES products(product_id);