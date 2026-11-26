extends Node3D

@onready var ciudad: CityWorld = $Ciudad
@onready var ambiente: AmbienceController = $Ambiente
@onready var jugador: Player = $Jugador
@onready var camara: CameraController = $Camara

var hud: Hud

var _muerte_restante: float = 0.0
var _punto_reaparicion: Vector3 = CityWorld.PUNTO_PLAZA


func _ready() -> void:
	InputSetup.registrar()
	camara.objetivo = jugador
	camara.yaw = 0.0
	camara.saltar_a(jugador.global_position)
	jugador.camara = camara
	ambiente.jugador = jugador
	for coloso in ciudad.colosos:
		coloso.jugador = jugador
	var martillo := HammerController.new()
	martillo.name = "Martillo"
	martillo.jugador = jugador
	add_child(martillo)
	var interaccion := InteractionController.new()
	interaccion.name = "Interaccion"
	interaccion.jugador = jugador
	add_child(interaccion)
	var tutorial := Onboarding.new()
	tutorial.name = "Tutorial"
	tutorial.jugador = jugador
	add_child(tutorial)
	hud = Hud.new()
	hud.name = "Hud"
	hud.jugador = jugador
	add_child(hud)
	ciudad.panel_pedido.connect(hud.abrir_panel)
	ciudad.viaje_pedido.connect(viajar_a)
	jugador.murio.connect(_al_morir)
	GameState.mejora_comprada.connect(func(_i: String, _n: int) -> void: GameState.guardar())
	GameState.zona_desbloqueada.connect(func(_i: String) -> void: GameState.guardar())
	if OS.is_debug_build():
		var dev := DevTools.new()
		dev.main = self
		add_child(dev)


func _process(delta: float) -> void:
	if _muerte_restante > 0.0:
		_muerte_restante -= delta
		hud.mostrar_muerte(_muerte_restante)
		if _muerte_restante <= 0.0:
			hud.ocultar_muerte()
			jugador.revivir(_punto_reaparicion)


func viajar_a(destino: String) -> void:
	if destino == "plaza":
		_reiniciar_colosos()
		jugador.teletransportar(CityWorld.PUNTO_PLAZA + Vector3(0, 0, -20))
	elif GameState.zona_abierta(destino):
		jugador.teletransportar(CityWorld.PUNTOS_ENTRADA[destino])
	else:
		hud.abrir_panel("unlock_" + destino)
		return
	Sfx.reproducir("comprar", -8.0)


func _reiniciar_colosos() -> void:
	for coloso in ciudad.colosos:
		if coloso.en_pelea():
			coloso.reiniciar()


func _coloso_activo() -> Coloso:
	for coloso in ciudad.colosos:
		if coloso.en_pelea():
			return coloso
	return null


func _al_morir() -> void:
	_muerte_restante = GameConfig.REAPARICION_COLOSO
	_punto_reaparicion = jugador.ultimo_punto_seguro
	var coloso := _coloso_activo()
	if coloso != null:
		_punto_reaparicion = coloso.punto_reaparicion()
		coloso.reiniciar()
	Sfx.reproducir("error")
