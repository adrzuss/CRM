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


-- Volcando estructura de base de datos para erp-super
CREATE DATABASE IF NOT EXISTS `erp-super` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `erp-super`;

-- Volcando estructura para tabla erp-super.alc_ib
CREATE TABLE IF NOT EXISTS `alc_ib` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(100) NOT NULL,
  `alicuota` decimal(20,6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.alc_ib: ~2 rows (aproximadamente)
REPLACE INTO `alc_ib` (`id`, `descripcion`, `alicuota`) VALUES
	(1, 'Tasa de comercio', 3.000000),
	(2, 'Tasa de industria', 1.500000);

-- Volcando estructura para tabla erp-super.alc_iva
CREATE TABLE IF NOT EXISTS `alc_iva` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(100) NOT NULL,
  `alicuota` decimal(20,6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.alc_iva: ~4 rows (aproximadamente)
REPLACE INTO `alc_iva` (`id`, `descripcion`, `alicuota`) VALUES
	(0, 'Sin IVA', 0.000000),
	(1, 'IVA 21', 21.000000),
	(2, 'IVA 10,5', 10.500000),
	(3, 'IVA 27', 27.000000);

-- Volcando estructura para tabla erp-super.articulos
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
  `costo_total` decimal(20,6) NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.articulos: ~59 rows (aproximadamente)
REPLACE INTO `articulos` (`id`, `codigo`, `detalle`, `costo`, `idiva`, `exento`, `impint`, `idib`, `idmarca`, `idrubro`, `idtipoarticulo`, `imagen`, `es_compuesto`, `costo_total`) VALUES
	(1, '7791290795570', 'Antigrasa gatillo 500ml', 4200.000000, 1, 0.000000, 0.000000, 1, 8, 6, 1, 'cif-limpiador-liquido-gatillo-antigrasa.jpg', 0, 5082.000000),
	(2, '7798065440154', 'Vinagre de alcohol 1lt', 2300.000000, 1, 0.000000, 0.000000, 1, 9, 3, 1, 'Ambali_vinagre_alcohol.webp', 0, 2783.000000),
	(3, '7791290793750', 'Suavizante 900 ml', 1230.000000, 1, 0.000000, 0.000000, 1, 10, 6, 1, 'Suavizante-Vivere-Clasico-900ml.webp', 0, 1185.800000),
	(4, '4005900773821', 'Agua Micelar Rose Care quita maquillaje 400ml', 6780.000000, 1, 0.000000, 0.000000, 1, 11, 5, 1, 'agua_micelar_rose_careg.webp', 0, 8203.800000),
	(5, '4005808555727', 'Protector solar 30 fps', 4700.000000, 1, 0.000000, 0.000000, 1, 11, 5, 1, 'protector-solar-nivea-sun-protect-hydrate-fps-30-x-400-ml_imagen-1.webp', 0, 5687.000000),
	(6, '7792389000551', 'Mata mosca y mosquitos aerosol', 8700.000000, 1, 0.000000, 0.000000, 1, 12, 7, 1, 'aero-matamoscas-x5.png', 0, 10527.000000),
	(7, '7793147009199', 'Cerveza lata 473 cm3', 2300.000000, 1, 0.000000, 0.000000, 1, 13, 8, 1, 'Heineken_473s.jpeg', 0, 2783.000000),
	(8, '7790895003202', 'Agua Tónica 310ml', 2800.000000, 1, 0.000000, 0.000000, 1, 14, 9, 1, 'Agua-Tonica-Schweppes-310-Ml-_1.webp', 0, 3388.000000),
	(9, '7790990003138', 'Detergente 500ml', 3510.000000, 1, 0.000000, 0.000000, 1, 15, 6, 1, 'Magistral_500ml.webp', 0, 4222.900000),
	(10, '7702018913688', 'Desodorante gel power rusn', 6700.000000, 1, 0.000000, 0.000000, 1, 17, 5, 1, 'gillette_specialized_power_rusn.jpg', 0, 8107.000000),
	(11, '7790520981967', 'Limpiahornos', 7800.000000, 1, 0.000000, 0.000000, 1, 16, 6, 1, 'Mr.Musculo_limpiahornos.jpeg', 0, 9438.000000),
	(12, '7791290796058', 'Detergente desengrasante Bioactive Limon 1,25', 7800.000000, 1, 0.000000, 0.000000, 1, 8, 6, 1, 'detergente_cif_125.jpeg', 0, 9438.000000),
	(13, '7791290795792', 'Desinfectante de ambientes y superficies frescura citrica', 2980.000000, 1, 0.000000, 0.000000, 1, 8, 6, 1, 'Cif_desinfectante_frescura_citrica.png', 0, 3509.000000),
	(14, '77939113013689', 'Yogur sabor natural 140g', 670.000000, 1, 0.000000, 0.000000, 1, 19, 1, 1, 'YOGUR-ENTERO-SABOR-NATURAL-TREGAR-140-GR-1-49841.webp', 0, 810.700000),
	(15, '7791337007390', 'Yogur con cereales clásico 159g', 1200.000000, 1, 0.000000, 0.000000, 1, 7, 1, 1, 'YogurClasicoLS.jpg', 0, 1452.000000),
	(16, '7790360720122', 'Icadillo de carne 90g', 1200.000000, 1, 0.000000, 0.000000, 1, 21, 10, 1, 'picadillo_de_carne_la_blanca.webp', 0, 1452.000000),
	(17, '7791100000399', 'Bicarbonato de sodio 50g', 990.000000, 1, 0.000000, 0.000000, 1, 18, 3, 1, 'bicarbonato_chango.png', 0, 1197.900000),
	(18, '7794000006478', 'Mostaza original 250g', 4500.000000, 1, 0.000000, 0.000000, 1, 22, 3, 1, 'savora_original_250.webp', 0, 5445.000000),
	(19, '7790072001038', 'Salero x 500g Celusal', 3500.000000, 1, 0.000000, 0.000000, 1, 4, 3, 1, 'Salero500Celusal.jpg', 0, 4235.000000),
	(20, '7794000006072', 'Mayonesa clásica x 500g', 3500.000000, 1, 0.000000, 0.000000, 1, 24, 3, 1, 'helmanns_500g.webp', 0, 4235.000000),
	(21, '7794980362953', 'Pimienta en grano negra 25g', 780.000000, 1, 0.000000, 0.000000, 1, 23, 3, 1, 'Pimineta_yuspe.jpg', 0, 943.800000),
	(22, '7792104000163', 'Sal fina 500g', 690.000000, 1, 0.000000, 0.000000, 1, 25, 3, 1, 'Donasal_500.jpg', 0, 834.900000),
	(23, '7791176218711', 'Garbanzos 400g', 670.000000, 1, 0.000000, 0.000000, 1, 27, 11, 1, 'garbanzos_cadea.webp', 0, 810.700000),
	(24, '7790220000043', 'Harina de trigo 000 1 kg', 1200.000000, 1, 0.000000, 0.000000, 1, 5, 2, 1, 'GracielaReal_000_1.jpg', 0, 1452.000000),
	(25, '7791290795471', 'Ultra brillo multisuperficies 400ml', 3200.000000, 1, 0.000000, 0.000000, 1, 8, 6, 1, 'cif-limpiador-liquido-ultra-brillo-anti-polvo.jpg', 0, 3872.000000),
	(26, '7790150330166', 'Te Manzanilla 25 saquitos', 2300.000000, 1, 0.000000, 0.000000, 1, 3, 12, 1, 'Manzanilla_25_squitos.jpg', 0, 2783.000000),
	(27, '7790150310267', 'Te Boldo 25 saquitos', 2300.000000, 1, 0.000000, 0.000000, 1, 3, 12, 1, 'images.jpeg', 0, 2783.000000),
	(28, '7790150250327', 'Te rosa mosqueta y manzanilla x 25', 2300.000000, 1, 0.000000, 0.000000, 1, 3, 12, 1, 'La_virginia_te_mansanilla_y_rosa_mosquetas.webp', 0, 2783.000000),
	(29, '7790387800159', 'Te en saquitos x 100', 6800.000000, 1, 0.000000, 0.000000, 1, 20, 12, 1, 'Te_taragui_100.webp', 0, 8228.000000),
	(30, '7790070318381', 'Fideos letritas 500g', 1500.000000, 1, 0.000000, 0.000000, 1, 6, 13, 1, 'Lucchetti-fideos-letritas-x-500-grs-1596117028-0-0.png', 0, 1815.000000),
	(31, '7790070336453', 'Fideos tirabuzón x 500g', 2450.000000, 1, 0.000000, 0.000000, 1, 29, 13, 1, 'fideos-tirabuzon-terrabusi-500g.jpg', 0, 2964.500000),
	(32, '7790070318671', 'Fideos nido fettuccine x 500g', 2450.000000, 1, 0.000000, 0.000000, 1, 30, 13, 1, 'fettuccine_nido.webp', 0, 2964.500000),
	(33, '7798028020508', 'Yerba mate 1kg', 3870.000000, 1, 0.000000, 0.000000, 1, 2, 12, 1, '7721_0.jpeg', 0, 4682.700000),
	(34, '7793913013214', 'Queso crema light 190g', 3500.000000, 1, 0.000000, 0.000000, 1, 19, 1, 1, 'queso_crema_tregar.webp', 0, 4235.000000),
	(35, '7791337061439', 'Queso untable clásico 290g', 5230.000000, 1, 0.000000, 0.000000, 1, 7, 1, 1, 'La_sereinisima_queso_untable.png', 0, 6328.300000),
	(36, 'Trincha', 'Pan trincha unidad', 670.000000, 1, 0.000000, 0.000000, 1, 31, 4, 1, '', 0, 810.700000),
	(37, 'caserito', 'Pan estilo casero', 1300.000000, 1, 0.000000, 0.000000, 1, 31, 4, 1, '', 0, 1573.000000),
	(38, 'semita', 'Semita por unidad', 90.000000, 1, 0.000000, 0.000000, 1, 31, 4, 1, '', 0, 108.900000),
	(39, '7509552922318', 'Shampoo aloe hidra celan', 7900.000000, 1, 0.000000, 0.000000, 1, 32, 5, 1, 'Fructis__aloehidraclean.webp', 0, 9559.000000),
	(40, '7509552922295', 'Acondicionador aloe hidra celan', 7900.000000, 1, 0.000000, 0.000000, 1, 32, 5, 1, 'acondicionador_aleohidraclean.jpeg', 0, 9559.000000),
	(41, '7509552876536', 'Acondicionador hidra lyss', 7890.000000, 1, 0.000000, 0.000000, 1, 32, 5, 1, 'Fructis__hidralyss.webp', 0, 9546.900000),
	(42, '7790033285484', 'Acondicionador recarga nutritiva 600ml', 9800.000000, 1, 0.000000, 0.000000, 1, 32, 5, 1, 'Fructis_Recarganutritiva.webp', 0, 11858.000000),
	(43, '7500435162586', 'Shampoo protección caida 650ml', 12300.000000, 1, 0.000000, 0.000000, 1, 33, 5, 1, 'HeadShoulder_proteccioncaida.jpg', 0, 14883.000000),
	(44, '7790040147720', 'Galletas surtido', 4700.000000, 0, 0.000000, 0.000000, 1, 34, 14, 1, 'surtido_bagley.jpg', 0, 5687.000000),
	(45, 'maple grandre', 'Maple huevos grandes', 4200.000000, 0, 0.000000, 0.000000, 1, 35, 15, 1, '', 0, 5082.000000),
	(46, 'maple super', 'Maple huevos super', 4400.000000, 0, 0.000000, 0.000000, 1, 35, 15, 1, '', 0, 5324.000000),
	(47, 'maple mediano', 'Maple huevos medianos', 4200.000000, 0, 0.000000, 0.000000, 1, 35, 15, 1, '', 0, 5082.000000),
	(48, '7790070012050', 'Aceite girasol 900ml', 1200.000000, 1, 0.000000, 0.000000, 1, 36, 3, 1, 'Aceite-Cocinero-Girasol-X-900-Cc-1-244.jpg', 0, 1452.000000),
	(49, '7791664000033', 'Tapas para pacualina de hojaldre', 2300.000000, 1, 0.000000, 0.000000, 1, 37, 16, 1, 'pascualina-hojaldre.png', 0, 2783.000000),
	(50, '7790036006727', 'Extracto de tomate 133g', 2340.000000, 1, 0.000000, 0.000000, 1, 38, 17, 1, 'Extracto_tomate_baggio_133.jpeg', 0, 2831.400000),
	(51, '7798057860045', 'Espuma limpiadora', 3400.000000, 1, 0.000000, 0.000000, 1, 43, 6, 1, 'lem_espuma_limpiadora.webp', 0, 4114.000000),
	(52, '7791120032561', 'arroz largo fino 500g', 890.000000, 1, 0.000000, 0.000000, 1, 42, 11, 1, 'arroz_53_largo_fino_500.jpg', 0, 1076.900000),
	(53, '7790895000218', 'Retornable 2L sabor original', 1900.000000, 1, 0.000000, 0.000000, 1, 39, 9, 1, 'coca-cola-retornable-2-lt-.jpg', 0, 2299.000000),
	(54, '7791293027760', 'Eficient tlco desodorante', 2800.000000, 1, 0.000000, 0.000000, 1, 41, 5, 1, 'exona_eficient_200g.jpg', 0, 3388.000000),
	(55, '7790645002363', 'Atun desmenuzado al natural', 1200.000000, 1, 0.000000, 0.000000, 1, 40, 10, 1, 'Atun-Caracas-Desmenuzado-Natural-170-Gr-1-1633.webp', 0, 1452.000000),
	(56, '7790645001786', 'Atun en aceite y agua', 2300.000000, 1, 0.000000, 0.000000, 1, 40, 10, 1, 'atun_en_aceite_agua_caracas.jpg', 0, 2783.000000),
	(57, 'prepizza', 'Pre pizza 2 unidades', 3500.000000, 1, 0.000000, 0.000000, 1, 31, 4, 1, '', 0, 4235.000000),
	(58, '7794940000833', 'Edulcorante 200ml', 3450.000000, 1, 0.000000, 0.000000, 1, 45, 18, 1, 'hiletet_1200x1200.webp', 0, 4174.500000),
	(59, '7891000350157', 'Café instantaneo tradicional lata 120g', 7600.000000, 1, 0.000000, 0.000000, 1, 44, 12, 1, 'lata_nescafe.jpg', 0, 9196.000000);

-- Volcando estructura para tabla erp-super.art_compuesto
CREATE TABLE IF NOT EXISTS `art_compuesto` (
  `idarticulo` int NOT NULL,
  `idart_comp` int NOT NULL,
  `cantidad` decimal(20,6) NOT NULL,
  PRIMARY KEY (`idarticulo`,`idart_comp`),
  KEY `idart_comp` (`idart_comp`),
  CONSTRAINT `art_compuesto_ibfk_1` FOREIGN KEY (`idarticulo`) REFERENCES `articulos` (`id`),
  CONSTRAINT `art_compuesto_ibfk_2` FOREIGN KEY (`idart_comp`) REFERENCES `articulos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.art_compuesto: ~0 rows (aproximadamente)

-- Volcando estructura para tabla erp-super.balance
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

-- Volcando datos para la tabla erp-super.balance: ~0 rows (aproximadamente)

-- Volcando estructura para tabla erp-super.cambio_precios
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

-- Volcando datos para la tabla erp-super.cambio_precios: ~0 rows (aproximadamente)

-- Volcando estructura para tabla erp-super.clientes
CREATE TABLE IF NOT EXISTS `clientes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) DEFAULT NULL,
  `documento` varchar(13) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` varchar(100) DEFAULT NULL,
  `localidad` varchar(100) DEFAULT NULL,
  `provincia` varchar(100) DEFAULT NULL,
  `ctacte` tinyint(1) DEFAULT NULL,
  `baja` date NOT NULL,
  `id_tipo_doc` int DEFAULT NULL,
  `id_tipo_iva` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_tipo_doc` (`id_tipo_doc`),
  KEY `id_tipo_iva` (`id_tipo_iva`),
  CONSTRAINT `clientes_ibfk_1` FOREIGN KEY (`id_tipo_doc`) REFERENCES `tipo_doc` (`id`),
  CONSTRAINT `clientes_ibfk_2` FOREIGN KEY (`id_tipo_iva`) REFERENCES `tipo_iva` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.clientes: ~6 rows (aproximadamente)
REPLACE INTO `clientes` (`id`, `nombre`, `documento`, `email`, `telefono`, `direccion`, `localidad`, `provincia`, `ctacte`, `baja`, `id_tipo_doc`, `id_tipo_iva`) VALUES
	(1, 'Consumidor final', '11111111', '', '', 'nada', NULL, NULL, 0, '1900-01-01', 1, 3),
	(2, 'Adrian Zussino', '20218767401', '', '', 'Saavedra', NULL, NULL, 0, '1900-01-01', 3, 2),
	(3, 'Ricardo Castro', '22786345', '', '', 'San Luis', NULL, NULL, 1, '1900-01-01', 1, 3),
	(4, 'Miguel Perez', '11111111', '', '', 'sn', NULL, NULL, 1, '1900-01-01', 1, 3),
	(5, 'Mario Irrazabal', '11111111', '', '', 'sn', NULL, NULL, 1, '1900-01-01', 1, 3),
	(6, 'Carlos Vila', '31674324', '', '', 'mitre 38', NULL, NULL, 1, '1900-01-01', 1, 3);

-- Volcando estructura para tabla erp-super.configuracion
CREATE TABLE IF NOT EXISTS `configuracion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre_propietario` varchar(100) NOT NULL,
  `nombre_fantasia` varchar(100) NOT NULL,
  `direccion` varchar(200) NOT NULL,
  `localidad` varchar(100) NOT NULL,
  `provincia` varchar(100) NOT NULL,
  `tipo_iva` int NOT NULL,
  `tipo_documento` int NOT NULL,
  `documento` varchar(13) NOT NULL,
  `telefono` varchar(30) NOT NULL,
  `mail` varchar(100) NOT NULL,
  `clave` varchar(100) NOT NULL,
  `vencimiento` date NOT NULL,
  `licencia` varchar(200) NOT NULL,
  `paso_cert` varchar(200) DEFAULT NULL,
  `paso_key` varchar(200) DEFAULT NULL,
  `dias_vto_cta_cte` smallint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.configuracion: ~1 rows (aproximadamente)
REPLACE INTO `configuracion` (`id`, `nombre_propietario`, `nombre_fantasia`, `direccion`, `localidad`, `provincia`, `tipo_iva`, `tipo_documento`, `documento`, `telefono`, `mail`, `clave`, `vencimiento`, `licencia`, `paso_cert`, `paso_key`, `dias_vto_cta_cte`) VALUES
	(1, 'José Perez', 'El Super Mercado', 'Siempre Viva 123', 'Localidad', 'San Juan', 2, 1, '20218767401', '264', 'elsupermercado@elsupermercado.com.ar', 'lvzp dana lypt gxqd', '2025-09-13', '1234', 'AdrianZussino_55300e84f645e58b.crt', 'privada.key', 30);

-- Volcando estructura para tabla erp-super.cta_cte_cli
CREATE TABLE IF NOT EXISTS `cta_cte_cli` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idcliente` int NOT NULL,
  `fecha` date NOT NULL,
  `debe` decimal(20,6) DEFAULT NULL,
  `haber` decimal(20,6) DEFAULT NULL,
  `idcomp` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idcliente` (`idcliente`),
  CONSTRAINT `cta_cte_cli_ibfk_1` FOREIGN KEY (`idcliente`) REFERENCES `clientes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.cta_cte_cli: ~10 rows (aproximadamente)
REPLACE INTO `cta_cte_cli` (`id`, `idcliente`, `fecha`, `debe`, `haber`, `idcomp`) VALUES
	(1, 3, '2025-05-08', 34500.000000, 0.000000, 19),
	(2, 6, '2025-04-01', 35760.000000, 0.000000, NULL),
	(3, 6, '2025-04-02', 0.000000, 10760.000000, NULL),
	(4, 4, '2025-03-09', 10000.000000, 0.000000, NULL),
	(5, 5, '2025-04-02', 0.000000, 10000.000000, NULL),
	(6, 3, '2025-05-09', 0.000000, 30000.000000, NULL),
	(7, 3, '2025-05-01', 0.000000, 500.000000, NULL),
	(8, 6, '2025-05-05', 0.000000, 760.000000, NULL),
	(9, 6, '2025-05-06', 0.000000, 240.000000, 27),
	(15, 6, '2025-05-09', 0.000000, 4000.000000, 28),
	(16, 4, '2025-05-15', 8530.500000, 0.000000, 44);

-- Volcando estructura para tabla erp-super.cta_cte_prov
CREATE TABLE IF NOT EXISTS `cta_cte_prov` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idproveedor` int NOT NULL,
  `fecha` date NOT NULL,
  `debe` decimal(20,6) NOT NULL,
  `haber` decimal(20,6) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idproveedor` (`idproveedor`),
  CONSTRAINT `cta_cte_prov_ibfk_1` FOREIGN KEY (`idproveedor`) REFERENCES `proveedores` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.cta_cte_prov: ~6 rows (aproximadamente)
REPLACE INTO `cta_cte_prov` (`id`, `idproveedor`, `fecha`, `debe`, `haber`) VALUES
	(1, 1, '2025-04-15', 0.000000, 120000.000000),
	(2, 3, '2025-04-15', 0.000000, 405720.000000),
	(3, 5, '2025-04-10', 0.000000, 123500.000000),
	(4, 4, '2025-04-08', 0.000000, 56300.000000),
	(5, 1, '2025-05-05', 0.000000, 189500.000000),
	(6, 3, '2025-05-05', 0.000000, 130700.000000);

-- Volcando estructura para tabla erp-super.entidades
CREATE TABLE IF NOT EXISTS `entidades` (
  `id` int NOT NULL AUTO_INCREMENT,
  `entidad` varchar(200) NOT NULL,
  `telefono` varchar(200) NOT NULL,
  `baja` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.entidades: ~4 rows (aproximadamente)
REPLACE INTO `entidades` (`id`, `entidad`, `telefono`, `baja`) VALUES
	(1, 'Visa', '1234', '0000-00-00'),
	(2, 'Master', '231221323', '0000-00-00'),
	(3, 'Mercado pago', '1234', '1900-01-01'),
	(4, 'Naranja', '12345', '1900-01-01');

-- Volcando estructura para tabla erp-super.facturac
CREATE TABLE IF NOT EXISTS `facturac` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idproveedor` int NOT NULL,
  `fecha` date NOT NULL,
  `periodo` date NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.facturac: ~17 rows (aproximadamente)
REPLACE INTO `facturac` (`id`, `idproveedor`, `fecha`, `periodo`, `total`, `iva`, `exento`, `impint`, `idsucursal`, `idtipocomprobante`, `idusuario`, `idplancuenta`, `nro_comprobante`) VALUES
	(5, 1, '2025-04-28', '2025-04-28', 0.000000, 0.000000, 0.000000, 0.000000, 1, 11, 2, 0, '0001-00000001'),
	(6, 2, '2025-04-29', '2025-04-29', 0.000000, 0.000000, 0.000000, 0.000000, 1, 11, 2, 0, '0001-00000001'),
	(8, 2, '2025-04-29', '2025-04-01', 100000.000000, 0.000000, 0.000000, 0.000000, 1, 1, 2, 6, '0002-00000001'),
	(9, 2, '2025-04-29', '2025-04-01', 1000.000000, 0.000000, 0.000000, 0.000000, 1, 1, 2, 6, '0002-00000002'),
	(10, 2, '2025-04-29', '2025-04-01', 1000.000000, 0.000000, 0.000000, 0.000000, 1, 1, 2, 6, '0002-00000003'),
	(11, 2, '2025-04-29', '2025-04-01', 1000.000000, 0.000000, 0.000000, 0.000000, 1, 1, 2, 6, '0002-00000004'),
	(12, 2, '2025-04-29', '2025-04-01', 1000.000000, 0.000000, 0.000000, 0.000000, 1, 1, 2, 6, '0002-00000005'),
	(13, 2, '2025-04-29', '2025-04-01', 1000.000000, 0.000000, 0.000000, 0.000000, 1, 1, 2, 6, '0002-00000006'),
	(14, 2, '2025-04-29', '2025-04-01', 1000.000000, 0.000000, 0.000000, 0.000000, 1, 1, 2, 6, '0002-00000007'),
	(15, 1, '2025-04-15', '2025-04-01', 120000.000000, 0.000000, 0.000000, 0.000000, 1, 1, 2, 6, '0002-00000001'),
	(16, 3, '2025-04-15', '2025-04-15', 0.000000, 0.000000, 0.000000, 0.000000, 1, 11, 2, 0, '0001-00000001'),
	(17, 3, '2025-04-15', '2025-04-01', 406720.000000, 0.000000, 0.000000, 0.000000, 1, 1, 2, 6, '0002-00000001'),
	(18, 5, '2025-04-10', '2025-04-01', 123500.000000, 0.000000, 0.000000, 0.000000, 1, 1, 2, 5, '0005-00000001'),
	(19, 4, '2025-04-08', '2025-04-01', 56300.000000, 0.000000, 0.000000, 0.000000, 1, 3, 2, 4, '0004-00000001'),
	(20, 1, '2025-05-05', '2025-05-05', 0.000000, 0.000000, 0.000000, 0.000000, 1, 11, 3, 0, '0023-00000235'),
	(21, 1, '2025-05-05', '2025-05-01', 189500.000000, 0.000000, 0.000000, 0.000000, 1, 1, 3, 6, '0023-00002345'),
	(22, 6, '2025-05-02', '2025-05-01', 230000.000000, 0.000000, 0.000000, 0.000000, 1, 1, 2, 3, '0124-00763985'),
	(23, 3, '2025-05-05', '2025-05-01', 130700.000000, 0.000000, 0.000000, 0.000000, 1, 1, 3, 6, '0030-00004231'),
	(24, 4, '2025-05-02', '2025-05-01', 20300.000000, 0.000000, 0.000000, 0.000000, 1, 1, 3, 4, '0004-00001098'),
	(25, 3, '2025-05-13', '2025-05-13', 0.000000, 0.000000, 0.000000, 0.000000, 1, 11, 3, 0, '0030-00003956');

-- Volcando estructura para tabla erp-super.facturav
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
  `punto_vta` int NOT NULL DEFAULT (0),
  `cae` varchar(20) DEFAULT NULL,
  `cae_vto` date DEFAULT NULL,
  `fecha_emision` date DEFAULT (curdate()),
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
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.facturav: ~43 rows (aproximadamente)
REPLACE INTO `facturav` (`id`, `idcliente`, `idlista`, `fecha`, `total`, `iva`, `exento`, `impint`, `idtipocomprobante`, `idsucursal`, `idusuario`, `nro_comprobante`, `punto_vta`, `cae`, `cae_vto`, `fecha_emision`) VALUES
	(1, 1, 1, '2025-04-28', 3255.000000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000016', 1, '75181233223281', '2025-05-15', '2025-05-05'),
	(2, 1, 1, '2025-04-28', 28500.000000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000013', 1, '75181233219789', '2025-05-15', '2025-05-05'),
	(3, 1, 1, '2025-04-28', 24060.000000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000015', 1, '75181233221425', '2025-05-15', '2025-05-05'),
	(4, 1, 1, '2025-04-29', 810.000000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000014', 1, '75181233221365', '2025-05-15', '2025-05-05'),
	(5, 1, 1, '2025-05-05', 7125.000000, 1236.570248, 0.000000, 0.000000, 3, 1, 2, '0001-00000017', 1, NULL, NULL, '2025-05-05'),
	(6, 1, 1, '2025-05-05', 3450.000000, 598.760331, 0.000000, 0.000000, 3, 1, 2, '0001-00000009', 1, NULL, NULL, NULL),
	(7, 1, 1, '2025-05-05', 11700.000000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000017', 1, '75181233242346', '2025-05-15', '2025-05-05'),
	(8, 1, 1, '2025-05-05', 5670.000000, 0.000000, 0.000000, 0.000000, 3, 1, 3, '0001-00000012', 1, NULL, NULL, NULL),
	(9, 1, 1, '2025-05-05', 15195.000000, 0.000000, 0.000000, 0.000000, 3, 1, 3, '0001-00000013', 1, NULL, NULL, NULL),
	(10, 1, 1, '2025-05-05', 9945.000000, 0.000000, 0.000000, 0.000000, 3, 2, 5, '0002-00000000', 2, NULL, NULL, NULL),
	(11, 1, 1, '2025-05-07', 5250.000000, 0.000000, 0.000000, 0.000000, 3, 1, 3, '0001-00000018', 1, '75191233459827', '2025-05-17', '2025-05-07'),
	(12, 1, 1, '2025-05-07', 11850.000000, 0.000000, 0.000000, 0.000000, 3, 1, 3, '0003-00000001', 3, '75191233476948', '2025-05-17', '2025-05-07'),
	(13, 1, 1, '2025-05-08', 16935.000000, 0.000000, 0.000000, 0.000000, 3, 1, 3, '0001-00000019', 1, '75191233572632', '2025-05-18', '2025-05-08'),
	(14, 1, 1, '2025-05-08', 7650.000000, 0.000000, 0.000000, 0.000000, 3, 1, 3, '0001-00000020', 1, '75191233572674', '2025-05-18', '2025-05-08'),
	(15, 1, 1, '2025-05-08', 3900.000000, 0.000000, 0.000000, 0.000000, 3, 1, 3, '0001-00000021', 1, '75191233572894', '2025-05-18', '2025-05-08'),
	(16, 1, 1, '2025-05-08', 13095.000000, 0.000000, 0.000000, 0.000000, 3, 1, 3, '0001-00000022', 1, '75191233573104', '2025-05-18', '2025-05-08'),
	(17, 1, 1, '2025-05-08', 10425.000000, 0.000000, 0.000000, 0.000000, 3, 1, 3, '0001-00000023', 1, '75191233573811', '2025-05-18', '2025-05-08'),
	(18, 3, 1, '2025-05-08', 20700.000000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000020', 1, NULL, NULL, NULL),
	(19, 3, 1, '2025-05-08', 34500.000000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000021', 1, NULL, NULL, NULL),
	(20, 2, 1, '2025-05-08', 6300.000000, 0.000000, 0.000000, 0.000000, 3, 2, 5, '0002-00000001', 2, NULL, NULL, NULL),
	(21, 4, 1, '2025-05-08', 7200.000000, 0.000000, 0.000000, 0.000000, 3, 2, 5, '0002-00000002', 2, NULL, NULL, NULL),
	(22, 1, 1, '2025-05-08', 13500.000000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000024', 1, '75191233672799', '2025-05-18', '2025-05-08'),
	(23, 1, 1, '2025-05-08', 26475.000000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000023', 1, NULL, NULL, NULL),
	(24, 3, 1, '2025-05-09', -30000.000000, 0.000000, 0.000000, 0.000000, 12, 1, 2, '0001-00000011', 1, NULL, NULL, NULL),
	(25, 3, 1, '2025-05-01', -500.000000, 0.000000, 0.000000, 0.000000, 12, 1, 2, '0001-00000012', 1, NULL, NULL, NULL),
	(26, 6, 1, '2025-05-05', -760.000000, 0.000000, 0.000000, 0.000000, 12, 1, 2, '0001-00000013', 1, NULL, NULL, NULL),
	(27, 6, 1, '2025-05-06', -240.000000, 0.000000, 0.000000, 0.000000, 12, 1, 2, '0001-00000014', 1, NULL, NULL, NULL),
	(28, 6, 1, '2025-05-09', -4000.000000, 0.000000, 0.000000, 0.000000, 12, 1, 2, '0001-00000015', 1, NULL, NULL, NULL),
	(29, 1, 1, '2025-05-12', 6663.000000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000024', 1, NULL, NULL, NULL),
	(30, 1, 1, '2025-05-12', 8421.600000, 0.000000, 0.000000, 0.000000, 3, 2, 3, '0002-00000003', 2, NULL, NULL, NULL),
	(31, 1, 1, '2025-05-12', 20100.000000, 0.000000, 0.000000, 0.000000, 3, 2, 5, '0004-00000000', 4, NULL, NULL, NULL),
	(32, 1, 1, '2025-05-13', 13394.700000, 0.000000, 0.000000, 0.000000, 3, 2, 5, '0002-00000004', 2, NULL, NULL, NULL),
	(33, 1, 1, '2025-05-13', 10599.600000, 0.000000, 0.000000, 0.000000, 3, 2, 5, '0002-00000005', 2, NULL, NULL, NULL),
	(34, 1, 1, '2025-05-13', 11507.100000, 0.000000, 0.000000, 0.000000, 3, 2, 5, '0002-00000006', 2, NULL, NULL, NULL),
	(35, 1, 1, '2025-05-15', 11797.500000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0003-00000003', 3, NULL, NULL, NULL),
	(42, 4, 1, '2025-05-15', 8530.500000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0003-00000010', 3, NULL, NULL, NULL),
	(44, 4, 1, '2025-05-15', 8530.500000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0003-00000012', 3, NULL, NULL, NULL),
	(45, 1, 1, '2025-05-16', 32924.100000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000025', 1, NULL, NULL, NULL),
	(46, 1, 1, '2025-05-30', 6352.500000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000026', 1, NULL, NULL, NULL),
	(47, 1, 1, '2025-05-30', 11071.500000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000027', 1, NULL, NULL, NULL),
	(48, 1, 1, '2025-06-02', 2178.000000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000025', 1, '75221245624320', '2025-06-12', '2025-06-02'),
	(49, 1, 1, '2025-06-02', 6171.000000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000026', 1, '75221245624524', '2025-06-12', '2025-06-02'),
	(50, 1, 1, '2025-06-02', 12160.500000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0003-00000002', 3, '75221245980587', '2025-06-12', '2025-06-02'),
	(62, 1, 1, '2025-06-03', 1216.050000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000041', 1, NULL, NULL, NULL),
	(63, 1, 1, '2025-06-03', 1216.050000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000042', 1, NULL, NULL, NULL),
	(64, 1, 1, '2025-06-04', 6352.500000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000043', 1, NULL, NULL, NULL),
	(65, 1, 1, '2025-06-04', 8167.500000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000044', 1, NULL, NULL, NULL),
	(66, 1, 1, '2025-06-04', 6152.850000, 0.000000, 0.000000, 0.000000, 3, 1, 2, '0001-00000045', 1, NULL, NULL, NULL);

-- Volcando estructura para tabla erp-super.itemsc
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

-- Volcando datos para la tabla erp-super.itemsc: ~31 rows (aproximadamente)
REPLACE INTO `itemsc` (`idfactura`, `id`, `idarticulo`, `cantidad`, `precio_unitario`, `precio_total`, `iva`, `idalciva`, `exento`, `impint`) VALUES
	(5, 0, 43, 10.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(5, 1, 10, 10.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(5, 2, 30, 12.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(6, 0, 38, 50.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(6, 1, 37, 12.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(6, 2, 36, 12.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(16, 0, 39, 10.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(16, 1, 43, 10.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(16, 2, 40, 8.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(16, 3, 41, 8.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(16, 4, 42, 8.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(17, 0, 39, 10.000000, 7900.000000, 79000.000000, 16590.000000, 1, 0.000000, 0.000000),
	(17, 1, 43, 10.000000, 12300.000000, 123000.000000, 25830.000000, 1, 0.000000, 0.000000),
	(17, 2, 40, 8.000000, 7900.000000, 63200.000000, 13272.000000, 1, 0.000000, 0.000000),
	(17, 3, 41, 8.000000, 7890.000000, 63120.000000, 13255.200000, 1, 0.000000, 0.000000),
	(17, 4, 42, 8.000000, 9800.000000, 78400.000000, 16464.000000, 1, 0.000000, 0.000000),
	(20, 0, 55, 10.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(20, 1, 56, 10.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(20, 2, 7, 24.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(20, 3, 30, 12.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(20, 4, 31, 12.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(20, 5, 32, 12.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(23, 0, 1, 7.000000, 4200.000000, 29400.000000, 6174.000000, 1, 0.000000, 0.000000),
	(23, 1, 3, 10.000000, 1230.000000, 12300.000000, 2583.000000, 1, 0.000000, 0.000000),
	(23, 2, 9, 10.000000, 3510.000000, 35100.000000, 7371.000000, 1, 0.000000, 0.000000),
	(23, 3, 11, 5.000000, 7800.000000, 39000.000000, 8190.000000, 1, 0.000000, 0.000000),
	(23, 4, 13, 5.000000, 2980.000000, 14900.000000, 3129.000000, 1, 0.000000, 0.000000),
	(25, 0, 2, 12.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(25, 1, 8, 12.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(25, 2, 17, 10.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000),
	(25, 3, 20, 12.000000, 0.000000, 0.000000, 0.000000, 0, 0.000000, 0.000000);

-- Volcando estructura para tabla erp-super.itemsv
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

-- Volcando datos para la tabla erp-super.itemsv: ~74 rows (aproximadamente)
REPLACE INTO `itemsv` (`idfactura`, `id`, `idarticulo`, `cantidad`, `precio_unitario`, `precio_total`, `iva`, `idalciva`, `ingbto`, `idingbto`, `exento`, `impint`) VALUES
	(1, 0, 36, 1.000000, 1216.050000, 1216.050000, 0.000000, 0, 36.481500, 1, 0.000000, 0.000000),
	(1, 1, 30, 1.000000, 2722.500000, 2722.500000, 0.000000, 0, 81.675000, 1, 0.000000, 0.000000),
	(2, 0, 43, 1.000000, 22324.500000, 22324.500000, 0.000000, 0, 669.735000, 1, 0.000000, 0.000000),
	(2, 1, 10, 1.000000, 12160.500000, 12160.500000, 0.000000, 0, 364.815000, 1, 0.000000, 0.000000),
	(3, 0, 29, 1.000000, 12342.000000, 12342.000000, 0.000000, 0, 370.260000, 1, 0.000000, 0.000000),
	(3, 1, 40, 1.000000, 14338.500000, 14338.500000, 0.000000, 0, 430.155000, 1, 0.000000, 0.000000),
	(3, 2, 36, 2.000000, 1216.050000, 2432.100000, 0.000000, 0, 72.963000, 1, 0.000000, 0.000000),
	(4, 0, 38, 6.000000, 163.350000, 980.100000, 0.000000, 0, 29.403000, 1, 0.000000, 0.000000),
	(5, 0, 26, 1.000000, 4174.500000, 4174.500000, 0.000000, 0, 125.235000, 1, 0.000000, 0.000000),
	(5, 1, 32, 1.000000, 4446.750000, 4446.750000, 0.000000, 0, 133.402500, 1, 0.000000, 0.000000),
	(6, 0, 7, 1.000000, 4174.500000, 4174.500000, 0.000000, 0, 125.235000, 1, 0.000000, 0.000000),
	(7, 0, 11, 1.000000, 14157.000000, 14157.000000, 0.000000, 0, 424.710000, 1, 0.000000, 0.000000),
	(8, 0, 3, 1.000000, 1778.700000, 1778.700000, 0.000000, 0, 53.361000, 1, 0.000000, 0.000000),
	(8, 1, 8, 1.000000, 5082.000000, 5082.000000, 0.000000, 0, 152.460000, 1, 0.000000, 0.000000),
	(9, 0, 35, 1.000000, 9492.450000, 9492.450000, 0.000000, 0, 284.773500, 1, 0.000000, 0.000000),
	(9, 1, 31, 2.000000, 4446.750000, 8893.500000, 0.000000, 0, 266.805000, 1, 0.000000, 0.000000),
	(10, 0, 21, 1.000000, 1415.700000, 1415.700000, 0.000000, 0, 42.471000, 1, 0.000000, 0.000000),
	(10, 1, 17, 2.000000, 1796.850000, 3593.700000, 0.000000, 0, 107.811000, 1, 0.000000, 0.000000),
	(10, 2, 33, 1.000000, 7024.050000, 7024.050000, 0.000000, 0, 210.721500, 1, 0.000000, 0.000000),
	(11, 0, 34, 1.000000, 6352.500000, 6352.500000, 0.000000, 0, 190.575000, 1, 0.000000, 0.000000),
	(12, 0, 40, 1.000000, 14338.500000, 14338.500000, 0.000000, 0, 430.155000, 1, 0.000000, 0.000000),
	(13, 0, 11, 1.000000, 14157.000000, 14157.000000, 0.000000, 0, 424.710000, 1, 0.000000, 0.000000),
	(13, 1, 9, 1.000000, 6334.350000, 6334.350000, 0.000000, 0, 190.030500, 1, 0.000000, 0.000000),
	(14, 0, 2, 1.000000, 4174.500000, 4174.500000, 0.000000, 0, 125.235000, 1, 0.000000, 0.000000),
	(14, 1, 8, 1.000000, 5082.000000, 5082.000000, 0.000000, 0, 152.460000, 1, 0.000000, 0.000000),
	(15, 0, 37, 2.000000, 2359.500000, 4719.000000, 0.000000, 0, 141.570000, 1, 0.000000, 0.000000),
	(16, 0, 35, 1.000000, 9492.450000, 9492.450000, 0.000000, 0, 284.773500, 1, 0.000000, 0.000000),
	(16, 1, 20, 1.000000, 6352.500000, 6352.500000, 0.000000, 0, 190.575000, 1, 0.000000, 0.000000),
	(17, 0, 3, 1.000000, 1778.700000, 1778.700000, 0.000000, 0, 53.361000, 1, 0.000000, 0.000000),
	(17, 1, 1, 1.000000, 7623.000000, 7623.000000, 0.000000, 0, 228.690000, 1, 0.000000, 0.000000),
	(17, 2, 21, 1.000000, 1415.700000, 1415.700000, 0.000000, 0, 42.471000, 1, 0.000000, 0.000000),
	(17, 3, 17, 1.000000, 1796.850000, 1796.850000, 0.000000, 0, 53.905500, 1, 0.000000, 0.000000),
	(18, 0, 7, 6.000000, 4174.500000, 25047.000000, 0.000000, 0, 751.410000, 1, 0.000000, 0.000000),
	(19, 0, 7, 10.000000, 4174.500000, 41745.000000, 0.000000, 0, 1252.350000, 1, 0.000000, 0.000000),
	(20, 0, 47, 1.000000, 7623.000000, 7623.000000, 0.000000, 0, 228.690000, 1, 0.000000, 0.000000),
	(21, 0, 37, 1.000000, 2359.500000, 2359.500000, 0.000000, 0, 70.785000, 1, 0.000000, 0.000000),
	(21, 1, 20, 1.000000, 6352.500000, 6352.500000, 0.000000, 0, 190.575000, 1, 0.000000, 0.000000),
	(22, 0, 46, 1.000000, 7986.000000, 7986.000000, 0.000000, 0, 239.580000, 1, 0.000000, 0.000000),
	(22, 1, 7, 2.000000, 4174.500000, 8349.000000, 0.000000, 0, 250.470000, 1, 0.000000, 0.000000),
	(23, 0, 43, 1.000000, 22324.500000, 22324.500000, 0.000000, 0, 669.735000, 1, 0.000000, 0.000000),
	(23, 1, 13, 1.000000, 5263.500000, 5263.500000, 0.000000, 0, 157.905000, 1, 0.000000, 0.000000),
	(23, 2, 31, 1.000000, 4446.750000, 4446.750000, 0.000000, 0, 133.402500, 1, 0.000000, 0.000000),
	(29, 0, 48, 1.000000, 2178.000000, 2178.000000, 0.000000, 0, 65.340000, 1, 0.000000, 0.000000),
	(29, 1, 2, 1.000000, 4174.500000, 4174.500000, 0.000000, 0, 125.235000, 1, 0.000000, 0.000000),
	(29, 2, 22, 1.000000, 1252.350000, 1252.350000, 0.000000, 0, 37.570500, 1, 0.000000, 0.000000),
	(30, 0, 49, 1.000000, 4174.500000, 4174.500000, 0.000000, 0, 125.235000, 1, 0.000000, 0.000000),
	(30, 1, 50, 1.000000, 4247.100000, 4247.100000, 0.000000, 0, 127.413000, 1, 0.000000, 0.000000),
	(31, 0, 46, 1.000000, 7986.000000, 7986.000000, 0.000000, 0, 239.580000, 1, 0.000000, 0.000000),
	(31, 1, 15, 1.000000, 2178.000000, 2178.000000, 0.000000, 0, 65.340000, 1, 0.000000, 0.000000),
	(31, 2, 12, 1.000000, 14157.000000, 14157.000000, 0.000000, 0, 424.710000, 1, 0.000000, 0.000000),
	(32, 0, 55, 2.000000, 2178.000000, 4356.000000, 0.000000, 0, 108.000000, 1, 0.000000, 0.000000),
	(32, 1, 21, 1.000000, 1415.700000, 1415.700000, 0.000000, 0, 35.100000, 1, 0.000000, 0.000000),
	(32, 2, 49, 1.000000, 4174.500000, 4174.500000, 0.000000, 0, 103.500000, 1, 0.000000, 0.000000),
	(32, 3, 53, 1.000000, 3448.500000, 3448.500000, 0.000000, 0, 85.500000, 1, 0.000000, 0.000000),
	(33, 0, 50, 1.000000, 4247.100000, 4247.100000, 0.000000, 0, 105.300000, 1, 0.000000, 0.000000),
	(33, 1, 57, 1.000000, 6352.500000, 6352.500000, 0.000000, 0, 157.500000, 1, 0.000000, 0.000000),
	(34, 0, 27, 1.000000, 4174.500000, 4174.500000, 0.000000, 0, 103.500000, 1, 0.000000, 0.000000),
	(34, 1, 38, 6.000000, 163.350000, 980.100000, 0.000000, 0, 24.300000, 1, 0.000000, 0.000000),
	(34, 2, 34, 1.000000, 6352.500000, 6352.500000, 0.000000, 0, 157.500000, 1, 0.000000, 0.000000),
	(35, 0, 53, 1.000000, 3448.500000, 3448.500000, 0.000000, 0, 85.500000, 1, 0.000000, 0.000000),
	(35, 1, 7, 2.000000, 4174.500000, 8349.000000, 0.000000, 0, 207.000000, 1, 0.000000, 0.000000),
	(42, 0, 5, 1.000000, 8530.500000, 8530.500000, 0.000000, 0, 211.500000, 1, 0.000000, 0.000000),
	(44, 0, 5, 1.000000, 8530.500000, 8530.500000, 0.000000, 0, 211.500000, 1, 0.000000, 0.000000),
	(45, 0, 57, 2.000000, 6352.500000, 12705.000000, 0.000000, 0, 315.000000, 1, 0.000000, 0.000000),
	(45, 1, 50, 1.000000, 4247.100000, 4247.100000, 0.000000, 0, 105.300000, 1, 0.000000, 0.000000),
	(45, 2, 7, 3.000000, 4174.500000, 12523.500000, 0.000000, 0, 310.500000, 1, 0.000000, 0.000000),
	(45, 3, 53, 1.000000, 3448.500000, 3448.500000, 0.000000, 0, 85.500000, 1, 0.000000, 0.000000),
	(46, 0, 24, 1.000000, 2178.000000, 2178.000000, 0.000000, 0, 54.000000, 1, 0.000000, 0.000000),
	(46, 1, 56, 1.000000, 4174.500000, 4174.500000, 0.000000, 0, 103.500000, 1, 0.000000, 0.000000),
	(47, 0, 28, 1.000000, 4174.500000, 4174.500000, 0.000000, 0, 103.500000, 1, 0.000000, 0.000000),
	(47, 1, 53, 2.000000, 3448.500000, 6897.000000, 0.000000, 0, 171.000000, 1, 0.000000, 0.000000),
	(48, 0, 24, 1.000000, 2178.000000, 2178.000000, 0.000000, 0, 54.000000, 1, 0.000000, 0.000000),
	(49, 0, 53, 1.000000, 3448.500000, 3448.500000, 0.000000, 0, 85.500000, 1, 0.000000, 0.000000),
	(49, 1, 30, 1.000000, 2722.500000, 2722.500000, 0.000000, 0, 67.500000, 1, 0.000000, 0.000000),
	(50, 0, 10, 1.000000, 12160.500000, 12160.500000, 0.000000, 0, 301.500000, 1, 0.000000, 0.000000),
	(62, 0, 23, 1.000000, 1216.050000, 1216.050000, 0.000000, 0, 30.150000, 1, 0.000000, 0.000000),
	(63, 0, 23, 1.000000, 1216.050000, 1216.050000, 0.000000, 0, 30.150000, 1, 0.000000, 0.000000),
	(64, 0, 20, 1.000000, 6352.500000, 6352.500000, 0.000000, 0, 157.500000, 1, 0.000000, 0.000000),
	(65, 0, 53, 1.000000, 3448.500000, 3448.500000, 0.000000, 0, 85.500000, 1, 0.000000, 0.000000),
	(65, 1, 37, 2.000000, 2359.500000, 4719.000000, 0.000000, 0, 117.000000, 1, 0.000000, 0.000000),
	(66, 0, 30, 1.000000, 2722.500000, 2722.500000, 0.000000, 0, 67.500000, 1, 0.000000, 0.000000),
	(66, 1, 22, 1.000000, 1252.350000, 1252.350000, 0.000000, 0, 31.050000, 1, 0.000000, 0.000000),
	(66, 2, 16, 1.000000, 2178.000000, 2178.000000, 0.000000, 0, 54.000000, 1, 0.000000, 0.000000);

-- Volcando estructura para tabla erp-super.item_balance
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

-- Volcando datos para la tabla erp-super.item_balance: ~0 rows (aproximadamente)

-- Volcando estructura para tabla erp-super.item_cambio_precios
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

-- Volcando datos para la tabla erp-super.item_cambio_precios: ~0 rows (aproximadamente)

-- Volcando estructura para tabla erp-super.item_remito_sucs
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

-- Volcando datos para la tabla erp-super.item_remito_sucs: ~0 rows (aproximadamente)

-- Volcando estructura para tabla erp-super.listas_precio
CREATE TABLE IF NOT EXISTS `listas_precio` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `markup` decimal(20,6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.listas_precio: ~3 rows (aproximadamente)
REPLACE INTO `listas_precio` (`id`, `nombre`, `markup`) VALUES
	(1, 'Contado', 1.500000),
	(2, 'Tarjeta', 2.000000),
	(3, 'Mercado libre', 2.200000);

-- Volcando estructura para tabla erp-super.marcas
CREATE TABLE IF NOT EXISTS `marcas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.marcas: ~40 rows (aproximadamente)
REPLACE INTO `marcas` (`id`, `nombre`) VALUES
	(1, 'El Super Mercado'),
	(2, 'La Posadeña'),
	(3, 'La Virginia'),
	(4, 'Celusal'),
	(5, 'Graciela Real'),
	(6, 'Lucchetti'),
	(7, 'La Serenisima'),
	(8, 'Cif'),
	(9, 'Ambalí'),
	(10, 'Vivere'),
	(11, 'Nivea'),
	(12, 'X-5'),
	(13, 'Heineken'),
	(14, 'Schweppes'),
	(15, 'Magistral'),
	(16, 'Mr. Musculo'),
	(17, 'Gillette'),
	(18, 'Chango'),
	(19, 'Tregar'),
	(20, 'Taragüí'),
	(21, 'La Blanca'),
	(22, 'Savora'),
	(23, 'Yuspe'),
	(24, 'Hellmann\'s'),
	(25, 'Doña sal'),
	(26, 'Graciela Real'),
	(27, 'Cadea'),
	(28, 'Legumpack'),
	(29, 'Terrabusi'),
	(30, 'Matarazzo'),
	(31, 'Panadería Lucia'),
	(32, 'Garnier'),
	(33, 'Head & Shoulders'),
	(34, 'Bagley'),
	(35, 'Avicola Gilardi'),
	(36, 'Cocinero'),
	(37, 'La Italiana'),
	(38, 'Baggio'),
	(39, 'Coca Cola'),
	(40, 'Caracas'),
	(41, 'Rexona'),
	(42, '53'),
	(43, 'Lem'),
	(44, 'Nescafe'),
	(45, 'Hileret');

-- Volcando estructura para tabla erp-super.pagos_cobros
CREATE TABLE IF NOT EXISTS `pagos_cobros` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pagos_cobros` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.pagos_cobros: ~2 rows (aproximadamente)
REPLACE INTO `pagos_cobros` (`id`, `pagos_cobros`) VALUES
	(1, 'Efectivo'),
	(2, 'Tarjeta de crédito'),
	(3, 'Cta. Cte.');

-- Volcando estructura para tabla erp-super.pagos_fc
CREATE TABLE IF NOT EXISTS `pagos_fc` (
  `idfactura` int NOT NULL,
  `idpago` int NOT NULL,
  `tipo` int NOT NULL,
  `total` decimal(20,6) NOT NULL,
  PRIMARY KEY (`idfactura`,`idpago`),
  CONSTRAINT `pagos_fc_ibfk_1` FOREIGN KEY (`idfactura`) REFERENCES `facturac` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.pagos_fc: ~14 rows (aproximadamente)
REPLACE INTO `pagos_fc` (`idfactura`, `idpago`, `tipo`, `total`) VALUES
	(8, 1, 1, 100000.000000),
	(9, 1, 1, 1000.000000),
	(10, 1, 1, 1000.000000),
	(11, 1, 1, 1000.000000),
	(12, 1, 1, 1000.000000),
	(13, 1, 1, 1000.000000),
	(14, 1, 1, 1000.000000),
	(15, 3, 3, 120000.000000),
	(17, 3, 3, 405720.000000),
	(18, 3, 3, 123500.000000),
	(19, 3, 3, 56300.000000),
	(21, 3, 3, 189500.000000),
	(22, 1, 1, 230000.000000),
	(23, 3, 3, 130700.000000),
	(24, 1, 1, 20300.000000);

-- Volcando estructura para tabla erp-super.pagos_fv
CREATE TABLE IF NOT EXISTS `pagos_fv` (
  `idfactura` int NOT NULL,
  `idpago` int NOT NULL,
  `tipo` int NOT NULL,
  `total` decimal(20,6) NOT NULL,
  `entidad` int NOT NULL,
  PRIMARY KEY (`idfactura`,`idpago`),
  CONSTRAINT `pagos_fv_ibfk_1` FOREIGN KEY (`idfactura`) REFERENCES `facturav` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.pagos_fv: ~40 rows (aproximadamente)
REPLACE INTO `pagos_fv` (`idfactura`, `idpago`, `tipo`, `total`, `entidad`) VALUES
	(1, 1, 1, 3255.000000, 0),
	(2, 2, 2, 28500.000000, 1),
	(3, 1, 1, 10000.000000, 0),
	(3, 2, 2, 14060.000000, 1),
	(4, 1, 1, 810.000000, 0),
	(5, 1, 1, 7125.000000, 0),
	(6, 1, 1, 3450.000000, 0),
	(7, 2, 2, 11700.000000, 1),
	(8, 2, 2, 5670.000000, 2),
	(9, 1, 1, 15195.000000, 0),
	(10, 2, 2, 9945.000000, 1),
	(11, 1, 1, 5250.000000, 0),
	(12, 2, 2, 11850.000000, 2),
	(13, 1, 1, 16935.000000, 0),
	(14, 2, 2, 7650.000000, 1),
	(15, 1, 1, 3900.000000, 0),
	(16, 1, 1, 13095.000000, 0),
	(17, 2, 2, 10425.000000, 2),
	(18, 2, 2, 20700.000000, 1),
	(19, 3, 3, 34500.000000, 0),
	(20, 1, 1, 6300.000000, 0),
	(21, 1, 1, 7200.000000, 0),
	(22, 1, 1, 13500.000000, 0),
	(23, 2, 2, 26475.000000, 1),
	(28, 1, 1, 4000.000000, 0),
	(29, 1, 1, 6663.000000, 0),
	(30, 2, 2, 8421.600000, 1),
	(31, 2, 2, 20100.000000, 2),
	(32, 1, 1, 13394.700000, 0),
	(33, 1, 1, 10599.600000, 0),
	(34, 1, 1, 11507.100000, 0),
	(35, 2, 2, 11797.500000, 1),
	(42, 1, 1, 8530.500000, 0),
	(44, 3, 3, 8530.500000, 0),
	(45, 2, 2, 32924.100000, 3),
	(46, 1, 1, 6352.500000, 0),
	(47, 2, 2, 11071.500000, 3),
	(48, 1, 1, 2178.000000, 0),
	(49, 2, 2, 6171.000000, 3),
	(50, 1, 1, 12160.500000, 0),
	(62, 1, 1, 1216.050000, 0),
	(63, 1, 1, 1216.050000, 0),
	(64, 1, 1, 6352.500000, 0),
	(65, 1, 1, 8167.500000, 0),
	(66, 2, 2, 6152.850000, 3);

-- Volcando estructura para tabla erp-super.plan_ctas
CREATE TABLE IF NOT EXISTS `plan_ctas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.plan_ctas: ~7 rows (aproximadamente)
REPLACE INTO `plan_ctas` (`id`, `nombre`) VALUES
	(0, 'Sin cuenta'),
	(1, 'Alquileres'),
	(2, 'Telefono'),
	(3, 'Energia electrica'),
	(4, 'Libreria'),
	(5, 'Limpieza'),
	(6, 'Mercadería');

-- Volcando estructura para tabla erp-super.precios
CREATE TABLE IF NOT EXISTS `precios` (
  `idlista` int NOT NULL,
  `idarticulo` int NOT NULL,
  `precio` decimal(20,6) NOT NULL,
  `ult_modificacion` date NOT NULL,
  PRIMARY KEY (`idlista`,`idarticulo`),
  KEY `idarticulo` (`idarticulo`),
  CONSTRAINT `precios_ibfk_1` FOREIGN KEY (`idlista`) REFERENCES `listas_precio` (`id`),
  CONSTRAINT `precios_ibfk_2` FOREIGN KEY (`idarticulo`) REFERENCES `articulos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.precios: ~156 rows (aproximadamente)
REPLACE INTO `precios` (`idlista`, `idarticulo`, `precio`, `ult_modificacion`) VALUES
	(1, 1, 7623.000000, '2025-05-13'),
	(1, 2, 4174.500000, '2025-05-13'),
	(1, 3, 1778.700000, '2025-05-13'),
	(1, 4, 12305.700000, '2025-05-13'),
	(1, 5, 8530.500000, '2025-05-13'),
	(1, 6, 15790.500000, '2025-05-13'),
	(1, 7, 4174.500000, '2025-05-13'),
	(1, 8, 5082.000000, '2025-05-13'),
	(1, 9, 6334.350000, '2025-05-13'),
	(1, 10, 12160.500000, '2025-05-13'),
	(1, 11, 14157.000000, '2025-05-13'),
	(1, 12, 14157.000000, '2025-05-13'),
	(1, 13, 5263.500000, '2025-05-13'),
	(1, 14, 1216.050000, '2025-05-13'),
	(1, 15, 2178.000000, '2025-05-13'),
	(1, 16, 2178.000000, '2025-05-13'),
	(1, 17, 1796.850000, '2025-05-13'),
	(1, 18, 8167.500000, '2025-05-13'),
	(1, 19, 6352.500000, '2025-05-13'),
	(1, 20, 6352.500000, '2025-05-13'),
	(1, 21, 1415.700000, '2025-05-13'),
	(1, 22, 1252.350000, '2025-05-13'),
	(1, 23, 1216.050000, '2025-05-13'),
	(1, 24, 2178.000000, '2025-05-13'),
	(1, 25, 5808.000000, '2025-05-13'),
	(1, 26, 4174.500000, '2025-05-13'),
	(1, 27, 4174.500000, '2025-05-13'),
	(1, 28, 4174.500000, '2025-05-13'),
	(1, 29, 12342.000000, '2025-05-13'),
	(1, 30, 2722.500000, '2025-05-13'),
	(1, 31, 4446.750000, '2025-05-13'),
	(1, 32, 4446.750000, '2025-05-13'),
	(1, 33, 7024.050000, '2025-05-13'),
	(1, 34, 6352.500000, '2025-05-13'),
	(1, 35, 9492.450000, '2025-05-13'),
	(1, 36, 1216.050000, '2025-05-13'),
	(1, 37, 2359.500000, '2025-05-13'),
	(1, 38, 163.350000, '2025-05-13'),
	(1, 39, 14338.500000, '2025-05-13'),
	(1, 40, 14338.500000, '2025-05-13'),
	(1, 41, 14320.350000, '2025-05-13'),
	(1, 42, 17787.000000, '2025-05-13'),
	(1, 43, 22324.500000, '2025-05-13'),
	(1, 44, 8530.500000, '2025-05-13'),
	(1, 45, 7623.000000, '2025-05-13'),
	(1, 46, 7986.000000, '2025-05-13'),
	(1, 47, 7623.000000, '2025-05-13'),
	(1, 48, 2178.000000, '2025-05-13'),
	(1, 49, 4174.500000, '2025-05-13'),
	(1, 50, 4247.100000, '2025-05-13'),
	(1, 51, 6171.000000, '2025-05-13'),
	(1, 52, 1615.350000, '2025-05-13'),
	(1, 53, 3448.500000, '2025-05-13'),
	(1, 54, 5082.000000, '2025-05-13'),
	(1, 55, 2178.000000, '2025-05-13'),
	(1, 56, 4174.500000, '2025-05-13'),
	(1, 57, 6352.500000, '2025-05-13'),
	(1, 58, 6261.750000, '2025-05-13'),
	(1, 59, 13794.000000, '2025-05-13'),
	(2, 1, 10164.000000, '2025-05-13'),
	(2, 2, 5566.000000, '2025-05-13'),
	(2, 3, 2371.600000, '2025-05-13'),
	(2, 4, 16407.600000, '2025-05-13'),
	(2, 5, 11374.000000, '2025-05-13'),
	(2, 6, 21054.000000, '2025-05-13'),
	(2, 7, 5566.000000, '2025-05-13'),
	(2, 8, 6776.000000, '2025-05-13'),
	(2, 9, 8445.800000, '2025-05-13'),
	(2, 10, 16214.000000, '2025-05-13'),
	(2, 11, 18876.000000, '2025-05-13'),
	(2, 12, 18876.000000, '2025-05-13'),
	(2, 13, 7018.000000, '2025-05-13'),
	(2, 14, 1621.400000, '2025-05-13'),
	(2, 15, 2904.000000, '2025-05-13'),
	(2, 16, 2904.000000, '2025-05-13'),
	(2, 17, 2395.800000, '2025-05-13'),
	(2, 18, 10890.000000, '2025-05-13'),
	(2, 19, 8470.000000, '2025-05-13'),
	(2, 20, 8470.000000, '2025-05-13'),
	(2, 21, 1887.600000, '2025-05-13'),
	(2, 22, 1669.800000, '2025-05-13'),
	(2, 23, 1621.400000, '2025-05-13'),
	(2, 24, 2904.000000, '2025-05-13'),
	(2, 25, 7744.000000, '2025-05-13'),
	(2, 26, 5566.000000, '2025-05-13'),
	(2, 27, 5566.000000, '2025-05-13'),
	(2, 28, 5566.000000, '2025-05-13'),
	(2, 29, 16456.000000, '2025-05-13'),
	(2, 30, 3630.000000, '2025-05-13'),
	(2, 31, 5929.000000, '2025-05-13'),
	(2, 32, 5929.000000, '2025-05-13'),
	(2, 33, 9365.400000, '2025-05-13'),
	(2, 34, 8470.000000, '2025-05-13'),
	(2, 35, 12656.600000, '2025-05-13'),
	(2, 36, 1621.400000, '2025-05-13'),
	(2, 37, 3146.000000, '2025-05-13'),
	(2, 38, 217.800000, '2025-05-13'),
	(2, 39, 19118.000000, '2025-05-13'),
	(2, 40, 19118.000000, '2025-05-13'),
	(2, 41, 19093.800000, '2025-05-13'),
	(2, 42, 23716.000000, '2025-05-13'),
	(2, 43, 29766.000000, '2025-05-13'),
	(2, 44, 11374.000000, '2025-05-13'),
	(2, 45, 10164.000000, '2025-05-13'),
	(2, 46, 10648.000000, '2025-05-13'),
	(2, 47, 10164.000000, '2025-05-13'),
	(2, 48, 2904.000000, '2025-05-13'),
	(2, 49, 5566.000000, '2025-05-13'),
	(2, 50, 5662.800000, '2025-05-13'),
	(2, 51, 8228.000000, '2025-05-13'),
	(2, 52, 2153.800000, '2025-05-13'),
	(2, 53, 4598.000000, '2025-05-13'),
	(2, 54, 6776.000000, '2025-05-13'),
	(2, 55, 2904.000000, '2025-05-13'),
	(2, 56, 5566.000000, '2025-05-13'),
	(2, 57, 8470.000000, '2025-05-13'),
	(2, 58, 8349.000000, '2025-05-13'),
	(2, 59, 18392.000000, '2025-05-13'),
	(3, 1, 11180.400000, '2025-05-13'),
	(3, 2, 6122.600000, '2025-05-13'),
	(3, 3, 2608.760000, '2025-05-13'),
	(3, 4, 18048.360000, '2025-05-13'),
	(3, 5, 12511.400000, '2025-05-13'),
	(3, 6, 23159.400000, '2025-05-13'),
	(3, 7, 6122.600000, '2025-05-13'),
	(3, 8, 7453.600000, '2025-05-13'),
	(3, 9, 9290.380000, '2025-05-13'),
	(3, 10, 17835.400000, '2025-05-13'),
	(3, 11, 20763.600000, '2025-05-13'),
	(3, 12, 20763.600000, '2025-05-13'),
	(3, 13, 7719.800000, '2025-05-13'),
	(3, 14, 1783.540000, '2025-05-13'),
	(3, 15, 3194.400000, '2025-05-13'),
	(3, 16, 3194.400000, '2025-05-13'),
	(3, 17, 2635.380000, '2025-05-13'),
	(3, 18, 11979.000000, '2025-05-13'),
	(3, 19, 9317.000000, '2025-05-13'),
	(3, 20, 9317.000000, '2025-05-13'),
	(3, 21, 2076.360000, '2025-05-13'),
	(3, 22, 1836.780000, '2025-05-13'),
	(3, 23, 1783.540000, '2025-05-13'),
	(3, 24, 3194.400000, '2025-05-13'),
	(3, 25, 8518.400000, '2025-05-13'),
	(3, 26, 6122.600000, '2025-05-13'),
	(3, 27, 6122.600000, '2025-05-13'),
	(3, 28, 6122.600000, '2025-05-13'),
	(3, 29, 18101.600000, '2025-05-13'),
	(3, 30, 3993.000000, '2025-05-13'),
	(3, 31, 6521.900000, '2025-05-13'),
	(3, 32, 6521.900000, '2025-05-13'),
	(3, 33, 10301.940000, '2025-05-13'),
	(3, 34, 9317.000000, '2025-05-13'),
	(3, 35, 13922.260000, '2025-05-13'),
	(3, 36, 1783.540000, '2025-05-13'),
	(3, 37, 3460.600000, '2025-05-13'),
	(3, 38, 239.580000, '2025-05-13'),
	(3, 39, 21029.800000, '2025-05-13'),
	(3, 40, 21029.800000, '2025-05-13'),
	(3, 41, 21003.180000, '2025-05-13'),
	(3, 42, 26087.600000, '2025-05-13'),
	(3, 43, 32742.600000, '2025-05-13'),
	(3, 44, 12511.400000, '2025-05-13'),
	(3, 45, 11180.400000, '2025-05-13'),
	(3, 46, 11712.800000, '2025-05-13'),
	(3, 47, 11180.400000, '2025-05-13'),
	(3, 48, 3194.400000, '2025-05-13'),
	(3, 49, 6122.600000, '2025-05-13'),
	(3, 50, 6229.080000, '2025-05-13'),
	(3, 51, 9050.800000, '2025-05-13'),
	(3, 52, 2369.180000, '2025-05-13'),
	(3, 53, 5057.800000, '2025-05-13'),
	(3, 54, 7453.600000, '2025-05-13'),
	(3, 55, 3194.400000, '2025-05-13'),
	(3, 56, 6122.600000, '2025-05-13'),
	(3, 57, 9317.000000, '2025-05-13'),
	(3, 58, 9183.900000, '2025-05-13'),
	(3, 59, 20231.200000, '2025-05-13');

-- Volcando estructura para tabla erp-super.proveedores
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
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.proveedores: ~4 rows (aproximadamente)
REPLACE INTO `proveedores` (`id`, `nombre`, `email`, `telefono`, `documento`, `direccion`, `id_tipo_doc`, `id_tipo_iva`) VALUES
	(1, 'Cafe America', '', '', '33-71631410-9', NULL, 3, 1),
	(2, 'Panadería Lucia', '', '', '20-21666777-4', NULL, 3, 2),
	(3, 'Cabral mayorista', '', '', '20-19345860-3', NULL, 3, 1),
	(4, 'Libreria Guzman', '', '', '20-21623777-4', NULL, 3, 2),
	(5, 'La Marina', '', '', '20-08987345-4', NULL, 3, 1),
	(6, 'Naturgy', '', '', '30681688540', NULL, 3, 1);

-- Volcando estructura para tabla erp-super.puntos_venta
CREATE TABLE IF NOT EXISTS `puntos_venta` (
  `id` int NOT NULL AUTO_INCREMENT,
  `punto_vta` int NOT NULL,
  `idsucursal` int DEFAULT NULL,
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
  `certificado_p12` varchar(300) DEFAULT NULL,
  `clave_certificado` varchar(50) DEFAULT NULL,
  `token` varchar(1000) DEFAULT NULL,
  `sign` varchar(500) DEFAULT NULL,
  `expiration` datetime DEFAULT NULL,
  `fac_electronica` smallint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idsucursal` (`idsucursal`),
  CONSTRAINT `puntos_venta_ibfk_1` FOREIGN KEY (`idsucursal`) REFERENCES `sucursales` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.puntos_venta: ~4 rows (aproximadamente)
REPLACE INTO `puntos_venta` (`id`, `punto_vta`, `idsucursal`, `ultima_fac_a`, `ultima_fac_b`, `ultima_tkt`, `ultima_fac_c`, `ultima_deb_a`, `ultima_deb_b`, `ultima_deb_c`, `ultima_nc_a`, `ultima_nc_b`, `ultima_nc_c`, `ultimo_rem_x`, `ultimo_rec_x`, `certificado_p12`, `clave_certificado`, `token`, `sign`, `expiration`, `fac_electronica`) VALUES
	(1, 1, 1, 0, 0, 46, 16, 0, 0, 1, 0, 0, 1, 2, 1, 'alias.p12', 'clave123', 'PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9InllcyI/Pgo8c3NvIHZlcnNpb249IjIuMCI+CiAgICA8aWQgc3JjPSJDTj13c2FhaG9tbywgTz1BRklQLCBDPUFSLCBTRVJJQUxOVU1CRVI9Q1VJVCAzMzY5MzQ1MDIzOSIgZHN0PSJDTj13c2ZlLCBPPUFGSVAsIEM9QVIiIHVuaXF1ZV9pZD0iMTMyNzgyNjY3NSIgZ2VuX3RpbWU9IjE3NDg4NjA2NTIiIGV4cF90aW1lPSIxNzQ4OTAzOTEyIi8+CiAgICA8b3BlcmF0aW9uIHR5cGU9ImxvZ2luIiB2YWx1ZT0iZ3JhbnRlZCI+CiAgICAgICAgPGxvZ2luIGVudGl0eT0iMzM2OTM0NTAyMzkiIHNlcnZpY2U9IndzZmUiIHVpZD0iU0VSSUFMTlVNQkVSPUNVSVQgMjAyMTg3Njc0MDEsIENOPWFkcmlhbnp1c3Npbm8iIGF1dGhtZXRob2Q9ImNtcyIgcmVnbWV0aG9kPSIyMiI+CiAgICAgICAgICAgIDxyZWxhdGlvbnM+CiAgICAgICAgICAgICAgICA8cmVsYXRpb24ga2V5PSIyMDIxODc2NzQwMSIgcmVsdHlwZT0iNCIvPgogICAgICAgICAgICA8L3JlbGF0aW9ucz4KICAgICAgICA8L2xvZ2luPgogICAgPC9vcGVyYXRpb24+Cjwvc3NvPgo=', 'A5atS4RYX4c4WefrIhmPjOTzl/Hl3KuR4JZ0KIP8YgjQeK2NfV8tCgB16p95jc7IWyGpwMb7jxzxEFo2Vs95lU1PrS8XGncRJo4Ylo+bpAOdcXtPaQLhfeuWuVgfilCVhBaPxOEMaQP7PtJd2A3cZ3MGk/WA0GHyOh+puvVgujA=', '2025-06-02 19:38:33', 1),
	(2, 2, 2, 0, 0, 7, 3, 0, 0, 1, 0, 0, 1, 2, 3, NULL, NULL, NULL, NULL, NULL, 0),
	(3, 3, 1, 0, 0, 14, 4, 0, 0, 1, 0, 0, 1, 0, 0, 'alias.p12', 'clave123', 'PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9InllcyI/Pgo8c3NvIHZlcnNpb249IjIuMCI+CiAgICA8aWQgc3JjPSJDTj13c2FhaG9tbywgTz1BRklQLCBDPUFSLCBTRVJJQUxOVU1CRVI9Q1VJVCAzMzY5MzQ1MDIzOSIgZHN0PSJDTj13c2ZlLCBPPUFGSVAsIEM9QVIiIHVuaXF1ZV9pZD0iMzk0NDQ2NDA3IiBnZW5fdGltZT0iMTc0ODg3NTk4MSIgZXhwX3RpbWU9IjE3NDg5MTkyNDEiLz4KICAgIDxvcGVyYXRpb24gdHlwZT0ibG9naW4iIHZhbHVlPSJncmFudGVkIj4KICAgICAgICA8bG9naW4gZW50aXR5PSIzMzY5MzQ1MDIzOSIgc2VydmljZT0id3NmZSIgdWlkPSJTRVJJQUxOVU1CRVI9Q1VJVCAyMDIxODc2NzQwMSwgQ049YWRyaWFuenVzc2lubyIgYXV0aG1ldGhvZD0iY21zIiByZWdtZXRob2Q9IjIyIj4KICAgICAgICAgICAgPHJlbGF0aW9ucz4KICAgICAgICAgICAgICAgIDxyZWxhdGlvbiBrZXk9IjIwMjE4NzY3NDAxIiByZWx0eXBlPSI0Ii8+CiAgICAgICAgICAgIDwvcmVsYXRpb25zPgogICAgICAgIDwvbG9naW4+CiAgICA8L29wZXJhdGlvbj4KPC9zc28+Cg==', 'QUH54LPctLNMAs2p393oWU/Xn7ZmxBIlLSQvmOXIuEXdhhqo1R2IeuLUcUpcbMZMkLDfVtysSRNsXvuocs+VH8P8zTsRfPzm0UrmwB7Z7yv0Ec0CI5KQqR94pUiOzzSVewPzctAap+wuUKRZCYS3oPr1eJkAPckqCOHEQUGz7Pk=', '2025-06-02 23:54:02', 1),
	(4, 4, 2, 0, 0, 1, 3, 0, 0, 1, 0, 0, 1, 0, 0, NULL, NULL, NULL, NULL, NULL, 0);

-- Volcando estructura para tabla erp-super.remito_facturas
CREATE TABLE IF NOT EXISTS `remito_facturas` (
  `idremito` int NOT NULL,
  `idfactura` int NOT NULL,
  PRIMARY KEY (`idremito`,`idfactura`),
  KEY `idfactura` (`idfactura`),
  CONSTRAINT `remito_facturas_ibfk_1` FOREIGN KEY (`idremito`) REFERENCES `facturac` (`id`),
  CONSTRAINT `remito_facturas_ibfk_2` FOREIGN KEY (`idfactura`) REFERENCES `facturac` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.remito_facturas: ~2 rows (aproximadamente)
REPLACE INTO `remito_facturas` (`idremito`, `idfactura`) VALUES
	(6, 14),
	(5, 15),
	(16, 17),
	(20, 21);

-- Volcando estructura para tabla erp-super.remito_sucursales
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

-- Volcando datos para la tabla erp-super.remito_sucursales: ~0 rows (aproximadamente)

-- Volcando estructura para tabla erp-super.rubros
CREATE TABLE IF NOT EXISTS `rubros` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.rubros: ~18 rows (aproximadamente)
REPLACE INTO `rubros` (`id`, `nombre`) VALUES
	(1, 'Lacteos'),
	(2, 'Harinas'),
	(3, 'Aderezos'),
	(4, 'Panificación'),
	(5, 'Cuidado personal'),
	(6, 'Art. de Limpieza'),
	(7, 'Insecticidas y repelentes'),
	(8, 'Cervezas'),
	(9, 'Gaseosas, aguas saborizadas y amargos'),
	(10, 'Conservas'),
	(11, 'Cereales y legumbres'),
	(12, 'Te, cafe y yerbas'),
	(13, 'Fideos y pastas secas'),
	(14, 'Galletas dulces'),
	(15, 'Avicola'),
	(16, 'Fideos y pastas frescas'),
	(17, 'Salsas'),
	(18, 'Azucares y edulcorantes');

-- Volcando estructura para tabla erp-super.stocks
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

-- Volcando datos para la tabla erp-super.stocks: ~54 rows (aproximadamente)
REPLACE INTO `stocks` (`idstock`, `idarticulo`, `idsucursal`, `actual`, `maximo`, `deseable`) VALUES
	(1, 1, 1, 6.000000, 0.000000, 0.000000),
	(1, 2, 1, 10.000000, 0.000000, 0.000000),
	(1, 3, 1, 8.000000, 0.000000, 0.000000),
	(1, 5, 1, -2.000000, 0.000000, 0.000000),
	(1, 7, 1, 0.000000, 0.000000, 0.000000),
	(1, 8, 1, 10.000000, 0.000000, 0.000000),
	(1, 9, 1, 9.000000, 0.000000, 0.000000),
	(1, 10, 1, 8.000000, 0.000000, 0.000000),
	(1, 11, 1, 3.000000, 0.000000, 0.000000),
	(1, 13, 1, 4.000000, 0.000000, 0.000000),
	(1, 16, 1, -1.000000, 0.000000, 0.000000),
	(1, 17, 1, 9.000000, 0.000000, 0.000000),
	(1, 20, 1, 10.000000, 0.000000, 0.000000),
	(1, 21, 1, -1.000000, 0.000000, 0.000000),
	(1, 22, 1, -2.000000, 0.000000, 0.000000),
	(1, 23, 1, -2.000000, 0.000000, 0.000000),
	(1, 24, 1, -2.000000, 0.000000, 0.000000),
	(1, 26, 1, -1.000000, 0.000000, 0.000000),
	(1, 28, 1, -1.000000, 0.000000, 0.000000),
	(1, 29, 1, -1.000000, 0.000000, 0.000000),
	(1, 30, 1, 21.000000, 0.000000, 0.000000),
	(1, 31, 1, 9.000000, 0.000000, 0.000000),
	(1, 32, 1, 11.000000, 0.000000, 0.000000),
	(1, 34, 1, -1.000000, 0.000000, 0.000000),
	(1, 35, 1, -2.000000, 0.000000, 0.000000),
	(1, 36, 1, 9.000000, 0.000000, 0.000000),
	(1, 37, 1, 8.000000, 0.000000, 0.000000),
	(1, 38, 1, 44.000000, 0.000000, 0.000000),
	(1, 39, 1, 20.000000, 0.000000, 0.000000),
	(1, 40, 1, 14.000000, 0.000000, 0.000000),
	(1, 41, 1, 16.000000, 0.000000, 0.000000),
	(1, 42, 1, 16.000000, 0.000000, 0.000000),
	(1, 43, 1, 28.000000, 0.000000, 0.000000),
	(1, 46, 1, -1.000000, 0.000000, 0.000000),
	(1, 48, 1, -1.000000, 0.000000, 0.000000),
	(1, 50, 1, -1.000000, 0.000000, 0.000000),
	(1, 53, 1, -6.000000, 0.000000, 0.000000),
	(1, 55, 1, 10.000000, 0.000000, 0.000000),
	(1, 56, 1, 9.000000, 0.000000, 0.000000),
	(1, 57, 1, -2.000000, 0.000000, 0.000000),
	(2, 12, 2, -1.000000, 0.000000, 0.000000),
	(2, 15, 2, -1.000000, 0.000000, 0.000000),
	(2, 17, 2, -2.000000, 0.000000, 0.000000),
	(2, 20, 2, -1.000000, 0.000000, 0.000000),
	(2, 21, 2, -2.000000, 0.000000, 0.000000),
	(2, 27, 2, -1.000000, 0.000000, 0.000000),
	(2, 33, 2, -1.000000, 0.000000, 0.000000),
	(2, 34, 2, -1.000000, 0.000000, 0.000000),
	(2, 37, 2, -1.000000, 0.000000, 0.000000),
	(2, 38, 2, -6.000000, 0.000000, 0.000000),
	(2, 46, 2, -1.000000, 0.000000, 0.000000),
	(2, 47, 2, -1.000000, 0.000000, 0.000000),
	(2, 49, 2, -2.000000, 0.000000, 0.000000),
	(2, 50, 2, -2.000000, 0.000000, 0.000000),
	(2, 53, 2, -1.000000, 0.000000, 0.000000),
	(2, 55, 2, -2.000000, 0.000000, 0.000000),
	(2, 57, 2, -1.000000, 0.000000, 0.000000);

-- Volcando estructura para tabla erp-super.sucursales
CREATE TABLE IF NOT EXISTS `sucursales` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `direccion` varchar(100) NOT NULL,
  `telefono` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `alta` datetime NOT NULL,
  `baja` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.sucursales: ~2 rows (aproximadamente)
REPLACE INTO `sucursales` (`id`, `nombre`, `direccion`, `telefono`, `email`, `alta`, `baja`) VALUES
	(1, 'Central', 'tucuman', '1234', 'el_super_mercado@elsupermercado.com.ar', '2024-11-27 15:00:17', '0000-00-00 00:00:00'),
	(2, 'Rivadavia', 'tucuman', '12345', 'el_super_mercado@elsupermercado.com.ar', '2024-11-28 08:18:31', '0000-00-00 00:00:00');

-- Volcando estructura para tabla erp-super.tareas
CREATE TABLE IF NOT EXISTS `tareas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tarea` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.tareas: ~5 rows (aproximadamente)
REPLACE INTO `tareas` (`id`, `tarea`) VALUES
	(1, 'Supervisor'),
	(2, 'Administrativo'),
	(3, 'Cajero'),
	(4, 'Vendedor'),
	(5, 'Deposito');

-- Volcando estructura para tabla erp-super.tareas_usuario
CREATE TABLE IF NOT EXISTS `tareas_usuario` (
  `idtarea` int NOT NULL,
  `idusuario` int NOT NULL,
  PRIMARY KEY (`idtarea`,`idusuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.tareas_usuario: ~0 rows (aproximadamente)
REPLACE INTO `tareas_usuario` (`idtarea`, `idusuario`) VALUES
	(1, 2);

-- Volcando estructura para tabla erp-super.tipo_articulos
CREATE TABLE IF NOT EXISTS `tipo_articulos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.tipo_articulos: ~3 rows (aproximadamente)
REPLACE INTO `tipo_articulos` (`id`, `nombre`) VALUES
	(1, 'Producto'),
	(2, 'Servicio'),
	(3, 'Insumo');

-- Volcando estructura para tabla erp-super.tipo_balances
CREATE TABLE IF NOT EXISTS `tipo_balances` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.tipo_balances: ~2 rows (aproximadamente)
REPLACE INTO `tipo_balances` (`id`, `nombre`) VALUES
	(1, 'Balance'),
	(2, 'Ajuste');

-- Volcando estructura para tabla erp-super.tipo_comprobantes
CREATE TABLE IF NOT EXISTS `tipo_comprobantes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_afip` int DEFAULT NULL,
  `nombre` varchar(50) DEFAULT NULL,
  `discrimina_iva` smallint NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.tipo_comprobantes: ~12 rows (aproximadamente)
REPLACE INTO `tipo_comprobantes` (`id`, `id_afip`, `nombre`, `discrimina_iva`) VALUES
	(1, 1, 'A', 1),
	(2, 6, 'B', 1),
	(3, 11, 'C', 0),
	(4, 0, 'TKT', 1),
	(5, 3, 'CRED A', 1),
	(6, 8, 'CRED B', 1),
	(7, 0, 'CRED C', 0),
	(8, 2, 'DEB A', 1),
	(9, 7, 'DEB B', 1),
	(10, 0, 'DEB C', 0),
	(11, 0, 'REM X', 0),
	(12, 0, 'REC X', 0);

-- Volcando estructura para tabla erp-super.tipo_comp_aplica
CREATE TABLE IF NOT EXISTS `tipo_comp_aplica` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_iva_owner` int DEFAULT NULL,
  `id_iva_entidad` int DEFAULT NULL,
  `id_tipo_comp` int DEFAULT NULL,
  `id_tipo_oper` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_iva_owner` (`id_iva_owner`),
  KEY `id_iva_entidad` (`id_iva_entidad`),
  KEY `id_tipo_comp` (`id_tipo_comp`),
  KEY `id_tipo_oper` (`id_tipo_oper`),
  CONSTRAINT `tipo_comp_aplica_ibfk_1` FOREIGN KEY (`id_iva_owner`) REFERENCES `tipo_iva` (`id`),
  CONSTRAINT `tipo_comp_aplica_ibfk_2` FOREIGN KEY (`id_iva_entidad`) REFERENCES `tipo_iva` (`id`),
  CONSTRAINT `tipo_comp_aplica_ibfk_3` FOREIGN KEY (`id_tipo_comp`) REFERENCES `tipo_comprobantes` (`id`),
  CONSTRAINT `tipo_comp_aplica_ibfk_4` FOREIGN KEY (`id_tipo_oper`) REFERENCES `tipo_operacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.tipo_comp_aplica: ~8 rows (aproximadamente)
REPLACE INTO `tipo_comp_aplica` (`id`, `id_iva_owner`, `id_iva_entidad`, `id_tipo_comp`, `id_tipo_oper`) VALUES
	(1, 2, 1, 3, 1),
	(2, 2, 2, 3, 1),
	(3, 2, 3, 3, 1),
	(4, 2, 4, 3, 1),
	(5, 2, 1, 1, 2),
	(6, 2, 2, 3, 2),
	(7, 2, 3, 4, 2),
	(8, 2, 4, 2, 2),
	(9, 2, 1, 12, 6);

-- Volcando estructura para tabla erp-super.tipo_doc
CREATE TABLE IF NOT EXISTS `tipo_doc` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(30) DEFAULT NULL,
  `id_afip` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.tipo_doc: ~3 rows (aproximadamente)
REPLACE INTO `tipo_doc` (`id`, `nombre`, `id_afip`) VALUES
	(1, 'DNI', 96),
	(2, 'CUIL', 86),
	(3, 'CUIT', 80);

-- Volcando estructura para tabla erp-super.tipo_iva
CREATE TABLE IF NOT EXISTS `tipo_iva` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.tipo_iva: ~4 rows (aproximadamente)
REPLACE INTO `tipo_iva` (`id`, `descripcion`) VALUES
	(1, 'Responsable inscripto'),
	(2, 'Monotributista'),
	(3, 'Consumidor final'),
	(4, 'Exento');

-- Volcando estructura para tabla erp-super.tipo_operacion
CREATE TABLE IF NOT EXISTS `tipo_operacion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.tipo_operacion: ~6 rows (aproximadamente)
REPLACE INTO `tipo_operacion` (`id`, `nombre`) VALUES
	(1, 'VENTA'),
	(2, 'COMPRA'),
	(3, 'CREDITO'),
	(4, 'DEBITO'),
	(5, 'REMITO'),
	(6, 'RECIBO');

-- Volcando estructura para tabla erp-super.usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(80) DEFAULT NULL,
  `usuario` varchar(80) DEFAULT NULL,
  `clave` varchar(200) DEFAULT NULL,
  `documento` varchar(13) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Volcando datos para la tabla erp-super.usuarios: ~3 rows (aproximadamente)
REPLACE INTO `usuarios` (`id`, `nombre`, `usuario`, `clave`, `documento`, `email`, `telefono`, `direccion`) VALUES
	(2, 'Administrador', 'admin', '1234', '22117091', 'admin@elsupermercado.com.ar', '22333444', 'Sta Lucia'),
	(3, 'Vendedor Uno', 'vend1', '1234', '21876740', 'admin@elsupermercado.com.ar', '22333444', 'Saavedra'),
	(5, 'Vendedor Dos', 'vend2', '1234', '123456', 'admin@elsupermercado.com.ar', '22333444', 'Saavedra');

-- Volcando estructura para procedimiento erp-super.actualizar_precios_por_compra
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

-- Volcando estructura para procedimiento erp-super.actualizar_precios_por_lista
DELIMITER //
CREATE PROCEDURE `actualizar_precios_por_lista`(
	IN `p_idlista` INT,
	IN `p_markup` DECIMAL(10,2)
)
BEGIN

    DECLARE done INT DEFAULT 0;

    DECLARE v_idarticulo INT;

    DECLARE v_costo DECIMAL(10,2);

    

    -- Cursor para recorrer la tabla de artículos

    DECLARE articulo_cursor CURSOR FOR

        SELECT id, costo_total FROM articulos;



    -- Declaración de handler para salir del bucle del cursor

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;



    OPEN articulo_cursor;



    leer_articulo: LOOP

        FETCH articulo_cursor INTO v_idarticulo, v_costo;

        

        IF done THEN

            LEAVE leer_articulo;

        END IF;



        -- Insertar o actualizar el precio en la tabla de precios

        INSERT INTO precios (idlista, idarticulo, precio, ult_modificacion)

        VALUES (p_idlista, v_idarticulo, v_costo * p_markup, curdate())

        ON DUPLICATE KEY UPDATE precio = v_costo * p_markup, ult_modificacion = curdate();

        

    END LOOP;



    CLOSE articulo_cursor;

END//
DELIMITER ;

-- Volcando estructura para procedimiento erp-super.estado_resultado
DELIMITER //
CREATE PROCEDURE `estado_resultado`(
	IN `desde` DATE,
	IN `hasta` DATE
)
BEGIN

	SELECT SUM(iv.precio_total) ventas_total, SUM(iv.iva) IVA, SUM(iv.exento) exento, SUM(iv.impint) imp_int, SUM(iv.ingbto) ing_btos, SUM(iv.cantidad * a.costo_total) costo_total
	FROM facturav f
	JOIN itemsv iv ON iv.idfactura = f.id
	JOIN articulos a ON iv.idarticulo = a.id
	WHERE
	  f.fecha BETWEEN desde AND hasta and
	  f.idtipocomprobante IN (SELECT id_tipo_comp FROM tipo_comp_aplica WHERE id_tipo_oper = 1);
	  
	SELECT SUM(f.total) total_compras, pc.nombre cuenta
	FROM facturac f
	JOIN plan_ctas pc ON f.idplancuenta = pc.id
	WHERE
	  f.fecha BETWEEN desde AND hasta and
	  f.idtipocomprobante IN (SELECT id_tipo_comp FROM tipo_comp_aplica WHERE id_tipo_oper = 2)
	GROUP BY pc.nombre;  

END//
DELIMITER ;

-- Volcando estructura para procedimiento erp-super.estado_resultado_detalle
DELIMITER //
CREATE PROCEDURE `estado_resultado_detalle`(
	IN `desde` DATE,
	IN `hasta` DATE
)
BEGIN
-- Variables para el cursor
    DECLARE v_id INT;
    DECLARE v_precio_unitario DECIMAL(18, 2);
    DECLARE v_cantidad INT;
    DECLARE v_costo DECIMAL(18, 2);
    DECLARE v_impint DECIMAL(18, 2);
    DECLARE v_exento DECIMAL(18, 2);
    DECLARE v_id_al_iva INT;
    DECLARE v_costo_calculado DECIMAL(18, 2);
    DECLARE fin_cursor INT DEFAULT 0;

    -- 1️⃣ Declaración del cursor (antes de los handlers)
    DECLARE cursor_factura CURSOR FOR
        SELECT iv.idarticulo, iv.precio_unitario, sum(iv.cantidad), a.costo, a.impint, a.exento, a.idiva, a.idib
        FROM facturav f
        JOIN itemsv iv ON f.id = iv.idfactura
        JOIN articulos a ON a.id = iv.idarticulo
        WHERE f.fecha BETWEEN desde AND hasta
		  GROUP BY iv.idarticulo, iv.precio_unitario, a.costo, a.impint, a.exento, a.idiva, a.idib;

    -- 2️⃣ Handler para manejar el fin del cursor
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET fin_cursor = 1;

    -- 3️⃣ Crear tabla temporal para almacenar el resultado
    DROP TEMPORARY TABLE IF EXISTS tmp_resultado;
    CREATE TEMPORARY TABLE tmp_resultado (
        id INT,
        precio_unitario DECIMAL(18, 2),
        cantidad INT,
        costo DECIMAL(18, 2),
        impint DECIMAL(18, 2),
        exento DECIMAL(18, 2),
        id_al_iva INT,
        costo_calculado DECIMAL(18, 2)
    );

    -- Abrir el cursor
    OPEN cursor_factura;

    -- Iteración de los registros
    leer_loop: LOOP
        FETCH cursor_factura INTO v_id, v_precio_unitario, v_cantidad, v_costo, v_impint, v_exento, v_id_al_iva;

        -- Verificar si terminó el cursor
        IF fin_cursor = 1 THEN 
            LEAVE leer_loop; 
        END IF;

        -- Calculo del costo calculado (aquí puedes modificar la lógica según necesites)
        SET v_costo_calculado = (v_costo + v_impint + v_exento);

        -- Insertar en la tabla temporal
        INSERT INTO tmp_resultado VALUES (
            v_id, v_precio_unitario, v_cantidad, v_costo, v_impint, v_exento, v_id_al_iva, v_costo_calculado
        );
    END LOOP;

    -- Cerrar el cursor
    CLOSE cursor_factura;

    -- Seleccionar los datos procesados
    SELECT * FROM tmp_resultado;
END//
DELIMITER ;

-- Volcando estructura para procedimiento erp-super.get_clientes_cc_vencidas
DELIMITER //
CREATE PROCEDURE `get_clientes_cc_vencidas`(
	IN `empresa` INT
)
    COMMENT 'Obtiene la cantidad de clientes con cta cte vencida, que es aquellas cuentas con movimientos con fecha anterior a fecha - dias_vto'
BEGIN

   DECLARE dias_vto INT DEFAULT 0;        
   
   DECLARE cant_clientes int DEFAULT 0;
    

   SELECT COALESCE(dias_vto_cta_cte, 0) 
   FROM configuracion
   WHERE id = empresa
   INTO dias_vto;
 
   SELECT count(c.idcliente)
	FROM (
	    SELECT 
	        idcliente, 
	        SUM(debe - haber),
	        MAX(fecha) AS ultima_fecha 
	    FROM cta_cte_cli 
	    GROUP BY idcliente
	    HAVING SUM(debe-haber) > 0
	) c
	WHERE 
	c.ultima_fecha < CURDATE() - INTERVAL 30 DAY
	INTO cant_clientes;		

   SELECT cant_clientes AS CantidadClientes;

END//
DELIMITER ;

-- Volcando estructura para procedimiento erp-super.get_datosfac_fe
DELIMITER //
CREATE PROCEDURE `get_datosfac_fe`(
	IN `id` INT
)
BEGIN
SELECT 
  JSON_OBJECT(
    'cliente', JSON_OBJECT(
      'tipo_doc', td.id_afip,
      'nro_doc', c.documento,
      'nombre', c.nombre,
      'domicilio', c.direccion
    ),
    'tipo_comprobante', tc.id_afip,
    'punto_venta', f.punto_vta,
    'fecha', DATE_FORMAT(f.fecha, '%Y%m%d'),
    'items', (
      SELECT JSON_ARRAYAGG(
        JSON_OBJECT(
          'codigo', i.idarticulo,
          'descripcion', a.detalle,
          'cantidad', i.cantidad,
          'precio', ROUND(i.precio_unitario - i.iva - i.impint - i.exento, 2),
          'iva', iv.alicuota,
          'importe_neto', ROUND(i.precio_unitario - i.iva - i.impint - i.exento, 2),
          'importe_iva', i.iva
        )
      )
      FROM itemsv i 
      JOIN articulos a ON i.idarticulo = a.id
      JOIN alc_iva iv ON i.idalciva = iv.id
		WHERE i.idfactura = f.id
    )/*,
    'observaciones', f.observaciones*/
  ) AS json_factura
FROM facturav f
JOIN clientes c ON f.idcliente = c.id
JOIN tipo_doc td ON c.id_tipo_doc = td.id
JOIN tipo_comprobantes tc ON f.idtipocomprobante = tc.id
WHERE f.id = id;
END//
DELIMITER ;

-- Volcando estructura para procedimiento erp-super.get_saldos_cc_cli
DELIMITER //
CREATE PROCEDURE `get_saldos_cc_cli`(
	IN `empresa` INT
)
BEGIN
   DECLARE dias_vto INT DEFAULT 0;        
   DECLARE saldo DECIMAL(20,6) DEFAULT 0.0;
   DECLARE saldo_vencido DECIMAL(20,6) DEFAULT 0.0;

   DECLARE debe_tot DECIMAL(20,6) DEFAULT 0.0;
   DECLARE haber_tot DECIMAL(20,6) DEFAULT 0.0;
   DECLARE debe_venc DECIMAL(20,6) DEFAULT 0.0;
   DECLARE haber_venc DECIMAL(20,6) DEFAULT 0.0;
    

   SELECT COALESCE(dias_vto_cta_cte, 0) 
   FROM configuracion
   WHERE id = empresa
   INTO dias_vto;


   SELECT sum(debe), sum(haber)
   FROM cta_cte_cli
	INTO debe_tot, haber_tot;

   SET saldo = debe_tot - haber_tot;
 
   SELECT SUM(cc.debe), SUM(cc.haber)
	FROM cta_cte_cli AS cc
	join (
		    SELECT 
		        idcliente, 
		        MAX(fecha) AS ultima_fecha 
		    FROM cta_cte_cli 
		    GROUP BY idcliente
		) c ON c.idcliente = cc.idcliente
	WHERE c.ultima_fecha < CURDATE() - INTERVAL 30 DAY
	INTO debe_venc, haber_venc;

   SET saldo_vencido = debe_venc - haber_venc;
   
   IF (saldo_vencido < 0) THEN
   	SET saldo_vencido = 0;
   END IF;	

   SELECT saldo AS SaldoTotal, saldo_vencido AS SaldoVencido;

END//
DELIMITER ;

-- Volcando estructura para procedimiento erp-super.get_saldos_cc_prov
DELIMITER //
CREATE PROCEDURE `get_saldos_cc_prov`(
	IN `empresa` INT
)
BEGIN
   DECLARE dias_vto INT DEFAULT 0;        
   DECLARE saldo DECIMAL(20,6) DEFAULT 0.0;
   DECLARE saldo_vencido DECIMAL(20,6) DEFAULT 0.0;

   DECLARE debe_tot DECIMAL(20,6) DEFAULT 0.0;
   DECLARE haber_tot DECIMAL(20,6) DEFAULT 0.0;
   DECLARE debe_venc DECIMAL(20,6) DEFAULT 0.0;
   DECLARE haber_venc DECIMAL(20,6) DEFAULT 0.0;
    

   SELECT COALESCE(dias_vto_cta_cte, 0) 
   FROM configuracion
   WHERE id = empresa
   INTO dias_vto;


   SELECT sum(debe), sum(haber)
   FROM cta_cte_prov
	INTO debe_tot, haber_tot;

   SET saldo = debe_tot - haber_tot;
 
   SELECT SUM(cc.debe), SUM(cc.haber)
	FROM cta_cte_prov AS cc
	join (
		    SELECT 
		        idproveedor, 
		        MAX(fecha) AS ultima_fecha 
		    FROM cta_cte_prov 
		    GROUP BY idproveedor
		) c ON c.idproveedor = cc.idproveedor
	WHERE c.ultima_fecha < CURDATE() - INTERVAL 30 DAY
	INTO debe_venc, haber_venc;

   SET saldo_vencido = debe_venc - haber_venc;
   
   IF (saldo_vencido < 0) THEN
   	SET saldo_vencido = 0;
   END IF;	

   SELECT saldo AS SaldoTotal, saldo_vencido AS SaldoVencido;

END//
DELIMITER ;

-- Volcando estructura para procedimiento erp-super.get_stock_faltantes
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

-- Volcando estructura para procedimiento erp-super.get_stock_negativos
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

-- Volcando estructura para procedimiento erp-super.get_vta_desde_hasta
DELIMITER //
CREATE PROCEDURE `get_vta_desde_hasta`(
	IN `desde` DATE,
	IN `hasta` DATE
)
BEGIN
/*
	SELECT D.MES, D.ANIO, SUM(D.cantidad) AS cantidad_operaciones
	FROM D(
		SELECT 
		    MONTHNAME(fecha) AS mes, 
		    EXTRACT(YEAR FROM fecha) AS anio,
		    COUNT(id) AS cantidad
		FROM facturav
		WHERE fecha BETWEEN desde AND hasta
		GROUP BY fecha
		ORDER BY EXTRACT(YEAR FROM fecha), EXTRACT(MONTH FROM fecha);
  		) as D
  	GROUP BY D.MES, D.ANIO
*/
	SELECT 
    D.mes, 
    D.anio, 
    SUM(D.cantidad) AS cantidad_operaciones
FROM (
    SELECT 
        MONTHNAME(fecha) AS mes, 
        EXTRACT(YEAR FROM fecha) AS anio,
        COUNT(id) AS cantidad
    FROM facturav
    WHERE fecha BETWEEN desde AND hasta
    GROUP BY fecha
) AS D
GROUP BY D.mes, D.anio
ORDER BY D.anio, D.mes;
END//
DELIMITER ;

-- Volcando estructura para procedimiento erp-super.get_vta_sucursales
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

-- Volcando estructura para procedimiento erp-super.get_vta_vendedores
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

-- Volcando estructura para procedimiento erp-super.lst_clientes_cc_vencidas
DELIMITER //
CREATE PROCEDURE `lst_clientes_cc_vencidas`(
	IN `empresa` INT
)
    COMMENT 'Obtiene un listado de los cliente con cta cte vencida'
BEGIN
   DECLARE dias_vto INT DEFAULT 0;        
  
   SELECT COALESCE(dias_vto_cta_cte, 0) 
   FROM configuracion
   WHERE id = empresa
   INTO dias_vto;
 
 	SELECT c.id, c.nombre, sum(cc.debe - cc.haber) AS saldo
 	FROM clientes c
 	JOIN cta_cte_cli cc ON c.id = cc.idcliente
 	where
 		c.id IN (
		   SELECT d.idcliente
			FROM (
			    SELECT 
			        idcliente, 
			        MAX(fecha) AS ultima_fecha 
			    FROM cta_cte_cli 
			    GROUP BY idcliente
			) d
			WHERE 
			d.ultima_fecha < CURDATE() - INTERVAL 30 DAY)
	GROUP BY c.id, c.nombre
	HAVING sum(cc.debe - cc.haber) > 0;

END//
DELIMITER ;

-- Volcando estructura para procedimiento erp-super.lst_compuesto
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

-- Volcando estructura para procedimiento erp-super.mas_vendidos
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

-- Volcando estructura para procedimiento erp-super.prueba_cursor
DELIMITER //
CREATE PROCEDURE `prueba_cursor`()
BEGIN
    -- Variables
    DECLARE v_id INT;
    DECLARE fin_cursor INT DEFAULT 0;

    -- 1️⃣ Declaración del cursor (debe estar ANTES de los handlers)
    DECLARE cursor_test CURSOR FOR
        SELECT id FROM articulos LIMIT 5;

    -- 2️⃣ Handlers para manejar el fin del cursor
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET fin_cursor = 1;

    -- Abrir el cursor
    OPEN cursor_test;

    leer_loop: LOOP
        FETCH cursor_test INTO v_id;

        -- Verificar si terminó el cursor
        IF fin_cursor = 1 THEN 
            LEAVE leer_loop; 
        END IF;

        -- Mostrar el valor obtenido
        SELECT v_id AS ID_Articulo;

    END LOOP;

    -- Cerrar el cursor
    CLOSE cursor_test;

END//
DELIMITER ;

-- Volcando estructura para procedimiento erp-super.ultimas_10_ventas
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

-- Volcando estructura para procedimiento erp-super.venta_articulos
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

-- Volcando estructura para procedimiento erp-super.venta_clientes
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
