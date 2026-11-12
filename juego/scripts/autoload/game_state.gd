extends Node

signal scrap_cambio(valor: int)
signal mejora_comprada(id: String, nivel: int)
signal zona_desbloqueada(id: String)
signal objeto_roto(def: Dictionary, zona: String)
signal toast(texto: String, tipo: String)
signal ajustes_cambio()
signal prompt_cambio(texto: String, progreso: float)
signal boss_estado(datos: Dictionary)
signal tutorial_cambio(paso: int)
signal panel_cambio()
signal coloso_vencido(resultado: Dictionary)
signal maestria_terminada(resultado: Dictionary)
signal juego_completado(resultado: Dictionary)

const VERSION_GUARDADO := 2

var scrap: int = 0
var mejoras: Dictionary = {}
var zonas: Array = ["scrap_yard"]
var rotos_por_zona: Dictionary = {}
var colosos: Dictionary = {}
var objetos_rotos: int = 0
var golpes: int = 0
var dano_total: float = 0.0
var scrap_total: int = 0
var tiempo_juego: float = 0.0
var completado: bool = false
var tutorial_paso: int = 0
var tutorial_completo: bool = false
var ajustes: Dictionary = {"camera_shake": true, "damage_numbers": true, "sfx": true}

var paneles_abiertos: int = 0
var boton_wreck: bool = false
var ruta_guardado: String = "user://wreckrush_save.json"
var guardado_habilitado: bool = true
var _tiempo_autoguardado: float = 0.0
var _scrap_anterior: int = 0


func _ready() -> void:
	reiniciar()
	if guardado_habilitado:
		cargar()


func _process(delta: float) -> void:
	tiempo_juego += delta
	_tiempo_autoguardado += delta
	if _tiempo_autoguardado >= GameConfig.AUTOGUARDADO_SEGUNDOS:
		_tiempo_autoguardado = 0.0
		guardar()


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		guardar()


func reiniciar() -> void:
	scrap = 0
	mejoras = {}
	for id in GameConfig.ORDEN_MEJORAS:
		mejoras[id] = 0
	zonas = ["scrap_yard"]
	rotos_por_zona = {}
	for zona in GameConfig.ORDEN_ZONAS:
		rotos_por_zona[zona] = 0
	colosos = {}
	for c in GameConfig.COLOSOS:
		colosos[int(c["numero"])] = {"vencido": false, "est_tiempo": false, "est_sin_dano": false, "mejor_tiempo": 0.0}
	objetos_rotos = 0
	golpes = 0
	dano_total = 0.0
	scrap_total = 0
	tiempo_juego = 0.0
	completado = false
	tutorial_paso = 0
	tutorial_completo = false
	paneles_abiertos = 0
	boton_wreck = false
	_scrap_anterior = 0


func nivel_mejora(id: String) -> int:
	return int(mejoras.get(id, 0))


func dano_base_golpe() -> float:
	return Formulas.dano_golpe(float(GameConfig.MARTILLO["dano"]), nivel_mejora("damage"))


func cooldown_ataque() -> float:
	return Formulas.cooldown_ataque(float(GameConfig.MARTILLO["cooldown"]), nivel_mejora("attack_speed"))


func alcance_ataque() -> float:
	return float(GameConfig.MARTILLO["alcance"])


func puede_retar_coloso() -> bool:
	return dano_base_golpe() >= GameConfig.DANO_REQUERIDO_COLOSO


func agregar_scrap(cantidad: int) -> void:
	if cantidad <= 0:
		return
	scrap += cantidad
	scrap_total += cantidad
	scrap_cambio.emit(scrap)
	_revisar_hitos()


func gastar_scrap(cantidad: int) -> bool:
	if cantidad < 0 or scrap < cantidad:
		return false
	scrap -= cantidad
	_scrap_anterior = scrap
	scrap_cambio.emit(scrap)
	return true


func registrar_golpe(dano: float) -> void:
	golpes += 1
	dano_total += dano


func registrar_objeto_roto(def: Dictionary, zona: String) -> int:
	var pago := int(def["scrap"])
	agregar_scrap(pago)
	objetos_rotos += 1
	rotos_por_zona[zona] = int(rotos_por_zona.get(zona, 0)) + 1
	objeto_roto.emit(def, zona)
	return pago


func precio_mejora(id: String) -> int:
	var def: Dictionary = GameConfig.MEJORAS[id]
	return Formulas.precio_mejora(float(def["base"]), nivel_mejora(id) + 1, int(def["desfase"]))


func estado_mejora(id: String) -> Dictionary:
	var def: Dictionary = GameConfig.MEJORAS[id]
	if nivel_mejora(id) >= int(def["max"]):
		return {"ok": false, "razon": "MAXED"}
	var precio := precio_mejora(id)
	if scrap < precio:
		return {"ok": false, "razon": "NOT ENOUGH SCRAP", "precio": precio}
	return {"ok": true, "razon": "", "precio": precio}


func comprar_mejora(id: String) -> Dictionary:
	var estado := estado_mejora(id)
	if not estado["ok"]:
		toast.emit(String(estado["razon"]), "bad")
		return estado
	gastar_scrap(int(estado["precio"]))
	mejoras[id] = nivel_mejora(id) + 1
	mejora_comprada.emit(id, mejoras[id])
	return estado


func hay_mejora_asequible() -> bool:
	for id in GameConfig.ORDEN_MEJORAS:
		if estado_mejora(id)["ok"]:
			return true
	return false


func zona_abierta(id: String) -> bool:
	return zonas.has(id)


func desbloquear_zona(id: String) -> bool:
	if zona_abierta(id):
		return true
	if not gastar_scrap(int(GameConfig.ZONAS[id]["costo"])):
		toast.emit("NOT ENOUGH SCRAP", "bad")
		return false
	zonas.append(id)
	zona_desbloqueada.emit(id)
	toast.emit("ISLAND %d · %s UNLOCKED!" % [int(GameConfig.ZONAS[id]["isla"]), GameConfig.ZONAS[id]["nombre"]], "good")
	return true


func rotos_en(zona: String) -> int:
	return int(rotos_por_zona.get(zona, 0))


func coloso_vencido_p(numero: int) -> bool:
	return bool(colosos[numero]["vencido"])


func todos_vencidos() -> bool:
	for numero in colosos:
		if not colosos[numero]["vencido"]:
			return false
	return true


func estrellas(numero: int) -> int:
	return int(bool(colosos[numero]["est_tiempo"])) + int(bool(colosos[numero]["est_sin_dano"]))


func registrar_victoria_coloso(numero: int, tiempo: float, sin_dano: bool, maestria: bool) -> Dictionary:
	var datos: Dictionary = GameConfig.COLOSOS[numero - 1]
	var entrada: Dictionary = colosos[numero]
	var resultado := {"numero": numero, "nombre": datos["nombre"], "tiempo": tiempo, "sin_dano": sin_dano, "maestria": maestria, "scrap": 0, "estrellas_nuevas": 0, "estrellas": estrellas(numero)}
	if maestria:
		var antes := estrellas(numero)
		if tiempo < float(datos["maestria_segundos"]):
			entrada["est_tiempo"] = true
		if sin_dano:
			entrada["est_sin_dano"] = true
		resultado["estrellas"] = estrellas(numero)
		resultado["estrellas_nuevas"] = estrellas(numero) - antes
		maestria_terminada.emit(resultado)
		guardar()
		return resultado
	entrada["vencido"] = true
	if float(entrada["mejor_tiempo"]) <= 0.0 or tiempo < float(entrada["mejor_tiempo"]):
		entrada["mejor_tiempo"] = tiempo
	var premio := int(datos["recompensa"])
	if premio > 0:
		agregar_scrap(premio)
	resultado["scrap"] = premio
	coloso_vencido.emit(resultado)
	if todos_vencidos() and not completado:
		completado = true
		juego_completado.emit({"tiempo_total": tiempo_juego, "objetos_rotos": objetos_rotos, "golpes": golpes})
	guardar()
	return resultado


func plan_de_metas() -> Array:
	var plan: Array = []
	for n in range(1, 9):
		plan.append(["damage", n])
	plan.append(["zona", "downtown"])
	plan.append(["damage", 9])
	plan.append(["attack_speed", 1])
	plan.append(["damage", 10])
	plan.append(["attack_speed", 2])
	plan.append(["attack_speed", 3])
	plan.append(["zona", "industrial"])
	plan.append(["damage", 11])
	plan.append(["damage", 12])
	plan.append(["coloso", 1])
	plan.append(["coloso", 2])
	plan.append(["attack_speed", 4])
	plan.append(["attack_speed", 5])
	plan.append(["coloso", 3])
	return plan


func _meta_cumplida(meta: Array) -> bool:
	match meta[0]:
		"damage", "attack_speed":
			return nivel_mejora(meta[0]) >= int(meta[1])
		"zona":
			return zona_abierta(meta[1])
		"coloso":
			return coloso_vencido_p(int(meta[1]))
	return true


func siguiente_meta() -> Dictionary:
	for meta in plan_de_metas():
		if _meta_cumplida(meta):
			continue
		match meta[0]:
			"damage", "attack_speed":
				var def: Dictionary = GameConfig.MEJORAS[meta[0]]
				var precio := Formulas.precio_mejora(float(def["base"]), int(meta[1]), int(def["desfase"]))
				return {"texto": "%s %d" % [def["nombre"], int(meta[1])], "actual": scrap, "meta": precio, "listo": false}
			"zona":
				return {"texto": "ISLAND %d" % int(GameConfig.ZONAS[meta[1]]["isla"]), "actual": scrap, "meta": int(GameConfig.ZONAS[meta[1]]["costo"]), "listo": false}
			"coloso":
				var datos: Dictionary = GameConfig.COLOSOS[int(meta[1]) - 1]
				var rotos := rotos_en(datos["zona"])
				var umbral: int = datos["giro_cabeza"]
				if not zona_abierta(datos["zona"]):
					return {"texto": "ISLAND %d" % int(GameConfig.ZONAS[datos["zona"]]["isla"]), "actual": scrap, "meta": int(GameConfig.ZONAS[datos["zona"]]["costo"]), "listo": false}
				if rotos < umbral:
					return {"texto": "WAKE COLOSSUS %d" % int(meta[1]), "actual": rotos, "meta": umbral, "listo": false}
				if not puede_retar_coloso():
					return {"texto": "DAMAGE 40", "actual": int(dano_base_golpe()), "meta": 40, "listo": false}
				return {"texto": "COLOSSUS %d" % int(meta[1]), "actual": 1, "meta": 1, "listo": true}
	return {"texto": "MASTERY STARS", "actual": 1, "meta": 1, "listo": true}


func _revisar_hitos() -> void:
	var antes := _scrap_anterior
	_scrap_anterior = scrap
	var meta := siguiente_meta()
	if meta["listo"] or int(meta["meta"]) <= 0:
		return
	var precio: int = meta["meta"]
	var texto: String = meta["texto"]
	var cortes: Array = [0.5]
	if texto == "ISLAND 3":
		cortes.append(0.75)
	for corte in cortes:
		var limite := int(precio * float(corte))
		if antes < limite and scrap >= limite:
			toast.emit("NEXT %s: %s / %s" % [texto, Formulas.abreviar(scrap), Formulas.abreviar(precio)], "good")


func avanzar_tutorial() -> void:
	if tutorial_completo:
		return
	tutorial_paso += 1
	if tutorial_paso >= GameConfig.TUTORIAL.size():
		tutorial_completo = true
	tutorial_cambio.emit(tutorial_paso)


func saltar_tutorial() -> void:
	tutorial_completo = true
	tutorial_paso = GameConfig.TUTORIAL.size()
	tutorial_cambio.emit(tutorial_paso)


func abrir_panel() -> void:
	paneles_abiertos += 1
	panel_cambio.emit()


func cerrar_panel() -> void:
	paneles_abiertos = maxi(paneles_abiertos - 1, 0)
	panel_cambio.emit()


func hay_panel_abierto() -> bool:
	return paneles_abiertos > 0


func cambiar_ajuste(clave: String, valor: bool) -> void:
	ajustes[clave] = valor
	ajustes_cambio.emit()


func a_diccionario() -> Dictionary:
	var datos_colosos := {}
	for numero in colosos:
		datos_colosos[str(numero)] = colosos[numero]
	return {
		"version": VERSION_GUARDADO,
		"scrap": scrap,
		"mejoras": mejoras,
		"zonas": zonas,
		"rotos_por_zona": rotos_por_zona,
		"colosos": datos_colosos,
		"objetos_rotos": objetos_rotos,
		"golpes": golpes,
		"dano_total": dano_total,
		"scrap_total": scrap_total,
		"tiempo_juego": tiempo_juego,
		"completado": completado,
		"tutorial_paso": tutorial_paso,
		"tutorial_completo": tutorial_completo,
		"ajustes": ajustes,
	}


func desde_diccionario(datos: Dictionary) -> void:
	reiniciar()
	scrap = maxi(int(datos.get("scrap", 0)), 0)
	var guardadas: Dictionary = datos.get("mejoras", {})
	for id in GameConfig.ORDEN_MEJORAS:
		mejoras[id] = clampi(int(guardadas.get(id, 0)), 0, int(GameConfig.MEJORAS[id]["max"]))
	zonas = []
	for id in datos.get("zonas", ["scrap_yard"]):
		if GameConfig.ZONAS.has(id) and id != "plaza":
			zonas.append(String(id))
	if not zonas.has("scrap_yard"):
		zonas.append("scrap_yard")
	var rotos: Dictionary = datos.get("rotos_por_zona", {})
	for zona in GameConfig.ORDEN_ZONAS:
		rotos_por_zona[zona] = maxi(int(rotos.get(zona, 0)), 0)
	var guardados: Dictionary = datos.get("colosos", {})
	for numero in colosos:
		var e: Dictionary = guardados.get(str(numero), {})
		colosos[numero]["vencido"] = bool(e.get("vencido", false))
		colosos[numero]["est_tiempo"] = bool(e.get("est_tiempo", false))
		colosos[numero]["est_sin_dano"] = bool(e.get("est_sin_dano", false))
		colosos[numero]["mejor_tiempo"] = float(e.get("mejor_tiempo", 0.0))
	objetos_rotos = int(datos.get("objetos_rotos", 0))
	golpes = int(datos.get("golpes", 0))
	dano_total = float(datos.get("dano_total", 0.0))
	scrap_total = int(datos.get("scrap_total", 0))
	tiempo_juego = float(datos.get("tiempo_juego", 0.0))
	completado = todos_vencidos()
	tutorial_paso = int(datos.get("tutorial_paso", 0))
	tutorial_completo = bool(datos.get("tutorial_completo", false))
	var ajustes_guardados: Dictionary = datos.get("ajustes", {})
	for clave in ajustes.keys():
		ajustes[clave] = bool(ajustes_guardados.get(clave, ajustes[clave]))
	_scrap_anterior = scrap


func guardar() -> bool:
	if not guardado_habilitado:
		return false
	var archivo := FileAccess.open(ruta_guardado, FileAccess.WRITE)
	if archivo == null:
		push_warning("No se pudo guardar: %s" % error_string(FileAccess.get_open_error()))
		return false
	archivo.store_string(JSON.stringify(a_diccionario()))
	return true


func cargar() -> bool:
	if not FileAccess.file_exists(ruta_guardado):
		return false
	var archivo := FileAccess.open(ruta_guardado, FileAccess.READ)
	if archivo == null:
		return false
	var datos: Variant = JSON.parse_string(archivo.get_as_text())
	if typeof(datos) != TYPE_DICTIONARY:
		push_warning("Guardado corrupto, se ignora")
		return false
	desde_diccionario(datos)
	return true


func borrar_guardado() -> void:
	if FileAccess.file_exists(ruta_guardado):
		DirAccess.remove_absolute(ruta_guardado)
