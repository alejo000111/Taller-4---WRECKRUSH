extends Node

var _fallos: int = 0
var _total: int = 0


func _verificar(condicion: bool, nombre: String) -> void:
	_total += 1
	if condicion:
		print("  ok   ", nombre)
	else:
		_fallos += 1
		print("  FAIL ", nombre)


func _cerca(a: float, b: float, tol: float = 0.001) -> bool:
	return absf(a - b) <= tol


func _nuevo_estado() -> Node:
	var gs: Node = load("res://scripts/autoload/game_state.gd").new()
	gs.guardado_habilitado = false
	gs.reiniciar()
	return gs


func _ready() -> void:
	_test_formulas()
	_test_tablas_taller()
	_test_economia()
	_test_progreso()
	_test_guardado()
	_test_seleccion()
	_test_ritmo()
	_test_camara()
	_test_ambiente()
	_test_assets()
	await _test_coloso()
	print("\n%d pruebas, %d fallos" % [_total, _fallos])
	get_tree().quit(1 if _fallos > 0 else 0)


func _test_formulas() -> void:
	print("Formulas")
	var esperados := [38, 56, 84, 127, 190, 285, 427, 641, 961, 1442, 2162, 3244]
	var ok := true
	var suma := 0
	for n in range(1, 13):
		var precio := Formulas.precio_mejora(25.0, n)
		suma += precio
		ok = ok and precio == esperados[n - 1]
	_verificar(ok, "precios de DAMAGE niveles 1 a 12 (38 ... 3,244)")
	_verificar(suma == 9657, "los 12 niveles de daño suman 9,657 Scrap")
	var velocidades := [600, 900, 1350, 2025, 3038]
	ok = true
	for m in range(1, 6):
		ok = ok and Formulas.precio_mejora(600.0, m, -1) == velocidades[m - 1]
	_verificar(ok, "precios de ATTACK SPEED 600, 900, 1350, 2025, 3038")
	_verificar(Formulas.dano_golpe(10.0, 1) == 12.5, "DAMAGE 1 = 12.5")
	_verificar(Formulas.dano_golpe(10.0, 8) == 30.0, "DAMAGE 8 = 30")
	_verificar(Formulas.dano_golpe(10.0, 10) == 35.0, "DAMAGE 10 = 35")
	_verificar(Formulas.dano_golpe(10.0, 12) == 40.0, "DAMAGE 12 = 40")
	_verificar(_cerca(Formulas.cooldown_ataque(0.45, 3), 0.381, 0.001), "velocidad 3 = golpe cada 0.381 s")
	_verificar(_cerca(Formulas.cooldown_ataque(0.45, 5), 0.346, 0.001), "velocidad 5 = golpe cada 0.346 s")
	_verificar(Formulas.golpes_para_romper(30.0, 10.0) == 3 and _cerca(Formulas.segundos_para_romper(3, 0.45), 0.9), "barril: 3 golpes, 0.9 s")
	_verificar(Formulas.golpes_para_romper(300.0, 10.0) == 30 and _cerca(Formulas.segundos_para_romper(30, 0.45), 13.05), "coche: 30 golpes, 13.05 s")
	_verificar(Formulas.golpes_para_romper(1200.0, 10.0) == 120 and _cerca(Formulas.segundos_para_romper(120, 0.45), 53.55), "contenedor: 120 golpes, 53.55 s")
	_verificar(Formulas.golpes_para_romper(4800.0, 30.0) == 160 and _cerca(Formulas.segundos_para_romper(160, 0.45), 71.55), "kiosco con daño 30: 160 golpes, 71.55 s")
	_verificar(Formulas.vida_placa(1) == 800.0 and Formulas.vida_placa(2) == 1000.0 and Formulas.vida_placa(3) == 1200.0, "placas 800 / 1,000 / 1,200")
	_verificar(Formulas.vida_nucleo(1) == 700.0 and Formulas.vida_nucleo(3) == 900.0, "nucleos 700 / 800 / 900")
	_verificar(Formulas.intervalo_golpe_suelo(1) == 6.0 and Formulas.intervalo_golpe_suelo(3) == 4.0, "golpe al suelo cada 6 / 5 / 4 s")
	var altura := 1.0 / GameConfig.METROS_POR_STUD
	var v := Formulas.velocidad_salto(altura, 0.9)
	var g := Formulas.gravedad_salto(altura, 0.9)
	_verificar(_cerca(2.0 * v / g, 0.9) and _cerca(v * v / (2.0 * g), altura), "salto: 1 m de alto y 0.9 s en el aire")
	_verificar(_cerca(Player.VELOCIDAD_SALTO, v, 0.05) and _cerca(Player.GRAVEDAD, g, 0.05), "el jugador usa esos valores de salto")
	_verificar(_cerca(Formulas.studs_a_metros(Player.VELOCIDAD), 4.5, 0.05), "caminar = 4.5 m/s")
	_verificar(_cerca(Formulas.studs_a_metros(GameState_alcance()), 3.0, 0.1), "alcance del golpe = 3 m")
	_verificar(_cerca(Formulas.studs_a_metros(195.0), 55.0, 0.5), "spawn a Scrap Yard = 55 m")
	_verificar(Formulas.abreviar(1500) == "1.5K" and Formulas.abreviar(6000) == "6K" and Formulas.abreviar(999) == "999", "abreviar")
	_verificar(Formulas.formato_tiempo(125.0) == "2:05", "formato_tiempo")
	_verificar(_cerca(Curvas.suavizado(5.0, 0.5), 0.918, 0.001), "suavizado(5, 0.5) = 0.918")


func GameState_alcance() -> float:
	return float(GameConfig.MARTILLO["alcance"])


func _test_tablas_taller() -> void:
	print("Tablas de los talleres")
	_verificar(GameConfig.total_objetos("scrap_yard") == 29, "Isla 1: 29 objetos")
	_verificar(GameConfig.total_objetos("downtown") == 24, "Isla 2: 24 objetos")
	_verificar(GameConfig.total_objetos("industrial") == 24, "Isla 3: 24 objetos")
	_verificar(GameConfig.scrap_por_vuelta("scrap_yard") == 1631, "Isla 1: una vuelta paga 1,631 Scrap")
	_verificar(GameConfig.scrap_por_vuelta("downtown") == 6396, "Isla 2: una vuelta paga 6,396 Scrap")
	_verificar(GameConfig.scrap_por_vuelta("industrial") == 11664, "Isla 3: una vuelta paga 11,664 Scrap")
	var barril := GameConfig.objeto_por_id("scrap_yard", "scrap_barrel")
	_verificar(barril["scrap"] == 12 and barril["cantidad"] == 8 and barril["respawn"] == 5, "barril: 12 Scrap, 8 en el mapa, vuelve en 5 s")
	var contenedor := GameConfig.objeto_por_id("scrap_yard", "rusty_container")
	_verificar(contenedor["vida"] == 1200 and contenedor["scrap"] == 360 and contenedor["cantidad"] == 1, "contenedor: 1,200 vida, 360 Scrap, 1 en el mapa")
	var ok := true
	for zona in GameConfig.ORDEN_ZONAS:
		for def in GameConfig.OBJETOS[zona]:
			ok = ok and def["respawn"] >= 5 and def["respawn"] <= 35
	_verificar(ok, "reaparicion entre 5 y 35 s")
	_verificar(GameConfig.ZONAS["downtown"]["costo"] == 1500 and GameConfig.ZONAS["industrial"]["costo"] == 6000, "puertas: 1,500 y 6,000 Scrap")
	_verificar(GameConfig.COLOSO["aviso"] >= 1.0 and GameConfig.COLOSO["dano"] == 25.0 and GameConfig.VIDA_JUGADOR == 100.0, "aviso 1.5 s, daño 25, vida 100")
	_verificar(GameConfig.COLOSO["ventana_expuesta"] == 16.0, "nucleo expuesto 16 s")
	_verificar(GameConfig.COLOSOS[0]["recompensa"] == 1500 and GameConfig.COLOSOS[1]["recompensa"] == 3600 and GameConfig.COLOSOS[2]["recompensa"] == 0, "premios de colosos 1,500 / 3,600 / 0")
	_verificar(GameConfig.COLOSOS[0]["maestria_segundos"] == 50.0 and GameConfig.COLOSOS[2]["maestria_segundos"] == 70.0, "maestria 50 / 60 / 70 s")


func _test_economia() -> void:
	print("Economia")
	var gs := _nuevo_estado()
	gs.registrar_objeto_roto(GameConfig.objeto_por_id("scrap_yard", "scrap_barrel"), "scrap_yard")
	gs.registrar_objeto_roto(GameConfig.objeto_por_id("scrap_yard", "wooden_crate"), "scrap_yard")
	_verificar(gs.scrap == 30, "barril + caja = 30 Scrap")
	_verificar(not gs.estado_mejora("damage")["ok"] and gs.precio_mejora("damage") == 38, "DAMAGE 1 cuesta 38 y aun no alcanza")
	gs.agregar_scrap(8)
	gs.comprar_mejora("damage")
	_verificar(gs.scrap == 0 and gs.dano_base_golpe() == 12.5, "comprar DAMAGE 1 cobra 38 y sube a 12.5")
	_verificar(gs.precio_mejora("damage") == 56, "DAMAGE 2 cuesta 56")
	_verificar(gs.precio_mejora("attack_speed") == 600, "ATTACK SPEED 1 cuesta 600")
	_verificar(not gs.desbloquear_zona("downtown"), "Downtown bloqueada sin Scrap")
	gs.agregar_scrap(1500)
	_verificar(gs.desbloquear_zona("downtown") and gs.zona_abierta("downtown") and gs.scrap == 0, "Downtown se paga con 1,500 y queda abierta")
	_verificar(gs.rotos_en("scrap_yard") == 2, "se cuentan los objetos rotos por isla")
	gs.mejoras["damage"] = 12
	_verificar(gs.estado_mejora("damage")["razon"] == "MAXED" and gs.puede_retar_coloso(3), "DAMAGE 12 = 40: tope y permite retar al coloso 3")
	gs.free()


func _test_progreso() -> void:
	print("Progreso y metas")
	var gs := _nuevo_estado()
	_verificar(gs.siguiente_meta()["texto"] == "DAMAGE 1" and gs.siguiente_meta()["meta"] == 38, "primera meta: DAMAGE 1 = 38")
	for n in 6:
		gs.mejoras["damage"] = n + 1
	_verificar(gs.siguiente_meta()["texto"] == "WAKE COLOSSUS 1", "con daño 25 (nivel 6) toca despertar al coloso 1")
	gs.rotos_por_zona["scrap_yard"] = 29
	_verificar(gs.siguiente_meta()["texto"] == "COLOSSUS 1" and gs.siguiente_meta()["listo"], "con 29 objetos rotos el coloso 1 esta listo")
	var r1: Dictionary = gs.registrar_victoria_coloso(1, 62.0, false, false)
	_verificar(r1["scrap"] == 1500 and gs.scrap == 1500 and gs.coloso_vencido_p(1), "coloso 1: premio 1,500 Scrap")
	var r1b: Dictionary = gs.registrar_victoria_coloso(1, 45.0, true, true)
	_verificar(r1b["estrellas"] == 2 and gs.scrap == 1500 and r1b["scrap"] == 0, "maestria: 2 estrellas, sin Scrap")
	_verificar(gs.siguiente_meta()["texto"] == "ISLAND 2" and gs.siguiente_meta()["meta"] == 1500, "tras el coloso 1 la meta es la puerta de 1,500 y su premio la paga")
	gs.zonas.append("downtown")
	gs.mejoras["damage"] = 10
	gs.rotos_por_zona["downtown"] = 24
	_verificar(gs.siguiente_meta()["texto"] == "COLOSSUS 2" and gs.siguiente_meta()["listo"], "con daño 35 y 24 objetos el coloso 2 esta listo")
	_verificar(not gs.completado, "no hay final hasta vencer a los 3")
	var r2: Dictionary = gs.registrar_victoria_coloso(2, 76.0, false, false)
	_verificar(r2["scrap"] == 3600, "coloso 2: premio 3,600 Scrap")
	var final: Array = []
	gs.juego_completado.connect(func(r: Dictionary) -> void: final.append(r))
	gs.registrar_victoria_coloso(3, 82.0, false, false)
	_verificar(gs.completado and final.size() == 1 and gs.scrap == 5100, "coloso 3 completa el juego (1,500 + 3,600 = 5,100)")
	var lento: Dictionary = gs.registrar_victoria_coloso(2, 61.0, false, true)
	_verificar(lento["estrellas"] == 0, "maestria sin cumplir condiciones: 0 estrellas")
	var rapido: Dictionary = gs.registrar_victoria_coloso(2, 59.0, false, true)
	_verificar(rapido["estrellas"] == 1 and rapido["estrellas_nuevas"] == 1, "coloso 2 en menos de 60 s: 1 estrella")
	var sin_dano: Dictionary = gs.registrar_victoria_coloso(2, 90.0, true, true)
	_verificar(sin_dano["estrellas"] == 2, "las estrellas se acumulan (tiempo + sin daño)")
	gs.free()
	var m := _nuevo_estado()
	var avisos: Array = []
	m.toast.connect(func(t: String, _tipo: String) -> void: avisos.append(t))
	m.agregar_scrap(19)
	m.agregar_scrap(20)
	_verificar(avisos.size() == 1, "aviso al llegar a la mitad de la meta (19 de 38)")
	m.free()


func _test_guardado() -> void:
	print("Guardado")
	var gs := _nuevo_estado()
	gs.agregar_scrap(777)
	gs.mejoras["damage"] = 3
	gs.zonas.append("downtown")
	gs.rotos_por_zona["downtown"] = 12
	gs.colosos[1]["vencido"] = true
	gs.colosos[1]["est_tiempo"] = true
	gs.ajustes["sfx"] = false
	var datos: Dictionary = JSON.parse_string(JSON.stringify(gs.a_diccionario()))
	var otro := _nuevo_estado()
	otro.desde_diccionario(datos)
	_verificar(otro.scrap == 777 and otro.nivel_mejora("damage") == 3, "ida y vuelta por JSON")
	_verificar(otro.zona_abierta("downtown") and otro.rotos_en("downtown") == 12, "zonas y objetos rotos persisten")
	_verificar(otro.coloso_vencido_p(1) and otro.estrellas(1) == 1 and not otro.coloso_vencido_p(2), "colosos y estrellas persisten")
	_verificar(otro.ajustes["sfx"] == false, "ajustes persisten")
	otro.desde_diccionario({"mejoras": {"damage": 9999, "attack_speed": -4}, "zonas": ["fantasma"]})
	_verificar(otro.nivel_mejora("damage") == 12 and otro.nivel_mejora("attack_speed") == 0 and otro.zona_abierta("scrap_yard"), "guardado corrupto se sanea")
	gs.free()
	otro.free()


func _test_seleccion() -> void:
	print("Combate")
	var lista := [{"id": 1, "distancia": 9.0}, {"id": 2, "distancia": 2.0}, {"id": 3, "distancia": 5.0}]
	var elegidos := HammerController.seleccionar(lista, 1)
	_verificar(elegidos.size() == 1 and elegidos[0]["id"] == 2, "elige el objetivo mas cercano")
	_verificar(HammerController.seleccionar(lista, 3).size() == 3, "se puede pedir mas de un objetivo")


func _test_ritmo() -> void:
	print("Ritmo (islas y colosos)")
	var gs := _nuevo_estado()
	var barril := GameConfig.objeto_por_id("scrap_yard", "scrap_barrel")
	var buzon := GameConfig.objeto_por_id("downtown", "mailbox")
	var tuberia := GameConfig.objeto_por_id("industrial", "pipe_stack")
	_verificar(gs.registrar_objeto_roto(barril, "scrap_yard") == 12, "isla 1 paga x1 (barril 12)")
	_verificar(gs.registrar_objeto_roto(buzon, "downtown") == 96, "isla 2 paga x2 (buzon 48 -> 96)")
	_verificar(gs.registrar_objeto_roto(tuberia, "industrial") == 216, "isla 3 paga x3 (tuberia 72 -> 216)")
	_verificar(gs.scrap == 12 + 96 + 216, "el Scrap suma lo que pago cada objeto")
	_verificar(GameConfig.scrap_por_vuelta("downtown") == 6396, "las tablas del taller no cambian (6,396 por vuelta en la isla 2)")
	gs.mejoras["damage"] = 5
	_verificar(not gs.puede_retar_coloso(1), "con daño 22.5 aun no se puede retar al coloso 1")
	gs.mejoras["damage"] = 6
	_verificar(gs.puede_retar_coloso(1) and not gs.puede_retar_coloso(2), "con daño 25 si al coloso 1, no al 2")
	gs.mejoras["damage"] = 10
	_verificar(gs.puede_retar_coloso(2) and not gs.puede_retar_coloso(3), "con daño 35 si al coloso 2, no al 3")
	gs.mejoras["damage"] = 12
	_verificar(gs.puede_retar_coloso(3), "con daño 40 se puede retar a los tres")
	_verificar(GameConfig.texto_dano(25.0) == "25" and GameConfig.texto_dano(32.5) == "32.5", "el texto del daño no muestra decimales de mas")
	gs.free()


func _test_camara() -> void:
	print("Camara y control")
	var adelante0 := Player.direccion_adelante(0.0)
	_verificar(_cerca(adelante0.x, 0.0) and _cerca(adelante0.y, -1.0), "con yaw 0 el jugador avanza hacia -Z")
	_verificar(_cerca(Player.direccion_adelante(PI * 0.5).x, -1.0), "con yaw +90 grados avanza hacia -X (su izquierda)")
	var cam := CameraController.new()
	for i in 60:
		cam.seguir_jugador(1.5, 0.1)
	_verificar(_cerca(cam.yaw, 1.5, 0.02), "la camara termina detras del jugador cuando este se voltea")
	cam.yaw = 0.0
	var yaw_jugador := 0.0
	var max_desfase := 0.0
	for i in 60:
		yaw_jugador -= Player.VELOCIDAD_GIRO / 60.0
		cam.seguir_jugador(yaw_jugador, 1.0 / 60.0)
		max_desfase = maxf(max_desfase, absf(angle_difference(cam.yaw, yaw_jugador)))
	_verificar(max_desfase < 0.6, "si el jugador gira 1 s seguido, la camara va casi pegada a el")
	cam.yaw = 0.0
	cam.girar_a_mano(1.0)
	_verificar(_cerca(cam.yaw, 1.0), "girar a mano mueve la camara al instante")
	for i in 10:
		cam.seguir_jugador(0.0, 0.1)
	_verificar(absf(cam.yaw - 1.0) < 0.05, "durante la pausa la camara se queda donde la dejaste")
	for i in 60:
		cam.seguir_jugador(0.0, 0.1)
	_verificar(absf(cam.yaw) < 0.05, "despues de la pausa vuelve sola detras del jugador")
	cam.yaw = 1.0
	var atras := Vector2(cam.desfase_actual().x, cam.desfase_actual().z).normalized()
	_verificar(_cerca(atras.dot(Player.direccion_adelante(1.0)), -1.0), "con el mismo yaw, la camara queda detras de la direccion de avance")
	cam.free()
	print("Menus con teclado")
	var panel := Control.new()
	var cerrar := UIKit.boton("X")
	cerrar.set_meta("sin_foco_inicial", true)
	var comprar := UIKit.boton("BUY")
	panel.add_child(cerrar)
	panel.add_child(comprar)
	add_child(panel)
	UIKit.activar_foco(panel)
	_verificar(comprar.focus_mode == Control.FOCUS_ALL and cerrar.focus_mode == Control.FOCUS_ALL, "los botones del menu se pueden enfocar con el teclado")
	_verificar(comprar.has_focus(), "el foco inicial va al primer boton util, no a cerrar")
	comprar.disabled = true
	UIKit.activar_foco(panel)
	_verificar(cerrar.has_focus(), "si no hay nada que comprar, el foco queda en cerrar")
	panel.queue_free()


func _test_ambiente() -> void:
	print("Ambiente")
	_verificar(AmbienceController.distrito_en(Vector3(0, 0, 0)) == "plaza", "centro = plaza")
	_verificar(AmbienceController.distrito_en(Vector3(0, 0, -240)) == "scrap_yard", "(0,-240) = isla 1")
	_verificar(AmbienceController.distrito_en(Vector3(240, 0, -240)) == "downtown", "(240,-240) = isla 2")
	_verificar(AmbienceController.distrito_en(Vector3(240, 0, 0)) == "industrial", "(240,0) = isla 3")
	_verificar(Formulas.elevacion_sol(GameConfig.HORA_ARENA) > Formulas.elevacion_sol(GameConfig.HORA_CIUDAD), "sol mas alto en la arena del coloso")


func _test_assets() -> void:
	print("Assets")
	var faltan: Array = []
	for zona in GameConfig.OBJETOS:
		for def in GameConfig.OBJETOS[zona]:
			if def.has("modelo") and not Modelos.existe(String(def["modelo"])):
				faltan.append(def["modelo"])
	for c in GameConfig.COLOSOS:
		if not Modelos.existe(String(c["modelo"])):
			faltan.append(c["modelo"])
	for m in [GameConfig.COLOSO["modelo_placa"], GameConfig.COLOSO["modelo_nucleo"], GameConfig.MARTILLO["modelo"]]:
		if not Modelos.existe(String(m)):
			faltan.append(m)
	_verificar(faltan.is_empty(), "todos los modelos de GameConfig existen %s" % [faltan])
	var iconos_ok := true
	for id in GameConfig.ZONAS:
		iconos_ok = iconos_ok and Iconos.zona(id) != null
	for id in GameConfig.MEJORAS:
		iconos_ok = iconos_ok and Iconos.cargar(String(GameConfig.MEJORAS[id]["icono"])) != null
	_verificar(iconos_ok, "iconos de zonas y mejoras cargan")
	var barril := Modelos.instanciar("ScrapBarrel", true)
	var tipos_ok := barril != null and Modelos.es_superficie(Modelos.material_de(barril, "Body")) and Modelos.material_de(barril, "Body").albedo_texture != null
	_verificar(tipos_ok, "el modelo trae su atlas de color y material de superficie")
	var caja := Vector3(2.7, 3.5, 2.7)
	Modelos.encajar(barril, caja)
	var l := Modelos.limites(barril)
	var escalado := AABB(l.position * barril.scale + barril.position, l.size * barril.scale)
	_verificar(escalado.size.x <= caja.x + 0.01 and escalado.size.y <= caja.y + 0.01 and absf(escalado.position.y) < 0.01, "el modelo encaja en su caja con la base en el suelo")
	barril.free()
	_verificar(AmbienceController.cubemap_cielo().get_layers() == 6, "el cielo del atardecer arma las 6 caras")


func _test_coloso() -> void:
	print("Coloso")
	var gs: Node = get_node("/root/GameState")
	gs.guardado_habilitado = false
	gs.reiniciar()
	var c := Coloso.crear(3)
	add_child(c)
	await get_tree().process_frame
	_verificar(c.placas.size() == 4 and c.placas[0].vida_max == 1200.0 and c.nucleo.vida_max == 900.0, "coloso 3: placas de 1,200 y nucleo de 900")
	_verificar(c.estado == Coloso.Estado.INACTIVO and not c.esta_encendido(), "empieza dormido")
	_verificar(c._texto_consola().begins_with("Colossus asleep"), "consola apagada hasta romper 24 objetos")
	c._intentar_retar()
	_verificar(c.estado == Coloso.Estado.INACTIVO, "dormido no se puede retar")
	gs.rotos_por_zona["industrial"] = 12
	c.refrescar_aspecto()
	_verificar(c._material_ojos.albedo_color == GameColors.ROJO, "con 12 objetos rotos los ojos se ponen rojos")
	gs.rotos_por_zona["industrial"] = 24
	_verificar(c.esta_encendido() and c._texto_consola() == "DAMAGE 40 REQUIRED", "con 24 objetos se enciende, pero pide daño 40")
	c._intentar_retar()
	_verificar(c.estado == Coloso.Estado.INACTIVO, "con daño menor a 40 la consola no deja retar")
	gs.mejoras["damage"] = 12
	_verificar(c.nucleo.distancia_a(c.nucleo.global_position + Vector3(0, 0, 20)) > 11.0, "alcance medido desde la superficie")
	c.nucleo.recibir_golpe(100.0)
	_verificar(c.nucleo.vida == c.nucleo.vida_max, "nucleo protegido sin pelea")
	c._intentar_retar()
	_verificar(c.estado == Coloso.Estado.INTRO, "con daño 40 empieza la intro")
	c.actualizar(GameConfig.COLOSO["duracion_intro"] + 0.1)
	_verificar(c.estado == Coloso.Estado.ARMADURA, "pasa a ARMADURA")
	c.nucleo.recibir_golpe(100.0)
	_verificar(c.nucleo.vida == c.nucleo.vida_max, "nucleo inmune con placas")
	c.placas[0].recibir_golpe(40.0)
	_verificar(c.placas[0].vida == 1160.0, "cada golpe quita el daño completo (sin tope)")
	for placa in c.placas:
		while not placa.roto:
			placa.recibir_golpe(40.0)
	_verificar(c.estado == Coloso.Estado.EXPUESTO, "4 placas rotas: nucleo expuesto")
	c.actualizar(16.1)
	_verificar(c.estado == Coloso.Estado.ARMADURA and c.placas_restantes() == 4, "a los 16 s vuelven las placas")
	for placa in c.placas:
		while not placa.roto:
			placa.recibir_golpe(40.0)
	while not c.nucleo.roto:
		c.nucleo.recibir_golpe(40.0)
	_verificar(c.estado == Coloso.Estado.DERROTADO and gs.coloso_vencido_p(3), "nucleo roto: victoria registrada")
	_verificar(c._material_ojos.albedo_color == Coloso.COLOR_OJO_VERDE, "al vencerlo los ojos pasan a verde")
	c.reiniciar()
	_verificar(c._texto_consola().begins_with("DAMAGE") == false and c._texto_consola().find("defeated") >= 0, "vencido y sin los otros 2: no se puede repetir")
	gs.colosos[1]["vencido"] = true
	gs.colosos[2]["vencido"] = true
	_verificar(c._texto_consola().begins_with("Mastery"), "con los 3 vencidos se habilita la maestria")
	c.iniciar_pelea(true)
	c.actualizar(GameConfig.COLOSO["duracion_intro"] + 0.1)
	c.actualizar(GameConfig.COLOSO["inactividad_reinicio"] + 0.1)
	_verificar(c.estado == Coloso.Estado.INACTIVO, "60 s sin actividad reinicia la pelea")
	c.queue_free()
