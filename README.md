# WRECKRUSH — v1.0 (port a Godot)

**DESTROY. GET RICH. REBIRTH.** Simulador de destrucción 3D. Port a **Godot 4.7 (GDScript)** del juego de Roblox del equipo OpenGames, construido a partir de los talleres (Rol 1, 2, 3 y Entrega Final) y la *Guía completa* (estado al 13-oct-2026).

## Qué incluye la v1.0

Las reglas cerradas del **Taller 4** (Tramos 1, 2 y 3) sobre la base del Corte 1:

- **3 islas**: Scrap Yard (29 objetos), Downtown (24) y Industrial (24), cada una con su tabla de objetos. Las puertas de Downtown (1 500 Scrap) y Industrial (6 000 Scrap) quedan abiertas para siempre al pagarlas.
- **Una sola moneda, el Scrap**, que se suma directo al romper (sin orbes, imán ni bolsa).
- **2 mejoras**: DAMAGE (12 niveles, precio `25 × 1.5^n`, daño 40 al final) y ATTACK SPEED (5 niveles, `600 × 1.5^(m-1)`).
- **3 colosos** (Scrap Colossus, Downtown Crusher, Industrial Titan) con 4 placas, núcleo expuesto 16 s y golpe marcado 1.5 s antes (25 de daño; el jugador tiene 100). Retarlos pide **daño 40**. Se esquivan **saltando** (1 m, 0.9 s en el aire).
- Los colosos reaccionan: ojos rojos y giro de cabeza al romper objetos, ojos verdes al vencerlos. Al vencer a los 3 sale la **pantalla final con el tiempo total** y se abre el **modo maestría** (hasta 2 estrellas por coloso).
- Efectos y ambiente del taller visual: contorno amarillo, explosiones por tamaño, números flotantes, vibración de cámara, atardecer fijo, tinte por distrito.
- HUD con meta "NEXT", tutorial de 6 pasos con flecha, avisos de mitad de la meta y guardado automático.

Lo que **no** entra (ver `docs/ALCANCE_V1.md` y `docs/DECISIONES_TALLER_4.md`): Rebirth, Workshop, mascotas, tienda, críticos, XP y niveles, más de una herramienta, multijugador.

## Cómo ejecutarlo

1. Instala [Godot 4.7](https://godotengine.org/download) (estándar, no .NET). Si abres el proyecto con otra versión de 4.x, Godot avisa; es normal.
2. Abre la carpeta con Godot (la primera vez importa los recursos) y pulsa **F5**.

Por consola:

```bash
godot --headless --path . --import
godot --path .
```

## Controles

| Acción | Tecla |
|---|---|
| Moverse | WASD / flechas |
| Atacar (mantener) | Clic izquierdo o F, o botón WRECK |
| Saltar (esquivar al jefe) | Espacio |
| Interactuar (mantener en consolas) | E |
| Girar cámara | Arrastrar con clic derecho |
| Mejoras / Ajustes | U / Tab |
| Cerrar panel | Retroceso o Esc |

Trucos de desarrollo (solo builds de debug): **F1** +10K Scrap, **F2** mejoras al máximo, **F3** abrir las 3 islas, **F4** despertar a los colosos.

## Pruebas

```bash
godot --headless --path . --import
godot --headless --path . res://tests/test_runner.tscn
```

98 pruebas: fórmulas y tablas de los talleres (precios, objetos por vuelta, colosos), economía, metas, guardado, assets (modelos, iconos y cielo) y la máquina de estados del coloso. Sale con código 1 si algo falla.

## Estructura

```
scripts/core      Formulas, Curvas (funciones puras), colores, input
scripts/config    GameConfig: todo el balance
scripts/autoload  GameState (estado y guardado), Sfx, Fx (EffectsController)
scripts/player    Player, CameraController, HammerController, interacción, tutorial
scripts/world     CityWorld, Destructible, AmbienceController
scripts/boss      Coloso, BossPart, BossWarning
scripts/ui        HUD y paneles
shaders           contorno, barra de vida, aviso del jefe, cielo
tests             pruebas automáticas
docs              arquitectura y alcance
assets            arte que usa el juego: modelos, materiales, cielo, iconos, marca, efectos
assets_pendientes arte guardado para siguientes cortes (Godot no lo importa)
```
