class_name CameraController
extends Node3D

const DESFASE := Vector3(0, 8, 12)
const K := 5.0
const K_GIRO := 8.0
const K_RETORNO := 3.0
const PAUSA_MANUAL := 2.0
const DURACION_VIBRACION := 0.15
const SENSIBILIDAD := 0.005
const ALTURA_MIRADA := 3.0

var objetivo: Node3D
var yaw: float = 0.0
var inclinacion: float = 0.0
var camara: Camera3D

var _vibracion: float = 0.0
var _tiempo_vibracion: float = 0.0
var _vista_libre: float = 0.0
var _pausa_manual: float = 0.0


func _ready() -> void:
	camara = Camera3D.new()
	camara.fov = 70.0
	camara.near = 0.2
	camara.far = 6000.0
	camara.current = true
	add_child(camara)
	Fx.sacudida_camara.connect(vibrar)


func vibrar(intensidad: float) -> void:
	if not GameState.ajustes.get("camera_shake", true):
		return
	_vibracion = maxf(_vibracion, intensidad)
	_tiempo_vibracion = DURACION_VIBRACION


func seguir_jugador(yaw_jugador: float, dt: float) -> void:
	_pausa_manual = maxf(_pausa_manual - dt, 0.0)
	if _pausa_manual <= 0.0:
		_vista_libre = lerp_angle(_vista_libre, 0.0, Curvas.suavizado(K_RETORNO, dt))
	yaw = lerp_angle(yaw, yaw_jugador + _vista_libre, Curvas.suavizado(K_GIRO, dt))


func girar_a_mano(angulo: float) -> void:
	yaw += angulo
	_vista_libre = wrapf(_vista_libre + angulo, -PI, PI)
	_pausa_manual = PAUSA_MANUAL


func desfase_actual() -> Vector3:
	var inclinado := Basis(Vector3.RIGHT, inclinacion) * DESFASE
	return Basis(Vector3.UP, yaw) * inclinado


func posicion_meta() -> Vector3:
	return objetivo.global_position + desfase_actual()


func actualizar(dt: float) -> void:
	if objetivo == null:
		return
	if objetivo.has_method("yaw_mirada"):
		seguir_jugador(objetivo.call("yaw_mirada"), dt)
	global_position = Curvas.acercar(global_position, posicion_meta(), K, dt)
	look_at(objetivo.global_position + Vector3(0, ALTURA_MIRADA, 0), Vector3.UP)
	if _tiempo_vibracion > 0.0:
		_tiempo_vibracion -= dt
		var fuerza := _vibracion * clampf(_tiempo_vibracion / DURACION_VIBRACION, 0.0, 1.0)
		camara.h_offset = randf_range(-1.0, 1.0) * fuerza * 0.6
		camara.v_offset = randf_range(-1.0, 1.0) * fuerza * 0.6
	else:
		_vibracion = 0.0
		camara.h_offset = 0.0
		camara.v_offset = 0.0


func saltar_a(posicion: Vector3) -> void:
	if objetivo != null:
		global_position = posicion + desfase_actual()


func _process(delta: float) -> void:
	actualizar(delta)


func _unhandled_input(evento: InputEvent) -> void:
	if evento is InputEventMouseMotion and Input.is_action_pressed("camera_orbit"):
		girar_a_mano(-evento.relative.x * SENSIBILIDAD)
		inclinacion = clampf(inclinacion - evento.relative.y * SENSIBILIDAD, -0.6, 0.35)
