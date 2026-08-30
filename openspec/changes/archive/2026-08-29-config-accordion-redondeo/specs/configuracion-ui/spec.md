# Configuración UI — Accordion Redesign

## Purpose

Reemplazar las 12 secciones apiladas como `div.card.m-3` en la página de configuraciones por un acordeón Bootstrap 5.3.3 que mejora la navegación visual y reduce el scroll excesivo. Tipo IVAs y Tipo Documentos, actualmente lado a lado, se separan en items independientes.

## Requirements

### REQ-001: Wrapper Acordeón

Todas las secciones de configuración DEBEN estar envueltas en `<div class="accordion" id="configAccordion">`.

#### Scenario: SCE-001 — Header expande sección, colapsa otras

- GIVEN el usuario está en la página de configuraciones
- WHEN hace clic en el header de una sección del acordeón
- THEN esa sección se expande
- AND las demás se colapsan (exclusión mutua vía `data-bs-parent="#configAccordion"`)

#### Scenario: SCE-002 — Configuración general visible al cargar

- GIVEN el usuario carga la página de configuraciones
- WHEN la página termina de renderizar
- THEN la sección "Configuración general" está expandida (clase `show` en `accordion-collapse`)
- AND las demás secciones están colapsadas

### REQ-002: Estructura accordion-item

Cada sección DEBE ser un `accordion-item` con `accordion-header` + `accordion-collapse` + `accordion-body`. El contenido existente de `card-body` se mueve a `accordion-body`.

#### Scenario: SCE-007 — Tipo IVAs y Documentos separados

- GIVEN el usuario está en la página de configuraciones
- WHEN observa las secciones del acordeón
- THEN "Tipo IVA" y "Tipo Documentos" son items separados e independientes
- AND cada uno tiene su propio accordion-button con icono

### REQ-003: Configuración general expandida por defecto

La sección "Configuración general" DEBE tener la clase `show` en su `accordion-collapse` para que esté expandida al cargar la página.

(Ver Scenario SCE-002 arriba)

### REQ-004: Exclusión mutua

El atributo `data-bs-parent="#configAccordion"` DEBE estar presente en cada `accordion-collapse` para garantizar que solo una sección esté abierta a la vez.

(Ver Scenario SCE-001 arriba)

### REQ-005: Iconos en botones

Los botones del acordeón DEBEN incluir iconos de FontAwesome (ya cargado en `base.html`) para mejorar la jerarquía visual. Cada sección tiene un icono representativo.

#### Scenario: Iconos visibles

- GIVEN el usuario carga la página de configuraciones
- WHEN observa los headers del acordeón
- THEN cada botón muestra un icono FontAwesome junto al nombre de la sección

### REQ-006: Separación Tipo IVAs / Tipo Documentos

Las secciones "Tipo IVA" y "Tipo Documentos", actualmente lado a lado dentro de un mismo card, DEBEN separarse en dos `accordion-item` independientes.

(Ver Scenario SCE-007 arriba)

### REQ-007: HTMX intacto

Los atributos `hx-target` y `hx-swap` en los formularios y botones DEBEN permanecer sin cambios. El wrapper de acordeón NO afecta el funcionamiento HTMX existente.

#### Scenario: HTMX add funciona dentro de acordeón

- GIVEN el acordeón está renderizado con una sección expandida
- WHEN el usuario envía un formulario HTMX dentro de `accordion-body`
- THEN la petición HTMX se ejecuta correctamente
- AND el target de respuesta se actualiza sin recargar la página

#### Scenario: HTMX edit funciona dentro de acordeón

- GIVEN una tabla HTMX dentro de `accordion-body`
- WHEN el usuario hace clic en "Editar" de un registro
- THEN se abre el modal de edición
- AND al guardar, la tabla se actualiza vía HTMX

### REQ-008: Inner cards aplanados

Las tarjetas internas anidadas dentro de las secciones DEBEN aplanarse o estilizarse como secciones con borde sutil, eliminando la doble nesting visual.

#### Scenario: Secciones sin doble card

- GIVEN el usuario expande cualquier sección del acordeón
- WHEN observa el contenido
- THEN no hay cards anidadas dentro de `accordion-body`
- AND el contenido usa bordes sutiles o separadores en lugar de cards completas
