class_name Agarrador
extends Node3D
## Nivel 3: con E, agarra la pelota que tiene adelante (raycast de 3 m) y la lleva en la Mano;
## con E otra vez, la lanza hacia adelante con un impulso.

@export var modelo: Node3D          # el que gira hacia donde se camina (su -Z es "adelante")
@export var mano: Node3D
@export var alcance := 3.0          # m
@export var impulso_lanzamiento := 8.0   # N·s

var cargada: RigidBody3D = null
var antes := false


func _physics_process(_delta: float) -> void:
	var ahora := Input.is_key_pressed(KEY_E)
	if ahora and not antes:
		if cargada == null:
			agarrar()
		else:
			lanzar()
	antes = ahora


func adelante() -> Vector3:
	return -modelo.global_transform.basis.z.normalized()


func agarrar() -> void:
	var desde := global_position
	var consulta := PhysicsRayQueryParameters3D.create(desde, desde + adelante() * alcance, 2)   # máscara: solo pelotas
	var choque := get_world_3d().direct_space_state.intersect_ray(consulta)
	if choque.is_empty() or not (choque.collider is RigidBody3D):
		return
	cargada = choque.collider
	get_parent().add_collision_exception_with(cargada)   # el jugador no choca con lo que carga
	cargada.freeze = true
	cargada.reparent(mano)
	cargada.position = Vector3.ZERO


func lanzar() -> void:
	var p := cargada
	cargada = null
	p.reparent(owner)   # owner: la escena del Mundo (el Agarrador se guardó dentro de ella)
	get_parent().remove_collision_exception_with(p)
	p.freeze = false
	p.apply_central_impulse(adelante() * impulso_lanzamiento)
