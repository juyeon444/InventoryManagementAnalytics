-- Use or create the database
CREATE DATABASE IF NOT EXISTS inventory_management;
USE inventory_management;

-- Table: users
-- Stores information about users
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,         -- Unique identifier for each user
    username VARCHAR(50) UNIQUE NOT NULL,           -- Unique username for login
    password VARCHAR(255) NOT NULL,                 -- Hashed password for security
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone_number VARCHAR(15),
    role ENUM('admin', 'customer') NOT NULL,        -- Defines the role (admin or regular user)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: admins
-- Stores information about administrators
CREATE TABLE admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,                                            -- Links to the 'users' table
    admin_level ENUM('super admin', 'warehouse manager', 'sales manager', 'support manager') NOT NULL,   -- Defines admin privileges
    department ENUM(
        'Customer Service',
        'Warehouse Operations',
        'Sales',
        'Executive Management',
        'Marketing',
        'IT Administration',
        'Product Management'
    ) NOT NULL DEFAULT 'Customer Service',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Table: brands
-- Stores information about product brands
CREATE TABLE brands (
    brand_id INT AUTO_INCREMENT PRIMARY KEY,       -- Unique identifier for each brand
    brand_name VARCHAR(100) NOT NULL UNIQUE        -- Name of the brand
);

-- Table: suppliers
-- Stores supplier information
CREATE TABLE suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,    -- Unique identifier for each supplier
    supplier_name VARCHAR(100) NOT NULL,           -- Name of the supplier
    contact_email VARCHAR(100) NOT NULL UNIQUE,    -- Contact email of the supplier
    contact_phone_number VARCHAR(15) NOT NULL,     -- Contact phone number
    street VARCHAR(255) NOT NULL,                  -- Street address
    city VARCHAR(100) NOT NULL,                    -- City name
    state VARCHAR(100) NOT NULL,                   -- State or province
    postal_code VARCHAR(20) NOT NULL,              -- Postal or ZIP code
    country VARCHAR(100) NOT NULL                  -- Country name
);

-- Table: products
-- Stores product details
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,     -- Unique identifier for each product
    product_name VARCHAR(100) NOT NULL,            -- Name of the product
    product_description TEXT,                      -- Product description
    price DECIMAL(10, 2) NOT NULL,                 -- Price of the product
    brand_id INT,                                  -- Foreign key referencing brands
    supplier_id INT,                               -- Foreign key referencing suppliers (must be provided)
    FOREIGN KEY (brand_id) REFERENCES brands(brand_id) ON DELETE SET NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL
);

-- Table: inventory
-- Stores product inventory 
CREATE TABLE inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY, 
    product_id INT NOT NULL, 
    stock_quantity INT NOT NULL DEFAULT 0, 
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Table: addresses
-- Stores addresses associated with various entities
CREATE TABLE addresses (
    address_id INT AUTO_INCREMENT PRIMARY KEY,     -- Unique identifier for each address
    user_id INT NOT NULL,                          -- Foreign key referencing users
    street VARCHAR(255) NOT NULL,                  -- Street address
    city VARCHAR(100) NOT NULL,                    -- City name
    state VARCHAR(100) NOT NULL,                   -- State or province
    postal_code VARCHAR(20) NOT NULL,              -- Postal or ZIP code
    country VARCHAR(100) NOT NULL,                 -- Country name
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE -- Delete addresses when user is deleted
);

-- Table: orders
-- Stores order details
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,       -- Unique identifier for each order
    user_id INT,                          -- Foreign key referencing users
    total_amount DECIMAL(10, 2) NOT NULL,          -- Total amount of the order
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP, -- Date when the order was placed
    shipping_address_id INT,             -- Foreign key referencing addresses
    delivery_status ENUM('Pending', 'Shipped', 'Delivered', 'Cancelled') NOT NULL DEFAULT 'Pending', -- Delivery status
    status_updated_date DATETIME NULL,            -- Timestamp for delivery status
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id) ON DELETE SET NULL
);

-- Table: order_items
-- Stores items within an order
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,  -- Unique identifier for each order item
    order_id INT NOT NULL,                         -- Foreign key referencing orders
    product_id INT,                                -- Foreign key referencing products
    quantity INT NOT NULL,                         -- Quantity of the product in the order
    unit_price DECIMAL(10, 2) NOT NULL,            -- Price of the product at the time of order
    total_price DECIMAL(10, 2) NOT NULL,           -- Total price (price * quantity)
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE SET NULL
);

-- Mock Data
-- Insert data into users
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('cjowitte', 'aW6$8.r9&7r$(', 'cjowitte@omniture.com', 'Carmencita', 'Jowitt', '766-714-3007', 'customer', '2024-06-19 23:41:51');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('cparkerf', 'tH5.HT?7LY', 'cparkerf@nytimes.com', 'Cami', 'Parker', '255-212-9112', 'customer', '2024-04-15 09:32:26');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('jdowneg', 'gQ5~rv1zKN''9fl', 'jdowneg@163.com', 'Jessalin', 'Downe', '676-878-9878', 'customer', '2022-06-12 18:45:11');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('jrimmerh', 'sT1!,i>5a*', 'jrimmerh@nyu.edu', 'Jesus', 'Rimmer', '153-150-5070', 'customer', '2023-07-09 04:21:40');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('cfrodshami', 'uJ1!Agp@=mU*G%*~', 'cfrodshami@wp.com', 'Corabel', 'Frodsham', '179-348-5863', 'customer', '2023-04-01 02:51:56');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('kspracklingj', 'zS9{&<fKv', 'kspracklingj@youtube.com', 'Kevyn', 'Sprackling', '761-127-8220', 'customer', '2024-05-29 08:33:32');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('pcordsk', 'kV8<RDs~', 'pcordsk@theatlantic.com', 'Peterus', 'Cords', '954-990-9479', 'customer', '2022-09-12 23:15:47');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('kpatryl', 'kM8%`Cu6q$k3aOt', 'kpatryl@theatlantic.com', 'Kalindi', 'Patry', '908-538-9563', 'customer', '2023-01-11 22:58:07');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('vgrubbm', 'rZ8_>nt8a$mQ', 'vgrubbm@yolasite.com', 'Vinnie', 'Grubb', '708-380-6826', 'customer', '2023-12-01 23:38:58');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('phaneyn', 'mG0`*74YkUzV=', 'phaneyn@cloudflare.com', 'Parsifal', 'Haney`', '325-969-0988', 'customer', '2022-12-05 21:43:05');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('msearlo', 'rS5`Lfy6,0W4\~', 'msearlo@hp.com', 'Madlin', 'Searl', '833-426-2316', 'customer', '2023-10-11 16:03:49');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('tcrocettip', 'aA3,VQv6&', 'tcrocettip@altervista.org', 'Tybi', 'Crocetti', '618-739-0593', 'customer', '2023-05-31 13:26:12');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('mlukasq', 'jA3$vtgXT', 'mlukasq@netvibes.com', 'Maxie', 'Lukas', '719-257-7579', 'customer', '2023-06-05 08:01:48');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('wminallr', 'uC1$\eO+7pB5Z', 'wminallr@dot.gov', 'Winn', 'Minall', '217-572-2073', 'customer', '2024-09-28 17:23:57');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('cwindmills', 'lE6$s@2NvkL4IL2''', 'cwindmills@hostgator.com', 'Cyril', 'Windmill', '863-916-1580', 'customer', '2022-10-31 12:52:02');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('mpiett', 'cD5}#DwFC', 'mpiett@hexun.com', 'Marchelle', 'Piet', '842-788-4762', 'customer', '2024-06-05 05:26:35');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('gburcombeu', 'aD7`15UYp&8_viDm', 'gburcombeu@typepad.com', 'Godart', 'Burcombe', '578-330-6289', 'customer', '2023-10-02 04:36:24');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('rebanksv', 'vJ5/55X6h)h87', 'rebanksv@mit.edu', 'Ravid', 'Ebanks', '574-319-6898', 'customer', '2024-02-16 05:28:37');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('ecleerew', 'uS8(y6#e$FK94Sp', 'ecleerew@lulu.com', 'Ede', 'Cleere', '205-303-6141', 'customer', '2023-05-13 08:40:24');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('ekierx', 'zB6~DlG.#,', 'ekierx@xinhuanet.com', 'Elinor', 'Kier', '980-306-7534', 'customer', '2022-04-03 14:00:26');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('evogelery', 'hV7#cB/TqDxpN.3', 'evogelery@fema.gov', 'Elden', 'Vogeler', '160-828-9805', 'customer', '2024-02-13 05:43:17');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('ncollacombez', 'xV4(eT28', 'ncollacombez@ebay.co.uk', 'Nealon', 'Collacombe', '741-352-0802', 'customer', '2022-10-30 04:41:07');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('nredfield10', 'cR3_(f2|4~<Hqad_', 'nredfield10@msu.edu', 'Niel', 'Redfield', '853-728-7364', 'customer', '2024-12-05 12:45:25');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('fdominique27', 'jL8!dajX!&B1p4Y', 'fdominique27@google.pl', 'Frannie', 'Dominique', '890-972-2604', 'customer', '2023-06-13 14:59:03');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('jbunny28', 'nB2&s1q1}sb', 'jbunny28@instagram.com', 'Judd', 'Bunny', '763-249-3258', 'customer', '2023-09-27 05:33:48');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('plias29', 'jF9+j<.|Jk3d@w?w', 'plias29@feedburner.com', 'Patricia', 'Lias', '563-786-6813', 'customer', '2022-06-12 14:09:47');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('oholsey2a', 'wM8*WHFgN16xF', 'oholsey2a@rediff.com', 'Orin', 'Holsey', '597-371-1529', 'customer', '2023-01-19 09:52:08');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('ldevonish2b', 'kH4/flSH8DC&a3l', 'ldevonish2b@oracle.com', 'Leif', 'Devonish', '303-254-3069', 'customer', '2023-10-08 17:53:05');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('cferens2c', 'sC7<A0Lt"roMn%', 'cferens2c@constantcontact.com', 'Clerkclaude', 'Ferens', '858-496-0097', 'customer', '2024-01-23 10:03:08');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('igreensite2d', 'dS4&E/LQ', 'igreensite2d@marketwatch.com', 'Ilise', 'Greensite', '634-390-3140', 'admin', '2023-10-25 02:56:31');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('cbrito2e', 'cQ9!bolC', 'cbrito2e@senate.gov', 'Cherey', 'Brito', '545-200-3669', 'admin', '2023-09-20 22:21:37');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('hyanuk2f', 'zK4$Z6Mt', 'hyanuk2f@elpais.com', 'Haleigh', 'Yanuk', '179-645-7154', 'admin', '2023-03-20 20:34:33');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('wfettes2g', 'mD7?#(@4Ww#K/', 'wfettes2g@posterous.com', 'Witty', 'Fettes', '123-547-8340', 'admin', '2023-12-02 10:40:26');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('pcalcutt2h', 'cU8?W,jZWp@m', 'pcalcutt2h@mysql.com', 'Prudi', 'Calcutt', '157-761-5060', 'admin', '2023-05-06 21:23:02');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('kblodg2i', 'qP2$T+UJq2A', 'kblodg2i@ted.com', 'Ketty', 'Blodg', '975-528-5574', 'admin', '2023-03-24 11:21:39');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('awillis2j', 'nA5+Yw>wU>Dk', 'awillis2j@bizjournals.com', 'Ansel', 'Willis', '638-298-6517', 'admin', '2022-02-26 11:52:07');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('gpelos2k', 'yM7$S&?kzS', 'gpelos2k@whitehouse.gov', 'Gerhardine', 'Pelos', '646-951-5548', 'admin', '2023-10-11 16:46:21');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('dkimbrough2l', 'cY6~FuAu~n3yi', 'dkimbrough2l@dion.ne.jp', 'Doria', 'Kimbrough', '905-934-1126', 'admin', '2023-05-04 12:54:02');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('aitzig2m', 'qC9*1YNCC', 'aitzig2m@auda.org.au', 'Anna-maria', 'Itzig', '672-675-4822', 'admin', '2023-07-25 02:00:21');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('mdand2n', 'oV0*)BHWZhil&3mU', 'mdand2n@cdc.gov', 'Meade', 'Dand', '953-358-0468', 'admin', '2024-10-12 21:26:58');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('jbohlingolsen2o', 'gL5|qoC}*', 'jbohlingolsen2o@rakuten.co.jp', 'Jillayne', 'BoHlingolsen', '714-449-7823', 'admin', '2024-12-17 10:33:54');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('wweedall2p', 'gV5*kgh,Z"', 'wweedall2p@fema.gov', 'Walsh', 'Weedall', '651-293-1262', 'admin', '2023-04-02 22:18:36');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('cjemmison2q', 'pE7{u)miu}`V''buT', 'cjemmison2q@who.int', 'Caro', 'Jemmison', '913-968-7742', 'admin', '2024-09-14 06:58:26');
insert into users (username, password, email, first_name, last_name, phone_number, role, created_at) values ('zstroder2r', 'aA2.&{Q''{k7', 'zstroder2r@amazonaws.com', 'Zorah', 'Stroder', '278-714-3294', 'admin', '2024-11-21 08:10:22');

-- Insert data into admins
INSERT INTO admins (user_id, admin_level, department)
SELECT user_id, 
       CASE 
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 1 THEN 'Support Manager'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 2 THEN 'warehouse manager'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 3 THEN 'sales manager'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 4 THEN 'Support Manager'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 5 THEN 'warehouse manager'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 6 THEN 'warehouse manager'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 7 THEN 'super admin'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 8 THEN 'sales manager'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 9 THEN 'warehouse manager'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 10 THEN 'super admin'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 11 THEN 'sales manager'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 12 THEN 'Support Manager'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 13 THEN 'sales manager'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 14 THEN 'sales manager'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 15 THEN 'Support Manager'
       END AS admin_level,
       CASE 
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 1 THEN 'Customer Service'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 2 THEN 'Warehouse Operations'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 3 THEN 'Sales'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 4 THEN 'Customer Service'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 5 THEN 'Warehouse Operations'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 6 THEN 'Warehouse Operations'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 7 THEN 'Executive Management'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 8 THEN 'Marketing'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 9 THEN 'Warehouse Operations'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 10 THEN 'IT Administration'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 11 THEN 'Sales'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 12 THEN 'Customer Service'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 13 THEN 'Sales'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 14 THEN 'Marketing'
           WHEN ROW_NUMBER() OVER (ORDER BY user_id) = 15 THEN 'Customer Service'
       END AS department
FROM users
WHERE role = 'admin';

-- Insert data into brands
insert into brands (brand_name) values ('BLU');
insert into brands (brand_name) values ('Motorola');
insert into brands (brand_name) values ('alcatel');
insert into brands (brand_name) values ('Lenovo');
insert into brands (brand_name) values ('Qtek');
insert into brands (brand_name) values ('Sewon');
insert into brands (brand_name) values ('Panasonic');
insert into brands (brand_name) values ('Microsoft');
insert into brands (brand_name) values ('Micromax');
insert into brands (brand_name) values ('Emporia');
insert into brands (brand_name) values ('Ulefone');
insert into brands (brand_name) values ('ZTE');
insert into brands (brand_name) values ('Coolpad');
insert into brands (brand_name) values ('HTC');
insert into brands (brand_name) values ('Maxwest');
insert into brands (brand_name) values ('vivo');
insert into brands (brand_name) values ('Haier');
insert into brands (brand_name) values ('Nokia');
insert into brands (brand_name) values ('Philips');
insert into brands (brand_name) values ('Ericsson');
insert into brands (brand_name) values ('Sony');
insert into brands (brand_name) values ('Samsung');
insert into brands (brand_name) values ('Xiaomi');
insert into brands (brand_name) values ('Huawei');

-- Insert data into suppliers
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Denesik, Windler and Smitham', 'econyers0@kickstarter.com', '305-662-3245', '04 Loomis Court', 'Miami', 'Florida', '33196', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Torphy, Price and McClure', 'jhalliburton1@oracle.com', '386-540-5340', '905 Park Meadow Road', 'Daytona Beach', 'Florida', '32128', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Johnston, Glover and Nader', 'lshefton2@biblegateway.com', '786-388-1414', '788 Maywood Park', 'Miami', 'Florida', '33153', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Altenwerth, Hansen and Schaden', 'ndilks3@eventbrite.com', '386-528-1660', '59924 Southridge Junction', 'Daytona Beach', 'Florida', '32128', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Legros, Stanton and Stoltenberg', 'estubbley4@prnewswire.com', '904-363-4165', '820 Comanche Circle', 'Jacksonville', 'Florida', '32255', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Friesen, Durgan and Morar', 'alimbourne5@uiuc.edu', '954-560-6233', '7321 Summer Ridge Court', 'Fort Lauderdale', 'Florida', '33305', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Erdman-Littel', 'htoppes6@nyu.edu', '754-132-4009', '97993 Dakota Crossing', 'Pompano Beach', 'Florida', '33075', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Luettgen-Considine', 'cearwicker7@harvard.edu', '813-802-0602', '5073 Bartelt Avenue', 'Tampa', 'Florida', '33615', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Witting-Kreiger', 'rpinks8@bloglovin.com', '754-909-7869', '9981 Colorado Trail', 'Fort Lauderdale', 'Florida', '33310', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Muller Inc', 'mjochanany9@deliciousdays.com', '850-366-1925', '71 Main Alley', 'Pensacola', 'Florida', '32511', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Pouros-Larkin', 'bkubaceka@arstechnica.com', '305-936-9788', '28 Fuller Road', 'Miami', 'Florida', '33147', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Schiller-Russel', 'sgudgerb@linkedin.com', '904-984-3464', '32579 Norway Maple Pass', 'Jacksonville', 'Florida', '32255', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Schneider Inc', 'csaggc@vk.com', '863-733-4750', '4503 Donald Point', 'Lehigh Acres', 'Florida', '33972', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Jacobi-Tremblay', 'cgotlingd@jiathis.com', '321-577-0651', '55 Manley Road', 'Melbourne', 'Florida', '32919', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Schmidt, Parisian and Bayer', 'wracee@gravatar.com', '407-909-5529', '178 South Junction', 'Orlando', 'Florida', '32830', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Balistreri-Parker', 'mscrymgeourf@reverbnation.com', '727-476-7681', '52 Daystar Street', 'Saint Petersburg', 'Florida', '33710', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Halvorson-Brown', 'scancellariog@deliciousdays.com', '941-595-3363', '5963 Ramsey Point', 'Naples', 'Florida', '34102', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('McLaughlin-Padberg', 'bgundersonh@wp.com', '727-157-0953', '0 Portage Way', 'Clearwater', 'Florida', '33763', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Klein, Fisher and Kassulke', 'asherynei@hibu.com', '352-541-4426', '8335 Northfield Parkway', 'Gainesville', 'Florida', '32610', 'United States');
insert into suppliers (supplier_name, contact_email, contact_phone_number, street, city, state, postal_code, country) values ('Goldner-Green', 'lbrontj@dmoz.org', '239-342-2144', '7533 Marquette Terrace', 'Naples', 'Florida', '33963', 'United States');

-- Insert data into products
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('BLU Dash X', null, '539.44', 1, 1);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Motorola E770', null, '987.87', 2, 2);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('alcatel Fierce 2', null, '271.67', 3, 3);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Lenovo Vibe K5', null, '381.86', 4, 4);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Qtek 2020', null, '590.44', 5, 5);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Sewon SRS-3300', null, '1521.17', 6, 6);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Panasonic Eluga Icon', null, '982.96', 7, 7);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Microsoft Surface 2', null, '966.94', 8, 8);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Micromax X277', null, '391.52', 9, 9);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('BLU Dual SIM Lite', null, '950.22', 1, 1);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Emporia Elegance', null, '102.67', 10, 10);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Ulefone Armor 3W', null, '651.72', 11, 11);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('ZTE Chorus', null, '1972.23', 12, 12);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Coolpad Shine', null, '811.52', 13, 13);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('HTC Desire 19+', null, '191.65', 14, 14);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Maxwest Astro 5s', null, '922.09', 15, 15);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Motorola Motoluxe MT680', null, '276.28', 2, 2);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('ZTE nubia N2', null, '1058.93', 12, 12);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('vivo Xplay6', null, '1299.56', 16, 1);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Haier P7', null, '174.46', 17, 2);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Nokia C5-06', null, '931.22', 18, 3);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Ericsson T10s', null, '1134.65', 20, 4);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Sony Xperia acro HD SOI12', null, '350.45', 21, 5);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Samsung Galaxy J5', null, '1201.61', 22, 6);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Samsung S5230 Star', null, '1427.13', 22, 6);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Xiaomi Redmi Note 10', null, '1871.63', 23, 7);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Nokia C1-01', null, '1447.65', 18, 3);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Nokia E62', null, '1242.54', 18, 3);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Huawei G5500', null, '488.01', 24, 8);
insert into products (product_name, product_description, price, brand_id, supplier_id) values ('Philips Xenium K600', null, '257.00', 19, 9);


-- Insert data into inventory
insert into inventory (product_id, stock_quantity) values (1, 100);
insert into inventory (product_id, stock_quantity) values (2, 100);
insert into inventory (product_id, stock_quantity) values (3, 100);
insert into inventory (product_id, stock_quantity) values (4, 100);
insert into inventory (product_id, stock_quantity) values (5, 100);
insert into inventory (product_id, stock_quantity) values (6, 100);
insert into inventory (product_id, stock_quantity) values (7, 100);
insert into inventory (product_id, stock_quantity) values (8, 100);
insert into inventory (product_id, stock_quantity) values (9, 100);
insert into inventory (product_id, stock_quantity) values (10, 100);
insert into inventory (product_id, stock_quantity) values (11, 100);
insert into inventory (product_id, stock_quantity) values (12, 100);
insert into inventory (product_id, stock_quantity) values (13, 100);
insert into inventory (product_id, stock_quantity) values (14, 100);
insert into inventory (product_id, stock_quantity) values (15, 100);
insert into inventory (product_id, stock_quantity) values (16, 100);
insert into inventory (product_id, stock_quantity) values (17, 100);
insert into inventory (product_id, stock_quantity) values (18, 100);
insert into inventory (product_id, stock_quantity) values (19, 100);
insert into inventory (product_id, stock_quantity) values (20, 100);
insert into inventory (product_id, stock_quantity) values (21, 100);
insert into inventory (product_id, stock_quantity) values (22, 100);
insert into inventory (product_id, stock_quantity) values (23, 100);
insert into inventory (product_id, stock_quantity) values (24, 100);
insert into inventory (product_id, stock_quantity) values (25, 100);
insert into inventory (product_id, stock_quantity) values (26, 100);
insert into inventory (product_id, stock_quantity) values (27, 100);
insert into inventory (product_id, stock_quantity) values (28, 100);
insert into inventory (product_id, stock_quantity) values (29, 100);
insert into inventory (product_id, stock_quantity) values (30, 100);

-- Insert data into addresses
insert into addresses (user_id, street, city, state, postal_code, country) values (1, '11109 Stoughton Court', 'Saint Paul', 'Minnesota', '55172', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (2, '5 Farragut Park', 'Denver', 'Colorado', '80209', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (3, '486 Manley Way', 'Chicago', 'Illinois', '60641', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (4, '24586 Comanche Parkway', 'Birmingham', 'Alabama', '35242', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (5, '985 Mitchell Crossing', 'Aurora', 'Illinois', '60505', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (6, '324 Di Loreto Alley', 'Boise', 'Idaho', '83711', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (7, '20 Cody Hill', 'Anderson', 'Indiana', '46015', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (8, '286 Lake View Road', 'Fresno', 'California', '93704', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (9, '2 Express Circle', 'Anniston', 'Alabama', '36205', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (10, '70 Nelson Circle', 'San Diego', 'California', '92186', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (11, '861 Declaration Avenue', 'Atlanta', 'Georgia', '31119', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (12, '8559 Algoma Way', 'San Antonio', 'Texas', '78278', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (13, '3889 Mariners Cove Drive', 'San Antonio', 'Texas', '78210', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (14, '7892 Summit Street', 'San Jose', 'California', '95194', 'United States');
insert into addresses (user_id, street, city, state, postal_code, country) values (15, '65951 Maywood Street', 'Tallahassee', 'Florida', '32399', 'United States');

-- Create Trigger
-- Trigger: Update stock after an order is placed
DELIMITER $$

CREATE TRIGGER update_stock_after_order
BEFORE INSERT ON order_items
FOR EACH ROW
BEGIN
    -- Prevent negative stock before order placement
    IF (SELECT stock_quantity FROM inventory WHERE product_id = NEW.product_id) < NEW.quantity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Not enough stock available';
    END IF;
    
    -- Update the stock_quantity in the inventory table
    UPDATE inventory
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
END$$

DELIMITER ;

SELECT stock_quantity FROM inventory WHERE product_id = 24;
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (16, 4256.55, '2022-04-02 08:04:44', 13, 'Pending', '2022-05-12 08:04:44');
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (32, 24, 3, 1201.61, 3604.83); 
SELECT stock_quantity FROM inventory WHERE product_id = 24;

-- Insert data into orders
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (1, 191.65, '2022-03-01 23:39:10', 1, 'Delivered', '2022-03-11 23:39:10');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (2, 2793.66, '2024-06-21 04:37:36', 2, 'Delivered', '2024-07-01 04:37:36');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (3, 3845.52, '2023-01-09 13:32:53', 3, 'Delivered', '2023-01-19 13:32:53');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (4, 815.01, '2024-01-12 04:05:37', 4, 'Delivered', '2024-01-22 04:05:37');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (5, 6192.97, '2023-04-09 06:15:54', 5, 'Delivered', '2023-04-19 06:15:54');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (6, 4614.62, '2023-07-31 17:08:55', 6, 'Delivered', '2023-08-10 17:08:55');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (8, 7272.69, '2024-10-26 09:16:21', 7, 'Delivered', '2024-11-05 09:16:21');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (9, 6968.04, '2024-07-14 19:28:20', 8, 'Delivered', '2024-07-24 19:28:20');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (10, 2948.88, '2023-11-24 01:29:48', 9, 'Shipped', '2023-11-27 01:29:48'); 
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (11, 4241.62, '2023-12-26 10:41:18', 10, 'Cancelled', '2024-01-15 10:41:18');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (13, 1078.88, '2022-12-17 13:41:25', 11, 'Delivered', '2022-12-27 13:41:25');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (14, 3898.68, '2023-09-20 17:39:27', 12, 'Cancelled', '2023-10-10 17:39:27');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (16, 4083.53, '2024-09-20 08:03:05', 13, 'Delivered', '2024-09-30 08:03:05');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (7, 2269.30, '2023-05-26 20:58:07', 14, 'Delivered', '2023-06-05 20:58:07');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (9, 7512.39, '2022-09-22 02:35:18', 15, 'Delivered', '2022-10-02 02:35:18');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (10, 1180.88, '2023-02-04 18:45:46', 1, 'Delivered', '2023-02-14 18:45:46');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (11, 1521.17, '2025-01-04 18:14:01', 2, 'Shipped', '2025-01-07 18:14:01'); 
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (10, 6620.81, '2023-08-09 19:47:21', 1, 'Shipped', '2023-08-12 19:47:21'); 
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (11, 3613.89, '2024-12-24 20:43:20', 2, 'Delivered', '2025-01-03 20:43:20');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (13, 3064.55, '2022-09-29 15:36:36', 4, 'Delivered', '2022-10-09 15:36:36');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (13, 6731.70, '2024-08-02 02:21:48', 4, 'Delivered', '2024-08-12 02:21:48');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (12, 5183.68, '2024-10-24 11:27:42', 3, 'Cancelled', '2024-11-13 11:27:42');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (11, 7455.24, '2022-01-13 04:04:39', 2, 'Delivered', '2022-01-23 04:04:39');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (9, 4820.51, '2024-06-13 04:12:07', 15, 'Delivered', '2024-06-23 04:12:07');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (9, 1163.93, '2024-05-22 15:58:30', 15, 'Delivered', '2024-06-01 15:58:30');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (7, 1121.45, '2023-07-30 03:50:02', 14, 'Pending', '2023-08-01 03:50:02');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (6, 477.01, '2024-07-15 02:34:05', 13, 'Delivered', '2024-07-25 02:34:05');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (3, 7178.48, '2024-05-23 11:09:17', 11, 'Delivered', '2024-06-02 11:09:17');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (6, 2952.20, '2024-07-24 04:49:07', 13, 'Delivered', '2024-08-03 04:49:07');
INSERT INTO orders (user_id, total_amount, order_date, shipping_address_id, delivery_status, status_updated_date) VALUES (16, 4256.55, '2022-04-02 08:04:44', 13, 'Delivered', '2022-04-12 08:04:44');

-- Insert data into order_items
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (18, 23, 2, 350.45, 700.90);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (6, 27, 3, 1447.65, 4342.95);  
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (5, 17, 1, 276.28, 276.28);    
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (30, 12, 1, 651.72, 651.72);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (13, 7, 3, 982.96, 2948.88);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (1, 15, 1, 191.65, 191.65);    
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (6, 3, 1, 271.67, 271.67);     
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (15, 7, 3, 982.96, 2948.88);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (23, 28, 3, 1242.54, 3727.62); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (28, 27, 3, 1447.65, 4342.95); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (19, 4, 3, 381.86, 1145.58);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (14, 22, 2, 1134.65, 2269.30); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (25, 3, 3, 271.67, 815.01);    
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (18, 29, 1, 488.01, 488.01);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (20, 1, 3, 539.44, 1618.32);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (13, 22, 1, 1134.65, 1134.65); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (11, 1, 2, 539.44, 1078.88);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (19, 23, 1, 350.45, 350.45);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (21, 13, 3, 1972.23, 5916.69); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (3, 27, 2, 1447.65, 2895.30);  
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (12, 19, 3, 1299.56, 3898.68); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (25, 20, 2, 174.46, 348.92);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (10, 30, 2, 257.00, 514.00);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (18, 22, 2, 1134.65, 2269.30); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (7, 13, 2, 1972.23, 3944.46);  
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (17, 6, 1, 1521.17, 1521.17);  
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (27, 11, 2, 102.67, 205.34);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (19, 18, 2, 1058.93, 2117.86); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (10, 28, 3, 1242.54, 3727.62); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (24, 26, 1, 1871.63, 1871.63); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (21, 3, 3, 271.67, 815.01);    
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (7, 22, 2, 1134.65, 2269.30);  
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (27, 3, 1, 271.67, 271.67);    
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (8, 13, 3, 1972.23, 5916.69);  
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (7, 18, 1, 1058.93, 1058.93);  
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (24, 7, 3, 982.96, 2948.88);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (2, 21, 3, 931.22, 2793.66);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (4, 3, 3, 271.67, 815.01);     
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (18, 11, 3, 102.67, 308.01);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (18, 26, 1, 1871.63, 1871.63); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (8, 23, 3, 350.45, 1051.35);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (9, 7, 3, 982.96, 2948.88);    
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (22, 19, 3, 1299.56, 3898.68); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (29, 5, 2, 590.44, 1180.88);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (20, 9, 3, 391.52, 1174.56);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (26, 23, 1, 350.45, 350.45);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (28, 28, 2, 1242.54, 2485.08); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (29, 5, 3, 590.44, 1771.32);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (3, 10, 1, 950.22, 950.22);    
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (28, 23, 1, 350.45, 350.45);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (23, 28, 3, 1242.54, 3727.62); 
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (15, 6, 3, 1521.17, 4563.51);  
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (18, 7, 1, 982.96, 982.96);    
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (16, 5, 2, 590.44, 1180.88);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (20, 3, 1, 271.67, 271.67);    
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (5, 13, 3, 1972.23, 5916.69);  
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (22, 30, 2, 257.00, 514.00);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (22, 30, 3, 257.00, 771.00);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (26, 30, 3, 257.00, 771.00);   
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES (30, 24, 3, 1201.61, 3604.83); 

-- Create Indexes
CREATE INDEX idx_delivery_status ON orders (delivery_status);
CREATE INDEX idx_orders_order_date ON orders (order_date);

-- Create Views
-- View: Pending Order Summary
-- lists all order items from orders with a delivery status of Pending, including item details, product names, and associated order information.
CREATE VIEW pending_order_items AS
SELECT 
    oi.order_item_id, 
    oi.order_id, 
    o.delivery_status, 
    oi.product_id, 
    p.product_name, 
    oi.quantity, 
    oi.unit_price, 
    oi.total_price
FROM 
    order_items oi
JOIN 
    orders o ON oi.order_id = o.order_id
JOIN 
    products p ON oi.product_id = p.product_id
WHERE 
    o.delivery_status = 'Pending';

-- View: Low Stock Products
-- Lists all products with stock levels below a specified threshold.
CREATE VIEW low_stock_products AS
SELECT 
    p.product_id, 
    p.product_name, 
    i.stock_quantity, 
    b.brand_name, 
    s.supplier_name
FROM inventory i
JOIN products p ON i.product_id = p.product_id
JOIN brands b ON p.brand_id = b.brand_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE i.stock_quantity < 10;


-- View: Admin Role Summary
-- Lists all admins and their roles with department details.
CREATE VIEW admin_role_summary AS
SELECT 
    a.admin_id, 
    u.username AS admin_name, 
    a.admin_level, 
    a.department
FROM admins a
JOIN users u ON a.user_id = u.user_id;

-- Create Temporary Table
-- Temporary Table: High-Value Orders
-- This table captures all orders where the total amount exceeds a certain threshold for analysis purposes.
CREATE TEMPORARY TABLE temp_high_value_orders AS
SELECT 
    o.order_id, 
    o.user_id, 
    o.total_amount, 
    o.order_date
FROM orders o
WHERE o.total_amount > 1000
AND delivery_status = 'Delivered';

-- Temporary Table: Recent Orders
-- Stores orders placed within the last 7 days for quick retrieval and analysis.
CREATE TEMPORARY TABLE temp_recent_orders AS
SELECT 
    o.order_id, 
    o.user_id, 
    o.total_amount, 
    o.order_date, 
    o.delivery_status
FROM orders o
WHERE o.order_date >= CURDATE() - INTERVAL 30 DAY;

-- Stored Procedure: create admin account
DELIMITER //

CREATE PROCEDURE create_admin_account(
    IN p_username VARCHAR(50),
    IN p_password VARCHAR(255),
    IN p_email VARCHAR(100),
    IN p_first_name VARCHAR(50),
    IN p_last_name VARCHAR(50),
    IN p_phone_number VARCHAR(15),
    IN p_admin_level ENUM('super admin', 'warehouse manager', 'sales manager', 'support manager'),
    IN p_department VARCHAR(100)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        -- Rollback transaction in case of an error
        ROLLBACK;
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'An error occurred while creating the admin account.';
    END;

    -- Start transaction
    START TRANSACTION;

    -- Insert into users table
    INSERT INTO users (username, password, email, first_name, last_name, phone_number, role)
    VALUES (p_username, p_password, p_email, p_first_name, p_last_name, p_phone_number, 'admin');

    -- Get the last inserted user_id
    SET @user_id = LAST_INSERT_ID();

    -- Insert into admins table
    INSERT INTO admins (user_id, admin_level, department)
    VALUES (@user_id, p_admin_level, p_department);

    -- Commit the transaction
    COMMIT;
END //

DELIMITER ;

-- Stored Procedure: delete admin account 
DELIMITER $$

CREATE PROCEDURE delete_admin_account(IN admin_id_param INT)
BEGIN
    DECLARE user_id_var INT;

    -- Retrieve the user_id associated with the admin
    SELECT user_id INTO user_id_var FROM admins WHERE admin_id = admin_id_param;

    -- If an admin exists, proceed with deletion
    IF user_id_var IS NOT NULL THEN
        -- Delete the admin from the admins table
        DELETE FROM admins WHERE admin_id = admin_id_param;

        -- Update the user's role to 'customer' instead of deleting
        UPDATE users SET role = 'customer' WHERE user_id = user_id_var;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Admin not found.';
    END IF;
END $$

DELIMITER ;


-- Stored Procedure: promote user to admin
DELIMITER //

CREATE PROCEDURE promote_user_to_admin(
    IN input_user_id INT,
    IN input_admin_level ENUM('super admin', 'warehouse manager', 'sales manager', 'support manager'),
    IN input_department VARCHAR(100)
)
BEGIN
    DECLARE user_exists INT;

    -- Start a transaction
    START TRANSACTION;

    -- Check if the user exists in the users table
    SELECT COUNT(*)
    INTO user_exists
    FROM users
    WHERE user_id = input_user_id;

    -- If the user does not exist, raise an error
    IF user_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No user found with the given user_id.';
    ELSE
        -- Insert the user into the admins table
        INSERT INTO admins (user_id, admin_level, department)
        VALUES (input_user_id, input_admin_level, input_department);

        -- Update the user's role to 'admin' in the users table
        UPDATE users
        SET role = 'admin'
        WHERE user_id = input_user_id;
    END IF;

    -- Commit the transaction
    COMMIT;
END //

DELIMITER ;

CALL promote_user_to_admin(1, 'warehouse manager', 'Warehouse Operations');

-- Stored Procedure: Calculate revenue by product
-- Calculates the total revenue generated by each product.
DELIMITER //
CREATE PROCEDURE calculate_revenue_by_product()
BEGIN
    SELECT p.product_id, p.product_name, SUM(oi.total_price) AS total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.product_id, p.product_name;
END //
DELIMITER ;

-- Create Functions
-- Function: Calculate the total price of an order
DELIMITER //
CREATE FUNCTION calculate_order_total(orderID INT)
RETURNS DECIMAL(10, 2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10, 2);
    SELECT SUM(total_price) INTO total
    FROM order_items
    WHERE order_id = orderID;
    RETURN IFNULL(total, 0);
END;//
DELIMITER ;

SELECT calculate_order_total(1) AS TotalAmount;

-- Function: search for suppliers of the specified product
DELIMITER //

CREATE FUNCTION get_suppliers_for_product(product_id_param INT)
RETURNS TEXT
DETERMINISTIC
BEGIN
    DECLARE supplier_name TEXT;

    -- Retrieve the supplier for the specified product
    SELECT s.supplier_name 
    INTO supplier_name
    FROM products p
    JOIN suppliers s ON p.supplier_id = s.supplier_id
    WHERE p.product_id = product_id_param;

    -- Return the result or 'No suppliers found' if null
    RETURN IFNULL(supplier_name, 'No suppliers found');
END;
//

DELIMITER ;
