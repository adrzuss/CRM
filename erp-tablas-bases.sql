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

-- Volcando estructura para tabla erp.alc_ib
CREATE TABLE IF NOT EXISTS `alc_ib` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `alicuota` decimal(20,6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla erp.alc_ib: ~2 rows (aproximadamente)
REPLACE INTO `alc_ib` (`id`, `descripcion`, `alicuota`) VALUES
	(1, 'Tasa de comercio', 3.000000),
	(2, 'Tasa de industria', 1.500000);

-- Volcando estructura para tabla erp.alc_iva
CREATE TABLE IF NOT EXISTS `alc_iva` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `alicuota` decimal(20,6) NOT NULL DEFAULT '0.000000',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla erp.alc_iva: ~3 rows (aproximadamente)
REPLACE INTO `alc_iva` (`id`, `descripcion`, `alicuota`) VALUES
	(1, 'IVA 21', 21.000000),
	(2, 'IVA 10,5', 10.500000),
	(3, 'IVA 27', 27.000000);

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

-- Volcando datos para la tabla erp.configuracion: ~1 rows (aproximadamente)
REPLACE INTO `configuracion` (`id`, `nombre_propietario`, `nombre_fantasia`, `tipo_iva`, `tipo_documento`, `documento`, `telefono`, `mail`, `clave`, `vencimiento`, `licencia`) VALUES
	(1, 'Carolina Mañe', 'Fly Estética', 2, 1, '20218767401', '2645836223', 'adrzuss@gmail.com', 'lvzp dana lypt gxqd', '2025-09-13', '1234');

-- Volcando estructura para tabla erp.entidades
CREATE TABLE IF NOT EXISTS `entidades` (
  `id` int NOT NULL AUTO_INCREMENT,
  `entidad` varchar(200) COLLATE utf8mb4_general_ci NOT NULL,
  `telefono` varchar(200) COLLATE utf8mb4_general_ci NOT NULL,
  `baja` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla erp.entidades: ~2 rows (aproximadamente)
REPLACE INTO `entidades` (`id`, `entidad`, `telefono`, `baja`) VALUES
	(1, 'Visa', '1234', '0000-00-00'),
	(2, 'Master', '231221323', '0000-00-00');

-- Volcando estructura para tabla erp.listas_precio
CREATE TABLE IF NOT EXISTS `listas_precio` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `markup` decimal(20,6) NOT NULL DEFAULT '0.000000',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla erp.listas_precio: ~3 rows (aproximadamente)
REPLACE INTO `listas_precio` (`id`, `nombre`, `markup`) VALUES
	(1, 'Contado', 1.500000),
	(2, 'Tarjeta', 2.000000),
	(3, 'Mercado libre', 2.200000);

-- Volcando estructura para tabla erp.pagos_cobros
CREATE TABLE IF NOT EXISTS `pagos_cobros` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pagos_cobros` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp.pagos_cobros: ~0 rows (aproximadamente)

-- Volcando estructura para tabla erp.plan_ctas
CREATE TABLE IF NOT EXISTS `plan_ctas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla erp.plan_ctas: ~6 rows (aproximadamente)
REPLACE INTO `plan_ctas` (`id`, `nombre`) VALUES
	(1, 'Alquileres'),
	(2, 'Telefono'),
	(3, 'Energia electrica'),
	(4, 'Libreria'),
	(5, 'Limpieza'),
	(6, 'Mercadería');

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

-- Volcando datos para la tabla erp.puntos_venta: ~4 rows (aproximadamente)
REPLACE INTO `puntos_venta` (`id`, `punto_vta`, `idsucursal`, `ultima_fac_a`, `ultima_fac_b`, `ultima_tkt`, `ultima_fac_c`, `ultima_deb_a`, `ultima_deb_b`, `ultima_deb_c`, `ultima_nc_a`, `ultima_nc_b`, `ultima_nc_c`, `ultimo_rem_x`, `ultimo_rec_x`) VALUES
	(1, 1, 1, 0, 0, 6, 10, 0, 0, 1, 0, 0, 1, 2, 1),
	(2, 2, 2, 0, 0, 0, 3, 0, 0, 1, 0, 0, 1, 2, 3),
	(3, 3, 1, 0, 0, 0, 4, 0, 0, 1, 0, 0, 1, 0, 0),
	(4, 4, 2, 0, 0, 0, 3, 0, 0, 1, 0, 0, 1, 0, 0);

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

-- Volcando datos para la tabla erp.sucursales: ~2 rows (aproximadamente)
REPLACE INTO `sucursales` (`id`, `nombre`, `direccion`, `telefono`, `email`, `alta`, `baja`) VALUES
	(1, 'Fly estética Tucuman', 'tucuman', '1234', 'flyestetica@gmail.com', '2024-11-27 15:00:17', '0000-00-00 00:00:00'),
	(2, 'Fly estética Laprida', 'tucuman', '12345', 'flyestetica@gmail.com', '2024-11-28 08:18:31', '0000-00-00 00:00:00');

-- Volcando estructura para tabla erp.tareas
CREATE TABLE IF NOT EXISTS `tareas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tarea` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla erp.tareas: ~5 rows (aproximadamente)
REPLACE INTO `tareas` (`id`, `tarea`) VALUES
	(1, 'Supervisor'),
	(2, 'Administrativo'),
	(3, 'Cajero'),
	(4, 'Vendedor'),
	(5, 'Deposito');

-- Volcando estructura para tabla erp.tareas_usuario
CREATE TABLE IF NOT EXISTS `tareas_usuario` (
  `idtarea` int NOT NULL,
  `idusuario` int NOT NULL,
  PRIMARY KEY (`idtarea`,`idusuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp.tareas_usuario: ~0 rows (aproximadamente)

-- Volcando estructura para tabla erp.tipo_articulos
CREATE TABLE IF NOT EXISTS `tipo_articulos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(30) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla erp.tipo_articulos: ~3 rows (aproximadamente)
REPLACE INTO `tipo_articulos` (`id`, `nombre`) VALUES
	(1, 'Producto'),
	(2, 'Servicio'),
	(3, 'Insumo');

-- Volcando estructura para tabla erp.tipo_balances
CREATE TABLE IF NOT EXISTS `tipo_balances` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla erp.tipo_balances: ~2 rows (aproximadamente)
REPLACE INTO `tipo_balances` (`id`, `nombre`) VALUES
	(1, 'Balance'),
	(2, 'Ajuste');

-- Volcando estructura para tabla erp.tipo_comprobantes
CREATE TABLE IF NOT EXISTS `tipo_comprobantes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_afip` int NOT NULL DEFAULT '0',
  `nombre` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla erp.tipo_comprobantes: ~12 rows (aproximadamente)
REPLACE INTO `tipo_comprobantes` (`id`, `id_afip`, `nombre`) VALUES
	(1, 0, 'A'),
	(2, 0, 'B'),
	(3, 0, 'C'),
	(4, 0, 'TKT'),
	(5, 0, 'CRED A'),
	(6, 0, 'CRED B'),
	(7, 0, 'CRED C'),
	(8, 0, 'DEB A'),
	(9, 0, 'DEB B'),
	(10, 0, 'DEB C'),
	(11, 0, 'REM X'),
	(12, 0, 'REC X');

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

-- Volcando datos para la tabla erp.tipo_comp_aplica: ~8 rows (aproximadamente)
REPLACE INTO `tipo_comp_aplica` (`id`, `id_iva_owner`, `id_iva_entidad`, `id_tipo_comp`, `id_tipo_oper`) VALUES
	(1, 2, 1, 3, 1),
	(2, 2, 2, 3, 1),
	(3, 2, 3, 3, 1),
	(4, 2, 4, 3, 1),
	(5, 2, 1, 1, 2),
	(6, 2, 2, 3, 2),
	(7, 2, 3, 4, 2),
	(8, 2, 4, 2, 2);

-- Volcando estructura para tabla erp.tipo_doc
CREATE TABLE IF NOT EXISTS `tipo_doc` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `id_afip` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla erp.tipo_doc: ~3 rows (aproximadamente)
REPLACE INTO `tipo_doc` (`id`, `nombre`, `id_afip`) VALUES
	(1, 'DNI', 96),
	(2, 'CUIL', 86),
	(3, 'CUIT', 80);

-- Volcando estructura para tabla erp.tipo_iva
CREATE TABLE IF NOT EXISTS `tipo_iva` (
  `id` int NOT NULL,
  `descripcion` varchar(50) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla erp.tipo_iva: ~4 rows (aproximadamente)
REPLACE INTO `tipo_iva` (`id`, `descripcion`) VALUES
	(1, 'Responsable inscripto'),
	(2, 'Monotributista'),
	(3, 'Consumidor final'),
	(4, 'Exento');

-- Volcando estructura para tabla erp.tipo_operacion
CREATE TABLE IF NOT EXISTS `tipo_operacion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla erp.tipo_operacion: ~6 rows (aproximadamente)
REPLACE INTO `tipo_operacion` (`id`, `nombre`) VALUES
	(1, 'VENTA'),
	(2, 'COMPRA'),
	(3, 'CREDITO'),
	(4, 'DEBITO'),
	(5, 'REMITO'),
	(6, 'RECIBO');

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

-- Volcando datos para la tabla erp.usuarios: ~5 rows (aproximadamente)
REPLACE INTO `usuarios` (`id`, `nombre`, `usuario`, `clave`, `documento`, `email`, `telefono`, `direccion`) VALUES
	(2, 'Alejandra', 'alegram', '1234', '22117091', 'alegram@live.com.ar', '2645127842', 'Sta Lucia'),
	(3, 'Adrian', 'adrzuss', '1234', '21876740', 'adrzuss@gmail.com', '2645836223', 'Saavedra'),
	(5, 'Franco', 'franco', '1234', '123456', 'franco@gmail.com', '123456', 'Saavedra'),
	(6, 'Giuliana', 'giuli', '1234', '123456', 'giuliana@gmail.com', '123456', 'Saavedra'),
	(7, 'Gino', 'gino', '1234', '21876740', 'giuliana@gmail.com', '1234', 'Saavedra');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
