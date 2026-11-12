class_name Onboarding
extends Node

const DISTANCIA_FLECHA := 7.0
const DURACION_ULTIMO_PASO := 14.0
const OBJETOS_PASO_FINAL := 10

var jugador: Player

var _flecha: Node3D
var _paso_visto: int = -1
var _tiempo_paso: float = 0.0
var _base_rotos: int = 0


func _ready() -> void:
	_flecha = Node3D.new()
	var prisma := Formas.malla(_flecha, "prism", Vector3(5.0, 4.5, 0.2), Vector3.ZERO, Formas.material(GameColors.AMARILLO, 0.4, 0.0, 2.4), false)
	prisma.rotation.x = -PI * 0.5
	_flecha.visible = false
	add_child(_flecha)


func _process(delta: float) -> void:
	if GameState.tutorial_completo or jugador == null:
		_flecha.visible = false
		return
	var paso := GameState.tutorial_paso
	if paso != _paso_visto:
		_paso_visto = paso
		_tiempo_paso = 0.0
		_base_rotos = GameState.objetos_rotos
	_tiempo_paso += delta
	if _paso_cumplido(paso):
		GameState.avanzar_tutorial()
	_actualizar_flecha(paso)


func _paso_cumplido(paso: int) -> bool:
	match paso:
		0:
			return GameState.golpes > 0
		1:
			return GameState.objetos_rotos >= 1
		2:
			return GameState.scrap >= GameState.precio_mejora("damage") or GameState.nivel_mejora("damage") >= 1
		3:
			return GameState.nivel_mejora("damage") >= 1
		4:
			return GameState.objetos_rotos - _base_rotos >= OBJETOS_PASO_FINAL
		5:
			return _tiempo_paso >= DURACION_ULTIMO_PASO
	return false


func objetivo_para(paso: int) -> Variant:
	match paso:
		1, 2, 4:
			var distrito := AmbienceController.distrito_en(jugador.global_position)
			if distrito != "scrap_yard":
				return CityWorld.PUNTOS_ENTRADA["scrap_yard"]
			return _destructible_cercano()
		3:
			return Vector3(74, 0, -20)
	return null


func _destructible_cercano() -> Variant:
	var mejor: Node3D = null
	var mejor_d := INF
	for nodo in get_tree().get_nodes_in_group("destructibles"):
		var d := nodo as Destructible
		if d == null or not d.activo or d.zona != "scrap_yard":
			continue
		var dist := d.global_position.distance_to(jugador.global_position)
		if dist < mejor_d:
			mejor_d = dist
			mejor = d
	return mejor.global_position if mejor != null else null


func _actualizar_flecha(paso: int) -> void:
	var destino: Variant = objetivo_para(paso)
	if destino == null:
		_flecha.visible = false
		return
	var hacia: Vector3 = destino - jugador.global_position
	hacia.y = 0.0
	if hacia.length() < 12.0:
		_flecha.visible = false
		return
	var dir := hacia.normalized()
	_flecha.visible = true
	_flecha.global_position = jugador.global_position + dir * DISTANCIA_FLECHA + Vector3(0, 0.35, 0)
	_flecha.rotation.y = atan2(-dir.x, -dir.z)
	_flecha.scale = Vector3.ONE * (0.9 + 0.2 * Curvas.pulso(Time.get_ticks_msec() / 1000.0, 1.5))
