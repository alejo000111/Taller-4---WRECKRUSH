class_name Orientador
extends Node
## Responsabilidad: girar el Modelo (no el Jugador) hacia la dirección de movimiento.

@export var modelo: Node3D
@export var velocidad_giro := 10.0


func mirar(direccion: Vector3, dt: float) -> void:
	# Sin dirección no se toca el ángulo: el modelo se queda mirando hacia donde iba.
	if direccion == Vector3.ZERO:
		return
	modelo.rotation.y = lerp_angle(modelo.rotation.y, angulo_hacia(direccion), velocidad_giro * dt)


## En Godot "adelante" con ángulo 0 es -Z, y girar en +Y lleva -Z hacia -X:
## rotar (0, 0, -1) un ángulo θ da (-sen θ, 0, -cos θ), así que θ = atan2(-x, -z). En radianes.
static func angulo_hacia(d: Vector3) -> float:
	return atan2(-d.x, -d.z)
