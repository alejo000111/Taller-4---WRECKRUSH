class_name SettingsPanel
extends BasePanel

var _confirmar_reinicio: bool = false
var _boton_reinicio: Button


func _init() -> void:
	super._init("SETTINGS", GameColors.CIAN, 560.0, Iconos.AJUSTES)


func construir() -> void:
	var opciones := [["camera_shake", "CAMERA SHAKE"], ["damage_numbers", "DAMAGE NUMBERS"], ["sfx", "SOUND EFFECTS"]]
	for o in opciones:
		var fila := HBoxContainer.new()
		var nombre := UIKit.etiqueta(o[1], 20)
		nombre.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		fila.add_child(nombre)
		var boton := UIKit.boton("", GameColors.CIAN.darkened(0.3), Vector2(110, 40), 18)
		boton.set_meta("clave", o[0])
		boton.pressed.connect(func() -> void:
			GameState.cambiar_ajuste(o[0], not GameState.ajustes[o[0]])
			refrescar())
		fila.add_child(boton)
		contenido.add_child(fila)
	contenido.add_child(UIKit.separador(10))
	contenido.add_child(UIKit.etiqueta("MOVE W/S · TURN A/D · JUMP SPACE · WRECK F · INTERACT E · MENUS ARROWS + ENTER", 14, Color("#8A909C")))
	_boton_reinicio = UIKit.boton("RESET PROGRESS", GameColors.ROJO, Vector2(260, 44), 18)
	_boton_reinicio.pressed.connect(_reiniciar)
	contenido.add_child(_boton_reinicio)
	var logo := UIKit.icono(Iconos.LOGO_JUEGO, 120)
	logo.custom_minimum_size = Vector2(240, 120)
	logo.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	contenido.add_child(logo)
	contenido.add_child(UIKit.etiqueta("WRECKRUSH v%s  %s  (Godot port)" % [GameConfig.VERSION, GameConfig.NOMBRE_VERSION], 15, Color("#8A909C"), HORIZONTAL_ALIGNMENT_CENTER))


func refrescar() -> void:
	_confirmar_reinicio = false
	_boton_reinicio.text = "RESET PROGRESS"
	for fila in contenido.get_children():
		for hijo in fila.get_children():
			if hijo is Button and hijo.has_meta("clave"):
				hijo.text = "ON" if GameState.ajustes[hijo.get_meta("clave")] else "OFF"


func _reiniciar() -> void:
	if not _confirmar_reinicio:
		_confirmar_reinicio = true
		_boton_reinicio.text = "SURE? PRESS AGAIN"
		return
	GameState.borrar_guardado()
	GameState.reiniciar()
	get_tree().reload_current_scene()
