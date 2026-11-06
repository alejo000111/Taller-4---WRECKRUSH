class_name LectorEntrada
extends Node
## Responsabilidad: convertir las teclas en una dirección de largo 1 (o cero).


func leer_direccion() -> Vector3:
	var der := int(Input.is_key_pressed(KEY_D))
	var izq := int(Input.is_key_pressed(KEY_A))
	var atras := int(Input.is_key_pressed(KEY_S))
	var adelante := int(Input.is_key_pressed(KEY_W))
	return Vectores.normalizar(Vector3(der - izq, 0, atras - adelante))
