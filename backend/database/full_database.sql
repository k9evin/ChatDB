PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE departments (
                dept_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                budget DECIMAL(12, 2) NOT NULL,
                manager_id INTEGER,
                created_at DATE NOT NULL
            );
INSERT INTO departments VALUES(1,'Sales','New York',500000,1,'2023-01-01');
INSERT INTO departments VALUES(2,'Marketing','San Francisco',300000,6,'2023-01-01');
INSERT INTO departments VALUES(3,'Engineering','Seattle',800000,9,'2023-01-01');
INSERT INTO departments VALUES(4,'Customer Support','Austin',200000,14,'2023-01-01');
INSERT INTO departments VALUES(5,'Finance','New York',250000,17,'2023-01-01');
INSERT INTO departments VALUES(6,'Operations','Chicago',400000,19,'2023-01-01');
CREATE TABLE employees (
                emp_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                hire_date DATE NOT NULL,
                salary DECIMAL(10, 2) NOT NULL,
                dept_id INTEGER,
                manager_id INTEGER,
                job_title TEXT NOT NULL,
                FOREIGN KEY (dept_id) REFERENCES departments(dept_id),
                FOREIGN KEY (manager_id) REFERENCES employees(emp_id)
            );
INSERT INTO employees VALUES(1,'John','Anderson','john.anderson@company.com','555-0101','2020-01-15',120000,1,NULL,'VP of Sales');
INSERT INTO employees VALUES(2,'Sarah','Martinez','sarah.martinez@company.com','555-0102','2020-03-20',95000,1,1,'Sales Manager');
INSERT INTO employees VALUES(3,'Michael','Chen','michael.chen@company.com','555-0103','2021-05-10',75000,1,2,'Sales Representative');
INSERT INTO employees VALUES(4,'Emily','Johnson','emily.johnson@company.com','555-0104','2021-06-15',72000,1,2,'Sales Representative');
INSERT INTO employees VALUES(5,'David','Williams','david.williams@company.com','555-0105','2022-02-01',68000,1,2,'Sales Representative');
INSERT INTO employees VALUES(6,'Lisa','Brown','lisa.brown@company.com','555-0106','2019-11-01',110000,2,NULL,'Marketing Director');
INSERT INTO employees VALUES(7,'Robert','Taylor','robert.taylor@company.com','555-0107','2021-08-20',85000,2,6,'Marketing Manager');
INSERT INTO employees VALUES(8,'Jennifer','Davis','jennifer.davis@company.com','555-0108','2022-01-10',70000,2,7,'Marketing Specialist');
INSERT INTO employees VALUES(9,'James','Wilson','james.wilson@company.com','555-0109','2018-06-01',140000,3,NULL,'CTO');
INSERT INTO employees VALUES(10,'Patricia','Moore','patricia.moore@company.com','555-0110','2019-03-15',115000,3,9,'Engineering Manager');
INSERT INTO employees VALUES(11,'Richard','Jackson','richard.jackson@company.com','555-0111','2020-09-01',95000,3,10,'Senior Engineer');
INSERT INTO employees VALUES(12,'Linda','White','linda.white@company.com','555-0112','2021-04-01',85000,3,10,'Software Engineer');
INSERT INTO employees VALUES(13,'Thomas','Harris','thomas.harris@company.com','555-0113','2022-07-01',75000,3,10,'Junior Engineer');
INSERT INTO employees VALUES(14,'Barbara','Martin','barbara.martin@company.com','555-0114','2020-02-10',90000,4,NULL,'Support Manager');
INSERT INTO employees VALUES(15,'Charles','Thompson','charles.thompson@company.com','555-0115','2021-10-01',60000,4,14,'Support Specialist');
INSERT INTO employees VALUES(16,'Susan','Garcia','susan.garcia@company.com','555-0116','2022-03-15',58000,4,14,'Support Specialist');
INSERT INTO employees VALUES(17,'Joseph','Martinez','joseph.martinez@company.com','555-0117','2019-05-01',100000,5,NULL,'Finance Director');
INSERT INTO employees VALUES(18,'Jessica','Robinson','jessica.robinson@company.com','555-0118','2021-01-20',75000,5,17,'Financial Analyst');
INSERT INTO employees VALUES(19,'Daniel','Clark','daniel.clark@company.com','555-0119','2020-08-01',88000,6,NULL,'Operations Manager');
INSERT INTO employees VALUES(20,'Karen','Rodriguez','karen.rodriguez@company.com','555-0120','2021-11-01',65000,6,19,'Operations Coordinator');
CREATE TABLE customer_segments (
                segment_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                discount_rate DECIMAL(5, 2) DEFAULT 0.00
            );
INSERT INTO customer_segments VALUES(1,'VIP','Very Important Customers with high lifetime value',15);
INSERT INTO customer_segments VALUES(2,'Premium','Regular high-value customers',10);
INSERT INTO customer_segments VALUES(3,'Standard','Regular customers',5);
INSERT INTO customer_segments VALUES(4,'New','Newly registered customers',0);
CREATE TABLE customers (
                customer_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                date_of_birth DATE,
                registration_date DATE NOT NULL,
                segment_id INTEGER,
                total_spent DECIMAL(12, 2) DEFAULT 0.00,
                loyalty_points INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (segment_id) REFERENCES customer_segments(segment_id)
            );
INSERT INTO customers VALUES(1,'Alice','Johnson','alice.johnson@email.com','555-1001','1985-03-15','2023-01-10',1,15450,15450,'active');
INSERT INTO customers VALUES(2,'Bob','Smith','bob.smith@email.com','555-1002','1990-07-22','2023-02-15',2,8750,8750,'active');
INSERT INTO customers VALUES(3,'Carol','White','carol.white@email.com','555-1003','1988-11-08','2023-03-01',2,9200,9200,'active');
INSERT INTO customers VALUES(4,'David','Brown','david.brown@email.com','555-1004','1992-05-30','2023-04-05',3,3200,3200,'active');
INSERT INTO customers VALUES(5,'Eva','Davis','eva.davis@email.com','555-1005','1987-09-12','2023-05-12',1,12800,12800,'active');
INSERT INTO customers VALUES(6,'Frank','Miller','frank.miller@email.com','555-1006','1995-01-25','2023-06-20',3,2100,2100,'active');
INSERT INTO customers VALUES(7,'Grace','Wilson','grace.wilson@email.com','555-1007','1991-12-03','2023-07-08',2,6800,6800,'active');
INSERT INTO customers VALUES(8,'Henry','Moore','henry.moore@email.com','555-1008','1989-04-18','2023-08-15',3,4500,4500,'active');
INSERT INTO customers VALUES(9,'Iris','Taylor','iris.taylor@email.com','555-1009','1993-08-07','2023-09-22',4,850,850,'active');
INSERT INTO customers VALUES(10,'Jack','Anderson','jack.anderson@email.com','555-1010','1986-10-14','2023-10-05',1,11200,11200,'active');
INSERT INTO customers VALUES(11,'Kate','Thomas','kate.thomas@email.com','555-1011','1994-02-28','2023-10-18',4,1200,1200,'active');
INSERT INTO customers VALUES(12,'Leo','Jackson','leo.jackson@email.com','555-1012','1990-06-11','2023-11-01',3,3800,3800,'active');
INSERT INTO customers VALUES(13,'Mia','Harris','mia.harris@email.com','555-1013','1988-03-19','2022-12-10',2,7600,7600,'active');
INSERT INTO customers VALUES(14,'Noah','Martin','noah.martin@email.com','555-1014','1992-09-05','2023-01-25',3,2900,2900,'active');
INSERT INTO customers VALUES(15,'Olivia','Garcia','olivia.garcia@email.com','555-1015','1987-11-21','2023-02-08',2,8100,8100,'active');
CREATE TABLE customer_addresses (
                address_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                address_type TEXT NOT NULL,
                street TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                zip_code TEXT NOT NULL,
                country TEXT DEFAULT 'USA',
                is_default INTEGER DEFAULT 0,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
INSERT INTO customer_addresses VALUES(1,1,'Home','123 Main St','New York','NY','10001','USA',1);
INSERT INTO customer_addresses VALUES(2,1,'Work','456 Business Ave','New York','NY','10002','USA',0);
INSERT INTO customer_addresses VALUES(3,2,'Home','789 Oak Rd','Los Angeles','CA','90001','USA',1);
INSERT INTO customer_addresses VALUES(4,3,'Home','321 Pine St','Chicago','IL','60601','USA',1);
INSERT INTO customer_addresses VALUES(5,4,'Home','654 Elm Dr','Houston','TX','77001','USA',1);
INSERT INTO customer_addresses VALUES(6,5,'Home','987 Maple Ave','Phoenix','AZ','85001','USA',1);
INSERT INTO customer_addresses VALUES(7,6,'Home','147 Cedar Ln','Philadelphia','PA','19101','USA',1);
INSERT INTO customer_addresses VALUES(8,7,'Home','258 Birch St','San Antonio','TX','78201','USA',1);
INSERT INTO customer_addresses VALUES(9,8,'Home','369 Spruce Way','San Diego','CA','92101','USA',1);
INSERT INTO customer_addresses VALUES(10,9,'Home','741 Willow Blvd','Dallas','TX','75201','USA',1);
INSERT INTO customer_addresses VALUES(11,10,'Home','852 Cherry Ct','San Jose','CA','95101','USA',1);
INSERT INTO customer_addresses VALUES(12,11,'Home','963 Ash Pl','Austin','TX','78701','USA',1);
INSERT INTO customer_addresses VALUES(13,12,'Home','159 Poplar Rd','Jacksonville','FL','32201','USA',1);
INSERT INTO customer_addresses VALUES(14,13,'Home','357 Hickory Dr','Fort Worth','TX','76101','USA',1);
INSERT INTO customer_addresses VALUES(15,14,'Home','468 Sycamore St','Columbus','OH','43201','USA',1);
INSERT INTO customer_addresses VALUES(16,15,'Home','579 Walnut Ave','Charlotte','NC','28201','USA',1);
CREATE TABLE categories (
                category_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                parent_category_id INTEGER,
                description TEXT,
                FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
            );
INSERT INTO categories VALUES(1,'Electronics',NULL,'Electronic devices and accessories');
INSERT INTO categories VALUES(2,'Computers',1,'Desktop and laptop computers');
INSERT INTO categories VALUES(3,'Accessories',1,'Computer and device accessories');
INSERT INTO categories VALUES(4,'Furniture',NULL,'Office and home furniture');
INSERT INTO categories VALUES(5,'Office Furniture',4,'Furniture for office use');
INSERT INTO categories VALUES(6,'Home Furniture',4,'Furniture for home use');
INSERT INTO categories VALUES(7,'Stationery',NULL,'Office and school supplies');
INSERT INTO categories VALUES(8,'Writing Tools',7,'Pens, pencils, and markers');
INSERT INTO categories VALUES(9,'Paper Products',7,'Notebooks, paper, and pads');
CREATE TABLE suppliers (
                supplier_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                contact_name TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                city TEXT,
                country TEXT,
                rating DECIMAL(3, 2) DEFAULT 0.00
            );
INSERT INTO suppliers VALUES(1,'TechSupply Co','John Supplier','contact@techsupply.com','555-2001','100 Tech Blvd','San Jose','USA',4.799999999999999823);
INSERT INTO suppliers VALUES(2,'Global Electronics','Sarah Vendor','sales@globalelec.com','555-2002','200 Electronic Way','Shenzhen','China',4.5);
INSERT INTO suppliers VALUES(3,'Office Depot Wholesale','Mike Wholesale','b2b@officedepot.com','555-2003','300 Office Park','Atlanta','USA',4.599999999999999644);
INSERT INTO suppliers VALUES(4,'Furniture Plus','Lisa Furniture','info@furnitureplus.com','555-2004','400 Furniture Ave','High Point','USA',4.700000000000000177);
INSERT INTO suppliers VALUES(5,'Stationery World','Tom Stationery','orders@stationeryworld.com','555-2005','500 Paper St','Portland','USA',4.400000000000000356);
CREATE TABLE products (
                product_id INTEGER PRIMARY KEY,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                category_id INTEGER,
                base_price DECIMAL(10, 2) NOT NULL,
                cost_price DECIMAL(10, 2) NOT NULL,
                stock_quantity INTEGER DEFAULT 0,
                reorder_level INTEGER DEFAULT 10,
                weight_kg DECIMAL(8, 2),
                dimensions TEXT,
                status TEXT DEFAULT 'active',
                created_at DATE NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(category_id)
            );
INSERT INTO products VALUES(1,'LAPTOP-PRO-001','Laptop Pro 15"','High-performance laptop with 16GB RAM',2,1299.990000000000009,900,25,10,2.100000000000000088,'35x24x2 cm','active','2023-01-01');
INSERT INTO products VALUES(2,'LAPTOP-STD-001','Laptop Standard 14"','Standard laptop with 8GB RAM',2,799.990000000000009,550,40,15,1.800000000000000044,'33x22x2 cm','active','2023-01-01');
INSERT INTO products VALUES(3,'MOUSE-WIRELESS-001','Wireless Mouse Pro','Ergonomic wireless mouse',3,29.98999999999999844,12,150,50,0.1000000000000000055,'12x6x4 cm','active','2023-01-01');
INSERT INTO products VALUES(4,'KEYBOARD-MECH-001','Mechanical Keyboard','RGB mechanical keyboard',3,89.98999999999999489,45,80,30,0.8000000000000000444,'44x13x3 cm','active','2023-01-01');
INSERT INTO products VALUES(5,'MONITOR-27-001','27" 4K Monitor','Ultra HD 4K monitor',3,399.990000000000009,250,35,15,6.5,'61x36x5 cm','active','2023-01-01');
INSERT INTO products VALUES(6,'CHAIR-ERG-001','Ergonomic Office Chair','Adjustable ergonomic office chair',5,299.990000000000009,180,45,20,15,'65x65x120 cm','active','2023-01-01');
INSERT INTO products VALUES(7,'DESK-STAND-001','Standing Desk','Electric height-adjustable desk',5,599.990000000000009,380,20,10,35,'120x60x75 cm','active','2023-01-01');
INSERT INTO products VALUES(8,'LAMP-DESK-001','LED Desk Lamp','Adjustable LED desk lamp',5,49.99000000000000198,25,100,40,0.5,'30x15x45 cm','active','2023-01-01');
INSERT INTO products VALUES(9,'SOFA-OFFICE-001','Office Sofa','Comfortable office waiting area sofa',5,799.990000000000009,500,12,5,45,'200x90x85 cm','active','2023-01-01');
INSERT INTO products VALUES(10,'PEN-SET-001','Premium Pen Set','Set of 3 premium ballpoint pens',8,19.98999999999999843,8,200,80,0.1000000000000000055,'15x3x2 cm','active','2023-01-01');
INSERT INTO products VALUES(11,'NOTEBOOK-A4-001','A4 Notebook Set','Set of 5 A4 notebooks',9,24.98999999999999844,10,300,100,0.8000000000000000444,'21x30x5 cm','active','2023-01-01');
INSERT INTO products VALUES(12,'MARKER-SET-001','Marker Set 12pc','Set of 12 colored markers',8,14.99000000000000021,6,250,100,0.2000000000000000111,'15x10x2 cm','active','2023-01-01');
INSERT INTO products VALUES(13,'TABLET-PRO-001','Tablet Pro 12"','Professional tablet with stylus',2,899.990000000000009,600,30,15,0.5999999999999999778,'28x20x1 cm','active','2023-01-01');
INSERT INTO products VALUES(14,'HEADPHONE-WIRELESS-001','Wireless Headphones','Noise-cancelling wireless headphones',3,199.990000000000009,120,60,25,0.2999999999999999889,'20x20x8 cm','active','2023-01-01');
INSERT INTO products VALUES(15,'WEBCAM-HD-001','HD Webcam','1080p HD webcam',3,79.98999999999999489,40,90,35,0.2000000000000000111,'10x5x5 cm','active','2023-01-01');
CREATE TABLE product_suppliers (
                id INTEGER PRIMARY KEY,
                product_id INTEGER NOT NULL,
                supplier_id INTEGER NOT NULL,
                supplier_price DECIMAL(10, 2) NOT NULL,
                lead_time_days INTEGER,
                is_primary INTEGER DEFAULT 0,
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
                UNIQUE(product_id, supplier_id)
            );
INSERT INTO product_suppliers VALUES(1,1,1,900,14,1);
INSERT INTO product_suppliers VALUES(2,1,2,920,21,0);
INSERT INTO product_suppliers VALUES(3,2,1,550,14,1);
INSERT INTO product_suppliers VALUES(4,2,2,570,21,0);
INSERT INTO product_suppliers VALUES(5,3,1,12,7,1);
INSERT INTO product_suppliers VALUES(6,3,2,11.5,14,0);
INSERT INTO product_suppliers VALUES(7,4,1,45,10,1);
INSERT INTO product_suppliers VALUES(8,5,1,250,14,1);
INSERT INTO product_suppliers VALUES(9,6,4,180,21,1);
INSERT INTO product_suppliers VALUES(10,7,4,380,28,1);
INSERT INTO product_suppliers VALUES(11,8,3,25,7,1);
INSERT INTO product_suppliers VALUES(12,9,4,500,30,1);
INSERT INTO product_suppliers VALUES(13,10,5,8,5,1);
INSERT INTO product_suppliers VALUES(14,11,5,10,7,1);
INSERT INTO product_suppliers VALUES(15,12,5,6,5,1);
INSERT INTO product_suppliers VALUES(16,13,1,600,14,1);
INSERT INTO product_suppliers VALUES(17,14,1,120,10,1);
INSERT INTO product_suppliers VALUES(18,15,1,40,7,1);
CREATE TABLE inventory_transactions (
                transaction_id INTEGER PRIMARY KEY,
                product_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_cost DECIMAL(10, 2),
                transaction_date TIMESTAMP NOT NULL,
                reference_type TEXT,
                reference_id INTEGER,
                notes TEXT,
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );
INSERT INTO inventory_transactions VALUES(1,1,'purchase',30,900,'2024-01-01 10:00:00','purchase_order',101,'Initial stock');
INSERT INTO inventory_transactions VALUES(2,2,'purchase',50,550,'2024-01-01 10:00:00','purchase_order',102,'Initial stock');
INSERT INTO inventory_transactions VALUES(3,1,'sale',-1,1299.990000000000009,'2024-01-15 10:30:00','order',1,'Order ORD-2024-001');
INSERT INTO inventory_transactions VALUES(4,3,'sale',-2,29.98999999999999844,'2024-01-15 10:30:00','order',1,'Order ORD-2024-001');
INSERT INTO inventory_transactions VALUES(5,6,'purchase',50,180,'2024-01-05 14:00:00','purchase_order',103,'Restock');
INSERT INTO inventory_transactions VALUES(6,6,'sale',-1,299.990000000000009,'2024-01-20 14:20:00','order',2,'Order ORD-2024-002');
INSERT INTO inventory_transactions VALUES(7,1,'sale',-1,1299.990000000000009,'2024-02-10 11:45:00','order',4,'Order ORD-2024-004');
INSERT INTO inventory_transactions VALUES(8,7,'purchase',25,380,'2024-02-01 09:00:00','purchase_order',104,'New product');
INSERT INTO inventory_transactions VALUES(9,7,'sale',-1,599.990000000000009,'2024-02-15 16:30:00','order',5,'Order ORD-2024-005');
INSERT INTO inventory_transactions VALUES(10,5,'purchase',40,250,'2024-02-20 11:00:00','purchase_order',105,'Restock');
INSERT INTO inventory_transactions VALUES(11,5,'sale',-1,399.990000000000009,'2024-03-01 13:20:00','order',6,'Order ORD-2024-006');
INSERT INTO inventory_transactions VALUES(12,1,'sale',-1,1299.990000000000009,'2024-03-15 12:00:00','order',10,'Order ORD-2024-010');
INSERT INTO inventory_transactions VALUES(13,13,'purchase',35,600,'2024-03-01 10:00:00','purchase_order',106,'New product');
INSERT INTO inventory_transactions VALUES(14,13,'sale',-1,899.990000000000009,'2024-03-12 09:30:00','order',9,'Order ORD-2024-009');
INSERT INTO inventory_transactions VALUES(15,2,'purchase',45,550,'2024-04-01 09:00:00','purchase_order',107,'Restock');
INSERT INTO inventory_transactions VALUES(16,2,'sale',-1,799.990000000000009,'2024-05-01 15:15:00','order',20,'Order ORD-2024-020');
CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY,
                order_number TEXT UNIQUE NOT NULL,
                customer_id INTEGER NOT NULL,
                order_date DATE NOT NULL,
                ship_date DATE,
                delivery_date DATE,
                status TEXT NOT NULL,
                subtotal DECIMAL(10, 2) NOT NULL,
                tax_amount DECIMAL(10, 2) DEFAULT 0.00,
                shipping_cost DECIMAL(10, 2) DEFAULT 0.00,
                discount_amount DECIMAL(10, 2) DEFAULT 0.00,
                total_amount DECIMAL(10, 2) NOT NULL,
                payment_method TEXT,
                shipping_address_id INTEGER,
                sales_rep_id INTEGER,
                notes TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                FOREIGN KEY (shipping_address_id) REFERENCES customer_addresses(address_id),
                FOREIGN KEY (sales_rep_id) REFERENCES employees(emp_id)
            );
INSERT INTO orders VALUES(1,'ORD-2024-001',1,'2024-01-15','2024-01-16','2024-01-18','completed',1329.980000000000018,106.4000000000000056,25,199.5,1261.880000000000109,'credit_card',1,3,NULL);
INSERT INTO orders VALUES(2,'ORD-2024-002',2,'2024-01-20','2024-01-21','2024-01-23','completed',299.990000000000009,24,15,30,308.990000000000009,'credit_card',3,4,NULL);
INSERT INTO orders VALUES(3,'ORD-2024-003',1,'2024-02-05','2024-02-06','2024-02-08','completed',89.98999999999999489,7.200000000000000177,10,0,107.1899999999999978,'paypal',1,3,NULL);
INSERT INTO orders VALUES(4,'ORD-2024-004',3,'2024-02-10','2024-02-11','2024-02-13','completed',1299.990000000000009,104,30,130,1303.990000000000009,'credit_card',4,5,NULL);
INSERT INTO orders VALUES(5,'ORD-2024-005',5,'2024-02-15','2024-02-16','2024-02-18','completed',599.990000000000009,48,25,60,612.990000000000009,'credit_card',6,3,NULL);
INSERT INTO orders VALUES(6,'ORD-2024-006',2,'2024-03-01','2024-03-02','2024-03-04','completed',399.990000000000009,32,20,40,411.990000000000009,'credit_card',3,4,NULL);
INSERT INTO orders VALUES(7,'ORD-2024-007',7,'2024-03-05','2024-03-06','2024-03-08','completed',199.990000000000009,16,15,20,210.990000000000009,'paypal',8,5,NULL);
INSERT INTO orders VALUES(8,'ORD-2024-008',4,'2024-03-10','2024-03-11',NULL,'shipped',49.99000000000000198,4,10,0,63.99000000000000198,'credit_card',5,3,NULL);
INSERT INTO orders VALUES(9,'ORD-2024-009',1,'2024-03-12',NULL,NULL,'processing',899.990000000000009,72,30,135,866.990000000000009,'credit_card',1,3,NULL);
INSERT INTO orders VALUES(10,'ORD-2024-010',10,'2024-03-15','2024-03-16','2024-03-18','completed',1299.990000000000009,104,30,195,1238.990000000000009,'credit_card',11,4,NULL);
INSERT INTO orders VALUES(11,'ORD-2024-011',13,'2024-03-20','2024-03-21','2024-03-23','completed',79.98999999999999489,6.400000000000000355,10,8,88.39000000000000056,'paypal',14,5,NULL);
INSERT INTO orders VALUES(12,'ORD-2024-012',15,'2024-03-25','2024-03-26','2024-03-28','completed',299.990000000000009,24,20,30,313.990000000000009,'credit_card',16,3,NULL);
INSERT INTO orders VALUES(13,'ORD-2024-013',8,'2024-04-01','2024-04-02','2024-04-04','completed',799.990000000000009,64,35,80,818.990000000000009,'credit_card',9,4,NULL);
INSERT INTO orders VALUES(14,'ORD-2024-014',12,'2024-04-05','2024-04-06',NULL,'shipped',24.98999999999999844,2,8,0,34.99000000000000198,'paypal',13,5,NULL);
INSERT INTO orders VALUES(15,'ORD-2024-015',6,'2024-04-10',NULL,NULL,'pending',14.99000000000000021,1.199999999999999956,8,0,24.19000000000000127,'credit_card',7,3,NULL);
INSERT INTO orders VALUES(16,'ORD-2024-016',5,'2024-04-12','2024-04-13','2024-04-15','completed',399.990000000000009,32,20,60,391.990000000000009,'credit_card',6,4,NULL);
INSERT INTO orders VALUES(17,'ORD-2024-017',3,'2024-04-15','2024-04-16','2024-04-18','completed',89.98999999999999489,7.200000000000000177,10,9,98.1899999999999978,'paypal',4,5,NULL);
INSERT INTO orders VALUES(18,'ORD-2024-018',11,'2024-04-20','2024-04-21','2024-04-23','completed',19.98999999999999843,1.600000000000000088,8,0,29.58999999999999986,'credit_card',12,3,NULL);
INSERT INTO orders VALUES(19,'ORD-2024-019',14,'2024-04-25','2024-04-26','2024-04-28','completed',199.990000000000009,16,15,20,210.990000000000009,'credit_card',15,4,NULL);
INSERT INTO orders VALUES(20,'ORD-2024-020',7,'2024-05-01','2024-05-02','2024-05-04','completed',799.990000000000009,64,30,80,813.990000000000009,'credit_card',8,5,NULL);
CREATE TABLE order_items (
                item_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10, 2) NOT NULL,
                discount_percent DECIMAL(5, 2) DEFAULT 0.00,
                line_total DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );
INSERT INTO order_items VALUES(1,1,1,1,1299.990000000000009,15,1104.990000000000009);
INSERT INTO order_items VALUES(2,1,3,2,29.98999999999999844,0,59.97999999999999688);
INSERT INTO order_items VALUES(3,1,8,1,49.99000000000000198,0,49.99000000000000198);
INSERT INTO order_items VALUES(4,1,10,1,19.98999999999999843,0,19.98999999999999843);
INSERT INTO order_items VALUES(5,2,6,1,299.990000000000009,10,269.990000000000009);
INSERT INTO order_items VALUES(6,2,8,1,49.99000000000000198,0,49.99000000000000198);
INSERT INTO order_items VALUES(7,3,4,1,89.98999999999999489,0,89.98999999999999489);
INSERT INTO order_items VALUES(8,4,1,1,1299.990000000000009,10,1169.990000000000009);
INSERT INTO order_items VALUES(9,4,5,1,399.990000000000009,0,399.990000000000009);
INSERT INTO order_items VALUES(10,5,7,1,599.990000000000009,10,539.990000000000009);
INSERT INTO order_items VALUES(11,5,8,1,49.99000000000000198,0,49.99000000000000198);
INSERT INTO order_items VALUES(12,6,5,1,399.990000000000009,10,359.990000000000009);
INSERT INTO order_items VALUES(13,6,3,1,29.98999999999999844,0,29.98999999999999844);
INSERT INTO order_items VALUES(14,7,14,1,199.990000000000009,10,179.990000000000009);
INSERT INTO order_items VALUES(15,7,3,1,29.98999999999999844,0,29.98999999999999844);
INSERT INTO order_items VALUES(16,8,8,1,49.99000000000000198,0,49.99000000000000198);
INSERT INTO order_items VALUES(17,9,13,1,899.990000000000009,15,764.990000000000009);
INSERT INTO order_items VALUES(18,9,15,1,79.98999999999999489,0,79.98999999999999489);
INSERT INTO order_items VALUES(19,10,1,1,1299.990000000000009,15,1104.990000000000009);
INSERT INTO order_items VALUES(20,10,3,2,29.98999999999999844,0,59.97999999999999688);
INSERT INTO order_items VALUES(21,10,4,1,89.98999999999999489,0,89.98999999999999489);
INSERT INTO order_items VALUES(22,11,15,1,79.98999999999999489,10,71.98999999999999489);
INSERT INTO order_items VALUES(23,11,3,1,29.98999999999999844,0,29.98999999999999844);
INSERT INTO order_items VALUES(24,12,6,1,299.990000000000009,10,269.990000000000009);
INSERT INTO order_items VALUES(25,12,8,1,49.99000000000000198,0,49.99000000000000198);
INSERT INTO order_items VALUES(26,13,9,1,799.990000000000009,10,719.990000000000009);
INSERT INTO order_items VALUES(27,13,8,1,49.99000000000000198,0,49.99000000000000198);
INSERT INTO order_items VALUES(28,14,11,1,24.98999999999999844,0,24.98999999999999844);
INSERT INTO order_items VALUES(29,15,12,1,14.99000000000000021,0,14.99000000000000021);
INSERT INTO order_items VALUES(30,16,5,1,399.990000000000009,15,339.990000000000009);
INSERT INTO order_items VALUES(31,16,3,1,29.98999999999999844,0,29.98999999999999844);
INSERT INTO order_items VALUES(32,17,4,1,89.98999999999999489,10,80.98999999999999489);
INSERT INTO order_items VALUES(33,17,3,1,29.98999999999999844,0,29.98999999999999844);
INSERT INTO order_items VALUES(34,18,10,1,19.98999999999999843,0,19.98999999999999843);
INSERT INTO order_items VALUES(35,19,14,1,199.990000000000009,10,179.990000000000009);
INSERT INTO order_items VALUES(36,19,3,1,29.98999999999999844,0,29.98999999999999844);
INSERT INTO order_items VALUES(37,20,2,1,799.990000000000009,10,719.990000000000009);
INSERT INTO order_items VALUES(38,20,3,1,29.98999999999999844,0,29.98999999999999844);
INSERT INTO order_items VALUES(39,20,4,1,89.98999999999999489,0,89.98999999999999489);
CREATE TABLE payments (
                payment_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                payment_date TIMESTAMP NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                payment_method TEXT NOT NULL,
                transaction_id TEXT,
                status TEXT NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            );
INSERT INTO payments VALUES(1,1,'2024-01-15 10:30:00',1261.880000000000109,'credit_card','TXN-001','completed');
INSERT INTO payments VALUES(2,2,'2024-01-20 14:20:00',308.990000000000009,'credit_card','TXN-002','completed');
INSERT INTO payments VALUES(3,3,'2024-02-05 09:15:00',107.1899999999999978,'paypal','PP-001','completed');
INSERT INTO payments VALUES(4,4,'2024-02-10 11:45:00',1303.990000000000009,'credit_card','TXN-003','completed');
INSERT INTO payments VALUES(5,5,'2024-02-15 16:30:00',612.990000000000009,'credit_card','TXN-004','completed');
INSERT INTO payments VALUES(6,6,'2024-03-01 13:20:00',411.990000000000009,'credit_card','TXN-005','completed');
INSERT INTO payments VALUES(7,7,'2024-03-05 10:10:00',210.990000000000009,'paypal','PP-002','completed');
INSERT INTO payments VALUES(8,8,'2024-03-10 15:00:00',63.99000000000000198,'credit_card','TXN-006','completed');
INSERT INTO payments VALUES(9,9,'2024-03-12 09:30:00',866.990000000000009,'credit_card','TXN-007','pending');
INSERT INTO payments VALUES(10,10,'2024-03-15 12:00:00',1238.990000000000009,'credit_card','TXN-008','completed');
INSERT INTO payments VALUES(11,11,'2024-03-20 14:15:00',88.39000000000000056,'paypal','PP-003','completed');
INSERT INTO payments VALUES(12,12,'2024-03-25 10:45:00',313.990000000000009,'credit_card','TXN-009','completed');
INSERT INTO payments VALUES(13,13,'2024-04-01 11:20:00',818.990000000000009,'credit_card','TXN-010','completed');
INSERT INTO payments VALUES(14,14,'2024-04-05 13:30:00',34.99000000000000198,'paypal','PP-004','completed');
INSERT INTO payments VALUES(15,15,'2024-04-10 09:00:00',24.19000000000000127,'credit_card','TXN-011','pending');
INSERT INTO payments VALUES(16,16,'2024-04-12 16:45:00',391.990000000000009,'credit_card','TXN-012','completed');
INSERT INTO payments VALUES(17,17,'2024-04-15 10:20:00',98.1899999999999978,'paypal','PP-005','completed');
INSERT INTO payments VALUES(18,18,'2024-04-20 14:00:00',29.58999999999999986,'credit_card','TXN-013','completed');
INSERT INTO payments VALUES(19,19,'2024-04-25 11:30:00',210.990000000000009,'credit_card','TXN-014','completed');
INSERT INTO payments VALUES(20,20,'2024-05-01 15:15:00',813.990000000000009,'credit_card','TXN-015','completed');
CREATE TABLE refunds (
                refund_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                refund_date DATE NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                reason TEXT,
                status TEXT NOT NULL,
                processed_by INTEGER,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (processed_by) REFERENCES employees(emp_id)
            );
INSERT INTO refunds VALUES(1,2,'2024-01-25',299.990000000000009,'Product defect','completed',18);
INSERT INTO refunds VALUES(2,7,'2024-03-10',199.990000000000009,'Customer request','completed',18);
INSERT INTO refunds VALUES(3,11,'2024-03-25',79.98999999999999489,'Wrong item shipped','processing',18);
CREATE TABLE order_reviews (
                review_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                review_text TEXT,
                review_date DATE NOT NULL,
                helpful_count INTEGER DEFAULT 0,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
INSERT INTO order_reviews VALUES(1,1,1,5,'Excellent product, fast shipping!','2024-01-20',12);
INSERT INTO order_reviews VALUES(2,2,2,4,'Good quality, would buy again','2024-01-25',5);
INSERT INTO order_reviews VALUES(3,4,3,5,'Perfect! Exceeded expectations','2024-02-15',8);
INSERT INTO order_reviews VALUES(4,5,5,4,'Great desk, easy to assemble','2024-02-20',3);
INSERT INTO order_reviews VALUES(5,6,2,5,'Love the monitor, crystal clear','2024-03-05',15);
INSERT INTO order_reviews VALUES(6,10,10,5,'Amazing laptop, highly recommend','2024-03-20',20);
INSERT INTO order_reviews VALUES(7,12,15,4,'Comfortable chair, good value','2024-03-30',7);
INSERT INTO order_reviews VALUES(8,13,8,3,'Sofa is okay but delivery was slow','2024-04-10',2);
INSERT INTO order_reviews VALUES(9,16,5,5,'Great monitor, perfect for work','2024-04-18',10);
INSERT INTO order_reviews VALUES(10,20,7,4,'Good laptop for the price','2024-05-08',6);
CREATE TABLE projects (
                project_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                dept_id INTEGER,
                manager_id INTEGER,
                start_date DATE NOT NULL,
                end_date DATE,
                budget DECIMAL(12, 2),
                status TEXT NOT NULL,
                priority TEXT,
                FOREIGN KEY (dept_id) REFERENCES departments(dept_id),
                FOREIGN KEY (manager_id) REFERENCES employees(emp_id)
            );
INSERT INTO projects VALUES(1,'Website Redesign','Complete redesign of company website',2,7,'2024-01-01','2024-06-30',150000,'in_progress','high');
INSERT INTO projects VALUES(2,'Mobile App Development','New mobile application for customers',3,10,'2024-02-01','2024-08-31',250000,'in_progress','high');
INSERT INTO projects VALUES(3,'Customer Portal','Self-service portal for customers',3,10,'2024-03-01','2024-09-30',180000,'in_progress','medium');
INSERT INTO projects VALUES(4,'Q4 Marketing Campaign','Holiday season marketing campaign',2,7,'2024-10-01','2024-12-31',100000,'planned','high');
INSERT INTO projects VALUES(5,'Sales Training Program','Comprehensive sales training initiative',1,2,'2024-04-01','2024-07-31',50000,'in_progress','medium');
INSERT INTO projects VALUES(6,'Inventory System Upgrade','Modernize inventory management system',6,19,'2024-05-01','2024-10-31',120000,'planned','medium');
INSERT INTO projects VALUES(7,'Customer Support AI','AI chatbot for customer support',4,14,'2024-06-01','2024-11-30',200000,'planned','high');
CREATE TABLE project_tasks (
                task_id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                assigned_to INTEGER,
                due_date DATE,
                completed_date DATE,
                status TEXT NOT NULL,
                priority TEXT,
                estimated_hours DECIMAL(6, 2),
                actual_hours DECIMAL(6, 2),
                FOREIGN KEY (project_id) REFERENCES projects(project_id),
                FOREIGN KEY (assigned_to) REFERENCES employees(emp_id)
            );
INSERT INTO project_tasks VALUES(1,1,'Design Mockups','Create initial design mockups',8,'2024-01-31','2024-01-28','completed','high',40,38);
INSERT INTO project_tasks VALUES(2,1,'Frontend Development','Build frontend components',12,'2024-03-31',NULL,'in_progress','high',120,85);
INSERT INTO project_tasks VALUES(3,1,'Backend Integration','Integrate with backend APIs',11,'2024-04-30',NULL,'in_progress','high',80,45);
INSERT INTO project_tasks VALUES(4,2,'UI/UX Design','Design mobile app interface',8,'2024-02-28','2024-02-25','completed','high',60,58);
INSERT INTO project_tasks VALUES(5,2,'iOS Development','Develop iOS version',12,'2024-06-30',NULL,'in_progress','high',200,120);
INSERT INTO project_tasks VALUES(6,2,'Android Development','Develop Android version',13,'2024-07-31',NULL,'in_progress','high',200,95);
INSERT INTO project_tasks VALUES(7,3,'Database Schema','Design database schema',11,'2024-03-31','2024-03-28','completed','high',30,28);
INSERT INTO project_tasks VALUES(8,3,'API Development','Build REST APIs',11,'2024-06-30',NULL,'in_progress','high',100,60);
INSERT INTO project_tasks VALUES(9,5,'Training Materials','Create training documentation',2,'2024-05-31',NULL,'in_progress','medium',40,25);
INSERT INTO project_tasks VALUES(10,5,'Workshop Sessions','Conduct training workshops',2,'2024-07-15',NULL,'planned','medium',80,0);
CREATE TABLE employee_projects (
                id INTEGER PRIMARY KEY,
                emp_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                role TEXT,
                allocation_percent INTEGER DEFAULT 100,
                start_date DATE,
                end_date DATE,
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
                FOREIGN KEY (project_id) REFERENCES projects(project_id),
                UNIQUE(emp_id, project_id)
            );
INSERT INTO employee_projects VALUES(1,8,1,'Designer',100,'2024-01-01','2024-06-30');
INSERT INTO employee_projects VALUES(2,12,1,'Frontend Developer',80,'2024-02-01','2024-06-30');
INSERT INTO employee_projects VALUES(3,11,1,'Backend Developer',60,'2024-03-01','2024-06-30');
INSERT INTO employee_projects VALUES(4,8,2,'UI/UX Designer',50,'2024-02-01','2024-08-31');
INSERT INTO employee_projects VALUES(5,12,2,'iOS Developer',100,'2024-03-01','2024-08-31');
INSERT INTO employee_projects VALUES(6,13,2,'Android Developer',100,'2024-03-01','2024-08-31');
INSERT INTO employee_projects VALUES(7,11,3,'Backend Developer',80,'2024-03-01','2024-09-30');
INSERT INTO employee_projects VALUES(8,12,3,'Frontend Developer',60,'2024-04-01','2024-09-30');
INSERT INTO employee_projects VALUES(9,2,5,'Training Lead',50,'2024-04-01','2024-07-31');
INSERT INTO employee_projects VALUES(10,3,5,'Training Assistant',30,'2024-04-01','2024-07-31');
CREATE TABLE invoices (
                invoice_id INTEGER PRIMARY KEY,
                invoice_number TEXT UNIQUE NOT NULL,
                order_id INTEGER,
                customer_id INTEGER NOT NULL,
                issue_date DATE NOT NULL,
                due_date DATE NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                tax_amount DECIMAL(10, 2) DEFAULT 0.00,
                total_amount DECIMAL(10, 2) NOT NULL,
                status TEXT NOT NULL,
                paid_date DATE,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
INSERT INTO invoices VALUES(1,'INV-2024-001',1,1,'2024-01-15','2024-02-14',1261.880000000000109,106.4000000000000056,1368.279999999999973,'paid','2024-01-15');
INSERT INTO invoices VALUES(2,'INV-2024-002',2,2,'2024-01-20','2024-02-19',308.990000000000009,24,332.990000000000009,'paid','2024-01-20');
INSERT INTO invoices VALUES(3,'INV-2024-003',3,1,'2024-02-05','2024-03-06',107.1899999999999978,7.200000000000000177,114.3900000000000005,'paid','2024-02-05');
INSERT INTO invoices VALUES(4,'INV-2024-004',4,3,'2024-02-10','2024-03-11',1303.990000000000009,104,1407.990000000000009,'paid','2024-02-10');
INSERT INTO invoices VALUES(5,'INV-2024-005',5,5,'2024-02-15','2024-03-16',612.990000000000009,48,660.990000000000009,'paid','2024-02-15');
INSERT INTO invoices VALUES(6,'INV-2024-006',9,1,'2024-03-12','2024-04-11',866.990000000000009,72,938.990000000000009,'pending',NULL);
INSERT INTO invoices VALUES(7,'INV-2024-007',15,6,'2024-04-10','2024-05-10',24.19000000000000127,1.199999999999999956,25.39000000000000056,'pending',NULL);
CREATE TABLE expenses (
                expense_id INTEGER PRIMARY KEY,
                dept_id INTEGER,
                emp_id INTEGER,
                category TEXT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                expense_date DATE NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                approved_by INTEGER,
                FOREIGN KEY (dept_id) REFERENCES departments(dept_id),
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
                FOREIGN KEY (approved_by) REFERENCES employees(emp_id)
            );
INSERT INTO expenses VALUES(1,2,8,'Marketing',5000,'2024-01-10','Social media advertising','approved',6);
INSERT INTO expenses VALUES(2,3,11,'Software',1200,'2024-01-15','Development tools license','approved',9);
INSERT INTO expenses VALUES(3,1,3,'Travel',850,'2024-02-01','Client meeting travel','approved',1);
INSERT INTO expenses VALUES(4,2,7,'Marketing',3000,'2024-02-05','Trade show booth','approved',6);
INSERT INTO expenses VALUES(5,3,12,'Hardware',2500,'2024-02-10','Development equipment','approved',9);
INSERT INTO expenses VALUES(6,4,15,'Training',800,'2024-02-15','Customer service training','approved',14);
INSERT INTO expenses VALUES(7,6,19,'Equipment',1500,'2024-03-01','Warehouse equipment','approved',19);
INSERT INTO expenses VALUES(8,2,8,'Marketing',4500,'2024-03-10','Online campaign','pending',NULL);
INSERT INTO expenses VALUES(9,1,4,'Travel',1200,'2024-03-15','Sales conference','pending',NULL);
CREATE TABLE campaigns (
                campaign_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                start_date DATE NOT NULL,
                end_date DATE,
                budget DECIMAL(10, 2),
                spent DECIMAL(10, 2) DEFAULT 0.00,
                status TEXT NOT NULL,
                campaign_type TEXT
            );
INSERT INTO campaigns VALUES(1,'Spring Sale 2024','Spring promotion campaign','2024-03-01','2024-03-31',50000,48500,'completed','promotion');
INSERT INTO campaigns VALUES(2,'Summer Launch','New product launch campaign','2024-06-01','2024-08-31',75000,32000,'active','launch');
INSERT INTO campaigns VALUES(3,'Holiday Special','Holiday season campaign','2024-11-01','2024-12-31',100000,0,'planned','promotion');
INSERT INTO campaigns VALUES(4,'Referral Program','Customer referral incentive','2024-01-01','2024-12-31',30000,18500,'active','referral');
INSERT INTO campaigns VALUES(5,'Email Newsletter','Monthly email marketing','2024-01-01','2024-12-31',24000,12000,'active','email');
CREATE TABLE campaign_customers (
                id INTEGER PRIMARY KEY,
                campaign_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                enrolled_date DATE NOT NULL,
                conversion_date DATE,
                conversion_value DECIMAL(10, 2),
                FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                UNIQUE(campaign_id, customer_id)
            );
INSERT INTO campaign_customers VALUES(1,1,1,'2024-03-05','2024-03-10',1303.990000000000009);
INSERT INTO campaign_customers VALUES(2,1,2,'2024-03-08','2024-03-12',411.990000000000009);
INSERT INTO campaign_customers VALUES(3,1,3,'2024-03-10','2024-03-15',98.1899999999999978);
INSERT INTO campaign_customers VALUES(4,1,5,'2024-03-12','2024-03-18',391.990000000000009);
INSERT INTO campaign_customers VALUES(5,1,7,'2024-03-15',NULL,NULL);
INSERT INTO campaign_customers VALUES(6,2,10,'2024-06-05','2024-06-10',1238.990000000000009);
INSERT INTO campaign_customers VALUES(7,2,13,'2024-06-08','2024-06-12',88.39000000000000056);
INSERT INTO campaign_customers VALUES(8,4,1,'2024-01-15','2024-01-20',1261.880000000000109);
INSERT INTO campaign_customers VALUES(9,4,5,'2024-02-01','2024-02-15',612.990000000000009);
INSERT INTO campaign_customers VALUES(10,4,10,'2024-03-01','2024-03-15',1238.990000000000009);
INSERT INTO campaign_customers VALUES(11,5,1,'2024-01-10','2024-01-15',1261.880000000000109);
INSERT INTO campaign_customers VALUES(12,5,2,'2024-01-15','2024-01-20',308.990000000000009);
INSERT INTO campaign_customers VALUES(13,5,3,'2024-02-01','2024-02-10',1303.990000000000009);
INSERT INTO campaign_customers VALUES(14,5,4,'2024-02-05',NULL,NULL);
INSERT INTO campaign_customers VALUES(15,5,5,'2024-02-10','2024-02-15',612.990000000000009);
CREATE TABLE promotions (
                promotion_id INTEGER PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                discount_type TEXT NOT NULL,
                discount_value DECIMAL(10, 2) NOT NULL,
                min_purchase DECIMAL(10, 2),
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                max_uses INTEGER,
                used_count INTEGER DEFAULT 0,
                status TEXT NOT NULL
            );
INSERT INTO promotions VALUES(1,'SPRING2024','Spring Sale','15% off all items','percentage',15,100,'2024-03-01','2024-03-31',1000,245,'expired');
INSERT INTO promotions VALUES(2,'SUMMER10','Summer Discount','10% off orders over $200','percentage',10,200,'2024-06-01','2024-08-31',500,128,'active');
INSERT INTO promotions VALUES(3,'NEWCUSTOMER','New Customer Bonus','$20 off first order','fixed',20,50,'2024-01-01','2024-12-31',NULL,89,'active');
INSERT INTO promotions VALUES(4,'VIP15','VIP Discount','15% off for VIP customers','percentage',15,0,'2024-01-01','2024-12-31',NULL,156,'active');
INSERT INTO promotions VALUES(5,'FREESHIP','Free Shipping','Free shipping on orders over $100','fixed',0,100,'2024-01-01','2024-12-31',NULL,342,'active');
COMMIT;
