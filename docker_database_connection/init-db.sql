DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'distribuidos2025') THEN
      CREATE DATABASE distribuidos2025;
   END IF;
END
$$;

\connect distribuidos2025

DO
$$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'grupo1') THEN
      CREATE USER grupo1 WITH ENCRYPTED PASSWORD 'altaclavesecreta';
   END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE distribuidos2025 TO grupo1;

CREATE TABLE IF NOT EXISTS cliente (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS producto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    precio NUMERIC
);

CREATE TABLE IF NOT EXISTS venta (
    id SERIAL PRIMARY KEY,
    id_cliente INTEGER REFERENCES cliente(id),
    id_producto INTEGER REFERENCES producto(id),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO cliente (nombre, email) VALUES
('Juan Pérez', 'juan@example.com'),
('Ana Gómez', 'ana@example.com'),
('Carlos Ruiz', 'carlos@example.com')
ON CONFLICT DO NOTHING;

INSERT INTO producto (nombre, precio) VALUES
('Notebook', 1500),
('Celular', 900),
('Tablet', 600)
ON CONFLICT DO NOTHING;

INSERT INTO venta (id_cliente, id_producto) VALUES
(1, 2),
(2, 1),
(3, 3)
ON CONFLICT DO NOTHING;
