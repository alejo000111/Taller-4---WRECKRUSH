class_name UpgradesPanel
extends BasePanel

var _lista: VBoxContainer


func _init() -> void:
	super._init("UPGRADES", GameColors.AMARILLO, 780.0, Iconos.MEJORAS)


func construir() -> void:
	_lista = VBoxContainer.new()
	_lista.add_theme_constant_override("separation", 8)
	contenido.add_child(_lista)
	GameState.scrap_cambio.connect(func(_v: int) -> void: if abierto: refrescar())


func refrescar() -> void:
	limpiar(_lista)
	_lista.add_child(UIKit.con_icono(Iconos.SCRAP, UIKit.etiqueta("SCRAP  %s" % Formulas.abreviar(GameState.scrap), 22, GameColors.AMARILLO), 32))
	for id in GameConfig.ORDEN_MEJORAS:
		_lista.add_child(_tarjeta(id, GameConfig.MEJORAS[id]))
	var requisito := "Colossi need DAMAGE 25 / 35 / 40 (levels 6 / 10 / 12)."
	_lista.add_child(UIKit.etiqueta(requisito, 15, Color("#8A909C")))
	if abierto:
		enfocar()


func _valor_texto(id: String, nivel: int) -> String:
	if id == "damage":
		return "%s per hit" % GameConfig.texto_dano(Formulas.dano_golpe(float(GameConfig.MARTILLO["dano"]), nivel))
	return "every %.3fs" % Formulas.cooldown_ataque(float(GameConfig.MARTILLO["cooldown"]), nivel)


func _tarjeta(id: String, def: Dictionary) -> Control:
	var nivel := GameState.nivel_mejora(id)
	var estado := GameState.estado_mejora(id)
	var tarjeta := UIKit.tarjeta()
	var fila := HBoxContainer.new()
	fila.add_theme_constant_override("separation", 14)
	tarjeta.add_child(fila)
	var icono := PanelContainer.new()
	icono.custom_minimum_size = Vector2(64, 64)
	icono.add_theme_stylebox_override("panel", UIKit.estilo(GameColors.AMARILLO.darkened(0.55), GameColors.AMARILLO, 12, 3, 4))
	icono.add_child(UIKit.icono(Iconos.cargar(String(def["icono"])), 56))
	fila.add_child(icono)
	var info := VBoxContainer.new()
	info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	info.add_child(UIKit.etiqueta("%s   LV %d/%d" % [def["nombre"], nivel, int(def["max"])], 20))
	var siguiente := _valor_texto(id, nivel + 1) if nivel < int(def["max"]) else "MAX"
	info.add_child(UIKit.etiqueta("%s  >  %s" % [_valor_texto(id, nivel), siguiente], 16, Color("#B8BDC8")))
	if nivel < int(def["max"]) and not estado["ok"]:
		var falta := GameState.precio_mejora(id) - GameState.scrap
		info.add_child(UIKit.etiqueta("NEED %d MORE SCRAP" % falta, 14, Color("#FF9A9A")))
	fila.add_child(info)
	var acciones := VBoxContainer.new()
	fila.add_child(acciones)
	var comprar: Button
	if nivel >= int(def["max"]):
		comprar = UIKit.boton("MAXED", Color("#5A5F6A"), Vector2(190, 48), 16)
		UIKit.poner_icono(comprar, Iconos.OK, 26)
		comprar.disabled = true
	else:
		comprar = UIKit.boton("BUY  %s" % Formulas.abreviar(GameState.precio_mejora(id)), GameColors.AMARILLO.darkened(0.25), Vector2(190, 48), 16)
		UIKit.poner_icono(comprar, Iconos.SCRAP, 30)
		comprar.disabled = not estado["ok"]
		comprar.pressed.connect(func() -> void: _comprar(id))
	acciones.add_child(comprar)
	if nivel < int(def["max"]):
		var plan := GameState.plan_compra_mejoras(id)
		var maximo := UIKit.boton("BUY MAX (+%d)" % int(plan["niveles"]), GameColors.CIAN.darkened(0.45), Vector2(190, 40), 15)
		maximo.disabled = int(plan["niveles"]) == 0
		maximo.tooltip_text = "%d LEVELS · %d SCRAP" % [int(plan["niveles"]), int(plan["costo"])]
		maximo.pressed.connect(func() -> void: _comprar_max(id))
		acciones.add_child(maximo)
	return tarjeta


func _comprar(id: String) -> void:
	if GameState.comprar_mejora(id)["ok"]:
		Sfx.reproducir("comprar")
	else:
		Sfx.reproducir("error")
	refrescar()


func _comprar_max(id: String) -> void:
	var cantidad := GameState.comprar_max_mejoras(id)
	if cantidad > 0:
		Sfx.reproducir("comprar")
		GameState.toast.emit("%s +%d LEVELS" % [GameConfig.MEJORAS[id]["nombre"], cantidad], "good")
	else:
		Sfx.reproducir("error")
	refrescar()
