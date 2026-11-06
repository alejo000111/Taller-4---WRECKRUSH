@tool
class_name Modelos
extends RefCounted

const RAIZ := "res://assets/models/"
const CATEGORIAS := ["destructibles", "bosses", "world", "skyline", "tools"]
const ENERGIA_NEON := 2.4

static var _rutas: Dictionary = {}
static var _escenas: Dictionary = {}
static var _materiales: Dictionary = {}


static func carpeta(nombre: String) -> String:
	if nombre == "":
		return ""
	if _rutas.has(nombre):
		return _rutas[nombre]
	for categoria in CATEGORIAS:
		var ruta := RAIZ + String(categoria) + "/" + nombre + "/"
		if ResourceLoader.exists(ruta + nombre + ".glb"):
			_rutas[nombre] = ruta
			return ruta
	_rutas[nombre] = ""
	return ""


static func existe(nombre: String) -> bool:
	return carpeta(nombre) != ""


static func instanciar(nombre: String, materiales_unicos: bool = false) -> Node3D:
	var ruta := carpeta(nombre)
	if ruta == "":
		return null
	if not _escenas.has(nombre):
		_escenas[nombre] = load(ruta + nombre + ".glb")
	var modelo := (_escenas[nombre] as PackedScene).instantiate() as Node3D
	modelo.name = nombre
	var roles := _materiales_de(nombre)
	for malla in mallas(modelo):
		var material: StandardMaterial3D = roles.get(String(malla.name), roles.get("Body"))
		if material != null:
			malla.material_override = material.duplicate() if materiales_unicos else material
	return modelo


static func colocar(padre: Node, nombre: String, posicion: Vector3, escala: float = 1.0, giro_y: float = 0.0, sombras: bool = true, materiales_unicos: bool = false) -> Node3D:
	var modelo := instanciar(nombre, materiales_unicos)
	if modelo == null:
		return null
	modelo.position = posicion
	modelo.rotation.y = giro_y
	modelo.scale = Vector3.ONE * escala
	if not sombras:
		for malla in mallas(modelo):
			malla.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	padre.add_child(modelo)
	return modelo


static func mallas(nodo: Node) -> Array[MeshInstance3D]:
	var lista: Array[MeshInstance3D] = []
	if nodo is MeshInstance3D:
		lista.append(nodo)
	for hijo in nodo.get_children():
		lista.append_array(mallas(hijo))
	return lista


static func materiales(nodo: Node) -> Array[StandardMaterial3D]:
	var lista: Array[StandardMaterial3D] = []
	for malla in mallas(nodo):
		var material := malla.material_override as StandardMaterial3D
		if material != null and not lista.has(material):
			lista.append(material)
	return lista


static func material_de(nodo: Node, rol: String) -> StandardMaterial3D:
	for malla in mallas(nodo):
		if String(malla.name) == rol:
			return malla.material_override as StandardMaterial3D
	return null


static func es_superficie(material: Material) -> bool:
	return material != null and String(material.get_meta("tipo", "surface")) == "surface"


static func es_neon(material: Material) -> bool:
	return material != null and String(material.get_meta("tipo", "")) == "neon"


static func limites(nodo: Node3D) -> AABB:
	var total := AABB()
	var primero := true
	for malla in mallas(nodo):
		var transformacion := Transform3D.IDENTITY
		var actual: Node = malla
		while actual != null and actual != nodo:
			transformacion = (actual as Node3D).transform * transformacion
			actual = actual.get_parent()
		var caja := transformacion * malla.get_aabb()
		if primero:
			total = caja
			primero = false
		else:
			total = total.merge(caja)
	return total


static func encajar(modelo: Node3D, caja: Vector3, uniforme: bool = true, centrado_y: bool = false) -> Vector3:
	var l := limites(modelo)
	var tamano := Vector3(maxf(l.size.x, 0.001), maxf(l.size.y, 0.001), maxf(l.size.z, 0.001))
	var escala := caja / tamano
	if uniforme:
		var minima := minf(escala.x, minf(escala.y, escala.z))
		escala = Vector3.ONE * minima
	modelo.scale = escala
	var centro := l.get_center()
	var base_y := -centro.y if centrado_y else -l.position.y
	modelo.position = Vector3(-centro.x * escala.x, base_y * escala.y, -centro.z * escala.z)
	return escala


static func pintar_neon(nodo: Node, color: Color, energia: float = ENERGIA_NEON) -> void:
	for material in materiales(nodo):
		if es_neon(material):
			material.albedo_color = Color(color, material.albedo_color.a)
			material.emission = color
			material.emission_energy_multiplier = energia


static func _materiales_de(nombre: String) -> Dictionary:
	if _materiales.has(nombre):
		return _materiales[nombre]
	var ruta := carpeta(nombre)
	var manifiesto := _manifiesto(ruta + "manifest.json")
	var texturas: Dictionary = manifiesto.get("textures", {})
	var roles: Dictionary = manifiesto.get("roles", {})
	var resultado := {}
	for rol in roles:
		resultado[rol] = _material_rol(roles[rol], ruta, texturas)
	if not resultado.has("Body"):
		resultado["Body"] = _material_rol({}, ruta, texturas)
	_materiales[nombre] = resultado
	return resultado


static func _manifiesto(ruta: String) -> Dictionary:
	if ResourceLoader.exists(ruta):
		var recurso := load(ruta) as JSON
		if recurso != null and recurso.data is Dictionary:
			return recurso.data
	var datos: Variant = JSON.parse_string(FileAccess.get_file_as_string(ruta))
	return datos if datos is Dictionary else {}


static func _textura(ruta: String, texturas: Dictionary, clave: String) -> Texture2D:
	if not texturas.has(clave):
		return null
	var archivo := ruta + String(texturas[clave])
	return load(archivo) as Texture2D if ResourceLoader.exists(archivo) else null


static func _material_rol(rol: Dictionary, ruta: String, texturas: Dictionary) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	var c: Array = rol.get("color", [255, 255, 255])
	var color := Color8(int(c[0]), int(c[1]), int(c[2]))
	var tipo := String(rol.get("kind", "surface"))
	var transparencia := float(rol.get("transparency", 0.0))
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	m.albedo_color = color
	if tipo == "neon":
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = ENERGIA_NEON
		m.roughness = 0.35
	else:
		m.albedo_texture = _textura(ruta, texturas, "color")
		var normal := _textura(ruta, texturas, "normal")
		if normal != null:
			m.normal_enabled = true
			m.normal_texture = normal
		var rugosidad := _textura(ruta, texturas, "roughness")
		if rugosidad != null and tipo != "glass":
			m.roughness_texture = rugosidad
			m.roughness = 1.0
		else:
			m.roughness = 0.08 if tipo == "glass" else 0.8
		var metal := _textura(ruta, texturas, "metalness")
		if metal != null:
			m.metallic_texture = metal
			m.metallic = 1.0
		if tipo == "glass":
			m.metallic_specular = 0.9
	if transparencia > 0.0:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.albedo_color.a = clampf(1.0 - transparencia, 0.3, 1.0)
	m.set_meta("tipo", tipo)
	return m
