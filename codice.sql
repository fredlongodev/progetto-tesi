CREATE TABLE image_dhash (
    id SERIAL PRIMARY KEY,
    hash VARCHAR(16) NOT NULL,
    category VARCHAR(50) NOT NULL
);