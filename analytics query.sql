-- Stock Analysis
-- 1. Rank Products by Stock Levels
SELECT p.product_name, i.stock_quantity, RANK() OVER (ORDER BY i.stock_quantity DESC) AS stock_rank
FROM products p
JOIN inventory i ON p.product_id = i.product_id;

-- 2. Total stock per brand
SELECT b.brand_name, SUM(i.stock_quantity) AS total_stock
FROM brands b
JOIN products p ON b.brand_id = p.brand_id
JOIN inventory i ON p.product_id = i.product_id
GROUP BY b.brand_name
ORDER BY total_stock DESC;

-- 3. Calculate NTILE for stock levels
SELECT p.product_name, i.stock_quantity, NTILE(5) OVER (ORDER BY i.stock_quantity DESC) AS stock_tier
FROM products p
JOIN inventory i ON p.product_id = i.product_id;

-- Sales Performance
-- 1. Highest Sales per Product
SELECT p.product_name, MAX(oi.total_price) AS highest_sales_amount
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_name
ORDER BY highest_sales_amount DESC;

-- 2. Total Sales per Product
SELECT COALESCE(p.product_name, 'Grand Total') AS product_name, SUM(oi.total_price) AS total_sales
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_name WITH ROLLUP
ORDER BY total_sales DESC;

-- 3. Top-Selling Product per State
SELECT a.state, p.product_name, SUM(oi.total_price) AS total_sales
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN addresses a ON o.shipping_address_id = a.address_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY a.state, p.product_name
HAVING 
    total_sales = (
        SELECT MAX(state_sales)
        FROM (
            SELECT a_inner.state AS state, p_inner.product_name AS product_name, SUM(oi_inner.total_price) AS state_sales
            FROM order_items oi_inner    
            JOIN orders o_inner ON oi_inner.order_id = o_inner.order_id   
            JOIN addresses a_inner ON o_inner.shipping_address_id = a_inner.address_id    
            JOIN products p_inner ON oi_inner.product_id = p_inner.product_id    
            WHERE a_inner.state = a.state    
            GROUP BY a_inner.state, p_inner.product_name
        ) AS state_sales_table
    )
ORDER BY total_sales DESC;      

-- 4. Aggregate Product Sales by State
SELECT COALESCE(p.product_name, 'All Products') AS product_name, COALESCE(a.state, 'All States') AS state, SUM(oi.total_price) AS total_sales                       
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
JOIN addresses a ON o.shipping_address_id = a.address_id
GROUP BY p.product_name, a.state WITH ROLLUP                      
ORDER BY product_name, CASE WHEN state = 'All States' THEN 1 ELSE 0 END, CASE WHEN state = 'All States' THEN NULL ELSE state END;

-- 5. Top N Best-Selling Products by Order Count
SELECT p.product_name, COUNT(oi.order_id) AS order_count, DENSE_RANK() OVER (ORDER BY COUNT(oi.order_id) DESC) AS sales_rank
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_name
ORDER BY sales_rank;

-- Product Insights
-- 1. Cheapest & Expensive Products by Brand
WITH ProductRanked AS (
    SELECT 
        b.brand_name, 
        p.product_name, 
        p.price,
        FIRST_VALUE(p.product_name) OVER (PARTITION BY p.brand_id ORDER BY p.price ASC) AS cheapest_product,
        FIRST_VALUE(p.price) OVER (PARTITION BY p.brand_id ORDER BY p.price ASC) AS cheapest_price,
        LAST_VALUE(p.product_name) OVER (PARTITION BY p.brand_id ORDER BY p.price ASC 
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS expensive_product,
        LAST_VALUE(p.price) OVER (PARTITION BY p.brand_id ORDER BY p.price ASC 
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS expensive_price,
        ROW_NUMBER() OVER (PARTITION BY p.brand_id ORDER BY p.price ASC) AS row_num
    FROM Products p
    JOIN Brands b ON p.brand_id = b.brand_id
)
SELECT brand_name, cheapest_product, cheapest_price, expensive_product, expensive_price
FROM ProductRanked
WHERE row_num = 1
ORDER BY brand_name;

-- 2. Price-Based Groups
SELECT product_name, price, NTILE(4) OVER (ORDER BY price ASC) AS price_tier
FROM Products;

--  3. Top N Best-Selling Products by Price Tier
WITH ProductSales AS (
    SELECT p.product_name, p.price, SUM(oi.total_price) AS total_sales
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.product_name, p.price
),
PriceTiered AS (
    SELECT product_name, price, total_sales, NTILE(5) OVER (ORDER BY price DESC) AS price_tier
    FROM ProductSales
)
SELECT product_name, price, total_sales, price_tier,
    DENSE_RANK() OVER (PARTITION BY price_tier ORDER BY total_sales DESC) AS rank_within_tier
FROM PriceTiered
ORDER BY price_tier, rank_within_tier;

-- Customer Orders
-- 1. Quarterly Moving Avg Analysis
SELECT 
    YEAR(order_date) AS order_year,
    QUARTER(order_date) AS order_quarter,
    SUM(total_amount) AS total_amount,  
    ROUND(
        AVG(SUM(total_amount)) OVER (
            PARTITION BY YEAR(order_date) 
            ORDER BY QUARTER(order_date) 
            ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
        ), 2
    ) AS moving_avg_amount
FROM orders
GROUP BY order_year, order_quarter
ORDER BY order_year, order_quarter;

-- 2. Sales Difference Between Dates
WITH DailySales AS (
    SELECT 
        DATE(o.order_date) AS order_date,
        SUM(oi.total_price) AS current_sales  
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    GROUP BY DATE(o.order_date)  
)
SELECT 
    order_date,
    current_sales,
    COALESCE(LAG(current_sales) OVER (ORDER BY order_date), 0) AS previous_sales,  
    current_sales - COALESCE(LAG(current_sales) OVER (ORDER BY order_date), 0) AS sales_difference
FROM DailySales
ORDER BY order_date;

-- 3. Product Sales Contribution Analysis
WITH ProductSales AS (
    SELECT p.product_name, SUM(oi.total_price) AS total_sales
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.product_name
),
TotalSales AS (
    SELECT SUM(total_sales) AS overall_sales FROM ProductSales
)
SELECT ps.product_name, ps.total_sales, ts.overall_sales, ROUND((ps.total_sales * 100.0 / ts.overall_sales), 2) AS sales_percentage
FROM ProductSales ps
CROSS JOIN TotalSales ts
ORDER BY sales_percentage DESC;      

-- 4. Top N Customers by Purchase Amount
WITH CustomerSpending AS (
    SELECT 
        u.username,  
        CONCAT(u.first_name, ' ', u.last_name) AS customer_name,
        SUM(oi.total_price) AS total_spent,
        DENSE_RANK() OVER (ORDER BY SUM(oi.total_price) DESC) AS spending_rank
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN users u ON o.user_id = u.user_id
    WHERE u.role = 'customer'  
    GROUP BY u.username, customer_name
)
SELECT * FROM CustomerSpending
WHERE spending_rank <= 10  
ORDER BY spending_rank;                      

-- Market Trends
-- 1. Top-Selling Products by State
WITH ProductSales AS (
    SELECT 
        a.state, 
        p.product_name, 
        SUM(oi.total_price) AS total_sales,
        RANK() OVER (PARTITION BY a.state ORDER BY SUM(oi.total_price) DESC) AS sales_rank
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
    JOIN addresses a ON o.shipping_address_id = a.address_id
    GROUP BY a.state, p.product_name
)
SELECT 
    ps1.state,
    COALESCE(ps1.product_name, 'None') AS Product_1, COALESCE(ps1.total_sales, 0) AS Sales_1,
    COALESCE(ps2.product_name, 'None') AS Product_2, COALESCE(ps2.total_sales, 0) AS Sales_2,
    COALESCE(ps3.product_name, 'None') AS Product_3, COALESCE(ps3.total_sales, 0) AS Sales_3
FROM 
    (SELECT * FROM ProductSales WHERE sales_rank = 1) ps1
LEFT JOIN 
    (SELECT * FROM ProductSales WHERE sales_rank = 2) ps2 ON ps1.state = ps2.state
LEFT JOIN 
    (SELECT * FROM ProductSales WHERE sales_rank = 3) ps3 ON ps1.state = ps3.state
ORDER BY ps1.state;

-- 2. Pareto Sales Distribution (80/20 Rule)
WITH ProductSales AS (
    SELECT 
        p.product_name, 
        SUM(oi.total_price) AS total_sales
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id  
    JOIN products p ON oi.product_id = p.product_id  
    GROUP BY p.product_name
),
RankedProducts AS (
    SELECT 
        product_name,
        total_sales,
        SUM(total_sales) OVER (ORDER BY total_sales DESC) AS cumulative_sales,
        ROUND((SUM(total_sales) OVER (ORDER BY total_sales DESC) * 100.0) / SUM(total_sales) OVER (), 2) AS cumulative_percentage
    FROM ProductSales
)
SELECT 
    product_name,
    total_sales,
    cumulative_sales,
    cumulative_percentage,
    CASE WHEN cumulative_percentage <= 80 THEN 'Top 80%' ELSE 'Bottom 20%' END AS pareto_classification
FROM RankedProducts
ORDER BY cumulative_sales DESC; 

-- 3. Top Products in Each Price Tier
WITH ProductSales AS (
    SELECT 
        p.product_name,
        p.price,
        SUM(oi.total_price) AS total_sales
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.product_name, p.price
),
PriceTieredProducts AS (
    SELECT 
        product_name,
        price,
        total_sales,
        NTILE(5) OVER (ORDER BY price DESC) AS price_tier
    FROM ProductSales
)
SELECT 
    product_name,
    price,
    total_sales,
    price_tier,
    DENSE_RANK() OVER (PARTITION BY price_tier ORDER BY total_sales DESC) AS rank_within_tier
FROM PriceTieredProducts
ORDER BY price_tier, rank_within_tier;
