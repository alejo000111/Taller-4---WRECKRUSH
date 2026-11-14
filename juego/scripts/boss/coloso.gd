@tool
class_name Coloso
extends Node3D

signal victoria(resultado: Dictionary)
signal estado_cambio(estado: int)

enum Estado { INACTIVO, INTRO, ARMADURA, EXPUESTO, DERROTADO, ENFRIAMIENTO }

const TIEMPO_CARTEL_VICTORIA := 6.0
const PRIMER_ATAQUE := 2.5
const YAW_REPOSO := -PI * 0.5
const COLOR_OJO_VERDE := Color("#4CD964")
const ALTURA_PEDESTAL := 13.0
const GIRO_BRAZO := 70.0

var numero: int = 1
var datos: Dictionary = {}
var estado: int = Estado.INACTIVO
var placas: Array[BossPart] = []
var nucleo: BossPart
var jugador: Player
var tiempo_pelea: float = 0.0
var consola: Interactable
var modo_maestria: bool = false
var recibio_dano: bool = false

var _temporizador: float = 0.0
var _proximo_ataque: float = 0.0
var _contador_ataques: int = 0
var _inactividad: float = 0.0
var _brazos: Array[Node3D] = []
var _cabeza: Node3D
var _ojos: Array[MeshInstance3D] = []
var _material_ojos: StandardMaterial3D
var _material_pecho: StandardMaterial3D
var _robot: Node3D
var _tween_ataque: Tween
var _emitio_activo: bool = false


static func crear(numero_: int) -> Coloso:
	var c := Coloso.new()
	c.numero = numero_
	c.name = "Coloso%d" % numero_
	return c


func _ready() -> void:
	datos = GameConfig.COLOSOS[numero - 1]
	add_to_group("colosos")
	_construir()
	consola = Interactable.crear(self, Vector3(0, 0, 44), "Colossus", 10.0, float(GameConfig.COLOSO["mantener_consola"]))
	consola.texto_dinamico = _texto_consola
	consola.activado.connect(_intentar_retar)
	Formas.caja_solida(self, Vector3(3.0, 3.0, 2.0), Vector3(0, 1.5, 44), GameColors.GRIS_OSCURO, 1, true, Formas.material_pbr("WR_WallPanel", 4.0))
	Formas.malla(self, "box", Vector3(3.2, 0.5, 2.2), Vector3(0, 3.2, 44), Formas.material_franjas(GameColors.ROJO, 1.2))
	Formas.etiqueta(self, datos["nombre"], Vector3(0, 6.5, 44), 0.03, GameColors.ROJO, 0.0, true)
	Formas.icono_3d(self, Iconos.JEFE, Vector3(0, 9.0, 44), 2.4)
	if Engine.is_editor_hint():
		return
	GameState.objeto_roto.connect(func(_d: Dictionary, _z: String) -> void: refrescar_aspecto())
	GameState.juego_completado.connect(func(_r: Dictionary) -> void: refrescar_aspecto())
	refrescar_aspecto()
	_emitir_estado()


func punto_reaparicion() -> Vector3:
	return to_global(Vector3(0, 3, 52))


func _construir() -> void:
	var cubierta := Formas.material_pbr("WR_DeckPlate", 8.0)
	var oxido := Formas.material_pbr("WR_RustSheet", 6.0)
	Formas.caja_solida(self, Vector3(19, 2, 19), Vector3(0, 1, 0), Color("#3A3D44"), 8, true, cubierta)
	for sx in [-1, 1]:
		for sz in [-1, 1]:
			var pilar := Formas.caja_solida(self, Vector3(2.4, ALTURA_PEDESTAL - 2.0, 2.4), Vector3(sx * 7.5, ALTURA_PEDESTAL * 0.5 + 1.0, sz * 7.5), Color("#4A4E56"), 8, true, oxido)
			pilar.name = "Pilar"
	Formas.caja_solida(self, Vector3(19, 1.5, 19), Vector3(0, ALTURA_PEDESTAL + 0.75, 0), Color("#3A3D44"), 8, true, cubierta)
	Formas.malla(self, "box", Vector3(19.4, 0.5, 19.4), Vector3(0, ALTURA_PEDESTAL + 0.35, 0), Formas.material_franjas(Color.WHITE, 0.0, 4.0), false)
	_cabeza = Node3D.new()
	_cabeza.position = Vector3(0, ALTURA_PEDESTAL + 1.5, 0)
	_cabeza.rotation.y = YAW_REPOSO
	add_child(_cabeza)
	_material_ojos = Formas.material(Color("#2A2D33"), 0.4)
	_material_ojos.emission_enabled = true
	_material_ojos.emission = Color.BLACK
	_robot = Modelos.instanciar(String(datos.get("modelo", "")), true)
	if _robot != null:
		_robot.scale = Vector3.ONE * float(datos.get("escala", 0.7))
		_cabeza.add_child(_robot)
		for malla in Modelos.mallas(_robot):
			match String(malla.name):
				"Eyes":
					_material_ojos = malla.material_override as StandardMaterial3D
				"Core":
					_material_pecho = malla.material_override as StandardMaterial3D
				"ArmL", "ArmR":
					_brazos.append(_pivote_brazo(malla))
	else:
		Formas.malla(_cabeza, "box", Vector3(14, 12, 10), Vector3(0, 6, 0), Formas.material(datos["color"], 0.8, 0.3))
		for lado in [-1, 1]:
			_ojos.append(Formas.malla(_cabeza, "box", Vector3(1.4, 1.0, 0.6), Vector3(lado * 1.4, 9.0, -5.2), _material_ojos, false))
	var orientaciones := [
		[Vector3(6.5, 6.5, 0), Vector3(1.6, 9, 8), -PI * 0.5],
		[Vector3(-6.5, 6.5, 0), Vector3(1.6, 9, 8), PI * 0.5],
		[Vector3(0, 6.5, 6.5), Vector3(8, 9, 1.6), PI],
		[Vector3(0, 6.5, -6.5), Vector3(8, 9, 1.6), 0.0],
	]
	for i in int(GameConfig.COLOSO["cantidad_placas"]):
		var placa := BossPart.crear("placa", orientaciones[i][1], Formulas.vida_placa(numero), Color("#8A8F99"), String(GameConfig.COLOSO["modelo_placa"]), orientaciones[i][2])
		placa.position = orientaciones[i][0]
		placa.name = "Placa%d" % (i + 1)
		add_child(placa)
		placa.destruida.connect(_al_romper_placa)
		placa.golpeada.connect(_al_golpear)
		placas.append(placa)
	nucleo = BossPart.crear("nucleo", Vector3(5, 5, 5), Formulas.vida_nucleo(numero), Color("#5A1C1C"), String(GameConfig.COLOSO["modelo_nucleo"]))
	nucleo.position = Vector3(0, 7.0, 0)
	nucleo.name = "Nucleo"
	add_child(nucleo)
	nucleo.golpeada.connect(_al_golpear)
	nucleo.destruida.connect(_al_romper_nucleo)


func _pivote_brazo(malla: MeshInstance3D) -> Node3D:
	var caja := malla.get_aabb()
	var hombro := Vector3(caja.get_center().x, caja.end.y - caja.size.y * 0.08, caja.get_center().z)
	var pivote := Node3D.new()
	pivote.name = "Pivote" + String(malla.name)
	pivote.position = hombro
	_robot.add_child(pivote)
	malla.get_parent().remove_child(malla)
	pivote.add_child(malla)
	malla.position = -hombro
	return pivote


func _refrescar_pecho() -> void:
	if _material_pecho == null:
		return
	var color := Color("#FF7A1A")
	var energia := 0.5
	match estado:
		Estado.INTRO, Estado.ARMADURA:
			color = GameColors.ROJO
			energia = 2.2
		Estado.EXPUESTO:
			color = GameColors.AMARILLO
			energia = 3.5
		Estado.DERROTADO, Estado.ENFRIAMIENTO:
			color = COLOR_OJO_VERDE
			energia = 1.2
		_:
			if GameState.coloso_vencido_p(numero):
				color = COLOR_OJO_VERDE
				energia = 1.0
			elif esta_encendido():
				energia = 1.8
	_material_pecho.albedo_color = color
	_material_pecho.emission = color
	_material_pecho.emission_energy_multiplier = energia


func refrescar_aspecto() -> void:
	var vencido := GameState.coloso_vencido_p(numero)
	var rotos := GameState.rotos_en(datos["zona"])
	if vencido:
		_material_ojos.emission = COLOR_OJO_VERDE
		_material_ojos.emission_energy_multiplier = 3.0
		_material_ojos.albedo_color = COLOR_OJO_VERDE
	elif rotos >= int(datos["ojos_rojos"]):
		_material_ojos.emission = GameColors.ROJO
		_material_ojos.emission_energy_multiplier = 3.0
		_material_ojos.albedo_color = GameColors.ROJO
	else:
		_material_ojos.emission = Color.BLACK
		_material_ojos.albedo_color = Color("#2A2D33")
	_refrescar_pecho()


func esta_encendido() -> bool:
	return GameState.rotos_en(datos["zona"]) >= int(datos["giro_cabeza"]) or GameState.coloso_vencido_p(numero)


func mira_al_jugador() -> bool:
	if GameState.todos_vencidos():
		return true
	return esta_encendido()


func _texto_consola() -> String:
	var faltan: int = int(datos["giro_cabeza"]) - GameState.rotos_en(datos["zona"])
	if not esta_encendido():
		return "Colossus asleep · break %d more objects" % faltan
	if GameState.coloso_vencido_p(numero) and not GameState.todos_vencidos():
		return "%s defeated" % datos["nombre"]
	if not GameState.puede_retar_coloso(numero):
		return "DAMAGE %s REQUIRED" % GameConfig.texto_dano(GameConfig.dano_requerido(numero))
	if GameState.coloso_vencido_p(numero):
		return "Mastery · %s · stars %d/%d" % [datos["nombre"], GameState.estrellas(numero), int(GameConfig.COLOSO["estrellas_maximas"])]
	return "Challenge %s" % datos["nombre"]


func _intentar_retar() -> void:
	if estado != Estado.INACTIVO:
		return
	if not esta_encendido():
		GameState.toast.emit("BREAK %d MORE OBJECTS" % (int(datos["giro_cabeza"]) - GameState.rotos_en(datos["zona"])), "bad")
		return
	if not GameState.puede_retar_coloso(numero):
		GameState.toast.emit("DAMAGE %s REQUIRED" % GameConfig.texto_dano(GameConfig.dano_requerido(numero)), "bad")
		Sfx.reproducir("error")
		return
	var vencido := GameState.coloso_vencido_p(numero)
	if vencido and not GameState.todos_vencidos():
		GameState.toast.emit("COLOSSUS ALREADY DEFEATED", "bad")
		return
	iniciar_pelea(vencido)


func iniciar_pelea(maestria: bool = false) -> bool:
	if estado != Estado.INACTIVO:
		return false
	if jugador == null:
		jugador = get_tree().get_first_node_in_group("player") as Player
	if jugador != null and not jugador.recibio_dano.is_connected(_al_recibir_dano):
		jugador.recibio_dano.connect(_al_recibir_dano)
	modo_maestria = maestria
	recibio_dano = false
	_reiniciar_partes()
	tiempo_pelea = 0.0
	_inactividad = 0.0
	_contador_ataques = 0
	_temporizador = float(GameConfig.COLOSO["duracion_intro"])
	_cambiar_estado(Estado.INTRO)
	Sfx.reproducir("jefe", 0.0, 0.8)
	Fx.sacudida_camara.emit(0.8)
	GameState.toast.emit("%s AWAKENS%s" % [datos["nombre"], " · MASTERY" if maestria else ""], "bad")
	return true


func reiniciar(motivo: String = "") -> void:
	_reiniciar_partes()
	_cambiar_estado(Estado.INACTIVO)
	if motivo != "":
		GameState.toast.emit(motivo, "bad")


func en_pelea() -> bool:
	return estado == Estado.ARMADURA or estado == Estado.EXPUESTO or estado == Estado.INTRO


func placas_restantes() -> int:
	var restantes := 0
	for placa in placas:
		if not placa.roto:
			restantes += 1
	return restantes


func actualizar(delta: float) -> void:
	_girar_cabeza(delta)
	match estado:
		Estado.INTRO:
			_temporizador -= delta
			if _temporizador <= 0.0:
				_entrar_armadura()
		Estado.ARMADURA, Estado.EXPUESTO:
			tiempo_pelea += delta
			_inactividad += delta
			_actualizar_ataques(delta)
			if estado == Estado.EXPUESTO:
				_temporizador -= delta
				if _temporizador <= 0.0 and not nucleo.roto:
					_restaurar_armadura()
			if _inactividad >= float(GameConfig.COLOSO["inactividad_reinicio"]):
				reiniciar("COLOSSUS RESET: NO ACTIVITY")
		Estado.DERROTADO:
			_temporizador -= delta
			if _temporizador <= 0.0:
				_temporizador = float(GameConfig.COLOSO["espera_entre_peleas"])
				_cambiar_estado(Estado.ENFRIAMIENTO)
		Estado.ENFRIAMIENTO:
			_temporizador -= delta
			if _temporizador <= 0.0:
				reiniciar()
	_emitir_estado()


func _process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	actualizar(delta)


func _girar_cabeza(delta: float) -> void:
	var meta := YAW_REPOSO
	if jugador == null:
		jugador = get_tree().get_first_node_in_group("player") as Player
	if mira_al_jugador() and jugador != null and jugador.global_position.distance_to(global_position) < 160.0:
		var d := jugador.global_position - _cabeza.global_position
		meta = atan2(-d.x, -d.z) - rotation.y
	_cabeza.rotation.y = lerp_angle(_cabeza.rotation.y, meta, clampf(2.5 * delta, 0.0, 1.0))


func _entrar_armadura() -> void:
	for placa in placas:
		placa.reiniciar(true)
		placa.establecer_vulnerable(true)
	nucleo.establecer_vulnerable(false)
	_proximo_ataque = PRIMER_ATAQUE
	_cambiar_estado(Estado.ARMADURA)


func _exponer() -> void:
	_temporizador = float(GameConfig.COLOSO["ventana_expuesta"])
	nucleo.establecer_vulnerable(true)
	_cambiar_estado(Estado.EXPUESTO)
	GameState.toast.emit("CORE EXPOSED! HIT IT!", "good")


func _restaurar_armadura() -> void:
	nucleo.establecer_vulnerable(false)
	for placa in placas:
		placa.reiniciar(true)
		placa.establecer_vulnerable(true)
	_cambiar_estado(Estado.ARMADURA)
	GameState.toast.emit("ARMOR RESTORED", "bad")


func _derrotar() -> void:
	_temporizador = TIEMPO_CARTEL_VICTORIA
	_cambiar_estado(Estado.DERROTADO)
	Sfx.reproducir("victoria")
	Fx.sacudida_camara.emit(1.0)
	var resultado := GameState.registrar_victoria_coloso(numero, tiempo_pelea, not recibio_dano, modo_maestria)
	refrescar_aspecto()
	victoria.emit(resultado)


func _reiniciar_partes() -> void:
	for placa in placas:
		placa.reiniciar(true)
		placa.establecer_vulnerable(false)
	nucleo.reiniciar(true)
	nucleo.establecer_vulnerable(false)


func _al_recibir_dano() -> void:
	if en_pelea():
		recibio_dano = true


func _al_romper_placa(_parte: BossPart) -> void:
	_inactividad = 0.0
	if estado == Estado.ARMADURA and placas_restantes() == 0:
		_exponer()


func _al_romper_nucleo(_parte: BossPart) -> void:
	_inactividad = 0.0
	if estado == Estado.EXPUESTO:
		_derrotar()


func _al_golpear(_parte: BossPart) -> void:
	_inactividad = 0.0


func _actualizar_ataques(delta: float) -> void:
	_proximo_ataque -= delta
	if _proximo_ataque > 0.0:
		return
	if jugador == null or jugador.muerto:
		_proximo_ataque = 1.0
		return
	var plano := Vector2(jugador.global_position.x - global_position.x, jugador.global_position.z - global_position.z)
	if plano.length() > GameConfig.RADIO_ARENA + 10.0:
		_proximo_ataque = 1.0
		return
	_contador_ataques += 1
	_proximo_ataque = Formulas.intervalo_golpe_suelo(numero)
	if _contador_ataques % 3 == 0:
		_lanzar_anillo()
	else:
		_lanzar_disco()


func _lanzar_disco() -> void:
	var aviso := BossWarning.mostrar(self, jugador.global_position, float(GameConfig.COLOSO["radio_disco"]), float(GameConfig.COLOSO["aviso"]))
	aviso.impacto.connect(_resolver_impacto.bind(aviso))
	_animar_ataque()


func _lanzar_anillo() -> void:
	var aviso := BossWarning.mostrar(self, global_position, float(GameConfig.COLOSO["radio_anillo_exterior"]), float(GameConfig.COLOSO["aviso"]), float(GameConfig.COLOSO["radio_anillo_interior"]))
	aviso.impacto.connect(_resolver_impacto.bind(aviso))
	_animar_ataque()


func _resolver_impacto(aviso: BossWarning) -> void:
	if jugador == null or jugador.muerto or not en_pelea():
		return
	if aviso.contiene(jugador.global_position) and not jugador.esta_en_el_aire():
		jugador.tomar_dano(float(GameConfig.COLOSO["dano"]))


func _animar_ataque() -> void:
	if _tween_ataque != null and _tween_ataque.is_valid():
		_tween_ataque.kill()
	_tween_ataque = create_tween()
	_tween_ataque.set_parallel(true)
	for brazo in _brazos:
		brazo.rotation.x = deg_to_rad(GIRO_BRAZO)
		_tween_ataque.tween_property(brazo, "rotation:x", 0.0, 0.9).set_delay(0.7)


func _cambiar_estado(nuevo: int) -> void:
	estado = nuevo
	if consola != null:
		consola.habilitado = nuevo == Estado.INACTIVO
	_refrescar_pecho()
	estado_cambio.emit(nuevo)


func _objetivo_texto() -> String:
	match estado:
		Estado.INTRO:
			return "GET READY... JUMP TO DODGE ORANGE"
		Estado.ARMADURA:
			return "BREAK THE ARMOR PLATES  %d/%d" % [placas.size() - placas_restantes(), placas.size()]
		Estado.EXPUESTO:
			return "HIT THE CORE!  %ds" % int(ceil(_temporizador))
		Estado.DERROTADO:
			return "VICTORY!"
		Estado.ENFRIAMIENTO:
			return "COLOSSUS REPAIRING  %ds" % int(ceil(_temporizador))
	return ""


func _emitir_estado() -> void:
	var activo := estado != Estado.INACTIVO
	if not activo and not _emitio_activo:
		return
	_emitio_activo = activo
	GameState.boss_estado.emit({
		"activo": activo,
		"nombre": datos["nombre"] + (" · MASTERY" if modo_maestria else ""),
		"proporcion": nucleo.proporcion() if nucleo != null else 1.0,
		"objetivo": _objetivo_texto(),
		"estado": estado,
		"tiempo": tiempo_pelea,
	})
