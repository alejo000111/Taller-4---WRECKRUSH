@tool
class_name Formas
extends RefCounted

const SHADER_CONTORNO := preload("res://shaders/outline.gdshader")
const RAIZ_MATERIALES := "res://assets/materials/"
const TEXTURA_HALO := preload("res://assets/vfx/glow.png")
const TEXTURA_FRANJAS := preload("res://assets/vfx/hazard_stripe.png")

static var _pbr: Dictionary = {}


static func material(color: Color, rugosidad: float = 0.85, metalico: float = 0.0, emision: float = 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = rugosidad
	m.metallic = metalico
	if emision > 0.0:
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = emision
	return m


static func material_contorno(color: Color = GameColors.AMARILLO, grosor: float = 0.25) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = SHADER_CONTORNO
	m.set_shader_parameter("color", color)
	m.set_shader_parameter("grosor", grosor)
	m.set_shader_parameter("opacidad", 1.0)
	return m


static func material_pbr(nombre: String, baldosa: float = 16.0, tinte: Color = Color.WHITE, mundo: bool = true) -> StandardMaterial3D:
	var clave := "%s|%.2f|%s|%s" % [nombre, baldosa, tinte.to_html(), mundo]
	if _pbr.has(clave):
		return _pbr[clave]
	var ruta := RAIZ_MATERIALES + nombre + "/"
	var m := StandardMaterial3D.new()
	m.albedo_color = tinte
	m.albedo_texture = load(ruta + "color.png")
	m.normal_enabled = true
	m.normal_texture = load(ruta + "normal.png")
	m.roughness_texture = load(ruta + "roughness.png")
	m.roughness = 1.0
	if ResourceLoader.exists(ruta + "metalness.png"):
		m.metallic_texture = load(ruta + "metalness.png")
		m.metallic = 1.0
	m.uv1_triplanar = true
	m.uv1_world_triplanar = mundo
	m.uv1_scale = Vector3.ONE / baldosa
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	_pbr[clave] = m
	return m


static func material_franjas(color: Color = Color.WHITE, emision: float = 0.0, repeticiones: float = 1.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_texture = TEXTURA_FRANJAS
	m.albedo_color = color
	m.uv1_scale = Vector3(3.0 * repeticiones, 2.0, 1.0)
	m.roughness = 0.6
	if emision > 0.0:
		m.emission_enabled = true
		m.emission_texture = TEXTURA_FRANJAS
		m.emission = color
		m.emission_energy_multiplier = emision
	return m


static func material_destello() -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.albedo_color = Color(1, 1, 1, 0)
	return m


static func halo(padre: Node, posicion: Vector3, tamano: float, color: Color, energia: float = 1.0) -> MeshInstance3D:
	var quad := QuadMesh.new()
	quad.size = Vector2(tamano, tamano)
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.albedo_texture = TEXTURA_HALO
	m.albedo_color = Color(color.r * energia, color.g * energia, color.b * energia, 1.0)
	m.no_depth_test = false
	m.depth_draw_mode = BaseMaterial3D.DEPTH_DRAW_DISABLED
	var instancia := MeshInstance3D.new()
	instancia.mesh = quad
	instancia.material_override = m
	instancia.position = posicion
	instancia.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	padre.add_child(instancia)
	return instancia


static func icono_3d(padre: Node, textura: Texture2D, posicion: Vector3, ancho: float = 6.0, billboard: bool = true, giro_y: float = 0.0) -> Sprite3D:
	var s := Sprite3D.new()
	s.texture = textura
	s.pixel_size = ancho / float(maxi(textura.get_width(), 1))
	s.position = posicion
	s.rotation.y = giro_y
	s.shaded = false
	s.double_sided = true
	s.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	s.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	if billboard:
		s.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	padre.add_child(s)
	return s


static func malla(padre: Node, forma: String, tamano: Vector3, posicion: Vector3, material_aplicado: Material, sombras: bool = true) -> MeshInstance3D:
	var instancia := MeshInstance3D.new()
	match forma:
		"cyl":
			var c := CylinderMesh.new()
			c.top_radius = tamano.x * 0.5
			c.bottom_radius = tamano.x * 0.5
			c.height = tamano.y
			c.radial_segments = 20
			c.rings = 1
			instancia.mesh = c
		"sph":
			var s := SphereMesh.new()
			s.radius = tamano.x * 0.5
			s.height = tamano.x
			s.radial_segments = 20
			s.rings = 10
			instancia.mesh = s
		"cone":
			var k := CylinderMesh.new()
			k.top_radius = 0.0
			k.bottom_radius = tamano.x * 0.5
			k.height = tamano.y
			k.radial_segments = 16
			k.rings = 1
			instancia.mesh = k
		"prism":
			var p := PrismMesh.new()
			p.size = tamano
			instancia.mesh = p
		_:
			var b := BoxMesh.new()
			b.size = tamano
			instancia.mesh = b
	instancia.material_override = material_aplicado
	instancia.position = posicion
	if not sombras:
		instancia.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	padre.add_child(instancia)
	return instancia


static func caja_solida(padre: Node, tamano: Vector3, posicion: Vector3, color: Color, capa: int = 1, visible_: bool = true, material_aplicado: Material = null) -> StaticBody3D:
	var cuerpo := StaticBody3D.new()
	cuerpo.position = posicion
	cuerpo.collision_layer = capa
	cuerpo.collision_mask = 0
	var colision := CollisionShape3D.new()
	var forma := BoxShape3D.new()
	forma.size = tamano
	colision.shape = forma
	cuerpo.add_child(colision)
	if visible_:
		malla(cuerpo, "box", tamano, Vector3.ZERO, material_aplicado if material_aplicado != null else material(color))
	padre.add_child(cuerpo)
	return cuerpo


static func luz_puntual(padre: Node, posicion: Vector3, color: Color, energia: float, rango: float) -> OmniLight3D:
	var luz := OmniLight3D.new()
	luz.position = posicion
	luz.light_color = color
	luz.light_energy = energia
	luz.omni_range = rango
	luz.shadow_enabled = false
	padre.add_child(luz)
	return luz


static func etiqueta(padre: Node, texto: String, posicion: Vector3, pixel: float = 0.05, color: Color = GameColors.BLANCO, giro_y: float = 0.0, billboard: bool = false) -> Label3D:
	var e := Label3D.new()
	e.text = texto
	e.modulate = color
	e.outline_modulate = Color(0.06, 0.06, 0.08)
	e.outline_size = 12
	e.font_size = 64
	e.pixel_size = pixel
	e.position = posicion
	e.rotation.y = giro_y
	if billboard:
		e.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	padre.add_child(e)
	return e


static func decoracion(padre: Node3D, def: Dictionary, posicion: Vector3, giro_y: float = 0.0) -> Node3D:
	var raiz := Node3D.new()
	raiz.position = posicion
	raiz.rotation.y = giro_y
	for parte in def["partes"]:
		malla(raiz, parte[0], parte[1], parte[2], material(parte[3], 0.85, 0.1))
	padre.add_child(raiz)
	return raiz
