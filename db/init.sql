IF DB_ID('VentasDB') IS NULL
    CREATE DATABASE VentasDB;
GO
USE VentasDB;
GO

IF OBJECT_ID('orden_detalle','U') IS NOT NULL DROP TABLE orden_detalle;
IF OBJECT_ID('orden','U') IS NOT NULL DROP TABLE orden;
GO

CREATE TABLE orden (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cliente NVARCHAR(100) NOT NULL,
    fecha DATETIME DEFAULT GETDATE(),
    total DECIMAL(10,2) DEFAULT 0
);

CREATE TABLE orden_detalle (
    id INT IDENTITY(1,1) PRIMARY KEY,
    orden_id INT NOT NULL,
    producto NVARCHAR(100) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    CONSTRAINT FK_orden_detalle_orden
        FOREIGN KEY (orden_id) REFERENCES orden(id) ON DELETE CASCADE
);
GO

INSERT INTO orden (cliente, total) VALUES ('Cliente Demo 1', 150.00);
INSERT INTO orden_detalle (orden_id, producto, cantidad, precio_unitario)
VALUES (1, 'Producto A', 2, 75.00);
GO
