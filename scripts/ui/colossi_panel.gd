class_name ColossiPanel
extends BasePanel

var _lista: VBoxContainer
var _scroll: ScrollContainer


func _init() -> void:
	super._init("COLOSSI", GameColors.NARANJA, 780.0, Iconos.JEFE)


func construir() -> void:
	contenido.add_child(UIKit.etiqueta("Check your progress, then challenge each colossus at its console.", 16))
	_scroll = ScrollContainer.new()
	_scroll.custom_minimum_size = Vector2(0, 430)
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_lista = VBoxContainer.new()
	_lista.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_lista.add_theme_constant_override("separation", 8)
	_scroll.add_child(_lista)
	contenido.add_child(_scroll)
	GameState.objeto_roto.connect(func(_d: Dictionary, _z: String) -> void: if abierto: refrescar())
	GameState.mejora_comprada.connect(func(_i: String, _n: int) -> void: if abierto: refrescar())
	GameState.zona_desbloqueada.connect(func(_i: String) -> void: if abierto: refrescar())
	GameState.coloso_vencido.connect(func(_r: Dictionary) -> void: if abierto: refrescar())
	GameState.maestria_terminada.connect(func(_r: Dictionary) -> void: if abierto: refrescar())


func refrescar() -> void:
	limpiar(_lista)
	for def in GameConfig.COLOSOS:
		_lista.add_child(_tarjeta(def))


func _input(evento: InputEvent) -> void:
	if abierto and (evento.is_action_pressed("ui_down") or evento.is_action_pressed("ui_up")):
		_scroll.scroll_vertical += 70 if evento.is_action_pressed("ui_down") else -70
		get_viewport().set_input_as_handled()


func _tarjeta(def: Dictionary) -> Control:
	var datos := GameState.resumen_coloso(int(def["numero"]))
	var tarjeta := UIKit.tarjeta()
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 5)
	tarjeta.add_child(col)
	col.add_child(UIKit.etiqueta("%d · %s" % [int(def["numero"]), def["nombre"]], 21, GameColors.AMARILLO))
	col.add_child(UIKit.etiqueta("%s · %s" % [GameConfig.ZONAS[def["zona"]]["nombre"], datos["estado"]], 15, GameColors.CIAN))
	col.add_child(UIKit.etiqueta("OBJECTS %d/%d · DAMAGE %s/%s" % [datos["rotos"], datos["meta_objetos"], GameConfig.texto_dano(datos["dano"]), GameConfig.texto_dano(datos["dano_requerido"])], 16))
	var barra := UIKit.barra(GameColors.NARANJA, Vector2(0, 8))
	barra.value = float(datos["rotos"]) / float(datos["meta_objetos"])
	col.add_child(barra)
	var mejor := Formulas.formato_tiempo(datos["mejor_tiempo"]) if float(datos["mejor_tiempo"]) > 0.0 else "--:--"
	col.add_child(UIKit.etiqueta("BEST TIME %s · MASTERY %d/2" % [mejor, datos["estrellas"]], 17, GameColors.AMARILLO))
	col.add_child(UIKit.etiqueta("[%s] UNDER %s · [%s] NO DAMAGE TAKEN" % ["OK" if datos["est_tiempo"] else "--", Formulas.formato_tiempo(def["maestria_segundos"]), "OK" if datos["est_sin_dano"] else "--"], 15))
	return tarjeta
