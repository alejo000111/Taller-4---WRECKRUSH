@tool
class_name BossPart
extends StaticBody3D

signal golpeada(parte: BossPart)
signal destruida(parte: BossPart)

var tipo: String = "placa"
var vida_max: float = 100.0
var vida: float = 100.0
var caja: Vector3 = Vector3(2, 2, 2)
var color_principal: Color = Color("#6B7078")
var modelo: String = ""
var giro_modelo: float = 0.0
var vulnerable: bool = false
var roto: bool = false

var _visual: Node3D
var _superficies: Array[StandardMaterial3D] = []
var _brillos: Array[StandardMaterial3D] = []
var _mallas: Array[MeshInstance3D] = []
var _destello: StandardMaterial3D
var _contorno: ShaderMaterial
var _luz: OmniLight3D
var _halo: MeshInstance3D
var _colision: CollisionShape3D
var _tween: Tween


static func crear(tipo_: String, tamano: Vector3, vida_: float, color: Color, modelo_: String = "", giro_: float = 0.0) -> BossPart:
	var p := BossPart.new()
	p.tipo = tipo_
	p.caja = tamano
	p.vida_max = vida_
	p.vida = vida_
	p.color_principal = color
	p.modelo = modelo_
	p.giro_modelo = giro_
	return p


func _ready() -> void:
	add_to_group("golpeables")
	collision_layer = 8
	collision_mask = 0
	_contorno = Formas.material_contorno(GameColors.AMARILLO, 0.35)
	_destello = Formas.material_destello()
	_visual = Node3D.new()
	_visual.rotation.y = giro_modelo
	add_child(_visual)
	var instancia := Modelos.instanciar(modelo, true)
	if instancia != null:
		_visual.add_child(instancia)
		var girado := absf(sin(giro_modelo)) > 0.5
		var caja_local := Vector3(caja.z, caja.y, caja.x) if girado else caja
		var escala := Modelos.encajar(instancia, caja_local, tipo == "nucleo", true)
		_contorno.set_shader_parameter("grosor", 0.35 / maxf(minf(escala.x, escala.y), 0.01))
		for material in Modelos.materiales(instancia):
			if Modelos.es_superficie(material):
				material.next_pass = _contorno
				_superficies.append(material)
			elif Modelos.es_neon(material):
				_brillos.append(material)
	else:
		var material := Formas.material(color_principal, 0.6, 0.5)
		material.next_pass = _contorno
		_superficies.append(material)
		if tipo == "nucleo":
			_brillos.append(material)
		Formas.malla(_visual, "sph" if tipo == "nucleo" else "box", caja, Vector3.ZERO, material)
	_mallas = Modelos.mallas(_visual)
	if tipo == "nucleo":
		_luz = Formas.luz_puntual(self, Vector3.ZERO, GameColors.AMARILLO, 0.0, 28.0)
		_halo = Formas.halo(self, Vector3.ZERO, caja.x * 2.8, GameColors.AMARILLO, 0.9)
	_colision = CollisionShape3D.new()
	var forma := BoxShape3D.new()
	forma.size = caja
	_colision.shape = forma
	add_child(_colision)
	_aplicar_estado()


func puede_ser_golpeado() -> bool:
	return vulnerable and not roto


func distancia_a(punto: Vector3) -> float:
	var local := to_local(punto)
	var mitad := caja * 0.5
	var cercano := Vector3(clampf(local.x, -mitad.x, mitad.x), clampf(local.y, -mitad.y, mitad.y), clampf(local.z, -mitad.z, mitad.z))
	return local.distance_to(cercano)


func proporcion() -> float:
	return vida / vida_max


func establecer_vulnerable(valor: bool) -> void:
	vulnerable = valor
	_aplicar_estado()


func reiniciar(curar: bool = true) -> void:
	roto = false
	if curar:
		vida = vida_max
	visible = true
	if _colision != null:
		_colision.set_deferred("disabled", false)
	_aplicar_estado()


func recibir_golpe(dano: float, critico: bool = false) -> bool:
	if not puede_ser_golpeado():
		return false
	var aplicado := dano
	vida = maxf(vida - aplicado, 0.0)
	_parpadear()
	Fx.golpe(self, aplicado, critico)
	golpeada.emit(self)
	if vida <= 0.0:
		roto = true
		_colision.set_deferred("disabled", true)
		Fx.romper(self, "Large" if tipo == "placa" else "Huge")
		visible = false
		vulnerable = false
		destruida.emit(self)
		return true
	return false


func _aplicar_estado() -> void:
	if _contorno == null:
		return
	_contorno.set_shader_parameter("opacidad", 1.0 if puede_ser_golpeado() else 0.0)
	var color := GameColors.NARANJA
	var energia := 2.4 if vulnerable else 0.5
	if tipo == "nucleo":
		color = GameColors.AMARILLO if vulnerable else GameColors.ROJO
		energia = 3.0 if vulnerable else 0.6
		_luz.light_energy = 3.0 if vulnerable else 0.0
		_halo.visible = vulnerable
	for material in _brillos:
		material.emission_enabled = true
		material.albedo_color = color
		material.emission = color
		material.emission_energy_multiplier = energia


func _parpadear() -> void:
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_fijar_destello(true)
	_destello.albedo_color.a = 0.85
	_tween = create_tween()
	_tween.tween_property(_destello, "albedo_color:a", 0.0, 0.15)
	_tween.tween_callback(_fijar_destello.bind(false))


func _fijar_destello(activo: bool) -> void:
	for malla in _mallas:
		malla.material_overlay = _destello if activo else null
