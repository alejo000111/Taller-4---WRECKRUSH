# Orden recomendado para estudiar y reconstruir el juego

Léanlo en este orden; cada paso depende del anterior. Intenten explicar cada archivo con sus palabras antes de pasar al siguiente.

1. **Fórmulas puras** — `scripts/core/formulas.gd`, `curvas.gd`. Son las cuentas de los talleres (velocidad, imán, daño, suavizado). Ejecuten `tests/test_runner.tscn` y vean cómo se comprueban.
2. **Balance** — `scripts/config/game_config.gd`. Tablas de objetos, mejoras, herramientas y jefe, copiadas de la Guía.
3. **Estado del juego** — `scripts/autoload/game_state.gd`. Cash, Scrap, XP, mejoras, guardado. Aquí vive la economía.
4. **Jugador y cámara** — `scripts/player/player.gd`, `camera_controller.gd` (aceleración 80, fricción 64, k = 5).
5. **Objetos que se rompen** — `scripts/world/destructible.gd`, `scrap_orb.gd` y `scripts/autoload/effects_controller.gd`.
6. **Atacar** — `scripts/player/hammer_controller.gd` (cooldown, alcance, crítico).
7. **El mundo** — `scripts/world/city_world.gd`, `boss_island.gd`, `ambience_controller.gd`. En el editor se ven en la vista previa (están marcados `@tool`).
8. **El jefe** — `scripts/boss/` (`scrap_colossus.gd` es una máquina de estados: INTRO, ARMADURA, EXPUESTO...).
9. **Interfaz** — `scripts/ui/`. Todo se construye por código y escucha señales de `GameState`.
10. **Tutorial** — `scripts/player/onboarding.gd`.

La escena `scenes/main.tscn` junta las piezas: Ciudad, RustAtoll, Ambiente, Jugador y Cámara.
