# Rename Plan: world-forge to Atlasmancer

Estado: preparado, no ejecutado

Este plan existe para que el rename tecnico se haga una vez, con cuidado, y sin romper el prototipo actual mientras esperamos la spec de v0.2.

## Objetivo

Cambiar el proyecto de `world-forge` a Atlasmancer en producto, repo, paquete, CLI y documentacion.

## Estrategia

Hacer el rename en dos pasos:

1. Preparacion documental.
2. Rename tecnico con compatibilidad temporal.

Este commit cubre el paso 1.

## Paso 1: Preparacion documental

- [x] Decidir nombre oficial: Atlasmancer.
- [x] Registrar dominio objetivo: `Atlasmancer.gt.tc`.
- [x] Crear decisiones del proyecto.
- [x] Crear base de marca.
- [x] Crear checklist de rename.
- [x] Actualizar roadmap y deployment docs.
- [x] Mantener `world-forge` como CLI actual hasta ejecutar rename tecnico.

## Paso 2: Rename tecnico

Pendiente.

Cambios esperados:

- [ ] Renombrar paquete Python `world_forge` a `atlasmancer`.
- [ ] Cambiar paquete instalable `world-forge` a `atlasmancer`.
- [ ] Cambiar comando principal `world-forge` a `atlasmancer`.
- [ ] Mantener alias temporal `world-forge`.
- [ ] Actualizar imports internos.
- [ ] Actualizar tests.
- [ ] Actualizar README.
- [ ] Actualizar docs.
- [ ] Actualizar URLs de GitHub cuando el repo sea renombrado.
- [ ] Actualizar ejemplos.
- [ ] Validar `python -m unittest`.
- [ ] Validar `atlasmancer --help`.
- [ ] Validar alias `world-forge --help`.

## Compatibilidad recomendada

Durante v0.2:

- `atlasmancer` debe ser el comando nuevo.
- `world-forge` debe seguir funcionando como alias con aviso suave.
- `python -m world_forge` puede mantenerse solo durante una version.

En v0.3 o v0.4:

- Deprecar alias `world-forge`.
- Documentar fecha de retiro.

## Riesgos

- Romper instalaciones editables existentes.
- Romper imports de tests.
- Confundir usuarios si README promete `atlasmancer` antes de que exista.
- Dejar URLs antiguas en docs.

## Criterios de aceptacion del rename tecnico

- `python -m unittest` pasa.
- `atlasmancer --help` funciona.
- `world-forge --help` funciona como alias temporal.
- `python -m atlasmancer` funciona.
- README usa Atlasmancer como nombre principal.
- Docs no presentan World Forge como nombre actual.
- GitHub queda limpio sin archivos generados accidentales.
