-- ── 1. CREATE DATABASE ───────────────────────────────────
DROP DATABASE IF EXISTS restaurant_db;
CREATE DATABASE restaurant_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE restaurant_db;

-- ── 2. CREATE TABLES ─────────────────────────────────────

CREATE TABLE Customers (
    CustomerID   INT AUTO_INCREMENT PRIMARY KEY,
    CustomerName VARCHAR(100) NOT NULL,
    PhoneNumber  VARCHAR(15) UNIQUE NOT NULL,
    Address      VARCHAR(255)
);

CREATE TABLE Tables (
    TableID     INT AUTO_INCREMENT PRIMARY KEY,
    TableNumber INT UNIQUE NOT NULL,
    Status      ENUM('available','reserved') DEFAULT 'available'
);

CREATE TABLE MenuItems (
    DishID        INT AUTO_INCREMENT PRIMARY KEY,
    DishName      VARCHAR(150) NOT NULL,
    Price         DECIMAL(10,2) NOT NULL,
    Category      VARCHAR(50),
    Available     BOOLEAN DEFAULT TRUE,
    ImageFilename VARCHAR(100) DEFAULT 'placeholder.jpg'
);

CREATE TABLE Reservations (
    ReservationID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID    INT NOT NULL,
    TableID       INT NOT NULL,
    DateTime      DATETIME NOT NULL,
    GuestCount    INT NOT NULL,
    Status        ENUM('confirmed','cancelled') DEFAULT 'confirmed',
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (TableID)    REFERENCES Tables(TableID)
);

CREATE TABLE Invoices (
    InvoiceID     INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID    INT NOT NULL,
    TableID       INT NOT NULL,
    TotalAmount   DECIMAL(10,2) NOT NULL,
    PaymentDate   DATETIME DEFAULT CURRENT_TIMESTAMP,
    PaymentMethod ENUM('cash','card') DEFAULT 'cash',
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (TableID)    REFERENCES Tables(TableID)
);

CREATE TABLE InvoiceDetails (
    DetailID  INT AUTO_INCREMENT PRIMARY KEY,
    InvoiceID INT NOT NULL,
    DishID    INT NOT NULL,
    Quantity  INT NOT NULL,
    UnitPrice DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (InvoiceID) REFERENCES Invoices(InvoiceID),
    FOREIGN KEY (DishID)    REFERENCES MenuItems(DishID)
);

-- ── 3. INDEXES ───────────────────────────────────────────
CREATE INDEX idx_customer_phone     ON Customers(PhoneNumber);
CREATE INDEX idx_customer_name      ON Customers(CustomerName);
CREATE INDEX idx_reservation_date   ON Reservations(DateTime);
CREATE INDEX idx_reservation_customer ON Reservations(CustomerID);
CREATE INDEX idx_invoice_date       ON Invoices(PaymentDate);
CREATE INDEX idx_invoice_customer   ON Invoices(CustomerID);
CREATE INDEX idx_menu_category      ON MenuItems(Category);

-- ── 4. VIEWS ─────────────────────────────────────────────

CREATE OR REPLACE VIEW v_daily_bookings AS
SELECT
    r.ReservationID,
    DATE(r.DateTime)  AS BookingDate,
    r.DateTime,
    r.GuestCount,
    r.Status,
    c.CustomerName,
    c.PhoneNumber,
    t.TableNumber
FROM Reservations r
JOIN Customers c ON c.CustomerID = r.CustomerID
JOIN Tables    t ON t.TableID    = r.TableID;

CREATE OR REPLACE VIEW v_table_availability AS
SELECT
    t.TableID,
    t.TableNumber,
    t.Status,
    COUNT(r.ReservationID) AS UpcomingReservations
FROM Tables t
LEFT JOIN Reservations r
    ON r.TableID = t.TableID
    AND r.Status = 'confirmed'
    AND r.DateTime >= NOW()
GROUP BY t.TableID, t.TableNumber, t.Status;

CREATE OR REPLACE VIEW v_top_selling_dishes AS
SELECT
    m.DishID,
    m.DishName,
    m.Category,
    SUM(d.Quantity)                  AS TotalSold,
    SUM(d.Quantity * d.UnitPrice)    AS Revenue
FROM MenuItems m
JOIN InvoiceDetails d ON d.DishID    = m.DishID
JOIN Invoices       i ON i.InvoiceID = d.InvoiceID
GROUP BY m.DishID, m.DishName, m.Category
ORDER BY Revenue DESC;

-- ── 5. STORED PROCEDURES ─────────────────────────────────

DELIMITER $$

CREATE PROCEDURE sp_confirm_reservation(IN p_reservation_id INT)
BEGIN
    UPDATE Reservations
    SET    Status = 'confirmed'
    WHERE  ReservationID = p_reservation_id
    AND    Status != 'cancelled';
END$$

CREATE PROCEDURE sp_generate_invoice(
    IN p_customer_id    INT,
    IN p_table_id       INT,
    IN p_payment_method ENUM('cash','card')
)
BEGIN
    INSERT INTO Invoices(CustomerID, TableID, TotalAmount, PaymentMethod, PaymentDate)
    VALUES (p_customer_id, p_table_id, 0, p_payment_method, NOW());
    SELECT LAST_INSERT_ID() AS NewInvoiceID;
END$$

DELIMITER ;

-- ── 6. USER DEFINED FUNCTIONS ────────────────────────────

DELIMITER $$

CREATE FUNCTION fn_calculate_discount(total_amount DECIMAL(10,2))
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE discount DECIMAL(10,2);
    IF     total_amount >= 1000000 THEN SET discount = total_amount * 0.10;
    ELSEIF total_amount >=  500000 THEN SET discount = total_amount * 0.05;
    ELSE                                SET discount = 0;
    END IF;
    RETURN discount;
END$$

DELIMITER ;

-- ── 7. TRIGGERS ──────────────────────────────────────────

DELIMITER $$

CREATE TRIGGER trg_reserve_table
AFTER INSERT ON Reservations
FOR EACH ROW
BEGIN
    IF NEW.Status = 'confirmed' THEN
        UPDATE Tables
        SET    Status = 'reserved'
        WHERE  TableID = NEW.TableID;
    END IF;
END$$

CREATE TRIGGER trg_release_table_on_cancel
AFTER UPDATE ON Reservations
FOR EACH ROW
BEGIN
    IF NEW.Status = 'cancelled' AND OLD.Status = 'confirmed' THEN
        UPDATE Tables
        SET    Status = 'available'
        WHERE  TableID = NEW.TableID;
    END IF;
END$$

DELIMITER ;

-- ── 8. VERIFY ────────────────────────────────────────────
SHOW TABLES;
SHOW FULL TABLES WHERE Table_type = 'VIEW';
SHOW PROCEDURE STATUS WHERE Db = 'restaurant_db';
SHOW FUNCTION  STATUS WHERE Db = 'restaurant_db';
SHOW TRIGGERS  FROM restaurant_db;