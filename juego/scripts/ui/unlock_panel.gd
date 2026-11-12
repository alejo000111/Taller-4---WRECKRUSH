class_name UnlockPanel
extends BasePanel

var zona: String = "downtown"
var _texto: Label
var _icono: TextureRect
var _confirmar: Button


func _init() -> void:
	super._init("UNLOCK ISLAND", GameColors.AMARILLO, 560.0, Iconos.CANDADO)


func construir() -> void:
	_icono = UIKit.icono(Iconos.zona(zona), 120)
	_icono.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	contenido.add_child(_icono)
	_texto = UIKit.etiqueta("", 22, GameColors.BLANCO, HORIZONTAL_ALIGNMENT_CENTER)
	_texto.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	contenido.add_child(_texto)
	var fila := HBoxContainer.new()
	fila.alignment = BoxContainer.ALIGNMENT_CENTER
	fila.add_theme_constant_override("separation", 14)
	_confirmar = UIKit.boton("UNLOCK", GameColors.AMARILLO.darkened(0.25), Vector2(200, 50), 20)
	UIKit.poner_icono(_confirmar, Iconos.SCRAP, 32)
	_confirmar.pressed.connect(func() -> void:
		if GameState.desbloquear_zona(zona):
			Sfx.reproducir("comprar")
			cerrar()
		else:
			Sfx.reproducir("error"))
	fila.add_child(_confirmar)
	var cancelar := UIKit.boton("NO THANKS", Color("#4A505C"), Vector2(200, 50), 20)
	UIKit.poner_icono(cancelar, Iconos.CERRAR, 22)
	cancelar.pressed.connect(cerrar)
	fila.add_child(cancelar)
	contenido.add_child(fila)
	GameState.scrap_cambio.connect(func(_v: int) -> void: if abierto: refrescar())


func refrescar() -> void:
	var def: Dictionary = GameConfig.ZONAS[zona]
	var costo: int = def["costo"]
	_icono.texture = Iconos.zona(zona)
	_texto.text = "ISLAND %d · %s\n%d objects and a colossus\n\nCOST  %s SCRAP\nYOU HAVE  %s SCRAP\n\nOnce paid, it stays open forever." % [int(def["isla"]), def["nombre"], GameConfig.total_objetos(zona), Formulas.abreviar(costo), Formulas.abreviar(GameState.scrap)]
	_confirmar.disabled = GameState.scrap < costo
