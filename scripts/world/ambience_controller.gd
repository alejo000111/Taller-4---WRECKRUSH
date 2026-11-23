@tool
class_name AmbienceController
extends Node3D

const INTERVALO_DETECCION := 0.25
const DURACION_TRANSICION := 1.5
const SHADER_CIELO := preload("res://shaders/sky.gdshader")
const RUTA_CIELO := "res://assets/sky/WR_DuskSky/"
const CARAS_CIELO := ["Rt", "Lf", "Up", "Dn", "Bk", "Ft"]

var entorno: Environment
var sol: DirectionalLight3D
var jugador: Node3D
var distrito_actual: String = ""
var en_arena: bool = false
var hora: float = GameConfig.HORA_CIUDAD

var _cielo: ShaderMaterial
var _tinte: Color = Color.WHITE
var _tween_hora: Tween
var _tween_tinte: Tween
var _temporizador: float = 0.0


static func distrito_en(punto: Vector3) -> String:
	var celda := Vector2i(roundi(punto.x / CityWorld.SEPARACION), roundi(punto.z / CityWorld.SEPARACION))
	if celda == Vector2i(0, -1):
		return "scrap_yard"
	if celda == Vector2i(1, -1):
		return "downtown"
	if celda == Vector2i(1, 0):
		return "industrial"
	return "plaza"


static func cubemap_cielo() -> Cubemap:
	var imagenes: Array[Image] = []
	for cara in CARAS_CIELO:
		var imagen := (load(RUTA_CIELO + cara + ".png") as Texture2D).get_image()
		if imagen.is_compressed():
			imagen.decompress()
		imagen.convert(Image.FORMAT_RGB8)
		imagenes.append(imagen)
	var cubo := Cubemap.new()
	cubo.create_from_images(imagenes)
	return cubo


func _ready() -> void:
	_cielo = ShaderMaterial.new()
	_cielo.shader = SHADER_CIELO
	_cielo.set_shader_parameter("cielo", cubemap_cielo())
	var cielo := Sky.new()
	cielo.sky_material = _cielo
	entorno = Environment.new()
	entorno.background_mode = Environment.BG_SKY
	entorno.sky = cielo
	entorno.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	entorno.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	entorno.tonemap_exposure = 0.8
	entorno.glow_enabled = true
	entorno.glow_intensity = 0.35
	entorno.glow_strength = 1.0
	entorno.glow_bloom = 0.08
	entorno.glow_hdr_threshold = 1.4
	entorno.fog_enabled = true
	entorno.fog_density = 0.0006
	entorno.fog_aerial_perspective = 0.4
	var mundo := WorldEnvironment.new()
	mundo.environment = entorno
	add_child(mundo)
	sol = DirectionalLight3D.new()
	sol.shadow_enabled = true
	sol.directional_shadow_max_distance = 320.0
	sol.directional_shadow_mode = DirectionalLight3D.SHADOW_PARALLEL_2_SPLITS
	sol.shadow_blur = 1.6
	sol.light_energy = 1.35
	add_child(sol)
	_aplicar_hora(hora)
	cambiar_distrito("plaza")


func _process(delta: float) -> void:
	if Engine.is_editor_hint():
		return
	_temporizador -= delta
	if _temporizador > 0.0 or jugador == null:
		return
	_temporizador = INTERVALO_DETECCION
	var distrito := distrito_en(jugador.global_position)
	if distrito != distrito_actual:
		cambiar_distrito(distrito)
	var cerca := false
	for coloso in get_tree().get_nodes_in_group("colosos"):
		if coloso.global_position.distance_to(jugador.global_position) < GameConfig.RADIO_ARENA:
			cerca = true
	if cerca != en_arena:
		en_arena = cerca
		modo_isla_jefe(cerca)


func cambiar_distrito(zona: String) -> void:
	distrito_actual = zona
	var tinte: Color = GameConfig.ZONAS[zona]["tinte"]
	if _tween_tinte != null and _tween_tinte.is_valid():
		_tween_tinte.kill()
	_tween_tinte = create_tween()
	_tween_tinte.tween_method(_fijar_tinte, _tinte, tinte, DURACION_TRANSICION)


func modo_isla_jefe(activo: bool) -> void:
	var meta := GameConfig.HORA_ARENA if activo else GameConfig.HORA_CIUDAD
	if is_equal_approx(meta, hora) and (_tween_hora == null or not _tween_hora.is_running()):
		return
	if _tween_hora != null and _tween_hora.is_valid():
		_tween_hora.kill()
	_tween_hora = create_tween()
	_tween_hora.tween_method(_aplicar_hora, hora, meta, DURACION_TRANSICION)


func _aplicar_hora(valor: float) -> void:
	hora = valor
	var f := clampf((GameConfig.HORA_CIUDAD - hora) / (GameConfig.HORA_CIUDAD - GameConfig.HORA_ARENA), 0.0, 1.0)
	var elevacion := Formulas.elevacion_sol(hora)
	sol.rotation_degrees = Vector3(-elevacion, 215.0, 0.0)
	sol.light_color = Color("#FFB784").lerp(Color("#FFD6B0"), f)
	sol.light_energy = lerpf(0.75, 0.9, f)
	_cielo.set_shader_parameter("tinte", Color("#FFD2BC").lerp(Color("#FFF2E6"), f))
	_cielo.set_shader_parameter("energia", lerpf(0.85, 1.0, f))
	entorno.fog_light_color = Color("#D9A07A").lerp(Color("#F0B890"), f)
	entorno.ambient_light_energy = lerpf(0.4, 0.55, f)
	entorno.fog_density = lerpf(0.0006, 0.0004, f)


func _fijar_tinte(color: Color) -> void:
	_tinte = color
	entorno.ambient_light_color = Color("#FFE9D8").lerp(color, 0.3)
