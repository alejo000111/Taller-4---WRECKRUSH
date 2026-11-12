@tool
class_name Destructible
extends StaticBody3D

signal roto(destructible: Destructible)
signal reaparecio(destructible: Destructible)

const SHADER_BARRA := preload("res://shaders/healthbar.gdshader")
const TIEMPO_APAGADO_CONTORNO := 0.5

var def: Dictionary = {}
var zona: String = ""
var vida: float = 1.0
var vida_max: float = 1.0
var caja: Vector3 = Vector3(2, 2, 2)
var color_principal: Color = Color.GRAY
var activo: bool = true

var _raiz_visual: Node3D
var _material_contorno: ShaderMaterial
var _materiales: Array[StandardMaterial3D] = []
var _colores_base: Array[Color] = []
var _destello: StandardMaterial3D
var _mallas: Array[MeshInstance3D] = []
var _colision: CollisionShape3D
var _barra: MeshInstance3D
var _material_barra: ShaderMaterial
var _tween_golpe: Tween
var _tween_contorno: Tween


static func crear(definicion: Dictionary, zona_id: String) -> Destructible:
	var d := Destructible.new()
	d.def = definicion
	d.zona = zona_id
	d.vida_max = float(definicion["vida"])
	d.vida = d.vida_max
	d.caja = definicion["caja"]
	d.name = String(definicion["id"]).to_pascal_case()
	return d


func _ready() -> void:
	add_to_group("golpeables")
	add_to_group("destructibles")
	collision_layer = 4
	collision_mask = 0
	_construir()


func _construir() -> void:
	_raiz_visual = Node3D.new()
	add_child(_raiz_visual)
	_material_contorno = Formas.material_contorno(GameColors.AMARILLO, 0.28 if caja.y < 8.0 else 0.4)
	_destello = Formas.material_destello()
	color_principal = def["partes"][0][3]
	var modelo := Modelos.instanciar(String(def.get("modelo", "")), true)
	if modelo != null:
		_raiz_visual.add_child(modelo)
		var escala := Modelos.encajar(modelo, caja)
		_material_contorno.set_shader_parameter("grosor", (0.3 if caja.y < 8.0 else 0.42) / maxf(escala.x, 0.01))
		for material in Modelos.materiales(modelo):
			if Modelos.es_superficie(material):
				material.next_pass = _material_contorno
				_materiales.append(material)
				_colores_base.append(material.albedo_color)
	else:
		for parte in def["partes"]:
			var color: Color = parte[3]
			var material := Formas.material(color, 0.85, 0.12)
			material.next_pass = _material_contorno
			_materiales.append(material)
			_colores_base.append(color)
			Formas.malla(_raiz_visual, parte[0], parte[1], parte[2], material)
	_mallas = Modelos.mallas(_raiz_visual)
	_colision = CollisionShape3D.new()
	var forma := BoxShape3D.new()
	forma.size = caja
	_colision.shape = forma
	_colision.position = Vector3(0, caja.y * 0.5, 0)
	add_child(_colision)


func puede_ser_golpeado() -> bool:
	return activo


func distancia_a(punto: Vector3) -> float:
	var local := to_local(punto)
	var mitad := caja * 0.5
	var cercano := Vector3(clampf(local.x, -mitad.x, mitad.x), clampf(local.y, 0.0, caja.y), clampf(local.z, -mitad.z, mitad.z))
	return local.distance_to(cercano)


func recibir_golpe(dano: float, critico: bool = false) -> bool:
	if not activo:
		return false
	vida = maxf(vida - dano, 0.0)
	_reaccion_golpe()
	_actualizar_barra()
	Fx.golpe(self, dano, critico)
	if vida <= 0.0:
		_romper()
		return true
	return false


func _reaccion_golpe() -> void:
	var proporcion := vida / vida_max
	for i in _materiales.size():
		_materiales[i].albedo_color = _colores_base[i].lerp(Color(0.08, 0.08, 0.09, _colores_base[i].a), (1.0 - proporcion) * 0.55)
	if _tween_golpe != null and _tween_golpe.is_valid():
		_tween_golpe.kill()
	_raiz_visual.scale = Vector3.ONE
	_fijar_destello(true)
	_destello.albedo_color.a = 0.8
	_tween_golpe = create_tween()
	_tween_golpe.set_parallel(true)
	_tween_golpe.tween_property(_raiz_visual, "scale", Vector3(1.07, 0.94, 1.07), 0.04)
	_tween_golpe.chain().tween_property(_raiz_visual, "scale", Vector3.ONE, 0.09)
	_tween_golpe.tween_property(_destello, "albedo_color:a", 0.0, 0.14)
	_tween_golpe.chain().tween_callback(_fijar_destello.bind(false))


func _fijar_destello(activo: bool) -> void:
	for malla in _mallas:
		malla.material_overlay = _destello if activo else null


func _actualizar_barra() -> void:
	if _barra == null:
		_barra = MeshInstance3D.new()
		var quad := QuadMesh.new()
		quad.size = Vector2(maxf(maxf(caja.x, caja.z), 3.0), 0.55)
		_barra.mesh = quad
		_material_barra = ShaderMaterial.new()
		_material_barra.shader = SHADER_BARRA
		_material_barra.render_priority = 5
		_barra.material_override = _material_barra
		_barra.position = Vector3(0, caja.y + 1.4, 0)
		_barra.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(_barra)
	_barra.visible = true
	_material_barra.set_shader_parameter("proporcion", vida / vida_max)


func _romper() -> void:
	activo = false
	_colision.set_deferred("disabled", true)
	if _barra != null:
		_barra.visible = false
	var pago := GameState.registrar_objeto_roto(def, zona)
	Fx.romper(self, String(def["tamano"]), pago)
	if _tween_contorno != null and _tween_contorno.is_valid():
		_tween_contorno.kill()
	_tween_contorno = create_tween()
	_tween_contorno.set_parallel(true)
	_tween_contorno.tween_property(_raiz_visual, "scale", Vector3.ONE * 0.02, TIEMPO_APAGADO_CONTORNO).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	_tween_contorno.tween_method(_fijar_opacidad_contorno, 1.0, 0.0, TIEMPO_APAGADO_CONTORNO)
	_tween_contorno.chain().tween_callback(func() -> void: _raiz_visual.visible = false)
	roto.emit(self)
	get_tree().create_timer(float(def["respawn"])).timeout.connect(_reaparecer)


func _reaparecer() -> void:
	if not is_inside_tree():
		return
	vida = vida_max
	activo = true
	_colision.set_deferred("disabled", false)
	for i in _materiales.size():
		_materiales[i].albedo_color = _colores_base[i]
	_fijar_destello(false)
	_fijar_opacidad_contorno(1.0)
	_raiz_visual.visible = true
	_raiz_visual.scale = Vector3.ONE * 0.02
	var crecer := create_tween()
	crecer.tween_property(_raiz_visual, "scale", Vector3.ONE, 0.3).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	reaparecio.emit(self)


func _fijar_opacidad_contorno(valor: float) -> void:
	_material_contorno.set_shader_parameter("opacidad", valor)
