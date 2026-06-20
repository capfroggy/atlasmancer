# Atlasmancer v0.3 "Campaign Pack" — Especificación

Estado: propuesta para implementación
Autor del diseño: planificación/producto/narrativa (no código)
Implementación: Codex
Precondición: v0.2 Foundation cerrado completo (Bloques A-D — rename, i18n, `--audience`, `--format campaign`, `examples/`)
Referencia previa: [`docs/ROADMAP.md`](ROADMAP.md) "Fase 1: Campaign Pack local" y release "v0.3 Campaign Pack"

---

## 0. Qué es v0.3 en una frase

> Convertir `campaign.json` de "algo que solo se exporta" en "algo que también se puede volver a abrir": guardar un mundo, cerrarlo, reabrirlo, y re-exportarlo en cualquier formato o audiencia — sin volver a generarlo y sin perder ni un dato.

---

## 1. Visión de v0.3

En v0.2, `campaign.json` es de una sola vía: el motor genera un `World` en memoria y lo vuelca a disco. No hay manera de volver a cargar ese archivo. Hoy, técnicamente, eso no importa mucho porque la generación es determinista — el mismo seed siempre reproduce el mismo mundo. Pero esa garantía se rompe en el momento en que cualquier dato deje de depender solo del seed: y eso va a pasar pronto, porque el roadmap ya anuncia un editor (v0.8) donde el DM renombra lugares, mueve marcadores y bloquea elementos para que no cambien al regenerar. Si para entonces `campaign.json` sigue siendo de solo-escritura, esas ediciones no tienen dónde vivir.

v0.3 no construye el editor todavía. Construye la tubería que el editor va a necesitar: la capacidad de leer un `campaign.json` y reconstruir un mundo completo a partir de él, en lugar de a partir del seed. Es la diferencia entre "el seed es la fuente de verdad" (v0.1-v0.2) y "el archivo guardado es la fuente de verdad" (v0.3 en adelante).

Una regla de producto importante sale de esto, y conviene fijarla ahora: **el archivo guardado de una campaña siempre contiene los datos completos de DM**, sin importar qué audiencia se le pida a una exportación derivada. `--audience player` sigue existiendo, pero pasa a ser exclusivamente una propiedad de las exportaciones de salida (HTML/PNG/Markdown/JSON), nunca del archivo maestro. Esto evita un problema real: un DM no debería poder guardar accidentalmente su propia partida sin secretos y perderlos para siempre.

---

## 2. Features exactas

### 2.1 Cargar un `campaign.json` guardado

- Nueva función interna (no expuesta como subcomando — ver sección de decisión de diseño abajo) que lee un archivo `campaign.json` válido y reconstruye un objeto `World` idéntico en forma al que generó el archivo originalmente: mismos `Landmark` (con su `id`, `secret`, `danger`, `reward` completos), mismo `world_id`, mismo `seed`, mismo `locale`, mismo `tiles`.
- Esto **solo es posible** si el archivo fue guardado con los datos de DM completos. Un archivo exportado con `--audience player` (al que le falta el bloque `gm` en cada landmark) no se puede usar como archivo maestro — ver regla de la sección 1.
- Validación de `meta.schema_version` al cargar: si la versión del archivo no es una que esta versión de Atlasmancer reconoce, error claro y traducido (no un crash ni una carga silenciosa con datos corruptos). Para v0.3, la única versión reconocida es `"0.2.0"` y `"0.3.0"` — no hace falta un framework de migración todavía, solo una lista explícita de versiones soportadas.

### 2.2 Flujo "abrir y re-exportar" en el CLI

Decisión de diseño (ver justificación abajo): en vez de subcomandos nuevos (`create`/`open`/`export`) como sugería originalmente `docs/ROADMAP.md`, v0.3 extiende el CLI plano que ya existe con un flag `--open <archivo>`:

```bash
# Guardar una campaña (esto ya existe desde v0.2 — sigue igual)
atlasmancer --seed "salt-crown" --locale es --format campaign --output salt-crown.campaign.json

# Reabrir esa campaña y exportar un HTML para el DM
atlasmancer --open salt-crown.campaign.json --format html --output atlas.html

# Reabrir la misma campaña y exportar una versión segura para jugadores
atlasmancer --open salt-crown.campaign.json --format html --audience player --output atlas-jugadores.html

# Reabrir y volver a generar el mapa PNG imprimible
atlasmancer --open salt-crown.campaign.json --format png --output mapa.png
```

Reglas:

- Cuando se usa `--open`, las flags de generación (`--seed`, `--width`, `--height`, `--landmarks`) se ignoran porque el mundo ya existe; si el usuario las pasa igual, no es un error, simplemente no tienen efecto (evita que un typo rompa el flujo).
- Cuando se usa `--open`, `--locale` controla el idioma de la **exportación**, no del archivo guardado — un DM puede guardar en inglés y exportar al español sin volver a generar nada, porque el `campaign.json` guarda datos, no texto ya traducido.
- `--audience` sigue funcionando igual que en v0.2, pero ahora también aplica al re-exportar desde `--open`.
- Guardar (`--format campaign --output x.json`) **siempre** escribe con el bloque `gm` completo, sin importar qué `--audience` se haya pasado. Si el usuario pide explícitamente `--format campaign --audience player --output x.json`, Atlasmancer debe rechazarlo con un error claro explicando que los archivos maestros no se guardan en audiencia jugador (para eso existen los demás formatos de exportación).

### 2.3 Por qué `--open` en vez de subcomandos `create`/`open`/`export`

El roadmap original imaginaba subcomandos (`world-forge create`, `world-forge open`, `world-forge export`). Cambio esta recomendación por una razón concreta: introducir subcomandos significa reestructurar todo el parser de argparse y decidir qué flags pertenecen a cuál subcomando, un cambio de arquitectura grande para un beneficio que hoy no existe (`create` y "generar y exportar" son la misma operación: `--format campaign` ya hace exactamente eso desde v0.2). Un flag `--open` logra el mismo resultado funcional sin tocar nada del CLI que ya funciona y ya tiene tests. Si más adelante (v0.7 app web, o un CLI con muchas más acciones) el flujo realmente lo justifica, migrar a subcomandos en ese momento es razonable — pero no antes de que haya una segunda razón además de "abrir un archivo".

### 2.4 Documentación del formato

- README: nueva sección "Saving and reopening campaigns" con los cuatro comandos de ejemplo de la sección 2.2.
- `docs/ATLASMANCER_V0.2_SPEC.md` sección 5 ya documenta el schema; v0.3 no lo cambia, solo le agrega la capacidad de leerlo. (Si v0.3 necesita un campo nuevo, ver sección 5 de este documento.)

---

## 3. Qué NO debe entrar todavía

- ❌ Editor visual, edición manual de nombres/posiciones, "bloquear elementos para que no cambien al regenerar" (→ v0.8 Editor visual). v0.3 solo habilita la lectura/escritura del archivo; no agrega UI ni comandos de edición de campos individuales.
- ❌ Contenedor `.wforge` tipo ZIP con assets/notas/chunks. Mientras el único contenido sea el `campaign.json` plano (sin imágenes adjuntas, sin notas de sesión), un archivo `.json` simple es suficiente. Reconsiderar el contenedor cuando exista contenido binario real que empaquetar.
- ❌ Framework de migración de schema genérico. Una lista fija de versiones soportadas (`"0.2.0"`, `"0.3.0"`) es suficiente hasta que exista una tercera versión con cambios incompatibles reales.
- ❌ Subcomandos `create`/`open`/`export` (ver decisión de diseño 2.3).
- ❌ Guardado en IndexedDB / cualquier cosa de navegador (→ v0.7 Web MVP).
- ❌ Geografía, países, facciones, misiones — siguen siendo arrays vacíos reservados en el schema, sin tocar en v0.3.

---

## 4. Criterios de aceptación

| # | Criterio |
|---|---|
| 1 | `atlasmancer --seed x --format campaign --output save.json` seguido de `atlasmancer --open save.json --format html --output atlas.html` produce el mismo contenido narrativo (mismos hooks, NPCs, secretos) que `atlasmancer --seed x --format html --output atlas.html` directo. |
| 2 | Abrir un archivo guardado con `--audience player` (es decir, sin bloque `gm`) da un error claro y traducido, no una excepción cruda ni un mundo con campos faltantes silenciosos. |
| 3 | `atlasmancer --format campaign --audience player --output save.json` (intentar guardar un archivo maestro sin secretos) falla con un error claro explicando que el master siempre incluye datos de DM. |
| 4 | Abrir un archivo con un `meta.schema_version` no reconocido (ej. `"9.9.9"` inventado) da un error claro, no un crash. |
| 5 | `--open` ignora sin error las flags `--seed`/`--width`/`--height`/`--landmarks` si se pasan igual. |
| 6 | Reabrir y exportar en un `--locale` distinto al que se usó para guardar produce el texto narrativo en el nuevo idioma, sin tocar el seed, los nombres propios ni las posiciones. |
| 7 | Tests cubren: round-trip completo (guardar → abrir → comparar `World` reconstruido contra el original campo por campo), rechazo de archivo player-safe como maestro, rechazo de guardar maestro en audiencia jugador, rechazo de `schema_version` desconocida. |

---

## 5. Modelo de datos / cambios de formato

No se introduce un schema nuevo: v0.3 reutiliza `campaign.json` v0.2.0 tal cual está documentado en `docs/ATLASMANCER_V0.2_SPEC.md` sección 5. Dos adiciones puntuales:

- `meta.schema_version` pasa a aceptar `"0.3.0"` además de `"0.2.0"` — en la práctica ambas se leen igual en v0.3 (no hay cambios de estructura todavía, solo se documenta que la versión del *generador* avanzó). Escribir siempre con la versión actual; leer aceptando ambas.
- Ninguna clave nueva en el JSON. El round-trip usa exactamente `meta`, `title`, `map.width`, `map.height`, `map.ascii`, y `landmarks[].{id,symbol,kind,name,x,y,public.{hook,rumor,npc},gm.{secret,danger,reward}}` para reconstruir `World`/`Landmark` campo por campo.

Regla de reconstrucción: el `World` reconstruido debe ser indistinguible (mismos valores en todos los campos) del `World` que generó el archivo originalmente — esto es lo que el test de round-trip de la sección 4 verifica.

---

## 6. Textos nuevos EN/ES

| Clave | EN | ES |
|---|---|---|
| `cli.flags.open` | Reopen a previously saved campaign.json instead of generating a new world. | Reabre un campaign.json guardado en vez de generar un mundo nuevo. |
| `cli.errors.campaign_missing_gm_data` | This file has no GM data (it was exported with --audience player) and cannot be reopened as a campaign. Reopen the original GM save instead. | Este archivo no tiene datos de DM (se exportó con --audience player) y no se puede reabrir como campaña. Reabre el guardado original de DM. |
| `cli.errors.campaign_audience_player_not_allowed` | Campaign saves always include GM data; --audience player cannot be combined with --format campaign --output. Export another format if you need a player-safe copy. | Los guardados de campaña siempre incluyen datos de DM; --audience player no se puede combinar con --format campaign --output. Exporta otro formato si necesitas una copia segura para jugadores. |
| `cli.errors.unsupported_schema_version` | This file uses campaign schema '{version}', which this version of Atlasmancer does not support. Supported: {supported}. | Este archivo usa el schema de campaña '{version}', que esta versión de Atlasmancer no soporta. Soportados: {supported}. |

---

## 7. Riesgos

- **Determinismo silencioso vs. archivo como fuente de verdad**: hoy, regenerar con el mismo seed siempre da lo mismo, así que es tentador pensar que "abrir" y "regenerar desde el seed" son intercambiables. No lo serán en cuanto exista edición manual (v0.8). Construir el loader ahora, aunque parezca redundante con regenerar, es lo que evita una reescritura grande después.
- **Confusión entre "exportar" y "guardar"**: si la regla de la sección 2.2 (el master siempre es `gm`) no queda clara en los mensajes de error, un usuario puede terminar pensando que perdió datos cuando en realidad nunca los guardó en formato jugador a propósito. Los mensajes de error de la sección 6 están escritos para explicar el "por qué", no solo el "qué".
- **Archivos `campaign.json` de v0.2 "salvajes"**: cualquiera que haya generado un `campaign.json` antes de v0.3 ya tiene archivos válidos con `schema_version: "0.2.0"`. Hay que aceptarlos explícitamente, no solo la versión nueva.
- **Tentación de adelantar el contenedor `.wforge`**: cuando se diseña el loader es tentador "ya que estamos" envolver todo en un ZIP con manifest. Resistir eso — no hay todavía ningún asset binario que justifique la complejidad adicional.

---

## 8. Lista priorizada de tareas para Codex

1. Función de carga: leer un `campaign.json`, validar `meta.schema_version` contra una lista explícita de versiones soportadas (`"0.2.0"`, `"0.3.0"`), dar error traducido si no coincide.
2. Reconstrucción de `World`/`Landmark` a partir del JSON cargado (campo por campo, ver sección 5).
3. Detección de archivo sin bloque `gm` (exportado en audiencia jugador) al intentar abrirlo como maestro → error traducido (sección 6).
4. Flag `--open <archivo>` en `atlasmancer/cli.py`; cuando está presente, se omite la generación y se usa el mundo cargado; `--seed`/`--width`/`--height`/`--landmarks` se ignoran sin error.
5. Regla de guardado: `--format campaign --audience player --output <archivo>` debe fallar con el error de la sección 6; sin `--audience` o con `--audience gm` debe seguir funcionando como hoy.
6. Nuevas claves de locale (sección 6) en `locales/en.json` y `locales/es.json`.
7. Tests: round-trip completo, rechazo de archivo player-safe como maestro, rechazo de guardar maestro en audiencia jugador, rechazo de `schema_version` desconocida, `--open` ignorando flags de generación sin error.
8. README: sección "Saving and reopening campaigns" con los comandos de ejemplo de la sección 2.2.
9. Actualizar `examples/` si aplica: considerar agregar `examples/example-campaign.json` como caso de prueba real de `--open` en la suite de tests (reutilizar el ya existente de v0.2 en vez de crear uno nuevo).

Orden recomendado: 1 → 2 → 7 (parcial: round-trip) → 3 → 5 → 4 → 6 → 7 (resto) → 8 → 9.
