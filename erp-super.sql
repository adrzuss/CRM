-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         8.0.42 - MySQL Community Server - GPL
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.7.0.6850
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para erp
CREATE DATABASE IF NOT EXISTS `erp` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `erp`;

-- Volcando estructura para procedimiento erp.actualizar_precios_por_compra
DELIMITER //
CREATE PROCEDURE `actualizar_precios_por_compra`(

	IN `idfacc` INT

)
BEGIN

    DECLARE done INT DEFAULT 0;

    DECLARE done_listas INT DEFAULT 0;

    DECLARE v_idarticulo INT;

    DECLARE v_costo DECIMAL(10,2);

    DECLARE v_idlista INT;

    DECLARE v_markup DECIMAL(10,2);



    -- Cursor para recorrer la tabla de artículos

    DECLARE compra_cursor CURSOR FOR

        SELECT idarticulo, precio_unitario FROM itemsc

        WHERE idfactura = idfacc;



    -- Cursor para recorrer la tabla de listas de precios

    DECLARE listas_cursor CURSOR FOR

        SELECT id, markup FROM listas_precio;



    -- Declaración de handler para salir del bucle del cursor

    DECLARE CONTINUE HANDLER FOR NOT FOUND 

    BEGIN

        IF done = 0 THEN

            SET done = 1;

        ELSE

            SET done_listas = 1;

        END IF;

    END;



    OPEN compra_cursor;



    leer_articulo: LOOP

        FETCH compra_cursor INTO v_idarticulo, v_costo;



        IF done THEN

            LEAVE leer_articulo;

        END IF;



        -- Abrir el cursor de listas de precios

        SET done_listas = 0;

        OPEN listas_cursor;



        leer_listas: LOOP

            FETCH listas_cursor INTO v_idlista, v_markup;



            IF done_listas THEN

                LEAVE leer_listas;

            END IF;



            -- Insertar o actualizar el precio en la tabla de precios

            INSERT INTO precios (idlista, idarticulo, precio)

            VALUES (v_idlista, v_idarticulo, v_costo * v_markup)

            ON DUPLICATE KEY UPDATE precio = v_costo * v_markup;

        END LOOP;



        CLOSE listas_cursor;

    END LOOP;



    CLOSE compra_cursor;

END//
DELIMITER ;

-- Volcando estructura para procedimiento erp.actualizar_precios_por_lista
DELIMITER //
CREATE PROCEDURE `actualizar_precios_por_lista`(IN p_idlista INT, IN p_markup DECIMAL(10,2))
BEGIN

    DECLARE done INT DEFAULT 0;

    DECLARE v_idarticulo INT;

    DECLARE v_costo DECIMAL(10,2);

    

    -- Cursor para recorrer la tabla de artículos

    DECLARE articulo_cursor CURSOR FOR

        SELECT id, costo FROM articulos;



    -- Declaración de handler para salir del bucle del cursor

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;



    OPEN articulo_cursor;



    leer_articulo: LOOP

        FETCH articulo_cursor INTO v_idarticulo, v_costo;

        

        IF done THEN

            LEAVE leer_articulo;

        END IF;



        -- Insertar o actualizar el precio en la tabla de precios

        INSERT INTO precios (idlista, idarticulo, precio)

        VALUES (p_idlista, v_idarticulo, v_costo * p_markup)

        ON DUPLICATE KEY UPDATE precio = v_costo * p_markup;

        

    END LOOP;



    CLOSE articulo_cursor;

END//
DELIMITER ;

-- Volcando estructura para tabla erp.alc_ib
CREATE TABLE IF NOT EXISTS `alc_ib` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `alicuota` decimal(20,6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.alc_iva
CREATE TABLE IF NOT EXISTS `alc_iva` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `alicuota` decimal(20,6) NOT NULL DEFAULT '0.000000',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.articulos
CREATE TABLE IF NOT EXISTS `articulos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) NOT NULL,
  `detalle` varchar(200) NOT NULL,
  `costo` decimal(20,6) NOT NULL,
  `idiva` int DEFAULT NULL,
  `exento` decimal(20,6) NOT NULL,
  `impint` decimal(20,6) NOT NULL,
  `idib` int DEFAULT NULL,
  `idmarca` int DEFAULT NULL,
  `idrubro` int DEFAULT NULL,
  `idtipoarticulo` int DEFAULT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `es_compuesto` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idiva` (`idiva`),
  KEY `idib` (`idib`),
  KEY `idmarca` (`idmarca`),
  KEY `idrubro` (`idrubro`),
  KEY `idtipoarticulo` (`idtipoarticulo`),
  CONSTRAINT `articulos_ibfk_1` FOREIGN KEY (`idiva`) REFERENCES `alc_iva` (`id`),
  CONSTRAINT `articulos_ibfk_2` FOREIGN KEY (`idib`) REFERENCES `alc_ib` (`id`),
  CONSTRAINT `articulos_ibfk_3` FOREIGN KEY (`idmarca`) REFERENCES `marcas` (`id`),
  CONSTRAINT `articulos_ibfk_4` FOREIGN KEY (`idrubro`) REFERENCES `rubros` (`id`),
  CONSTRAINT `articulos_ibfk_5` FOREIGN KEY (`idtipoarticulo`) REFERENCES `tipo_articulos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.art_compuesto
CREATE TABLE IF NOT EXISTS `art_compuesto` (
  `idarticulo` int NOT NULL,
  `idart_comp` int NOT NULL,
  `cantidad` decimal(20,6) NOT NULL,
  PRIMARY KEY (`idarticulo`,`idart_comp`),
  KEY `idart_comp` (`idart_comp`),
  CONSTRAINT `art_compuesto_ibfk_1` FOREIGN KEY (`idarticulo`) REFERENCES `articulos` (`id`),
  CONSTRAINT `art_compuesto_ibfk_2` FOREIGN KEY (`idart_comp`) REFERENCES `articulos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.balance
CREATE TABLE IF NOT EXISTS `balance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `idtipo_balance` int DEFAULT NULL,
  `idsucursal` int DEFAULT NULL,
  `idusuario` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idtipo_balance` (`idtipo_balance`),
  KEY `idsucursal` (`idsucursal`),
  KEY `idusuario` (`idusuario`),
  CONSTRAINT `balance_ibfk_1` FOREIGN KEY (`idtipo_balance`) REFERENCES `tipo_balances` (`id`),
  CONSTRAINT `balance_ibfk_2` FOREIGN KEY (`idsucursal`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `balance_ibfk_3` FOREIGN KEY (`idusuario`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.cambio_precios
CREATE TABLE IF NOT EXISTS `cambio_precios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `idsucursal` int DEFAULT NULL,
  `idusuario` int DEFAULT NULL,
  `idlista` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idsucursal` (`idsucursal`),
  KEY `idusuario` (`idusuario`),
  KEY `idlista` (`idlista`),
  CONSTRAINT `cambio_precios_ibfk_1` FOREIGN KEY (`idsucursal`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `cambio_precios_ibfk_2` FOREIGN KEY (`idusuario`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `cambio_precios_ibfk_3` FOREIGN KEY (`idlista`) REFERENCES `listas_precio` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.clientes
CREATE TABLE IF NOT EXISTS `clientes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) DEFAULT NULL,
  `documento` varchar(13) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` varchar(100) DEFAULT NULL,
  `ctacte` tinyint(1) DEFAULT NULL,
  `baja` datetime NOT NULL,
  `id_tipo_doc` int DEFAULT NULL,
  `id_tipo_iva` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_tipo_doc` (`id_tipo_doc`),
  KEY `id_tipo_iva` (`id_tipo_iva`),
  CONSTRAINT `clientes_ibfk_1` FOREIGN KEY (`id_tipo_doc`) REFERENCES `tipo_doc` (`id`),
  CONSTRAINT `clientes_ibfk_2` FOREIGN KEY (`id_tipo_iva`) REFERENCES `tipo_iva` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.configuracion
CREATE TABLE IF NOT EXISTS `configuracion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre_propietario` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `nombre_fantasia` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `tipo_iva` int NOT NULL,
  `tipo_documento` int NOT NULL,
  `documento` varchar(13) COLLATE utf8mb4_general_ci NOT NULL,
  `telefono` varchar(30) COLLATE utf8mb4_general_ci NOT NULL,
  `mail` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `clave` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `vencimiento` date NOT NULL,
  `licencia` varchar(200) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.cta_cte_cli
CREATE TABLE IF NOT EXISTS `cta_cte_cli` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idcliente` int NOT NULL,
  `fecha` date NOT NULL,
  `debe` decimal(20,6) DEFAULT NULL,
  `haber` decimal(20,6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idcliente` (`idcliente`),
  CONSTRAINT `cta_cte_cli_ibfk_1` FOREIGN KEY (`idcliente`) REFERENCES `clientes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.cta_cte_prov
CREATE TABLE IF NOT EXISTS `cta_cte_prov` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idproveedor` int NOT NULL,
  `fecha` date NOT NULL,
  `debe` decimal(20,6) NOT NULL,
  `haber` decimal(20,6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idproveedor` (`idproveedor`),
  CONSTRAINT `cta_cte_prov_ibfk_1` FOREIGN KEY (`idproveedor`) REFERENCES `proveedores` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.entidades
CREATE TABLE IF NOT EXISTS `entidades` (
  `id` int NOT NULL AUTO_INCREMENT,
  `entidad` varchar(200) COLLATE utf8mb4_general_ci NOT NULL,
  `telefono` varchar(200) COLLATE utf8mb4_general_ci NOT NULL,
  `baja` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.facturac
CREATE TABLE IF NOT EXISTS `facturac` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idproveedor` int NOT NULL,
  `fecha` date NOT NULL,
  `total` decimal(20,6) NOT NULL,
  `iva` decimal(20,6) NOT NULL,
  `exento` decimal(20,6) NOT NULL,
  `impint` decimal(20,6) NOT NULL,
  `idsucursal` int DEFAULT NULL,
  `idtipocomprobante` int DEFAULT NULL,
  `idusuario` int DEFAULT NULL,
  `idplancuenta` int DEFAULT NULL,
  `nro_comprobante` varchar(13) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idproveedor` (`idproveedor`),
  KEY `idsucursal` (`idsucursal`),
  KEY `idtipocomprobante` (`idtipocomprobante`),
  KEY `idusuario` (`idusuario`),
  KEY `idplancuenta` (`idplancuenta`),
  CONSTRAINT `facturac_ibfk_1` FOREIGN KEY (`idproveedor`) REFERENCES `proveedores` (`id`),
  CONSTRAINT `facturac_ibfk_2` FOREIGN KEY (`idsucursal`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `facturac_ibfk_3` FOREIGN KEY (`idtipocomprobante`) REFERENCES `tipo_comprobantes` (`id`),
  CONSTRAINT `facturac_ibfk_4` FOREIGN KEY (`idusuario`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `facturac_ibfk_5` FOREIGN KEY (`idplancuenta`) REFERENCES `plan_ctas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.facturav
CREATE TABLE IF NOT EXISTS `facturav` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idcliente` int NOT NULL,
  `idlista` int NOT NULL,
  `fecha` date NOT NULL,
  `total` decimal(20,6) NOT NULL,
  `iva` decimal(20,6) NOT NULL,
  `exento` decimal(20,6) NOT NULL,
  `impint` decimal(20,6) NOT NULL,
  `idtipocomprobante` int DEFAULT NULL,
  `idsucursal` int DEFAULT NULL,
  `idusuario` int DEFAULT NULL,
  `nro_comprobante` varchar(13) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idcliente` (`idcliente`),
  KEY `idlista` (`idlista`),
  KEY `idtipocomprobante` (`idtipocomprobante`),
  KEY `idsucursal` (`idsucursal`),
  KEY `idusuario` (`idusuario`),
  CONSTRAINT `facturav_ibfk_1` FOREIGN KEY (`idcliente`) REFERENCES `clientes` (`id`),
  CONSTRAINT `facturav_ibfk_2` FOREIGN KEY (`idlista`) REFERENCES `listas_precio` (`id`),
  CONSTRAINT `facturav_ibfk_3` FOREIGN KEY (`idtipocomprobante`) REFERENCES `tipo_comprobantes` (`id`),
  CONSTRAINT `facturav_ibfk_4` FOREIGN KEY (`idsucursal`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `facturav_ibfk_5` FOREIGN KEY (`idusuario`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para procedimiento erp.get_stock_faltantes
DELIMITER //
CREATE PROCEDURE `get_stock_faltantes`(

	IN `sucursal` INT

)
BEGIN

  SELECT a.id, a.codigo, a.detalle, s.actual

  FROM articulos a

  JOIN stocks s

    ON a.id = s.idarticulo

  where

    a.idtipoarticulo IN (1, 3) AND /*solo productos e insumos*/

	 s.idsucursal = sucursal AND 

	 s.actual > 0 AND 

	 s.deseable > 0 AND

	 s.deseable > s.actual;  



END//
DELIMITER ;

-- Volcando estructura para procedimiento erp.get_stock_negativos
DELIMITER //
CREATE PROCEDURE `get_stock_negativos`(

	IN `sucursal` INT

)
BEGIN

  SELECT a.id, a.codigo, a.detalle, s.actual

  FROM articulos a

  JOIN stocks s

    ON a.id = s.idarticulo

  where

    a.idtipoarticulo IN (1, 3) AND /*solo productos e insumos*/

	 s.idsucursal = sucursal AND 

	 s.actual < 0;  



END//
DELIMITER ;

-- Volcando estructura para procedimiento erp.get_vta_sucursales
DELIMITER //
CREATE PROCEDURE `get_vta_sucursales`(

	IN `desde` DATE,

	IN `hasta` DATE

)
BEGIN

  SELECT s.nombre, SUM(v.total) as total, COUNT(v.id) AS operaciones, AVG(v.total) op_promedio

  FROM facturav v

  JOIN sucursales s ON v.idsucursal = s.id

  where

    v.fecha BETWEEN desde AND hasta

  GROUP BY s.nombre;  

END//
DELIMITER ;

-- Volcando estructura para procedimiento erp.get_vta_vendedores
DELIMITER //
CREATE PROCEDURE `get_vta_vendedores`(

	IN `desde` DATE,

	IN `hasta` DATE

)
BEGIN

  SELECT u.nombre, SUM(v.total) as total, COUNT(v.id) AS operaciones, AVG(v.total) op_promedio

  FROM facturav v

  JOIN usuarios u ON v.idusuario = u.id

  where

    v.fecha BETWEEN desde AND hasta

  GROUP BY u.nombre; 



END//
DELIMITER ;

-- Volcando estructura para tabla erp.itemsc
CREATE TABLE IF NOT EXISTS `itemsc` (
  `idfactura` int NOT NULL,
  `id` int NOT NULL,
  `idarticulo` int NOT NULL,
  `cantidad` decimal(20,6) NOT NULL,
  `precio_unitario` decimal(20,6) NOT NULL,
  `precio_total` decimal(20,6) NOT NULL,
  `iva` decimal(20,6) NOT NULL,
  `idalciva` int NOT NULL,
  `exento` decimal(20,6) NOT NULL,
  `impint` decimal(20,6) NOT NULL,
  PRIMARY KEY (`idfactura`,`id`),
  KEY `idarticulo` (`idarticulo`),
  KEY `idalciva` (`idalciva`),
  CONSTRAINT `itemsc_ibfk_1` FOREIGN KEY (`idfactura`) REFERENCES `facturac` (`id`),
  CONSTRAINT `itemsc_ibfk_2` FOREIGN KEY (`idarticulo`) REFERENCES `articulos` (`id`),
  CONSTRAINT `itemsc_ibfk_3` FOREIGN KEY (`idalciva`) REFERENCES `alc_iva` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.itemsv
CREATE TABLE IF NOT EXISTS `itemsv` (
  `idfactura` int NOT NULL,
  `id` int NOT NULL,
  `idarticulo` int NOT NULL,
  `cantidad` decimal(20,6) NOT NULL,
  `precio_unitario` decimal(20,6) NOT NULL,
  `precio_total` decimal(20,6) NOT NULL,
  `iva` decimal(20,6) NOT NULL,
  `idalciva` int NOT NULL,
  `ingbto` decimal(20,6) NOT NULL,
  `idingbto` int NOT NULL,
  `exento` decimal(20,6) NOT NULL,
  `impint` decimal(20,6) NOT NULL,
  PRIMARY KEY (`idfactura`,`id`),
  KEY `idarticulo` (`idarticulo`),
  KEY `idalciva` (`idalciva`),
  KEY `idingbto` (`idingbto`),
  CONSTRAINT `itemsv_ibfk_1` FOREIGN KEY (`idfactura`) REFERENCES `facturav` (`id`),
  CONSTRAINT `itemsv_ibfk_2` FOREIGN KEY (`idarticulo`) REFERENCES `articulos` (`id`),
  CONSTRAINT `itemsv_ibfk_3` FOREIGN KEY (`idalciva`) REFERENCES `alc_iva` (`id`),
  CONSTRAINT `itemsv_ibfk_4` FOREIGN KEY (`idingbto`) REFERENCES `alc_ib` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.item_balance
CREATE TABLE IF NOT EXISTS `item_balance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idbalance` int DEFAULT NULL,
  `idarticulo` int NOT NULL,
  `cantidad` decimal(20,6) NOT NULL,
  `precio_unitario` decimal(20,6) NOT NULL,
  `precio_total` decimal(20,6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idbalance` (`idbalance`),
  KEY `idarticulo` (`idarticulo`),
  CONSTRAINT `item_balance_ibfk_1` FOREIGN KEY (`idbalance`) REFERENCES `balance` (`id`),
  CONSTRAINT `item_balance_ibfk_2` FOREIGN KEY (`idarticulo`) REFERENCES `articulos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.item_cambio_precios
CREATE TABLE IF NOT EXISTS `item_cambio_precios` (
  `idcambioprecio` int NOT NULL,
  `id` int NOT NULL,
  `idarticulo` int NOT NULL,
  `precio_de` decimal(20,6) NOT NULL,
  `precio_a` decimal(20,6) NOT NULL,
  PRIMARY KEY (`idcambioprecio`,`id`),
  KEY `idarticulo` (`idarticulo`),
  CONSTRAINT `item_cambio_precios_ibfk_1` FOREIGN KEY (`idcambioprecio`) REFERENCES `cambio_precios` (`id`),
  CONSTRAINT `item_cambio_precios_ibfk_2` FOREIGN KEY (`idarticulo`) REFERENCES `articulos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.item_remito_sucs
CREATE TABLE IF NOT EXISTS `item_remito_sucs` (
  `idremito` int NOT NULL,
  `id` int NOT NULL,
  `idarticulo` int NOT NULL,
  `cantidad` decimal(20,6) DEFAULT NULL,
  PRIMARY KEY (`idremito`,`id`,`idarticulo`),
  KEY `idarticulo` (`idarticulo`),
  CONSTRAINT `item_remito_sucs_ibfk_1` FOREIGN KEY (`idremito`) REFERENCES `remito_sucursales` (`id`),
  CONSTRAINT `item_remito_sucs_ibfk_2` FOREIGN KEY (`idarticulo`) REFERENCES `articulos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.listas_precio
CREATE TABLE IF NOT EXISTS `listas_precio` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `markup` decimal(20,6) NOT NULL DEFAULT '0.000000',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para procedimiento erp.lst_compuesto
DELIMITER //
CREATE PROCEDURE `lst_compuesto`()
    COMMENT 'lista los artículos compuesto'
BEGIN



		SELECT distinct a.id, a.codigo, a.detalle, m.nombre AS marca, r.nombre AS rubro

		FROM articulos a

		JOIN art_compuesto ac

			ON ac.idarticulo = a.id

		LEFT JOIN marcas m

			ON m.id = a.idmarca

		LEFT JOIN rubros r

			ON r.id = a.idrubro;

END//
DELIMITER ;

-- Volcando estructura para tabla erp.marcas
CREATE TABLE IF NOT EXISTS `marcas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para procedimiento erp.mas_vendidos
DELIMITER //
CREATE PROCEDURE `mas_vendidos`(

	IN `sucursal` INT,

	IN `desde` DATE,

	IN `hasta` DATE,

	IN `cant_registros` INT

)
BEGIN

	SELECT  a.codigo, a.detalle, SUM(i.cantidad) AS cantidad

	FROM articulos a

	JOIN itemsv i ON a.id = i.idarticulo

	JOIN facturav f ON i.idfactura = f.id

	where

	   f.idsucursal = sucursal AND

		f.fecha BETWEEN desde AND hasta

	GROUP BY a.codigo, a.detalle

	ORDER BY cantidad desc

	LIMIT cant_registros;



END//
DELIMITER ;

-- Volcando estructura para tabla erp.pagos_cobros
CREATE TABLE IF NOT EXISTS `pagos_cobros` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pagos_cobros` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.pagos_fc
CREATE TABLE IF NOT EXISTS `pagos_fc` (
  `idfactura` int NOT NULL,
  `idpago` int NOT NULL,
  `tipo` int NOT NULL,
  `total` decimal(20,6) NOT NULL,
  PRIMARY KEY (`idfactura`,`idpago`),
  CONSTRAINT `pagos_fc_ibfk_1` FOREIGN KEY (`idfactura`) REFERENCES `facturac` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.pagos_fv
CREATE TABLE IF NOT EXISTS `pagos_fv` (
  `idfactura` int NOT NULL,
  `idpago` int NOT NULL,
  `tipo` int NOT NULL,
  `total` decimal(20,6) NOT NULL,
  `entidad` int NOT NULL,
  PRIMARY KEY (`idfactura`,`idpago`),
  CONSTRAINT `pagos_fv_ibfk_1` FOREIGN KEY (`idfactura`) REFERENCES `facturav` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.plan_ctas
CREATE TABLE IF NOT EXISTS `plan_ctas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.precios
CREATE TABLE IF NOT EXISTS `precios` (
  `idlista` int NOT NULL,
  `idarticulo` int NOT NULL,
  `precio` decimal(20,6) NOT NULL,
  `ult_modificacion` datetime NOT NULL,
  PRIMARY KEY (`idlista`,`idarticulo`),
  KEY `idarticulo` (`idarticulo`),
  CONSTRAINT `precios_ibfk_1` FOREIGN KEY (`idlista`) REFERENCES `listas_precio` (`id`),
  CONSTRAINT `precios_ibfk_2` FOREIGN KEY (`idarticulo`) REFERENCES `articulos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.proveedores
CREATE TABLE IF NOT EXISTS `proveedores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `documento` varchar(13) DEFAULT NULL,
  `direccion` varchar(80) DEFAULT NULL,
  `id_tipo_doc` int DEFAULT NULL,
  `id_tipo_iva` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_tipo_doc` (`id_tipo_doc`),
  KEY `id_tipo_iva` (`id_tipo_iva`),
  CONSTRAINT `proveedores_ibfk_1` FOREIGN KEY (`id_tipo_doc`) REFERENCES `tipo_doc` (`id`),
  CONSTRAINT `proveedores_ibfk_2` FOREIGN KEY (`id_tipo_iva`) REFERENCES `tipo_iva` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.puntos_venta
CREATE TABLE IF NOT EXISTS `puntos_venta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `punto_vta` int NOT NULL,
  `idsucursal` int NOT NULL,
  `ultima_fac_a` int NOT NULL,
  `ultima_fac_b` int NOT NULL,
  `ultima_tkt` int NOT NULL,
  `ultima_fac_c` int NOT NULL,
  `ultima_deb_a` int NOT NULL,
  `ultima_deb_b` int NOT NULL,
  `ultima_deb_c` int NOT NULL,
  `ultima_nc_a` int NOT NULL,
  `ultima_nc_b` int NOT NULL,
  `ultima_nc_c` int NOT NULL,
  `ultimo_rem_x` int NOT NULL,
  `ultimo_rec_x` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idsucursal` (`idsucursal`),
  CONSTRAINT `puntos_venta_ibfk_1` FOREIGN KEY (`idsucursal`) REFERENCES `sucursales` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.remito_sucursales
CREATE TABLE IF NOT EXISTS `remito_sucursales` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idsucursal` int NOT NULL,
  `iddestino` int NOT NULL,
  `idusuario` int NOT NULL,
  `fecha` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idsucursal` (`idsucursal`),
  KEY `iddestino` (`iddestino`),
  KEY `idusuario` (`idusuario`),
  CONSTRAINT `remito_sucursales_ibfk_1` FOREIGN KEY (`idsucursal`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `remito_sucursales_ibfk_2` FOREIGN KEY (`iddestino`) REFERENCES `sucursales` (`id`),
  CONSTRAINT `remito_sucursales_ibfk_3` FOREIGN KEY (`idusuario`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.rubros
CREATE TABLE IF NOT EXISTS `rubros` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.stocks
CREATE TABLE IF NOT EXISTS `stocks` (
  `idstock` int NOT NULL,
  `idarticulo` int NOT NULL,
  `idsucursal` int NOT NULL,
  `actual` decimal(20,6) NOT NULL,
  `maximo` decimal(20,6) DEFAULT NULL,
  `deseable` decimal(20,6) DEFAULT NULL,
  PRIMARY KEY (`idstock`,`idarticulo`,`idsucursal`),
  KEY `idarticulo` (`idarticulo`),
  KEY `idsucursal` (`idsucursal`),
  CONSTRAINT `stocks_ibfk_1` FOREIGN KEY (`idarticulo`) REFERENCES `articulos` (`id`),
  CONSTRAINT `stocks_ibfk_2` FOREIGN KEY (`idsucursal`) REFERENCES `sucursales` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.sucursales
CREATE TABLE IF NOT EXISTS `sucursales` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `direccion` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `telefono` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `alta` datetime NOT NULL,
  `baja` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.tareas
CREATE TABLE IF NOT EXISTS `tareas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tarea` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.tareas_usuario
CREATE TABLE IF NOT EXISTS `tareas_usuario` (
  `idtarea` int NOT NULL,
  `idusuario` int NOT NULL,
  PRIMARY KEY (`idtarea`,`idusuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.tipo_articulos
CREATE TABLE IF NOT EXISTS `tipo_articulos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(30) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.tipo_balances
CREATE TABLE IF NOT EXISTS `tipo_balances` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.tipo_comprobantes
CREATE TABLE IF NOT EXISTS `tipo_comprobantes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_afip` int NOT NULL DEFAULT '0',
  `nombre` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.tipo_comp_aplica
CREATE TABLE IF NOT EXISTS `tipo_comp_aplica` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_iva_owner` int NOT NULL,
  `id_iva_entidad` int NOT NULL,
  `id_tipo_comp` int NOT NULL,
  `id_tipo_oper` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_iva_owner` (`id_iva_owner`),
  KEY `FK_iva_entidad` (`id_iva_entidad`),
  KEY `FK_tipo_oper` (`id_tipo_oper`),
  KEY `FK_tipo_comp` (`id_tipo_comp`) USING BTREE,
  CONSTRAINT `FK_iva_entidad` FOREIGN KEY (`id_iva_entidad`) REFERENCES `tipo_iva` (`id`),
  CONSTRAINT `FK_iva_owner` FOREIGN KEY (`id_iva_owner`) REFERENCES `tipo_iva` (`id`),
  CONSTRAINT `FK_tipo_comp` FOREIGN KEY (`id_tipo_comp`) REFERENCES `tipo_comprobantes` (`id`),
  CONSTRAINT `FK_tipo_oper` FOREIGN KEY (`id_tipo_oper`) REFERENCES `tipo_operacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.tipo_doc
CREATE TABLE IF NOT EXISTS `tipo_doc` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `id_afip` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.tipo_iva
CREATE TABLE IF NOT EXISTS `tipo_iva` (
  `id` int NOT NULL,
  `descripcion` varchar(50) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para tabla erp.tipo_operacion
CREATE TABLE IF NOT EXISTS `tipo_operacion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para procedimiento erp.ultimas_10_ventas
DELIMITER //
CREATE PROCEDURE `ultimas_10_ventas`(

	IN `sucursal` INT

)
BEGIN



	SELECT f.id, c.nombre, f.total, u.nombre

	FROM facturav f

	JOIN clientes c

		ON f.idcliente = c.id

	JOIN usuarios u

		ON f.idusuario = u.id	

	where

		f.fecha = CURDATE() and

		f.idsucursal = sucursal

	ORDER BY f.id	

	DESC LIMIT 10;

END//
DELIMITER ;

-- Volcando estructura para tabla erp.usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `usuario` varchar(80) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `clave` varchar(200) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `documento` varchar(13) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `telefono` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `direccion` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- La exportación de datos fue deseleccionada.

-- Volcando estructura para procedimiento erp.venta_articulos
DELIMITER //
CREATE PROCEDURE `venta_articulos`(

	IN `desde` DATE,

	IN `hasta` DATE

)
BEGIN

	SELECT

		  a.id,

		  a.codigo,

		  a.detalle,

        SUM(i.cantidad) AS cantidad_total,

        SUM(i.precio_total) AS total_ventas

    FROM

        facturav f

    INNER JOIN itemsv i ON f.id = i.idfactura

    INNER JOIN articulos a ON i.idarticulo = a.id

   WHERE

      f.fecha BETWEEN DATE(desde) AND DATE(hasta)

    GROUP BY

        a.id, a.codigo, a.detalle;

	

END//
DELIMITER ;

-- Volcando estructura para procedimiento erp.venta_clientes
DELIMITER //
CREATE PROCEDURE `venta_clientes`(

	IN `desde` DATE,

	IN `hasta` DATE

)
BEGIN

	SELECT

		  c.id,

		  c.nombre,

        COUNT(f.id) AS cantidad_total,

        SUM(f.total) AS total_ventas

    FROM

        facturav f

    INNER JOIN clientes c ON f.idcliente = c.id

   WHERE

      f.fecha BETWEEN DATE(desde) AND DATE(hasta)

    GROUP BY

        c.id, c.nombre;

	

END//
DELIMITER ;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
