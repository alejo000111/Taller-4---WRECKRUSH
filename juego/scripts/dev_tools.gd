class_name DevTools
extends Node

var main: Node


func _unhandled_input(evento: InputEvent) -> void:
	if not (evento is InputEventKey and evento.pressed and not evento.echo):
		return
	match evento.physical_keycode:
		KEY_F1:
			GameState.agregar_scrap(10000)
			GameState.toast.emit("DEV: +10K SCRAP", "good")
		KEY_F2:
			for id in GameConfig.ORDEN_MEJORAS:
				GameState.mejoras[id] = int(GameConfig.MEJORAS[id]["max"])
			GameState.mejora_comprada.emit("damage", GameState.mejoras["damage"])
		KEY_F3:
			for id in GameConfig.ORDEN_ZONAS:
				if not GameState.zona_abierta(id):
					GameState.zonas.append(id)
					GameState.zona_desbloqueada.emit(id)
		KEY_F4:
			for zona in GameConfig.ORDEN_ZONAS:
				GameState.rotos_por_zona[zona] = GameConfig.total_objetos(zona)
			GameState.objeto_roto.emit({}, "scrap_yard")
