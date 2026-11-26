@tool
class_name Interactable
extends Node3D

signal activado

var texto: String = "Interact"
var radio: float = 9.0
var mantener: float = 0.0
var habilitado: bool = true
var texto_dinamico: Callable = Callable()


static func crear(padre: Node, posicion: Vector3, texto_: String, radio_: float = 9.0, mantener_: float = 0.0) -> Interactable:
	var i := Interactable.new()
	i.texto = texto_
	i.radio = radio_
	i.mantener = mantener_
	i.position = posicion
	padre.add_child(i)
	return i


func _ready() -> void:
	add_to_group("interactables")


func obtener_texto() -> String:
	if texto_dinamico.is_valid():
		return String(texto_dinamico.call())
	return texto


func distancia_horizontal(punto: Vector3) -> float:
	return Vector2(global_position.x - punto.x, global_position.z - punto.z).length()
