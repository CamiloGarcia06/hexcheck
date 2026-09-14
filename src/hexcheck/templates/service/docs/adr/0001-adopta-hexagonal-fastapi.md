# 0001 — Adopta el estándar hexagonal-fastapi

## Contexto

Servicio personal nuevo, un solo usuario, desplegado en la torre bajo `~/srv/`.

## Decisión

Se construye con el estándar `hexagonal-fastapi` (skill global) y se verifica
con `hexcheck` en `task check` y en CI. Estructura por funcionalidad; SQLite +
SQLAlchemy 2 + Alembic; síncrono; token solo para escrituras.

## Porqué

Todos los servicios personales tienen la misma forma: abrir cualquiera dentro
de un año debe bastar para entender qué es, cómo corre y por qué.

## Descartado

Layout plano (como el claude-fluent original); estructura por capas globales.

## Consecuencias

Cualquier excepción al estándar va en `[tool.hexcheck] allow` con su motivo.
