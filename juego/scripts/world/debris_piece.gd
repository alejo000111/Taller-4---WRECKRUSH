class_name DebrisPiece
extends MeshInstance3D

const GRAVEDAD := 90.0

var velocidad: Vector3 = Vector3.ZERO
var vida: float = 1.1
var _edad: float = 0.0
var _giro: Vector3 = Vector3.ZERO
var _escala_inicial: Vector3 = Vector3.ONE


func configurar(color: Color, tamano: Vector3, impulso: Vector3) -> void:
	var malla := BoxMesh.new()
	malla.size = tamano
	var material := StandardMaterial3D.new()
	material.albedo_color = color.darkened(randf_range(0.0, 0.35))
	material.roughness = 0.9
	malla.material = material
	mesh = malla
	velocidad = impulso
	_giro = Vector3(randf_range(-8, 8), randf_range(-8, 8), randf_range(-8, 8))
	vida = randf_range(0.8, 1.3)
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF


func _process(delta: float) -> void:
	_edad += delta
	velocidad.y -= GRAVEDAD * delta
	global_position += velocidad * delta
	if global_position.y < 0.2:
		global_position.y = 0.2
		velocidad.x *= 0.6
		velocidad.z *= 0.6
		velocidad.y = 0.0
	rotation += _giro * delta
	var restante := 1.0 - _edad / vida
	scale = Vector3.ONE * clampf(restante * 2.0, 0.0, 1.0)
	if _edad >= vida:
		queue_free()
