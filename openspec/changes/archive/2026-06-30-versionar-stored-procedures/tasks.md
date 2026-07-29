# Tasks: Versionar Stored Procedures

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~7,000 (generated) |
| 400-line budget risk | High (código generado) |
| Chained PRs recommended | No (es generado, no código manual) |
| Delivery strategy | ask-always |
| Decision needed before apply | No |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: High

## Phase 1: Extracción

- [x] 1.1 Conectarse a MySQL y listar todos los stored procedures
- [x] 1.2 Extraer cada procedure con `SHOW CREATE PROCEDURE`
- [x] 1.3 Guardar cada uno como archivo `.sql` individual

## Phase 2: Normalización

- [x] 2.1 Remover DEFINER de todos los archivos
- [x] 2.2 Comprimir líneas en blanco consecutivas
- [x] 2.3 Verificar que los archivos tengan DELIMITER correcto

## Phase 3: Combinación

- [x] 3.1 Generar `_all_procedures.sql` con todos los procedures
- [x] 3.2 Verificar que los 55 procedures del código están incluidos
- [x] 3.3 Limpiar scripts temporales de extracción
