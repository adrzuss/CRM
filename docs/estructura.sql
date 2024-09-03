CREATE TABLE IF NOT EXISTS clientes (
  id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre varchar NOT NULL,
  direccion varchar,
  documento varchar,
  tipo_iva smallint,
  tipo_doc smallint,
  telefono varchar,
  mail varchar,
  cta_cte tinyint
);

CREATE INDEX idx_tipo_iva ON clientes (tipo_iva);

CREATE TABLE IF NOT EXISTS tipo_ivas (
  id smallint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  tipo_iva varchar
);

CREATE TABLE IF NOT EXISTS tipo_docs (
  id smallint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  tipo_doc varchar
);

CREATE TABLE IF NOT EXISTS cta_cte_cli (
  id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  idcliente bigint,
  debe decimal,
  haber decimal,
  fecha date DEFAULT NULL,
  idcomprobante bigint
);

CREATE TABLE IF NOT EXISTS facturasv (
  id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  idcliente bigint,
  fecha date DEFAULT NULL,
  idtipo_comp smallint,
  nro_comp varchar,
  total decimal
);

CREATE TABLE IF NOT EXISTS tipo_comprobantes (
  id smallint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  tipo_comprobante varchar
);

CREATE TABLE IF NOT EXISTS articulos (
  id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  codigo varchar,
  descripcion varchar,
  idmarca bigint,
  idalc_iva smallint,
  idalc_ib smallint,
  costo decimal,
  alta date DEFAULT NULL,
  baja date DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS marcas (
  id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  marca bigint
);

CREATE TABLE IF NOT EXISTS alc_iva (
  id smallint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  iva varchar,
  alc decimal
);

CREATE TABLE IF NOT EXISTS alc_ib (
  id smallint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  ing_bto varchar,
  alc decimal
);

CREATE TABLE IF NOT EXISTS itemsv (
  idfactura bigint NOT NULL,
  id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  idarticulo bigint,
  cantidad decimal,
  neto decimal,
  exento decimal,
  imp_int decimal,
  iva decimal,
  total decimal
);

CREATE TABLE IF NOT EXISTS pagos_fv (
  idfactura bigint NOT NULL,
  id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  idpago smallint,
  monto decimal
);

CREATE TABLE IF NOT EXISTS pagos_cobros (
  id smallint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre varchar,
  habilitado tinyint,
  tipo smallint
);

CREATE TABLE IF NOT EXISTS proveedores (
  id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nombre varchar,
  fantasia varchar,
  direccion varchar,
  telefono varchar,
  mail bigint,
  idtipo_doc smallint,
  idtipo_iva smallint,
  documento varchar
);

CREATE TABLE IF NOT EXISTS cta_cte_prov (
  id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  idproveedor bigint,
  debe decimal,
  haber decimal,
  fecha date DEFAULT NULL,
  idcomprobante bigint
);

CREATE TABLE IF NOT EXISTS facturasc (
  id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  idproveedor bigint,
  fecha date DEFAULT NULL,
  idtipo_comp smallint,
  nro_comp varchar,
  total decimal
);

CREATE TABLE IF NOT EXISTS itemsc (
  idfactura bigint NOT NULL,
  id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  idarticulo bigint,
  cantidad decimal,
  neto decimal,
  exento decimal,
  imp_int decimal,
  iva decimal,
  total decimal
);

CREATE TABLE IF NOT EXISTS pagos_fc (
  idfactura bigint NOT NULL,
  id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
  idpago smallint,
  monto decimal
);

ALTER TABLE clientes ADD CONSTRAINT clientes_tipo_iva_fk FOREIGN KEY (tipo_iva) REFERENCES tipo_ivas (id);
ALTER TABLE clientes ADD CONSTRAINT clientes_tipo_doc_fk FOREIGN KEY (tipo_doc) REFERENCES tipo_docs (id);
ALTER TABLE cta_cte_cli ADD CONSTRAINT cta_cte_cli_idcliente_fk FOREIGN KEY (idcliente) REFERENCES clientes (id);
ALTER TABLE facturasv ADD CONSTRAINT facturasv_idcliente_fk FOREIGN KEY (idcliente) REFERENCES clientes (id);
ALTER TABLE cta_cte_cli ADD CONSTRAINT cta_cte_cli_idcomprobante_fk FOREIGN KEY (idcomprobante) REFERENCES facturasv (id);
ALTER TABLE facturasv ADD CONSTRAINT facturasv_tipo_comp_fk FOREIGN KEY (idtipo_comp) REFERENCES tipo_comprobantes (id);
ALTER TABLE articulos ADD CONSTRAINT articulos_idmarca_fk FOREIGN KEY (idmarca) REFERENCES marcas (id);
ALTER TABLE articulos ADD CONSTRAINT articulos_idalc_iva_fk FOREIGN KEY (idalc_iva) REFERENCES alc_iva (id);
ALTER TABLE articulos ADD CONSTRAINT articulos_idalc_ib_fk FOREIGN KEY (idalc_ib) REFERENCES alc_ib (id);
ALTER TABLE itemsv ADD CONSTRAINT itemsv_idfactura_fk FOREIGN KEY (idfactura) REFERENCES facturasv (id);
ALTER TABLE itemsv ADD CONSTRAINT itemsv_idarticulo_fk FOREIGN KEY (idarticulo) REFERENCES articulos (id);
ALTER TABLE pagos_fv ADD CONSTRAINT pagos_fv_idfactura_fk FOREIGN KEY (idfactura) REFERENCES facturasv (id);
ALTER TABLE pagos_fv ADD CONSTRAINT pagos_fv_idpago_fk FOREIGN KEY (idpago) REFERENCES pagos_cobros (id);
ALTER TABLE proveedores ADD CONSTRAINT proveedores_idtipo_doc_fk FOREIGN KEY (idtipo_doc) REFERENCES tipo_docs (id);
ALTER TABLE proveedores ADD CONSTRAINT proveedores_idtipo_iva_fk FOREIGN KEY (idtipo_iva) REFERENCES tipo_ivas (id);
ALTER TABLE cta_cte_prov ADD CONSTRAINT cta_cte_prov_idproveedor_fk FOREIGN KEY (idproveedor) REFERENCES proveedores (id);
ALTER TABLE facturasc ADD CONSTRAINT facturasc_idproveedor_fk FOREIGN KEY (idproveedor) REFERENCES proveedores (id);
ALTER TABLE facturasc ADD CONSTRAINT facturasc_tipo_comp_fk FOREIGN KEY (idtipo_comp) REFERENCES tipo_comprobantes (id);
ALTER TABLE itemsc ADD CONSTRAINT itemsc_idfactura_fk FOREIGN KEY (idfactura) REFERENCES facturasc (id);
ALTER TABLE itemsc ADD CONSTRAINT itemsc_idarticulo_fk FOREIGN KEY (idarticulo) REFERENCES articulos (id);
ALTER TABLE pagos_fc ADD CONSTRAINT pagos_fc_idfactura_fk FOREIGN KEY (idfactura) REFERENCES facturasc (id);
ALTER TABLE pagos_fc ADD CONSTRAINT pagos_fc_idpago_fk FOREIGN KEY (idpago) REFERENCES pagos_cobros (id);
