class_name InteractionController
extends Node

var jugador: Node3D
var objetivo: Interactable
var progreso: float = 0.0

var _texto_emitido: String = ""
var _progreso_emitido: float = -1.0


func _process(delta: float) -> void:
	if jugador == null:
		return
	var nuevo := _buscar()
	if nuevo != objetivo:
		objetivo = nuevo
		progreso = 0.0
	if objetivo == null or GameState.hay_panel_abierto():
		progreso = 0.0
		_emitir("", 0.0)
		return
	if objetivo.mantener <= 0.0:
		if Input.is_action_just_pressed("interact"):
			objetivo.activado.emit()
	else:
		if Input.is_action_pressed("interact"):
			progreso += delta / objetivo.mantener
			if progreso >= 1.0:
				progreso = 0.0
				objetivo.activado.emit()
		else:
			progreso = 0.0
	_emitir(objetivo.obtener_texto(), progreso)


func _buscar() -> Interactable:
	var mejor: Interactable = null
	var mejor_distancia := INF
	for nodo in get_tree().get_nodes_in_group("interactables"):
		var inter := nodo as Interactable
		if inter == null or not inter.habilitado or not inter.is_visible_in_tree():
			continue
		var distancia := inter.distancia_horizontal(jugador.global_position)
		if distancia <= inter.radio and distancia < mejor_distancia:
			mejor = inter
			mejor_distancia = distancia
	return mejor


func _emitir(texto: String, valor: float) -> void:
	if texto == _texto_emitido and is_equal_approx(valor, _progreso_emitido):
		return
	_texto_emitido = texto
	_progreso_emitido = valor
	GameState.prompt_cambio.emit(texto, valor)
