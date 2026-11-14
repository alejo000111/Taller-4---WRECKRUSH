class_name Hud
extends CanvasLayer

var jugador: Player
var paneles: Dictionary = {}

var _dano: Label
var _ritmo: Label
var _scrap: Label
var _meta_texto: Label
var _meta_barra: ProgressBar
var _punto_mejoras: Panel
var _boton_mejoras: Button
var _contenedor_jefe: PanelContainer
var _jefe_nombre: Label
var _jefe_barra: ProgressBar
var _jefe_objetivo: Label
var _toasts: VBoxContainer
var _aviso: PanelContainer
var _aviso_texto: Label
var _aviso_barra: ProgressBar
var _casillas: Array[Button] = []
var _vida: ProgressBar
var _muerte: ColorRect
var _muerte_texto: Label
var _tutorial: PanelContainer
var _tutorial_titulo: Label
var _tutorial_texto: Label
var _tutorial_paso: Label
var _victoria: Control
var _victoria_insignia: TextureRect
var _victoria_titulo: Label
var _victoria_texto: Label
var _fps: Label


func _ready() -> void:
	layer = 5
	_construir_perfil()
	_construir_menu()
	_construir_centro()
	_construir_inferior()
	_construir_tutorial()
	_construir_superposiciones()
	_construir_paneles()
	_construir_portada()
	GameState.scrap_cambio.connect(func(_v: int) -> void: _refrescar_recursos())
	GameState.mejora_comprada.connect(func(_i: String, _n: int) -> void: _refrescar_recursos())
	GameState.toast.connect(mostrar_toast)
	GameState.prompt_cambio.connect(_al_cambiar_prompt)
	GameState.boss_estado.connect(_al_estado_jefe)
	GameState.tutorial_cambio.connect(func(_p: int) -> void: _refrescar_tutorial())
	GameState.coloso_vencido.connect(_mostrar_coloso_vencido)
	GameState.maestria_terminada.connect(_mostrar_maestria)
	GameState.juego_completado.connect(_mostrar_final)
	_refrescar_todo()


func _process(_delta: float) -> void:
	var meta := GameState.siguiente_meta()
	_meta_texto.text = _texto_meta(meta)
	_meta_barra.value = clampf(float(meta["actual"]) / maxf(float(meta["meta"]), 1.0), 0.0, 1.0)
	_punto_mejoras.visible = GameState.hay_mejora_asequible()
	_fps.text = "%d FPS" % Engine.get_frames_per_second()
	if jugador != null:
		_vida.visible = jugador.salud < GameConfig.VIDA_JUGADOR and not jugador.muerto
		_vida.value = jugador.salud / GameConfig.VIDA_JUGADOR


func _texto_meta(meta: Dictionary) -> String:
	if meta["listo"]:
		return "READY: %s" % meta["texto"]
	return "NEXT: %s  %s/%s" % [meta["texto"], Formulas.abreviar(meta["actual"]), Formulas.abreviar(meta["meta"])]


func _construir_perfil() -> void:
	var caja := PanelContainer.new()
	caja.position = Vector2(16, 14)
	caja.add_theme_stylebox_override("panel", UIKit.estilo(Color(0.17, 0.18, 0.21, 0.88), GameColors.NARANJA, 12, 3, 10))
	caja.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 4)
	_dano = UIKit.etiqueta("", 20, GameColors.AMARILLO)
	col.add_child(UIKit.con_icono(Iconos.DANO, _dano, 30))
	_ritmo = UIKit.etiqueta("", 15, Color("#B8BDC8"))
	col.add_child(UIKit.con_icono(Iconos.VELOCIDAD, _ritmo, 24, 11))
	caja.add_child(col)
	add_child(caja)


func _construir_menu() -> void:
	var col := VBoxContainer.new()
	col.position = Vector2(16, 98)
	col.add_theme_constant_override("separation", 8)
	add_child(col)
	_boton_mejoras = _boton_menu(col, "UPGRADES [U]", GameColors.AMARILLO.darkened(0.25), "upgrades", Iconos.MEJORAS)
	_punto_mejoras = UIKit.punto_rojo()
	_punto_mejoras.position = Vector2(-6, -6)
	_boton_mejoras.add_child(_punto_mejoras)
	_boton_menu(col, "SETTINGS [TAB]", GameColors.CIAN.darkened(0.45), "settings", Iconos.AJUSTES)


func _boton_menu(padre: Control, texto: String, color: Color, panel: String, icono: Texture2D) -> Button:
	var b := UIKit.boton(texto, color, Vector2(210, 48), 17)
	UIKit.poner_icono(b, icono, 34)
	b.pressed.connect(func() -> void: abrir_panel(panel))
	padre.add_child(b)
	return b


func _construir_centro() -> void:
	var raiz := VBoxContainer.new()
	raiz.set_anchors_preset(Control.PRESET_CENTER_TOP)
	raiz.anchor_left = 0.5
	raiz.anchor_right = 0.5
	raiz.offset_left = -260
	raiz.offset_right = 260
	raiz.offset_top = 12
	raiz.add_theme_constant_override("separation", 6)
	raiz.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(raiz)
	var recursos := HBoxContainer.new()
	recursos.alignment = BoxContainer.ALIGNMENT_CENTER
	recursos.add_theme_constant_override("separation", 12)
	recursos.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_scrap = _pildora(recursos, "SCRAP 0", GameColors.AMARILLO, Iconos.SCRAP)
	raiz.add_child(recursos)
	var meta := PanelContainer.new()
	meta.add_theme_stylebox_override("panel", UIKit.estilo(Color(0.17, 0.18, 0.21, 0.85), GameColors.AMARILLO.darkened(0.3), 10, 2, 6))
	meta.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var metacol := VBoxContainer.new()
	_meta_texto = UIKit.etiqueta("", 17, GameColors.AMARILLO, HORIZONTAL_ALIGNMENT_CENTER)
	metacol.add_child(UIKit.con_icono(Iconos.FLECHA, _meta_texto, 20, 6, true))
	_meta_barra = UIKit.barra(GameColors.AMARILLO, Vector2(0, 10))
	metacol.add_child(_meta_barra)
	meta.add_child(metacol)
	raiz.add_child(meta)
	_contenedor_jefe = PanelContainer.new()
	_contenedor_jefe.visible = false
	_contenedor_jefe.add_theme_stylebox_override("panel", UIKit.estilo(Color(0.2, 0.08, 0.08, 0.9), GameColors.ROJO, 10, 3, 8))
	_contenedor_jefe.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var jefecol := VBoxContainer.new()
	_jefe_nombre = UIKit.etiqueta("COLOSSUS", 20, GameColors.ROJO, HORIZONTAL_ALIGNMENT_CENTER)
	jefecol.add_child(UIKit.con_icono(Iconos.JEFE, _jefe_nombre, 36, 8, true))
	_jefe_barra = UIKit.barra(GameColors.ROJO, Vector2(0, 18))
	jefecol.add_child(_jefe_barra)
	_jefe_objetivo = UIKit.etiqueta("", 16, GameColors.BLANCO, HORIZONTAL_ALIGNMENT_CENTER)
	jefecol.add_child(_jefe_objetivo)
	_contenedor_jefe.add_child(jefecol)
	raiz.add_child(_contenedor_jefe)
	_toasts = VBoxContainer.new()
	_toasts.add_theme_constant_override("separation", 4)
	_toasts.mouse_filter = Control.MOUSE_FILTER_IGNORE
	raiz.add_child(_toasts)


func _pildora(padre: Control, texto: String, color: Color, icono: Texture2D) -> Label:
	var caja := PanelContainer.new()
	caja.add_theme_stylebox_override("panel", UIKit.estilo(Color(0.12, 0.13, 0.16, 0.9), color, 18, 3, 6))
	caja.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var e := UIKit.etiqueta(texto, 24, color)
	caja.add_child(UIKit.con_icono(icono, e, 36))
	padre.add_child(caja)
	return e


func _construir_inferior() -> void:
	var barra := HBoxContainer.new()
	barra.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	barra.anchor_left = 0.5
	barra.anchor_right = 0.5
	barra.offset_left = -95
	barra.offset_right = 95
	barra.offset_top = -86
	barra.offset_bottom = -16
	barra.alignment = BoxContainer.ALIGNMENT_CENTER
	barra.add_theme_constant_override("separation", 8)
	add_child(barra)
	var b := UIKit.boton("", Color("#2B2F36"), Vector2(180, 66), 14)
	UIKit.poner_icono(b, Iconos.cargar(String(GameConfig.MARTILLO["icono"])), 48)
	b.disabled = false
	barra.add_child(b)
	_casillas.append(b)
	_aviso = PanelContainer.new()
	_aviso.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	_aviso.anchor_left = 0.5
	_aviso.anchor_right = 0.5
	_aviso.offset_left = -190
	_aviso.offset_right = 190
	_aviso.offset_top = -156
	_aviso.offset_bottom = -100
	_aviso.visible = false
	_aviso.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_aviso.add_theme_stylebox_override("panel", UIKit.estilo(Color(0.12, 0.13, 0.16, 0.92), GameColors.AMARILLO, 12, 3, 8))
	var avisocol := VBoxContainer.new()
	_aviso_texto = UIKit.etiqueta("", 20, GameColors.BLANCO, HORIZONTAL_ALIGNMENT_CENTER)
	avisocol.add_child(_aviso_texto)
	_aviso_barra = UIKit.barra(GameColors.AMARILLO, Vector2(0, 8))
	avisocol.add_child(_aviso_barra)
	_aviso.add_child(avisocol)
	add_child(_aviso)
	var wreck := UIKit.boton("WRECK", GameColors.NARANJA, Vector2(170, 110), 24)
	UIKit.poner_icono(wreck, Iconos.WRECK, 64)
	wreck.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
	wreck.vertical_icon_alignment = VERTICAL_ALIGNMENT_TOP
	wreck.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	wreck.anchor_left = 1.0
	wreck.anchor_top = 1.0
	wreck.anchor_right = 1.0
	wreck.anchor_bottom = 1.0
	wreck.offset_left = -196
	wreck.offset_top = -136
	wreck.offset_right = -26
	wreck.offset_bottom = -26
	wreck.button_down.connect(func() -> void: GameState.boton_wreck = true)
	wreck.button_up.connect(func() -> void: GameState.boton_wreck = false)
	add_child(wreck)
	_vida = UIKit.barra(GameColors.ROJO, Vector2(260, 18))
	_vida.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	_vida.anchor_top = 1.0
	_vida.anchor_bottom = 1.0
	_vida.offset_left = 20
	_vida.offset_top = -44
	_vida.offset_right = 280
	_vida.offset_bottom = -26
	_vida.max_value = 1.0
	_vida.visible = false
	add_child(_vida)
	_fps = UIKit.etiqueta("", 13, Color("#8A909C"), HORIZONTAL_ALIGNMENT_RIGHT)
	_fps.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_fps.anchor_left = 1.0
	_fps.anchor_right = 1.0
	_fps.offset_left = -90
	_fps.offset_top = 4
	_fps.offset_right = -8
	add_child(_fps)


func _construir_tutorial() -> void:
	_tutorial = PanelContainer.new()
	_tutorial.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	_tutorial.anchor_left = 1.0
	_tutorial.anchor_right = 1.0
	_tutorial.offset_left = -330
	_tutorial.offset_right = -16
	_tutorial.offset_top = 30
	_tutorial.add_theme_stylebox_override("panel", UIKit.estilo(Color(0.17, 0.18, 0.21, 0.92), GameColors.AMARILLO, 12, 3, 12))
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 4)
	_tutorial_paso = UIKit.etiqueta("", 14, Color("#8A909C"))
	col.add_child(_tutorial_paso)
	_tutorial_titulo = UIKit.etiqueta("", 22, GameColors.AMARILLO)
	col.add_child(UIKit.con_icono(Iconos.FLECHA, _tutorial_titulo, 24))
	_tutorial_texto = UIKit.etiqueta("", 16)
	_tutorial_texto.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_tutorial_texto.custom_minimum_size = Vector2(290, 0)
	col.add_child(_tutorial_texto)
	var saltar := UIKit.boton("SKIP", Color("#4A505C"), Vector2(90, 32), 14)
	saltar.pressed.connect(GameState.saltar_tutorial)
	col.add_child(saltar)
	_tutorial.add_child(col)
	add_child(_tutorial)


func _construir_superposiciones() -> void:
	_muerte = ColorRect.new()
	_muerte.color = Color(0.3, 0.02, 0.02, 0.55)
	_muerte.set_anchors_preset(Control.PRESET_FULL_RECT)
	_muerte.visible = false
	_muerte.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_muerte_texto = UIKit.etiqueta("", 46, GameColors.BLANCO, HORIZONTAL_ALIGNMENT_CENTER)
	_muerte_texto.set_anchors_preset(Control.PRESET_FULL_RECT)
	_muerte_texto.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_muerte.add_child(_muerte_texto)
	add_child(_muerte)
	_victoria = Control.new()
	_victoria.set_anchors_preset(Control.PRESET_FULL_RECT)
	_victoria.visible = false
	var fondo := ColorRect.new()
	fondo.color = Color(0, 0, 0, 0.6)
	fondo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_victoria.add_child(fondo)
	var centro := CenterContainer.new()
	centro.set_anchors_preset(Control.PRESET_FULL_RECT)
	_victoria.add_child(centro)
	var tarjeta := PanelContainer.new()
	tarjeta.add_theme_stylebox_override("panel", UIKit.estilo(GameColors.GRIS_OSCURO, GameColors.AMARILLO, 18, 5, 26))
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", 10)
	_victoria_insignia = UIKit.icono(Iconos.INSIGNIA_COLOSO, 128)
	_victoria_insignia.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	col.add_child(_victoria_insignia)
	_victoria_titulo = UIKit.etiqueta("", 36, GameColors.AMARILLO, HORIZONTAL_ALIGNMENT_CENTER)
	col.add_child(_victoria_titulo)
	_victoria_texto = UIKit.etiqueta("", 22, GameColors.BLANCO, HORIZONTAL_ALIGNMENT_CENTER)
	col.add_child(_victoria_texto)
	var seguir := UIKit.boton("CONTINUE", GameColors.NARANJA, Vector2(240, 52), 22)
	seguir.pressed.connect(func() -> void:
		_victoria.visible = false
		GameState.cerrar_panel())
	col.add_child(seguir)
	tarjeta.add_child(col)
	centro.add_child(tarjeta)
	add_child(_victoria)


func _construir_portada() -> void:
	var portada := Control.new()
	portada.set_anchors_preset(Control.PRESET_FULL_RECT)
	portada.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var fondo := TextureRect.new()
	fondo.texture = Iconos.FONDO_CARGA
	fondo.set_anchors_preset(Control.PRESET_FULL_RECT)
	fondo.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	fondo.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	fondo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	portada.add_child(fondo)
	var centro := CenterContainer.new()
	centro.set_anchors_preset(Control.PRESET_FULL_RECT)
	centro.mouse_filter = Control.MOUSE_FILTER_IGNORE
	portada.add_child(centro)
	var logo := UIKit.icono(Iconos.LOGO, 0)
	logo.custom_minimum_size = Vector2(720, 360)
	centro.add_child(logo)
	add_child(portada)
	var t := portada.create_tween()
	t.tween_interval(1.4)
	t.tween_property(portada, "modulate:a", 0.0, 0.6)
	t.tween_callback(portada.queue_free)


func _construir_paneles() -> void:
	paneles["upgrades"] = UpgradesPanel.new()
	paneles["settings"] = SettingsPanel.new()
	for id in ["downtown", "industrial"]:
		var panel := UnlockPanel.new()
		panel.zona = id
		paneles["unlock_" + id] = panel
	for panel in paneles.values():
		add_child(panel)


func abrir_panel(nombre: String) -> void:
	if not paneles.has(nombre):
		return
	for otro in paneles.values():
		if otro != paneles[nombre] and otro.abierto:
			otro.cerrar()
	paneles[nombre].abrir()
	if nombre == "upgrades" and GameState.tutorial_paso == 3:
		GameState.toast.emit("BUY DAMAGE", "good")


func _unhandled_input(evento: InputEvent) -> void:
	if evento.is_action_pressed("open_upgrades"):
		_alternar("upgrades")
	elif evento.is_action_pressed("open_settings"):
		_alternar("settings")


func _alternar(nombre: String) -> void:
	if paneles[nombre].abierto:
		paneles[nombre].cerrar()
	else:
		abrir_panel(nombre)


func mostrar_toast(texto: String, tipo: String = "neutral") -> void:
	var color := GameColors.BLANCO
	var borde := Color("#8A909C")
	if tipo == "good":
		color = Color("#9CF0A8")
		borde = Color("#4C8A5A")
	elif tipo == "bad":
		color = Color("#FF9A9A")
		borde = GameColors.ROJO
	var caja := PanelContainer.new()
	caja.add_theme_stylebox_override("panel", UIKit.estilo(Color(0.1, 0.11, 0.14, 0.92), borde, 10, 2, 6))
	caja.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var etiqueta := UIKit.etiqueta(texto, 20, color, HORIZONTAL_ALIGNMENT_CENTER)
	if tipo == "good":
		caja.add_child(UIKit.con_icono(Iconos.OK, etiqueta, 22, 6, true))
	elif tipo == "bad":
		caja.add_child(UIKit.con_icono(Iconos.CERRAR, etiqueta, 18, 6, true))
	else:
		caja.add_child(etiqueta)
	_toasts.add_child(caja)
	while _toasts.get_child_count() > 4:
		_toasts.get_child(0).queue_free()
		_toasts.remove_child(_toasts.get_child(0))
	var t := caja.create_tween()
	t.tween_interval(2.0)
	t.tween_property(caja, "modulate:a", 0.0, 0.5)
	t.tween_callback(caja.queue_free)


func _refrescar_todo() -> void:
	_refrescar_recursos()
	_refrescar_casillas()
	_refrescar_tutorial()


func _refrescar_recursos() -> void:
	_scrap.text = "SCRAP %s" % Formulas.abreviar(GameState.scrap)
	_dano.text = "DAMAGE %s" % Formulas.abreviar(GameState.dano_base_golpe())
	_ritmo.text = "HIT EVERY %.2fs" % GameState.cooldown_ataque()


func _refrescar_casillas() -> void:
	_casillas[0].text = "1\n%s" % GameConfig.MARTILLO["nombre"]
	_casillas[0].add_theme_stylebox_override("normal", UIKit.estilo(Color("#2B2F36"), GameColors.AMARILLO, 10, 4))


func _al_cambiar_prompt(texto: String, progreso: float) -> void:
	_aviso.visible = texto != ""
	_aviso_texto.text = "[E]  " + texto
	_aviso_barra.visible = progreso > 0.0
	_aviso_barra.value = progreso


func _al_estado_jefe(datos: Dictionary) -> void:
	_contenedor_jefe.visible = datos["activo"]
	if not _contenedor_jefe.visible:
		return
	_jefe_nombre.text = datos["nombre"]
	_jefe_barra.value = datos["proporcion"]
	_jefe_objetivo.text = datos["objetivo"]


func _refrescar_tutorial() -> void:
	_tutorial.visible = not GameState.tutorial_completo
	if GameState.tutorial_completo:
		return
	var paso := mini(GameState.tutorial_paso, GameConfig.TUTORIAL.size() - 1)
	var datos: Dictionary = GameConfig.TUTORIAL[paso]
	_tutorial_paso.text = "STEP %d / %d" % [paso + 1, GameConfig.TUTORIAL.size()]
	_tutorial_titulo.text = datos["titulo"]
	_tutorial_texto.text = datos["texto"]


func mostrar_muerte(restante: float) -> void:
	_muerte.visible = true
	_muerte_texto.text = "YOU WERE CRUSHED\nRESPAWN IN %d" % int(ceil(restante))


func ocultar_muerte() -> void:
	_muerte.visible = false


func _mostrar_coloso_vencido(r: Dictionary) -> void:
	await get_tree().create_timer(1.2).timeout
	_victoria_insignia.texture = Iconos.INSIGNIA_COLOSO
	_victoria_titulo.text = "%s DEFEATED" % r["nombre"]
	var lineas := "FIGHT TIME %s" % Formulas.formato_tiempo(r["tiempo"])
	if int(r["scrap"]) > 0:
		lineas = "+%s SCRAP\n" % Formulas.abreviar(r["scrap"]) + lineas
	lineas += "\nIts eyes turn green."
	_mostrar_tarjeta(lineas)


func _mostrar_maestria(r: Dictionary) -> void:
	await get_tree().create_timer(1.2).timeout
	_victoria_insignia.texture = Iconos.INSIGNIA_COLOSO
	_victoria_titulo.text = "MASTERY · %s" % r["nombre"]
	var lineas := "FIGHT TIME %s\n%s\nSTARS %d / %d" % [Formulas.formato_tiempo(r["tiempo"]), "NO DAMAGE TAKEN" if r["sin_dano"] else "DAMAGE TAKEN", int(r["estrellas"]), int(GameConfig.COLOSO["estrellas_maximas"])]
	_mostrar_tarjeta(lineas)


func _mostrar_final(r: Dictionary) -> void:
	await get_tree().create_timer(2.5).timeout
	_victoria_insignia.texture = Iconos.INSIGNIA_LEYENDA
	_victoria_titulo.text = "ALL COLOSSI DEFEATED"
	_mostrar_tarjeta("TOTAL TIME %s\nOBJECTS WRECKED %d\n\nReturn to any console for MASTERY mode:\nbeat the colossus fast or without damage." % [Formulas.formato_tiempo(r["tiempo_total"]), int(r["objetos_rotos"])])


func _mostrar_tarjeta(texto: String) -> void:
	_victoria_texto.text = texto
	if not _victoria.visible:
		GameState.abrir_panel()
	_victoria.visible = true
	UIKit.activar_foco(_victoria)
