USE ECOMMERCE_DATA;
CREATE TABLE orders (
  `order_id` INT NOT NULL,
  `id` INT NOT NULL,
  `size` INT DEFAULT NULL,
  `address` VARCHAR(600) NOT NULL,
  `total_price` DECIMAL(10,2) DEFAULT NULL,
  PRIMARY KEY (`order_id`, `id`)
);

