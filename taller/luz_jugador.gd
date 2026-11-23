class_name LuzJugador
extends OmniLight3D
## Tarea C · Niveles 1 y 3. El brillo del martillo: una luz hija del Jugador que lo acompaña.
## Cae como 1/d² (Attenuation 2) y Godot la corta en el Range.

@export var rango := 3.0           # m: hasta dónde alumbra el martillo
@export var altura := 1.0          # m sobre los pies del jugador (a la altura del martillo)


func _ready() -> void:
	position = Vector3(0.0, altura, 0.0)
	omni_range = rango
	omni_attenuation = 2.0         # la que se parece a 1/d²


## Nivel 1. Función pura: lo que llega a distancia d si a 1 m llega 1.
## El maxf evita dividir por cero en d = 0.
static func atenuacion(d: float, exponente: float = 2.0) -> float:
	return 1.0 / pow(maxf(d, 0.0001), exponente)


## Nivel 3. Función pura: el brillo de Blinn-Phong, max(0, n · h)^brillo,
## con h el vector medio entre "hacia la luz" y "hacia el ojo".
static func blinn_phong(normal: Vector3, hacia_luz: Vector3,
		hacia_ojo: Vector3, brillo: float) -> float:
	var n := Vectores.normalizar(normal)
	var l := Vectores.normalizar(hacia_luz)
	var v := Vectores.normalizar(hacia_ojo)
	var h := Vectores.normalizar(l + v)
	return pow(maxf(0.0, n.dot(h)), brillo)
