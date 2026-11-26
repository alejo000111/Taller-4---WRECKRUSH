class_name Player
extends CharacterBody3D

signal murio
signal salud_cambio(salud: float, maxima: float)
signal recibio_dano

const ACELERACION := 80.0
const FRICCION := 64.0
const VELOCIDAD := 16.0
const VELOCIDAD_SALTO := 15.87
const GRAVEDAD := 35.27
const ALTURA_CAPSULA := 5.0
const RADIO_CAPSULA := 1.0
const INTERVALO_PUNTO_SEGURO := 0.5
const POSE_DESCANSO := 0.87
const POSE_PREPARADO := 2.1
const POSE_GOLPE := -0.35
const VELOCIDAD_GIRO := 3.0
const FACTOR_RETROCESO := 0.6

var camara: CameraController
var salud: float = GameConfig.VIDA_JUGADOR
var muerto: bool = false
var ultimo_punto_seguro: Vector3 = Vector3(0, 3, 55)

var _modelo: Node3D
var _pivote_martillo: Node3D
var _cabeza_martillo: MeshInstance3D
var _material_cuerpo: StandardMaterial3D
var _tween_golpe: Tween
var _tiempo_punto_seguro: float = 0.0


func _ready() -> void:
	add_to_group("player")
	collision_layer = 2
	collision_mask = 1 | 4 | 8
	var colision := CollisionShape3D.new()
	var capsula := CapsuleShape3D.new()
	capsula.radius = RADIO_CAPSULA
	capsula.height = ALTURA_CAPSULA
	colision.shape = capsula
	colision.position = Vector3(0, ALTURA_CAPSULA * 0.5, 0)
	add_child(colision)
	_construir_modelo()


static func direccion_adelante(yaw_modelo: float) -> Vector2:
	return Vector2(-sin(yaw_modelo), -cos(yaw_modelo))


func yaw_mirada() -> float:
	return _modelo.rotation.y


func _construir_modelo() -> void:
	_modelo = Node3D.new()
	add_child(_modelo)
	_material_cuerpo = Formas.material(GameColors.NARANJA, 0.7)
	Formas.malla(_modelo, "cyl", Vector3(1.8, 2.6, 1.8), Vector3(0, 2.4, 0), _material_cuerpo)
	Formas.malla(_modelo, "box", Vector3(0.8, 2.0, 0.8), Vector3(-0.5, 0.9, 0), Formas.material(GameColors.GRIS_OSCURO))
	Formas.malla(_modelo, "box", Vector3(0.8, 2.0, 0.8), Vector3(0.5, 0.9, 0), Formas.material(GameColors.GRIS_OSCURO))
	Formas.malla(_modelo, "sph", Vector3(1.5, 1.5, 1.5), Vector3(0, 4.2, 0), Formas.material(Color("#E8C9A0")))
	Formas.malla(_modelo, "box", Vector3(1.6, 0.5, 1.6), Vector3(0, 4.9, 0), Formas.material(GameColors.AMARILLO, 0.6))
	_pivote_martillo = Node3D.new()
	_pivote_martillo.position = Vector3(1.3, 2.8, -0.3)
	_modelo.add_child(_pivote_martillo)
	var martillo := Modelos.instanciar(String(GameConfig.MARTILLO["modelo"]))
	if martillo != null:
		var soporte := Node3D.new()
		soporte.rotation.x = -PI * 0.5
		_pivote_martillo.add_child(soporte)
		soporte.add_child(martillo)
		var l := Modelos.limites(martillo)
		var escala := 4.9 / l.size.y
		martillo.scale = Vector3.ONE * escala
		martillo.position = Vector3(-l.get_center().x * escala, -l.position.y * escala - 0.4, -l.get_center().z * escala)
	else:
		Formas.malla(_pivote_martillo, "box", Vector3(0.35, 0.35, 3.4), Vector3(0, 0, -1.7), Formas.material(Color("#6B4A2A")))
		_cabeza_martillo = Formas.malla(_pivote_martillo, "box", Vector3(1.5, 1.5, 2.4), Vector3(0, 0, -3.6), Formas.material(GameConfig.MARTILLO["color"], 0.4, 0.8))
	_pivote_martillo.rotation.x = POSE_DESCANSO


func _physics_process(delta: float) -> void:
	if muerto:
		velocity = Vector3.ZERO
		return
	if not is_on_floor():
		velocity.y -= GRAVEDAD * delta
	elif velocity.y < 0.0:
		velocity.y = 0.0
	var giro := 0.0
	var avance := 0.0
	if not GameState.hay_panel_abierto():
		giro = Input.get_axis("move_left", "move_right")
		avance = Input.get_axis("move_back", "move_forward")
		if Input.is_action_just_pressed("jump") and is_on_floor():
			velocity.y = VELOCIDAD_SALTO
	_modelo.rotation.y -= giro * VELOCIDAD_GIRO * delta
	var horizontal := Vector2(velocity.x, velocity.z)
	if absf(avance) > 0.01:
		var factor := 1.0 if avance > 0.0 else FACTOR_RETROCESO
		var meta := direccion_adelante(_modelo.rotation.y) * avance * VELOCIDAD * factor
		horizontal = horizontal.move_toward(meta, ACELERACION * delta)
	else:
		horizontal = horizontal.move_toward(Vector2.ZERO, FRICCION * delta)
	velocity.x = horizontal.x
	velocity.z = horizontal.y
	move_and_slide()
	_vigilar_caida(delta)


func _vigilar_caida(delta: float) -> void:
	_tiempo_punto_seguro += delta
	if is_on_floor() and _tiempo_punto_seguro >= INTERVALO_PUNTO_SEGURO:
		_tiempo_punto_seguro = 0.0
		ultimo_punto_seguro = global_position + Vector3(0, 1.0, 0)
	if global_position.y < GameConfig.ALTURA_CAIDA:
		teletransportar(ultimo_punto_seguro)
	var limite := GameConfig.LIMITE_MAPA + 4.0
	if absf(global_position.x) < 1000.0 and absf(global_position.z) < 1000.0:
		if absf(global_position.x) > limite or absf(global_position.z) > limite:
			teletransportar(ultimo_punto_seguro)


func teletransportar(destino: Vector3) -> void:
	global_position = destino
	velocity = Vector3.ZERO
	if camara != null:
		camara.saltar_a(destino)


func animar_golpe(hacia: Vector3) -> void:
	var plano := Vector3(hacia.x - global_position.x, 0, hacia.z - global_position.z)
	if plano.length() > 0.1:
		_modelo.rotation.y = atan2(-plano.x, -plano.z)
	if _tween_golpe != null and _tween_golpe.is_valid():
		_tween_golpe.kill()
	_pivote_martillo.rotation.x = POSE_PREPARADO
	_tween_golpe = create_tween()
	_tween_golpe.tween_property(_pivote_martillo, "rotation:x", POSE_GOLPE, 0.07).set_ease(Tween.EASE_IN)
	_tween_golpe.tween_property(_pivote_martillo, "rotation:x", POSE_DESCANSO, 0.2)


func esta_en_el_aire() -> bool:
	return not is_on_floor()


func tomar_dano(cantidad: float) -> void:
	if muerto:
		return
	salud = maxf(salud - cantidad, 0.0)
	recibio_dano.emit()
	salud_cambio.emit(salud, GameConfig.VIDA_JUGADOR)
	var parpadeo := create_tween()
	_material_cuerpo.albedo_color = GameColors.ROJO
	parpadeo.tween_property(_material_cuerpo, "albedo_color", GameColors.NARANJA, 0.35)
	if salud <= 0.0:
		muerto = true
		murio.emit()


func revivir(posicion: Vector3) -> void:
	muerto = false
	salud = GameConfig.VIDA_JUGADOR
	salud_cambio.emit(salud, GameConfig.VIDA_JUGADOR)
	teletransportar(posicion)
