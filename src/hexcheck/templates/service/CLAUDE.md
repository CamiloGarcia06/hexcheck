# __NAME__

Sigue la skill global `hexagonal-fastapi`: una carpeta por funcionalidad en
`src/__APP__/<feature>/{domain,application,infrastructure}`, `shared/` sin
funcionalidades, `main.py` como única raíz de composición. `task check` antes de
cualquier PR; `hexcheck` dice qué capa puede importar qué.

## Particularidades de este servicio

_(Lo que no se deduce del código: invariantes, integraciones, trampas conocidas.)_

## Decisiones

Las del estándar están en la skill (`references/decisions.md`). Las de este
servicio, en `docs/adr/`. Solo se escribe un ADR si cambia una regla del
estándar o entra una pieza nueva en la plataforma.
