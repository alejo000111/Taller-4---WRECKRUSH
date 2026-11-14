class_name UIKit
extends RefCounted


static func estilo(color: Color, borde: Color = Color.TRANSPARENT, radio: int = 10, grosor: int = 0, margen: int = 0) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = color
	s.border_color = borde
	s.set_border_width_all(grosor)
	s.set_corner_radius_all(radio)
	s.set_content_margin_all(margen)
	return s


static func etiqueta(texto: String, tamano: int = 18, color: Color = GameColors.BLANCO, alineacion: HorizontalAlignment = HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var e := Label.new()
	e.text = texto
	e.add_theme_font_size_override("font_size", tamano)
	e.add_theme_color_override("font_color", color)
	e.add_theme_color_override("font_outline_color", Color(0.05, 0.05, 0.07))
	e.add_theme_constant_override("outline_size", 4 if tamano >= 20 else 2)
	e.horizontal_alignment = alineacion
	e.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return e


static func boton(texto: String, color: Color = GameColors.NARANJA, tamano: Vector2 = Vector2(120, 44), fuente: int = 18) -> Button:
	var b := Button.new()
	b.text = texto
	b.custom_minimum_size = tamano
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_font_size_override("font_size", fuente)
	b.add_theme_color_override("font_color", Color.WHITE)
	b.add_theme_color_override("font_hover_color", Color.WHITE)
	b.add_theme_color_override("font_pressed_color", Color.WHITE)
	b.add_theme_color_override("font_disabled_color", Color(0.62, 0.64, 0.68))
	b.add_theme_stylebox_override("normal", estilo(color, color.darkened(0.45), 10, 3))
	b.add_theme_stylebox_override("hover", estilo(color.lightened(0.18), color.darkened(0.3), 10, 3))
	b.add_theme_stylebox_override("pressed", estilo(color.darkened(0.2), color.darkened(0.55), 10, 3))
	b.add_theme_stylebox_override("disabled", estilo(Color("#454A54"), Color("#353941"), 10, 3))
	b.add_theme_stylebox_override("focus", estilo(Color.TRANSPARENT, Color.WHITE, 10, 4))
	return b


static func activar_foco(raiz: Node, preferido: Button = null) -> void:
	var botones: Array[Button] = []
	_recoger_botones(raiz, botones)
	var elegido := preferido
	for b in botones:
		b.focus_mode = Control.FOCUS_ALL
		if elegido == null and not b.disabled and not b.has_meta("sin_foco_inicial"):
			elegido = b
	if elegido == null and not botones.is_empty():
		elegido = botones[0]
	if elegido != null and elegido.is_visible_in_tree():
		elegido.grab_focus()


static func _recoger_botones(nodo: Node, lista: Array[Button]) -> void:
	for hijo in nodo.get_children():
		if hijo.is_queued_for_deletion():
			continue
		if hijo is Button:
			lista.append(hijo)
		_recoger_botones(hijo, lista)


static func barra(color: Color, tamano: Vector2) -> ProgressBar:
	var b := ProgressBar.new()
	b.custom_minimum_size = tamano
	b.show_percentage = false
	b.min_value = 0.0
	b.max_value = 1.0
	b.step = 0.0001
	b.mouse_filter = Control.MOUSE_FILTER_IGNORE
	b.add_theme_stylebox_override("background", estilo(Color(0.08, 0.09, 0.11, 0.9), Color(0, 0, 0, 0.6), 6, 2))
	b.add_theme_stylebox_override("fill", estilo(color, Color.TRANSPARENT, 5, 0))
	return b


static func tarjeta(color: Color = Color("#353A44")) -> PanelContainer:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", estilo(color, Color("#22252B"), 12, 2, 12))
	return p


static func punto_rojo() -> Panel:
	var p := Panel.new()
	p.custom_minimum_size = Vector2(16, 16)
	p.size = Vector2(16, 16)
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p.add_theme_stylebox_override("panel", estilo(GameColors.ROJO, Color.WHITE, 8, 2))
	return p


static func icono(textura: Texture2D, tamano: float = 32.0) -> TextureRect:
	var t := TextureRect.new()
	t.texture = textura
	t.custom_minimum_size = Vector2(tamano, tamano)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	t.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return t


static func con_icono(textura: Texture2D, control: Control, tamano: float = 28.0, separacion: int = 8, centrado: bool = false) -> HBoxContainer:
	var fila := HBoxContainer.new()
	fila.add_theme_constant_override("separation", separacion)
	fila.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if centrado:
		fila.alignment = BoxContainer.ALIGNMENT_CENTER
	fila.add_child(icono(textura, tamano))
	fila.add_child(control)
	return fila


static func poner_icono(boton: Button, textura: Texture2D, ancho: int = 28) -> void:
	boton.icon = textura
	boton.expand_icon = true
	boton.add_theme_constant_override("icon_max_width", ancho)
	boton.add_theme_constant_override("h_separation", 8)


static func separador(alto: int = 8) -> Control:
	var c := Control.new()
	c.custom_minimum_size = Vector2(0, alto)
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return c
