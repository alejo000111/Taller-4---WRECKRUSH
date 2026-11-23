extends Node

const TASA := 22050
const VOCES := 10

var _sonidos: Dictionary = {}
var _voces: Array[AudioStreamPlayer] = []
var _siguiente: int = 0
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.seed = 7
	for i in VOCES:
		var voz := AudioStreamPlayer.new()
		voz.bus = &"Master"
		add_child(voz)
		_voces.append(voz)
	_sonidos["golpe"] = _crear(0.12, func(t: float, d: float) -> float:
		return (_rng.randf_range(-1.0, 1.0) * 0.5 + sin(TAU * 150.0 * t) * 0.8) * pow(1.0 - t / d, 2.0))
	_sonidos["critico"] = _crear(0.2, func(t: float, d: float) -> float:
		return (_rng.randf_range(-1.0, 1.0) * 0.4 + sin(TAU * (260.0 + 700.0 * t) * t) * 0.7) * pow(1.0 - t / d, 1.6))
	_sonidos["romper"] = _crear(0.38, func(t: float, d: float) -> float:
		return (_rng.randf_range(-1.0, 1.0) * 0.8 + sin(TAU * 70.0 * t) * 0.6) * pow(1.0 - t / d, 2.2))
	_sonidos["orbe"] = _crear(0.09, func(t: float, d: float) -> float:
		return sin(TAU * (880.0 + 5000.0 * t) * t) * 0.45 * (1.0 - t / d))
	_sonidos["comprar"] = _crear(0.3, func(t: float, d: float) -> float:
		var nota := 523.0 if t < 0.1 else (659.0 if t < 0.2 else 784.0)
		return sin(TAU * nota * t) * 0.4 * (1.0 - t / d))
	_sonidos["error"] = _crear(0.16, func(t: float, d: float) -> float:
		return sign(sin(TAU * 110.0 * t)) * 0.3 * (1.0 - t / d))
	_sonidos["aviso"] = _crear(0.22, func(t: float, d: float) -> float:
		return sin(TAU * 440.0 * t) * 0.4 * (1.0 - t / d))
	_sonidos["jefe"] = _crear(0.6, func(t: float, d: float) -> float:
		return (_rng.randf_range(-1.0, 1.0) * 0.5 + sin(TAU * 48.0 * t) * 0.9) * pow(1.0 - t / d, 1.8))
	_sonidos["victoria"] = _crear(0.7, func(t: float, d: float) -> float:
		var nota := 523.0 if t < 0.15 else (659.0 if t < 0.3 else (784.0 if t < 0.45 else 1047.0))
		return sin(TAU * nota * t) * 0.4 * (1.0 - t / d))


func reproducir(nombre: String, volumen_db: float = 0.0, tono: float = 1.0) -> void:
	if not GameState.ajustes.get("sfx", true):
		return
	if not _sonidos.has(nombre) or _voces.is_empty():
		return
	var voz := _voces[_siguiente]
	_siguiente = (_siguiente + 1) % _voces.size()
	voz.stream = _sonidos[nombre]
	voz.volume_db = volumen_db
	voz.pitch_scale = tono
	voz.play()


func _crear(duracion: float, generador: Callable) -> AudioStreamWAV:
	var muestras := int(duracion * TASA)
	var bytes := PackedByteArray()
	bytes.resize(muestras * 2)
	for i in muestras:
		var t := float(i) / TASA
		var valor := clampf(float(generador.call(t, duracion)), -1.0, 1.0)
		bytes.encode_s16(i * 2, int(valor * 30000.0))
	var flujo := AudioStreamWAV.new()
	flujo.format = AudioStreamWAV.FORMAT_16_BITS
	flujo.mix_rate = TASA
	flujo.stereo = false
	flujo.data = bytes
	return flujo
