CREATE TABLE
  IF NOT EXISTS books (
    id INT NOT NULL AUTO_INCREMENT,
    url VARCHAR(255),
    title TEXT,
    upc VARCHAR(255),
    product_type VARCHAR(255),
    price_excl_tax DECIMAL(10, 2),
    price_incl_tax DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    availability INT,
    num_reviews INT,
    stars INT,
    category VARCHAR(255),
    description TEXT,
    PRIMARY KEY (id)
  );

INSERT INTO
  books (
    url,
    title,
    upc,
    product_type,
    price_excl_tax,
    price_incl_tax,
    tax,
    availability,
    num_reviews,
    stars,
    category,
    description
  )