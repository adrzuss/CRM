# Proposal: Versionar Stored Procedures

## Intent

El proyecto CRM tiene 63 stored procedures que solo existen en la base de datos MySQL y no están versionados en el repositorio. Si la base de datos se pierde o se clona el proyecto desde cero, toda la lógica de negocio encapsulada en estos procedures se pierde. Necesitamos extraerlos y mantenerlos versionados.

## Scope

### In Scope
- Extraer los 63 stored procedures desde la base de datos MySQL
- Crear `SQL/procedures/` con un archivo `.sql` individual por cada procedure
- Crear `SQL/procedures/_all_procedures.sql` combinado para deployment
- Normalizar los archivos (remover DEFINER, líneas en blanco excesivas)

### Out of Scope
- Modificar los procedures existentes
- Agregar tests para los procedures
- Refactorizar lógica de negocio de SQL a Python
- Migrar a otra base de datos

## Capabilities

### New Capabilities
None

### Modified Capabilities
None

## Approach

1. Conectarse a MySQL con pymysql
2. Ejecutar `SHOW PROCEDURE STATUS` para listar todos los procedures
3. Para cada uno, ejecutar `SHOW CREATE PROCEDURE` y guardar en archivo individual
4. Normalizar: remover DEFINER, comprimir líneas en blanco consecutivas
5. Generar archivo combinado `_all_procedures.sql`

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `SQL/procedures/*.sql` | New | 63 archivos individuales + 1 combinado |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| MySQL no accesible | Baja | Se verificó que el servicio está corriendo |
| Credenciales expuestas | Media | Ya están en .env, se rotarán en cambio futuro |

## Rollback Plan

Eliminar `SQL/procedures/` del repo. La app sigue funcionando porque los procedures ya están en la DB.

## Dependencies

- MySQL 8.0 corriendo en localhost
- pymysql instalado en el entorno

## Success Criteria

- [ ] 63 archivos `.sql` en `SQL/procedures/`
- [ ] `_all_procedures.sql` combinado listo para `source`
- [ ] Cada archivo tiene `DROP PROCEDURE IF EXISTS` + `CREATE PROCEDURE`
- [ ] Los 55 procedures llamados desde Python están incluidos
