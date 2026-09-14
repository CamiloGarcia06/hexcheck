# __NAME__

Servicio personal. Sigue el estándar `hexagonal-fastapi` (skill global) y lo
verifica `hexcheck`.

## Qué es

_(Una frase: qué problema resuelve y para quién. Es un servicio de un solo usuario.)_

## Correr en local

```bash
uv sync
cp .env.example .env          # y pon un token
task migrate                  # crea data/__APP__.db
task dev                      # http://127.0.0.1:8000/health
```

`task check` antes de abrir un PR: formato, lint, tipos, tests y `hexcheck`.

## Cómo se despliega

Push a `main` → CI (`check`) → job `deploy` en el runner de la torre →
`~/srv/bin/deploy __NAME__ <sha7>`. A mano: `task deploy`. Volver atrás:
`task rollback SHA=<anterior>`.

## Dónde corre

| URL | Puerto en la torre | Datos |
| --- | --- | --- |
| `http://__NAME__.torre` | _(ver `~/srv/__NAME__/compose.yaml`)_ | `~/srv/__NAME__/data/__APP__.db` |

## Cómo restaurar

`~/srv/bin/restore __NAME__ <copia>` (ver `~/srv/RUNBOOK.md`). Las copias
diarias están en `~/srv/__NAME__/backups/` y en `~/Backups/torre/` del portátil.
