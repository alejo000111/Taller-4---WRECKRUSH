class_name CamaraSeguidora
extends Camera3D
## Solución del Taller 2. Cámara que persigue al objetivo con suavidad.
## Va como hija de Mundo (no del Jugador), con process_priority mayor que el Jugador
## para moverse DESPUÉS de él en cada frame.

@export var objetivo: Node3D
@export var motor: Motor                  # opcional: para la anticipación (extra)
@export var desfase := Vector3(0, 5, 7)
@export var k := 3.0                      # rigidez: más grande, más pegada
@export var usar_factor_fijo := false     # nivel 2: lerp con factor fijo por frame
@export var factor_fijo := 0.1
@export var anticipacion := 0.0           # extra: segundos de velocidad hacia adelante


func _ready() -> void:
	global_position = posicion_deseada()   # arranca en su sitio, no viaja desde el origen
	look_at(objetivo.global_position)


func posicion_deseada() -> Vector3:
	var p := objetivo.global_position + desfase
	if motor != null:
		p += motor.velocidad * anticipacion
	return p


func _process(delta: float) -> void:
	var alpha := factor_fijo if usar_factor_fijo else alpha_exponencial(k, delta)
	global_position = suavizar(global_position, posicion_deseada(), alpha)
	look_at(objetivo.global_position)


## Nivel 3: fracción a avanzar en este frame. Tras 1 s queda e^(-k) a cualquier FPS.
static func alpha_exponencial(k_: float, dt: float) -> float:
	return 1.0 - exp(-k_ * dt)


## Función pura: lerp escrito a mano.
static func suavizar(actual: Vector3, deseada: Vector3, alpha: float) -> Vector3:
	return actual + (deseada - actual) * alpha


## Extra: la base que arma look_at, con productos cruz. La cámara mira hacia su -Z.
static func base_mirando(desde: Vector3, hacia: Vector3, arriba := Vector3.UP) -> Basis:
	var adelante := Vectores.normalizar(hacia - desde)
	var derecha := Vectores.normalizar(adelante.cross(arriba))   # cero si son paralelos
	var arriba_real := derecha.cross(adelante)
	return Basis(derecha, arriba_real, -adelante)
