CREATE DATABASE prueba_ladorian;

USE prueba_ladorian;

CREATE TABLE ventas (
    site_id INT NOT NULL,
    date DATE NOT NULL,
    product_id INT,
    category1_id INT,
    hour INT,
    units DECIMAL(12,2),
    total DECIMAL(12,2),
    site_name VARCHAR(255),
    is_holidays BOOLEAN
);

SELECT
    site_id,
    COUNT(DISTINCT site_name) AS number_of_names
FROM ventas
GROUP BY site_id
HAVING COUNT(DISTINCT site_name) > 1;

SELECT
    site_name,
    COUNT(DISTINCT site_id) AS number_of_ids
FROM ventas
GROUP BY site_name
HAVING COUNT(DISTINCT site_id) > 1;