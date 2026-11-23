class_name Curvas
extends RefCounted


static func suavizado(k: float, dt: float) -> float:
	return 1.0 - exp(-k * dt)


static func acercar(actual: Variant, objetivo: Variant, k: float, dt: float) -> Variant:
	return actual + (objetivo - actual) * suavizado(k, dt)


static func pulso(t: float, frecuencia: float) -> float:
	return 0.5 + 0.5 * sin(t * TAU * frecuencia)
