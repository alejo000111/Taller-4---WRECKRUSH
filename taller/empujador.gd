class_name Empujador
extends Node
## Responsabilidad: cuando el jugador choca con una pelota, empujarla con un impulso.
## move_and_slide no empuja: trata la pelota como una pared y se detiene. El empujón lo damos nosotros.


func empujar(cuerpo: CharacterBody3D, velocidad: Vector3) -> void:
	var empujados := []
	for i in cuerpo.get_slide_collision_count():
		var choque := cuerpo.get_slide_collision(i)
		var otro := choque.get_collider()
		if otro is RigidBody3D and not empujados.has(otro):
			empujados.append(otro)   # una sola vez por frame, aunque toque en varios puntos
			otro.apply_central_impulse(impulso_empuje(velocidad, otro.linear_velocity, choque.get_normal(), otro.mass))


## Función pura. impulso = m·Δv en la dirección del choque (horizontal).
## La normal apunta de la pelota hacia el jugador; la dirección del empujón es la contraria.
static func impulso_empuje(v_jugador: Vector3, v_pelota: Vector3, normal: Vector3, masa: float) -> Vector3:
	var n := Vectores.normalizar(Vector3(-normal.x, 0.0, -normal.z))
	var falta := v_jugador.dot(n) - v_pelota.dot(n)   # cuánto más rápido va el jugador que la pelota
	if falta <= 0.0:
		return Vector3.ZERO   # la pelota ya se aleja: no hay que empujar
	return n * masa * falta
