class_name InputSetup
extends RefCounted


static func registrar() -> void:
	_teclas("move_forward", [KEY_W, KEY_UP])
	_teclas("move_back", [KEY_S, KEY_DOWN])
	_teclas("move_left", [KEY_A, KEY_LEFT])
	_teclas("move_right", [KEY_D, KEY_RIGHT])
	_teclas("jump", [KEY_SPACE])
	_teclas("attack", [KEY_F])
	_mouse("attack", MOUSE_BUTTON_LEFT)
	_teclas("interact", [KEY_E])
	_teclas("tool_1", [KEY_1])
	_teclas("close_panel", [KEY_BACKSPACE, KEY_ESCAPE])
	_teclas("open_upgrades", [KEY_U])
	_teclas("open_settings", [KEY_TAB])
	_mouse("camera_orbit", MOUSE_BUTTON_RIGHT)


static func _asegurar(accion: String) -> void:
	if not InputMap.has_action(accion):
		InputMap.add_action(accion, 0.5)


static func _teclas(accion: String, teclas: Array) -> void:
	_asegurar(accion)
	for tecla in teclas:
		var evento := InputEventKey.new()
		evento.physical_keycode = tecla
		InputMap.action_add_event(accion, evento)


static func _mouse(accion: String, boton: MouseButton) -> void:
	_asegurar(accion)
	var evento := InputEventMouseButton.new()
	evento.button_index = boton
	InputMap.action_add_event(accion, evento)
