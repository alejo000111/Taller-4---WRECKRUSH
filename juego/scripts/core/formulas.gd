@tool
class_name Formulas
extends RefCounted

const CRECIMIENTO_PRECIO := 1.5
const PRECIO_MAXIMO := 1.0e15


static func multiplicador_dano(nivel_mejora: int) -> float:
	return 1.0 + 0.25 * nivel_mejora


static func dano_golpe(dano_herramienta: float, nivel_mejora: int) -> float:
	return dano_herramienta * multiplicador_dano(nivel_mejora)


static func cooldown_ataque(cooldown_base: float, nivel_velocidad: int) -> float:
	return cooldown_base / (1.0 + 0.06 * nivel_velocidad)


static func precio_mejora(precio_base: float, nivel_nuevo: int, desfase: int = 0) -> int:
	return int(round(minf(precio_base * pow(CRECIMIENTO_PRECIO, nivel_nuevo + desfase), PRECIO_MAXIMO)))


static func golpes_para_romper(vida: float, dano: float) -> int:
	return int(ceil(vida / dano))


static func segundos_para_romper(golpes: int, cooldown: float) -> float:
	return (golpes - 1) * cooldown


static func vida_placa(numero_coloso: int) -> float:
	return 800.0 + 200.0 * (numero_coloso - 1)


static func vida_nucleo(numero_coloso: int) -> float:
	return 700.0 + 100.0 * (numero_coloso - 1)


static func intervalo_golpe_suelo(numero_coloso: int) -> float:
	return 7.0 - numero_coloso


static func studs_a_metros(studs: float) -> float:
	return studs * GameConfig.METROS_POR_STUD


static func velocidad_salto(altura: float, tiempo_aire: float) -> float:
	return 4.0 * altura / tiempo_aire


static func gravedad_salto(altura: float, tiempo_aire: float) -> float:
	return 8.0 * altura / (tiempo_aire * tiempo_aire)


static func elevacion_sol(hora: float) -> float:
	return clampf((18.5 - hora) * 13.0, 4.0, 60.0)


static func abreviar(valor: float) -> String:
	var sufijos := ["", "K", "M", "B", "T"]
	var v := absf(valor)
	var i := 0
	while v >= 999.95 and i < sufijos.size() - 1:
		v /= 1000.0
		i += 1
	if i == 0:
		return str(int(v))
	return ("%.1f" % v).trim_suffix(".0") + sufijos[i]


static func formato_tiempo(segundos: float) -> String:
	var total := int(maxf(segundos, 0.0))
	return "%d:%02d" % [total / 60, total % 60]
