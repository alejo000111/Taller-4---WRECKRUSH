# Decisiones del Taller 4 aplicadas al juego

Fuente: `Tramo_1.docx` (Alejandro Rivera), `Tramo_2.docx` (Cristian Serrano) y `Tramo_3.docx`. El "documento de decisiones (versión Godot)" que citan **no estaba adjunto**: se dedujo de los tres tramos.

| Regla del taller | Dónde está en el código | Prueba |
|---|---|---|
| Tabla Isla 1: 8 barriles, 4 señales, 5 cajas, 3 llantas, 5 coches, 3 montacargas, 1 contenedor (29) | `GameConfig.OBJETOS["scrap_yard"]` | `Isla 1: 29 objetos`, `1,631 por vuelta` |
| Premio 30 %, y 40 % para los de 70 de vida o menos (barril 12, señal 14, caja 18, llantas 28) | mismo archivo, campo `scrap` | 1,631 Scrap por vuelta |
| Tabla Isla 2: buzón, banca, auto, autobús, kiosco (24), 6,396 por vuelta | `OBJETOS["downtown"]` | prueba de tablas |
| Tabla Isla 3: tubería, generador, camión, excavadora, silo (24), 11,664 por vuelta | `OBJETOS["industrial"]` | prueba de tablas |
| Reaparición 5 a 35 s | campo `respawn` | prueba de tablas |
| DAMAGE nivel n cuesta `25 × 1.5^n`, tope 12 (daño 40) | `Formulas.precio_mejora`, `GameConfig.MEJORAS` | 38 ... 3,244, suma 9,657 |
| ATTACK SPEED nivel m cuesta `600 × 1.5^(m-1)`, 5 niveles, golpe cada `0.45 / (1 + 0.06 m)` | mismo | 600 ... 3,038 y 0.381 / 0.346 s |
| Sin bolsa, sin orbes, sin imán | `GameState.agregar_scrap` suma directo | prueba de economía |
| Puertas 1,500 y 6,000 Scrap, abiertas para siempre | `GameState.desbloquear_zona`, `CityWorld` | prueba de economía |
| Coloso: 4 placas `800 + 200 (n-1)`, núcleo `700 + 100 (n-1)`, golpe al suelo cada `7 - n` s, núcleo expuesto 16 s, aviso 1.5 s, 25 de daño, jugador 100 | `Formulas`, `GameConfig.COLOSO`, `Coloso` | pruebas de fórmulas y del coloso |
| Retar un coloso pide daño 40; la consola dice "DAMAGE 40 REQUIRED" | `Coloso._intentar_retar` | prueba del coloso |
| Ojos rojos a los 15 / 12 / 12 objetos rotos; cabeza gira y consola se enciende a los 29 / 24 / 24 | `Coloso.refrescar_aspecto`, `GameConfig.COLOSOS` | prueba del coloso |
| Ojos verdes al vencerlo; con los 3 vencidos todos miran al jugador | `Coloso.mira_al_jugador` | prueba del coloso |
| Premios: coloso 1 = 1,500, coloso 2 = 3,600, coloso 3 = victoria final con tiempo total | `GameState.registrar_victoria_coloso`, `Hud._mostrar_final` | prueba de progreso |
| Maestría: menos de 50 / 60 / 70 s, o sin recibir daño; 1 estrella por condición (máx. 2); no da Scrap | `GameState.registrar_victoria_coloso` | prueba de progreso |
| Salto de 1 m y 0.9 s: esquiva si estás en el aire cuando cae el golpe | `Player`, `Coloso._resolver_impacto` | prueba de fórmulas |
| Distancias en metros (1 stud = 0.28 m) | `Formulas.studs_a_metros` (el mundo sigue en studs) | alcance 3 m, caminar 4.5 m/s, 55 m |
| Avisos de mitad de la meta (NEXT 750 de 1,500; 3,000 y 4,500 de 6,000; falta para daño 12) | `GameState._revisar_hitos` | prueba de progreso |
| Plan de metas (daño 1-8, puerta, daño 9, velocidad 1, ...) | `GameState.plan_de_metas` | prueba de progreso |

## Cosas que los tramos dejan sin resolver (para decidir en equipo)
- **Isla 3**: el Tramo 3 usa el 30 % para todos sus objetos; los Tramos 1 y 2 usaron 40 % para los de poca vida. Se siguió la tabla del Tramo 3 tal cual (la tubería de 240 de vida paga 72).
- **Reaparición**: la fórmula `5 + 30 (vida - 30) / 1170` no da los valores de la tabla de la Isla 3 (daría 10 y 14, la tabla dice 9 y 11). Se usaron los números de las tablas.
- **Tramo 1 vacío 3 y Tramo 2 vacío 3**: coinciden. El Tramo 3 menciona "mejora 12 = 3,244" y "velocidad 4 y 5" que se compran con el premio del coloso 2: el juego no las bloquea, solo las sugiere en la meta.
- **Los premios se pagan una sola vez** por coloso; en maestría no dan Scrap (así lo dice el Tramo 3, pero no aclara si se puede repetir antes de vencer a los 3: aquí no).
- **Muerte**: los tramos no dicen cuánto esperar; se mantuvieron los 45 s del Rol 3.
- Todos los tiempos de los tramos son cálculos, no pruebas de juego: hay que cronometrar jugando.
