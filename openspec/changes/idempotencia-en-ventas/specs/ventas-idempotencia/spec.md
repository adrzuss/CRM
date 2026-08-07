# Ventas Idempotencia Specification

## Purpose
Prevenir duplicados de facturación cuando el cliente envía el mismo pedido más de una vez (timeout de red, doble click, reintento manual).

## Requirements

### Requirement: Idempotency Key Acceptance

The system MUST accept an `_idempotency_key` field (UUID v4) as part of the invoice creation POST request.

#### Scenario: Valid UUID key submitted

- GIVEN the user submits the invoice form
- WHEN the form includes a valid UUID v4 in `_idempotency_key`
- THEN the system SHALL proceed with the invoice creation pipeline

#### Scenario: Missing key (backward compatibility)

- GIVEN the user submits the invoice form
- WHEN the form does NOT include `_idempotency_key`
- THEN the system SHALL process the request using the existing (non-idempotent) pipeline

#### Scenario: Invalid UUID format

- GIVEN the user submits the invoice form
- WHEN `_idempotency_key` is present but is not a valid UUID v4
- THEN the system SHOULD reject with error "Formato de clave de idempotencia inválido"

### Requirement: Duplicate Detection

The system MUST detect and handle repeated submissions with the same idempotency key.

#### Scenario: First submission with key

- GIVEN no invoice exists with the given `idempotency_key`
- WHEN the system receives the request
- THEN it SHALL create a new invoice
- AND it SHALL store the `idempotency_key` on the invoice record

#### Scenario: Repeated submission with same key

- GIVEN an invoice was already created with `idempotency_key = X`
- WHEN the system receives another request with `idempotency_key = X`
- THEN it MUST NOT create a new invoice
- AND it MUST return the existing invoice as `{success: true, id: <existing_id>}`

#### Scenario: Race condition — concurrent submissions

- GIVEN two concurrent requests arrive with the same `idempotency_key = X`
- WHEN both pass the application-level idempotency check simultaneously
- THEN the UNIQUE INDEX on `facturav.idempotency_key` MUST prevent the second INSERT
- AND the system MUST catch the IntegrityError, rollback, query by key, and return the existing invoice

### Requirement: Correlative Number Late Assignment

The system MUST delay `getNroComprobante` execution until all validations pass and the database transaction is ready to commit.

#### Scenario: Failed validation before correlative

- GIVEN the invoice form fails validation (e.g., incomplete data)
- WHEN the error occurs before `getNroComprobante` is called
- THEN no correlative number SHALL be consumed

#### Scenario: Successful invoice creation

- GIVEN all validations pass
- WHEN `getNroComprobante` is called just before the database commit
- THEN the correlative number MUST be consumed
- AND the invoice MUST be created with that number
- AND both operations MUST succeed or fail atomically

### Requirement: Composite UNIQUE Constraint

The system MUST enforce that no two invoices share the same (punto_vta, nro_comprobante, idtipocomprobante) combination.

#### Scenario: Duplicate number rejected

- GIVEN an invoice exists with punto_vta=A, nro_comprobante=B, idtipocomprobante=C
- WHEN another invoice insert attempts the same combination A, B, C
- THEN the UNIQUE INDEX SHALL reject the INSERT
- AND the system MUST return a descriptive error
