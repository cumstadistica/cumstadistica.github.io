# MEMORY.md - Memoria Curada

## Preferencias del usuario (Gonzalo)

- Quiere respuestas directas y orientadas a cerrar configuración rápido.
- En grupo, usar los alias cortos entre paréntesis: **C, U, J**.
- Mismo estilo de respuesta en DM y grupo (sin modo distinto).
- En Cumstadística, prioridad a publicar factos cuando la mención a "Chat" sea clara.

## Reglas operativas (Cumstadística)

- Si mencionan a "Chat" con un facto claro: publicar directamente en la web.
- No pedir comando explícito cuando la intención de publicar sea evidente.
- Respetar al máximo el texto original del facto; corregir solo lo mínimo.
- Mapa de autores: Gonzalo=@gonperezramirez → `c`; Hugo=@Ugo_Bugo → `u`; Jose Angel=@Presio6151 → `j`.

## Configuración relevante (Telegram)

- Bot/agent activo: `cumstadistica`.
- Group policy en cuenta `cumstadistica`: `allowlist`.
- Sender allowlist grupo: `978669545`, `1660589659`, `1541363642`.
- Grupos cuenta `cumstadistica`:
  - `*` → `requireMention: true`
  - `-1001291109015` → `requireMention: true`

## Automatizaciones de memoria

- Heartbeat activo para registrar decisiones/tareas en `memory/YYYY-MM-DD.md`.
- Cron diario: `memory-daily-consolidation` (22:30 Europe/Berlin, silencioso).
- Cron semanal: `memory-weekly-cleanup` (domingo 11:00 Europe/Berlin, silencioso).

## Nota

Actualizar esta memoria cuando cambien reglas del grupo, preferencias de trato o configuración de Telegram.
