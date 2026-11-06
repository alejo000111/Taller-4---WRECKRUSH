class_name BasePanel
extends Control

signal cerrado

var titulo: String = "PANEL"
var color_titulo: Color = GameColors.NARANJA
var ancho: float = 760.0
var icono: Texture2D
var abierto: bool = false

var contenido: VBoxContainer
var _ventana: PanelContainer


func _init(titulo_: String = "PANEL", color_: Color = GameColors.NARANJA, ancho_: float = 760.0, icono_: Texture2D = null) -> void:
	titulo = titulo_
	color_titulo = color_
	ancho = ancho_
	icono = icono_


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	visible = false
	mouse_filter = Control.MOUSE_FILTER_STOP
	var fondo := ColorRect.new()
	fondo.color = Color(0, 0, 0, 0.55)
	fondo.set_anchors_preset(Control.PRESET_FULL_RECT)
	fondo.gui_input.connect(_clic_fondo)
	add_child(fondo)
	var centro := CenterContainer.new()
	centro.set_anchors_preset(Control.PRESET_FULL_RECT)
	centro.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(centro)
	_ventana = PanelContainer.new()
	_ventana.custom_minimum_size = Vector2(ancho, 0)
	_ventana.add_theme_stylebox_override("panel", UIKit.estilo(GameColors.GRIS_OSCURO, color_titulo, 16, 4, 18))
	centro.add_child(_ventana)
	var raiz := VBoxContainer.new()
	raiz.add_theme_constant_override("separation", 10)
	_ventana.add_child(raiz)
	var cabecera := HBoxContainer.new()
	cabecera.add_theme_constant_override("separation", 10)
	if icono != null:
		cabecera.add_child(UIKit.icono(icono, 44))
	var t := UIKit.etiqueta(titulo, 30, color_titulo)
	t.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	cabecera.add_child(t)
	var cerrar_btn := UIKit.boton("", GameColors.ROJO, Vector2(44, 40), 20)
	UIKit.poner_icono(cerrar_btn, Iconos.CERRAR, 24)
	cerrar_btn.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
	cerrar_btn.pressed.connect(cerrar)
	cabecera.add_child(cerrar_btn)
	raiz.add_child(cabecera)
	contenido = VBoxContainer.new()
	contenido.add_theme_constant_override("separation", 8)
	raiz.add_child(contenido)
	construir()


func construir() -> void:
	pass


func refrescar() -> void:
	pass


func abrir() -> void:
	if abierto:
		return
	abierto = true
	visible = true
	GameState.abrir_panel()
	refrescar()
	_ventana.pivot_offset = _ventana.size * 0.5
	_ventana.scale = Vector2(0.92, 0.92)
	modulate.a = 0.0
	var t := create_tween().set_parallel(true)
	t.tween_property(_ventana, "scale", Vector2.ONE, 0.14).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	t.tween_property(self, "modulate:a", 1.0, 0.12)


func cerrar() -> void:
	if not abierto:
		return
	abierto = false
	visible = false
	GameState.cerrar_panel()
	cerrado.emit()


func _clic_fondo(evento: InputEvent) -> void:
	if evento is InputEventMouseButton and evento.pressed:
		cerrar()


func _unhandled_input(evento: InputEvent) -> void:
	if abierto and evento.is_action_pressed("close_panel"):
		cerrar()
		get_viewport().set_input_as_handled()


func limpiar(nodo: Node) -> void:
	for hijo in nodo.get_children():
		hijo.queue_free()
