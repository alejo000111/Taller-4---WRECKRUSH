class_name HammerController
extends Node

var jugador: Player

var _cooldown: float = 0.0
var _sostenido: bool = false


static func seleccionar(candidatos: Array, maximo: int = 1) -> Array:
	var ordenados := candidatos.duplicate()
	ordenados.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a["distancia"] < b["distancia"])
	return ordenados.slice(0, maximo)


func _unhandled_input(evento: InputEvent) -> void:
	if evento.is_action("attack"):
		_sostenido = evento.is_pressed()
	if evento.is_action_pressed("tool_1") and GameState.tutorial_paso == 0 and not GameState.tutorial_completo:
		GameState.avanzar_tutorial()


func _process(delta: float) -> void:
	_cooldown = maxf(_cooldown - delta, 0.0)
	if _sostenido and not Input.is_action_pressed("attack"):
		_sostenido = false
	if jugador == null or jugador.muerto or GameState.hay_panel_abierto():
		return
	if (_sostenido or GameState.boton_wreck) and _cooldown <= 0.0:
		_golpear()


func _candidatos() -> Array:
	var alcance := GameState.alcance_ataque()
	var lista: Array = []
	for nodo in get_tree().get_nodes_in_group("golpeables"):
		if not nodo.has_method("puede_ser_golpeado") or not nodo.puede_ser_golpeado():
			continue
		var distancia: float = nodo.distancia_a(jugador.global_position)
		if distancia <= alcance:
			lista.append({"nodo": nodo, "distancia": distancia})
	return lista


func _golpear() -> void:
	var objetivos := seleccionar(_candidatos(), 1)
	if objetivos.is_empty():
		return
	_cooldown = GameState.cooldown_ataque()
	jugador.animar_golpe(objetivos[0]["nodo"].global_position)
	for entrada in objetivos:
		var dano := GameState.dano_base_golpe()
		GameState.registrar_golpe(dano)
		entrada["nodo"].recibir_golpe(dano, false)
