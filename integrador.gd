class_name Integrador
## Nivel 3: el integrador propio (Euler semi-implícito), el mismo que usa el motor.
## Primero la velocidad con la aceleración; después la posición con la velocidad NUEVA.


static func paso(pos: Vector3, vel: Vector3, acel: Vector3, dt: float) -> Array:
	var v2 := vel + acel * dt
	return [pos + v2 * dt, v2]


## n pasos seguidos, sin escena: se prueba solo con números.
static func simular(pos: Vector3, vel: Vector3, acel: Vector3, dt: float, n: int) -> Array:
	var estado := [pos, vel]
	for i in n:
		estado = paso(estado[0], estado[1], acel, dt)
	return estado
