DROP DATABASE IF EXISTS trading_system;
CREATE DATABASE trading_system;

\c trading_system

CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    account_id INT,
    symbol TEXT,
    side TEXT,
    quantity FLOAT,
    price FLOAT,
    time_stamp TIMESTAMP
);

CREATE TABLE liquidations (
    id SERIAL PRIMARY KEY,
    account_id INT,
    reason TEXT,
    time_stamp TIMESTAMP
);

INSERT INTO trades 
    (account_id, symbol, side, quantity, price, time_stamp)
VALUES
    (1, 'USDT', 'BUY', 100, 1, '2025-08-10 00:00:00'),
    (2, 'USDT', 'BUY', 100, 1, '2025-08-10 00:00:00');




