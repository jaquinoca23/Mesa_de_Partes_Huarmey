-- Crea el usuario y la base de datos del proyecto en PostgreSQL.
-- Se ejecuta UNA SOLA VEZ, con el usuario administrador "postgres" (ver database/README.md).
--
-- ANTES DE EJECUTAR: reemplaza CAMBIAR_ESTA_CLAVE por una contraseña propia.
-- No subas a GitHub este archivo con tu contraseña real escrita.

-- Usuario propio del proyecto (no se usa "postgres" en la aplicación).
-- CREATEDB permite que Django cree una base temporal al ejecutar las pruebas automáticas.
CREATE USER mesa_partes_user WITH PASSWORD 'CAMBIAR_ESTA_CLAVE' CREATEDB;

-- Base de datos con codificación UTF8 (acentos y ñ), propiedad de ese usuario.
CREATE DATABASE mesa_partes_huarmey
    OWNER mesa_partes_user
    ENCODING 'UTF8'
    TEMPLATE template0;
