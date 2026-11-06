class_name BossWarning
extends Node3D

signal impacto
signal terminado

const SHADER := preload("res://shaders/warning.gdshader")
const ALTURA := 0.18
const TEXTO := "JUMP / LEAVE ORANGE"

var radio: float = 10.0
var radio_interior: float = 0.0
var duracion: float = 1.4
var _tiempo: float = 0.0
var _material: ShaderMaterial
var _impactado: bool = false


static func mostrar(padre: Node, posicion: Vector3, radio_: float, segundos: float, radio_interior_: float = 0.0) -> BossWarning:
	var aviso := BossWarning.new()
	aviso.radio = radio_
	aviso.radio_interior = radio_interior_
	aviso.duracion = maxf(segundos, 0.05)
	padre.add_child(aviso)
	aviso.global_position = Vector3(posicion.x, ALTURA, posicion.z)
	return aviso


func contiene(punto: Vector3) -> bool:
	var distancia := Vector2(punto.x - global_position.x, punto.z - global_position.z).length()
	return distancia <= radio and distancia >= radio_interior


func _ready() -> void:
	var plano := MeshInstance3D.new()
	var malla := PlaneMesh.new()
	malla.size = Vector2(radio * 2.0, radio * 2.0)
	plano.mesh = malla
	_material = ShaderMaterial.new()
	_material.shader = SHADER
	_material.set_shader_parameter("radio_interior", radio_interior / radio)
	_material.set_shader_parameter("progreso", 0.0)
	_material.render_priority = 2
	plano.material_override = _material
	plano.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(plano)
	var etiqueta := Label3D.new()
	etiqueta.text = TEXTO
	etiqueta.modulate = GameColors.NARANJA
	etiqueta.outline_modulate = Color(0.1, 0.02, 0.02)
	etiqueta.outline_size = 14
	etiqueta.font_size = 48
	etiqueta.pixel_size = 0.013
	etiqueta.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	etiqueta.no_depth_test = true
	etiqueta.position = Vector3(0, 6.0, 0) if radio_interior <= 0.0 else Vector3(0, 6.0, radio_interior + (radio - radio_interior) * 0.5)
	add_child(etiqueta)
	Sfx.reproducir("aviso", -4.0)


func _process(delta: float) -> void:
	_tiempo += delta
	_material.set_shader_parameter("progreso", clampf(_tiempo / duracion, 0.0, 1.0))
	_material.set_shader_parameter("parpadeo", Curvas.pulso(_tiempo, 5.0))
	if _tiempo >= duracion and not _impactado:
		_impactado = true
		impacto.emit()
		Fx.onda(global_position + Vector3(0, 0.1, 0), radio, GameColors.NARANJA, 0.4)
		Fx.sacudida_camara.emit(0.7)
		Sfx.reproducir("jefe", -2.0)
		var salida := create_tween()
		salida.tween_interval(0.12)
		salida.tween_callback(func() -> void:
			terminado.emit()
			queue_free())
