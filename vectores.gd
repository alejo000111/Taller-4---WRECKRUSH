class_name Vectores
## Solución del Taller 1. Operaciones de vectores hechas a mano:
## el taller prohíbe length(), normalized(), distance_to() y move_toward().


static func longitud(v: Vector3) -> float:
	return sqrt(v.x * v.x + v.y * v.y + v.z * v.z)


## Nivel 1. Sin tecla el vector es (0, 0, 0): dividir por cero daría NaN.
static func normalizar(v: Vector3) -> Vector3:
	var largo := longitud(v)
	if largo == 0.0:
		return Vector3.ZERO
	return v / largo


## Nivel 2. Avanza desde "actual" hacia "objetivo" como máximo "paso", sin pasarse.
static func acercar(actual: Vector3, objetivo: Vector3, paso: float) -> Vector3:
	var diferencia := objetivo - actual
	if longitud(diferencia) <= paso:
		return objetivo
	return actual + normalizar(diferencia) * paso
