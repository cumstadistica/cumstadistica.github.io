# MEMORY.md

## 1) Preferencias del usuario
- Nombre: Gonzalo.
- Trato preferido: en grupo usar alias cortos (C, U, J).
- Estilo: respuestas directas y orientadas a resolver rápido.
- DM y grupo: mantener el mismo estilo de respuesta.

## 2) Reglas de grupo (Cumstadística)
- Si mencionan a "Chat" con un facto claro, publicarlo directamente en la web.
- No pedir comando explícito cuando la intención de publicar sea evidente.
- Respetar al máximo el texto original del facto; corregir solo lo mínimo.
- Mapa de autores: Gonzalo (@gonperezramirez) = `c`; Hugo (@Ugo_Bugo) = `u`; Jose Angel (@Presio6151) = `j`.

## 3) Setup técnico estable
- Agente principal: `cumstadistica`.
- Canal activo principal: Telegram.
- Telegram por cuenta (`accounts.cumstadistica`):
  - `groupPolicy: allowlist`
  - `groupAllowFrom: [978669545, 1660589659, 1541363642]`
  - `groups[*].requireMention: true`
  - `groups[-1001291109015].requireMention: true`
- Hooks externos WAHA/OpenClaw: desactivados (`hooks.enabled: false`).
- Wrapper CLI local: `/home/node/.local/bin/openclaw`.

## 4) Automatizaciones (cron/heartbeat)
- Heartbeat: revisar actividad, registrar decisiones/tareas en `memory/YYYY-MM-DD.md`, consolidar en `MEMORY.md`.
- `memory-daily-consolidation`: diario 22:30 (Europe/Berlin), silencioso.
- `memory-weekly-cleanup`: domingo 11:00 (Europe/Berlin), silencioso.
- `gateway-weekly-healthcheck`: domingo 11:15 (Europe/Berlin), anunciado.

## 5) Decisiones tomadas (histórico corto)
- 2026-02-28 — Mantener mismo estilo de respuesta en grupo y privado.
- 2026-02-28 — Configuración de grupos Telegram centralizada por cuenta (`cumstadistica`) para evitar duplicados.
- 2026-02-28 — Desactivar hooks externos (`hooks.enabled=false`) al no usar conexión directa con WAHA.

## 6) Pendientes reales
- [ ] Hacer prueba E2E de grupo Telegram (sin mención/no responde; con mención/responde).
- [ ] Revisar periódicamente que los cron de salud y memoria sigan pasando en verde.

## 7) Operativa de memoria
- Los cierres diarios se mantienen breves, factuales y sin inventar datos.
- Si no hay novedades, dejar explícitamente: "sin cambios relevantes".
