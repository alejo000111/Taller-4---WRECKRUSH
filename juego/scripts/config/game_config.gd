@tool
class_name GameConfig
extends RefCounted

const VERSION := "1.0.0"
const NOMBRE_VERSION := "TALLER 4"
const METROS_POR_STUD := 0.28
const VIDA_JUGADOR := 100.0
const AUTOGUARDADO_SEGUNDOS := 120.0
const LIMITE_MAPA := 382.0
const ALTURA_CAIDA := -40.0
const REAPARICION_COLOSO := 45.0
const RADIO_ARENA := 60.0
const SALTO_ALTURA_METROS := 1.0
const SALTO_TIEMPO_AIRE := 0.9
const HORA_CIUDAD := 17.6
const HORA_ARENA := 16.3

const ZONAS := {
	"plaza": {"nombre": "SPAWN PLAZA", "centro": Vector2(0, 0), "costo": 0, "tinte": Color("#FFB070"), "material": "WR_PlazaTiles", "baldosa": 16.0, "icono": "res://assets/brand/logo_icon.png"},
	"scrap_yard": {"nombre": "SCRAP YARD", "isla": 1, "centro": Vector2(0, -240), "costo": 0, "tinte": Color("#FFA45C"), "material": "WR_ScrapDirt", "baldosa": 18.0, "icono": "res://assets/icons/zones/zone_scrap_yard.png"},
	"downtown": {"nombre": "DOWNTOWN", "isla": 2, "centro": Vector2(240, -240), "costo": 1500, "multiplicador_scrap": 2.0, "tinte": Color("#E8A0B8"), "material": "WR_Sidewalk", "baldosa": 14.0, "icono": "res://assets/icons/zones/zone_downtown.png"},
	"industrial": {"nombre": "INDUSTRIAL", "isla": 3, "centro": Vector2(240, 0), "costo": 6000, "multiplicador_scrap": 3.0, "tinte": Color("#A9B6CC"), "material": "WR_FactoryConcrete", "baldosa": 18.0, "icono": "res://assets/icons/zones/zone_industrial.png"},
}

const ORDEN_ZONAS := ["scrap_yard", "downtown", "industrial"]
const POSICION_COLOSO := Vector2(45, -10)

const OBJETOS := {
	"scrap_yard": [
		{"id": "scrap_barrel", "nombre": "SCRAP BARREL", "tamano": "Small", "vida": 30, "scrap": 12, "respawn": 5, "cantidad": 8,
			"modelo": "ScrapBarrel", "caja": Vector3(2.7, 3.5, 2.7), "partes": [["cyl", Vector3(2.4, 3, 2.4), Vector3(0, 1.5, 0), Color("#8C4A1E")], ["cyl", Vector3(2.5, 0.3, 2.5), Vector3(0, 2.2, 0), Color("#5A5F66")]]},
		{"id": "road_sign", "nombre": "ROAD SIGN", "tamano": "Small", "vida": 35, "scrap": 14, "respawn": 5, "cantidad": 4,
			"modelo": "RoadSign", "caja": Vector3(2.1, 6, 0.7), "partes": [["cyl", Vector3(0.3, 5, 0.3), Vector3(0, 2.5, 0), Color("#6E7078")], ["box", Vector3(2.6, 1.8, 0.2), Vector3(0, 4.6, 0), Color("#B84A2E")]]},
		{"id": "wooden_crate", "nombre": "WOODEN CRATE", "tamano": "Small", "vida": 45, "scrap": 18, "respawn": 5, "cantidad": 5,
			"modelo": "WoodenCrate", "caja": Vector3(3.4, 3.4, 3.3), "partes": [["box", Vector3(3, 3, 3), Vector3(0, 1.5, 0), Color("#8A6232")]]},
		{"id": "tire_stack", "nombre": "TIRE STACK", "tamano": "Small", "vida": 70, "scrap": 28, "respawn": 6, "cantidad": 3,
			"modelo": "TireStack", "caja": Vector3(3.5, 3.3, 3.4), "partes": [["cyl", Vector3(3.2, 1, 3.2), Vector3(0, 0.5, 0), Color("#1C1D20")], ["cyl", Vector3(3, 1, 3), Vector3(0, 1.5, 0), Color("#25262A")], ["cyl", Vector3(3.2, 1, 3.2), Vector3(0, 2.5, 0), Color("#1C1D20")]]},
		{"id": "rusty_car", "nombre": "RUSTY CAR", "tamano": "Medium", "vida": 300, "scrap": 90, "respawn": 12, "cantidad": 5,
			"modelo": "RustyCar", "caja": Vector3(4.9, 3.4, 9.8), "partes": [["box", Vector3(9, 2, 4.2), Vector3(0, 1.4, 0), Color("#7A3B24")], ["box", Vector3(4.6, 1.6, 3.8), Vector3(-0.4, 3.2, 0), Color("#5E4A3F")]]},
		{"id": "forklift", "nombre": "FORKLIFT", "tamano": "Medium", "vida": 550, "scrap": 165, "respawn": 18, "cantidad": 3,
			"modelo": "Forklift", "caja": Vector3(4.8, 6.3, 8.1), "partes": [["box", Vector3(4.6, 2.6, 3), Vector3(0, 1.8, 0), Color("#A8741F")], ["box", Vector3(0.6, 7.6, 2.6), Vector3(2.6, 3.8, 0), Color("#4C4F55")], ["box", Vector3(3, 0.4, 2.8), Vector3(3.8, 0.7, 0), Color("#4C4F55")]]},
		{"id": "rusty_container", "nombre": "RUSTY CONTAINER", "tamano": "Large", "vida": 1200, "scrap": 360, "respawn": 35, "cantidad": 1,
			"modelo": "ScrapContainer", "caja": Vector3(6, 6, 14.4), "partes": [["box", Vector3(14, 6.2, 5.2), Vector3(0, 3.1, 0), Color("#3F6B73")]]},
	],
	"downtown": [
		{"id": "mailbox", "nombre": "MAILBOX", "tamano": "Small", "vida": 120, "scrap": 48, "respawn": 7, "cantidad": 8,
			"modelo": "ParkingMeter", "caja": Vector3(1, 4.8, 0.8), "partes": [["cyl", Vector3(0.4, 3, 0.4), Vector3(0, 1.5, 0), Color("#6E7078")], ["box", Vector3(1.6, 1.6, 1.6), Vector3(0, 3.6, 0), Color("#3C6E8F")]]},
		{"id": "park_bench", "nombre": "PARK BENCH", "tamano": "Small", "vida": 180, "scrap": 72, "respawn": 9, "cantidad": 6,
			"caja": Vector3(5, 3, 1.8), "partes": [["box", Vector3(5, 0.5, 1.6), Vector3(0, 1.6, 0), Color("#8A6232")], ["box", Vector3(5, 1.6, 0.4), Vector3(0, 2.6, -0.7), Color("#8A6232")], ["box", Vector3(0.4, 1.6, 1.4), Vector3(-2.2, 0.8, 0), Color("#4C4F55")], ["box", Vector3(0.4, 1.6, 1.4), Vector3(2.2, 0.8, 0), Color("#4C4F55")]]},
		{"id": "city_car", "nombre": "CITY CAR", "tamano": "Medium", "vida": 1200, "scrap": 360, "respawn": 35, "cantidad": 6,
			"modelo": "TaxiCab", "caja": Vector3(4.8, 3.9, 9.5), "partes": [["box", Vector3(9, 2, 4.2), Vector3(0, 1.4, 0), Color("#C98C1A")], ["box", Vector3(4.4, 1.6, 3.8), Vector3(-0.4, 3.2, 0), Color("#B07A18")]]},
		{"id": "city_bus", "nombre": "CITY BUS", "tamano": "Large", "vida": 2200, "scrap": 660, "respawn": 35, "cantidad": 3,
			"modelo": "CityVan", "caja": Vector3(8, 8.5, 15.5), "partes": [["box", Vector3(16, 4.6, 4.6), Vector3(0, 2.7, 0), Color("#5D7A99")], ["box", Vector3(14, 1.4, 4.7), Vector3(0, 3.6, 0), Color("#9FC4D8")]]},
		{"id": "news_kiosk", "nombre": "NEWS KIOSK", "tamano": "Huge", "vida": 4800, "scrap": 1440, "respawn": 35, "cantidad": 1,
			"modelo": "NewsKiosk", "caja": Vector3(8.2, 7.7, 6.1), "partes": [["box", Vector3(7.6, 5, 5.6), Vector3(0, 2.5, 0), Color("#2E7D6B")], ["box", Vector3(8.4, 0.8, 6.4), Vector3(0, 5.4, 0), Color("#C45A3C")], ["box", Vector3(5, 1.6, 0.4), Vector3(0, 3, 2.9), Color("#9FC4D8")]]},
	],
	"industrial": [
		{"id": "pipe_stack", "nombre": "PIPE STACK", "tamano": "Small", "vida": 240, "scrap": 72, "respawn": 9, "cantidad": 8,
			"modelo": "PipeStack", "caja": Vector3(3.8, 2.7, 5.2), "partes": [["cyl", Vector3(1.6, 3.6, 1.6), Vector3(-1, 1, 0), Color("#8A8F99")], ["cyl", Vector3(1.6, 3.6, 1.6), Vector3(1, 1, 0), Color("#7A7F89")], ["cyl", Vector3(1.6, 3.6, 1.6), Vector3(0, 2.4, 0), Color("#9A9FA9")]]},
		{"id": "generator", "nombre": "GENERATOR", "tamano": "Medium", "vida": 360, "scrap": 108, "respawn": 11, "cantidad": 6,
			"modelo": "Generator", "caja": Vector3(4.2, 4.5, 5.7), "partes": [["box", Vector3(5, 3, 3.4), Vector3(0, 1.5, 0), Color("#B8761F")], ["box", Vector3(1.2, 1, 1.2), Vector3(1.4, 3.4, 0), Color("#4C4F55")]]},
		{"id": "dump_truck", "nombre": "DUMP TRUCK", "tamano": "Large", "vida": 2400, "scrap": 720, "respawn": 35, "cantidad": 6,
			"caja": Vector3(12, 6, 5), "partes": [["box", Vector3(12, 2, 4.8), Vector3(0, 1.8, 0), Color("#B8761F")], ["box", Vector3(7, 3.4, 4.8), Vector3(-2, 4.2, 0), Color("#8C5A1A")], ["box", Vector3(2.6, 3, 4.2), Vector3(4.4, 3.2, 0), Color("#4C4F55")]]},
		{"id": "excavator", "nombre": "EXCAVATOR", "tamano": "Large", "vida": 4400, "scrap": 1320, "respawn": 35, "cantidad": 3,
			"caja": Vector3(11, 8, 5), "partes": [["box", Vector3(8, 2.2, 4.6), Vector3(0, 1.5, 0), Color("#C98C1A")], ["box", Vector3(3.6, 3, 3.6), Vector3(-1, 3.7, 0), Color("#A8741F")], ["box", Vector3(7, 0.9, 1), Vector3(4.2, 6.2, 0), Color("#4C4F55")]]},
		{"id": "silo", "nombre": "SILO", "tamano": "Huge", "vida": 7200, "scrap": 2160, "respawn": 35, "cantidad": 1,
			"modelo": "FuelTank", "caja": Vector3(12.5, 15.1, 12.5), "partes": [["cyl", Vector3(8, 18, 8), Vector3(0, 9, 0), Color("#7A8088")], ["cone", Vector3(8.4, 4, 8.4), Vector3(0, 20, 0), Color("#5C6068")]]},
	],}

const MEJORAS := {
	"damage": {"nombre": "DAMAGE", "base": 25.0, "max": 12, "desfase": 0, "icono": "res://assets/icons/stats/stat_damage.png"},
	"attack_speed": {"nombre": "ATTACK SPEED", "base": 600.0, "max": 5, "desfase": -1, "icono": "res://assets/icons/stats/stat_attack_speed.png"},
}

const ORDEN_MEJORAS := ["damage", "attack_speed"]

const MARTILLO := {"nombre": "SCRAP HAMMER", "dano": 10.0, "cooldown": 0.45, "alcance": 11.0, "color": Color("#B7BCC4"), "modelo": "ScrapHammer", "icono": "res://assets/icons/tools/tool_scrap_hammer.png"}

const COLOSOS := [
	{"numero": 1, "id": "scrap_colossus", "nombre": "SCRAP COLOSSUS", "zona": "scrap_yard", "dano_requerido": 25.0, "recompensa": 1500, "maestria_segundos": 50.0, "ojos_rojos": 15, "giro_cabeza": 29, "color": Color("#7A3B24"), "modelo": "ScrapColossus", "escala": 0.68},
	{"numero": 2, "id": "downtown_crusher", "nombre": "DOWNTOWN CRUSHER", "zona": "downtown", "dano_requerido": 35.0, "recompensa": 3600, "maestria_segundos": 60.0, "ojos_rojos": 12, "giro_cabeza": 24, "color": Color("#4E5F77"), "modelo": "DowntownCrusher", "escala": 0.7},
	{"numero": 3, "id": "industrial_titan", "nombre": "INDUSTRIAL TITAN", "zona": "industrial", "dano_requerido": 40.0, "recompensa": 0, "maestria_segundos": 70.0, "ojos_rojos": 12, "giro_cabeza": 24, "color": Color("#8C5A1A"), "modelo": "IndustrialTitan", "escala": 0.62},
]

const COLOSO := {
	"cantidad_placas": 4,
	"ventana_expuesta": 16.0,
	"aviso": 1.5,
	"dano": 25.0,
	"duracion_intro": 3.0,
	"inactividad_reinicio": 60.0,
	"espera_entre_peleas": 12.0,
	"mantener_consola": 0.6,
	"radio_disco": 14.0,
	"radio_anillo_interior": 11.0,
	"radio_anillo_exterior": 34.0,
	"estrellas_maximas": 2,
	"modelo_placa": "ArmorPlate",
	"modelo_nucleo": "WeakPoint",
}

const TUTORIAL := [
	{"titulo": "GRAB YOUR TOOL", "texto": "Press 1 or tap the hammer in your hotbar"},
	{"titulo": "BREAK SOMETHING", "texto": "Follow the arrow. Hold WRECK to keep hitting"},
	{"titulo": "GET SCRAP", "texto": "Wreck objects to collect Scrap"},
	{"titulo": "UPGRADE", "texto": "Open UPGRADES and buy DAMAGE for 38 Scrap"},
	{"titulo": "WRECK MORE", "texto": "Wreck 10 objects"},
	{"titulo": "PLAY YOUR WAY", "texto": "Reach damage 25 to challenge the first colossus. Each new island pays more Scrap"},
]


static func objeto_por_id(zona: String, id: String) -> Dictionary:
	for def in OBJETOS[zona]:
		if def["id"] == id:
			return def
	return {}


static func total_objetos(zona: String) -> int:
	var total := 0
	for def in OBJETOS[zona]:
		total += int(def["cantidad"])
	return total


static func scrap_por_vuelta(zona: String) -> int:
	var total := 0
	for def in OBJETOS[zona]:
		total += int(def["scrap"]) * int(def["cantidad"])
	return total


static func multiplicador_scrap(zona: String) -> float:
	return float(ZONAS.get(zona, {}).get("multiplicador_scrap", 1.0))


static func dano_requerido(numero: int) -> float:
	return float(COLOSOS[numero - 1]["dano_requerido"])


static func texto_dano(valor: float) -> String:
	return str(int(valor)) if is_equal_approx(valor, floorf(valor)) else "%.1f" % valor


static func coloso_de_zona(zona: String) -> Dictionary:
	for c in COLOSOS:
		if c["zona"] == zona:
			return c
	return {}
