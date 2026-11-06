@tool
class_name Iconos
extends RefCounted

const SCRAP := preload("res://assets/icons/currency/scrap.png")
const MEJORAS := preload("res://assets/icons/nav/nav_upgrades.png")
const AJUSTES := preload("res://assets/icons/nav/nav_settings.png")
const WRECK := preload("res://assets/icons/nav/button_wreck.png")
const DANO := preload("res://assets/icons/stats/stat_damage.png")
const VELOCIDAD := preload("res://assets/icons/stats/stat_attack_speed.png")
const FLECHA := preload("res://assets/icons/ui/icon_arrow.png")
const OK := preload("res://assets/icons/ui/icon_check.png")
const CERRAR := preload("res://assets/icons/ui/icon_close.png")
const CANDADO := preload("res://assets/icons/ui/icon_lock.png")
const JEFE := preload("res://assets/icons/events/event_boss.png")
const INSIGNIA_COLOSO := preload("res://assets/icons/badges/badge_boss_slayer.png")
const INSIGNIA_LEYENDA := preload("res://assets/icons/badges/badge_wreck_legend.png")
const LOGO := preload("res://assets/brand/logo_main.png")
const LOGO_JUEGO := preload("res://assets/brand/logo_ingame.png")
const LOGO_ICONO := preload("res://assets/brand/logo_icon.png")
const FONDO_CARGA := preload("res://assets/brand/loading_background.png")
const ZONAS_BLOQUEADAS := {
	"vip": preload("res://assets/icons/zones/zone_vip.png"),
	"chaos_core": preload("res://assets/icons/zones/zone_chaos_core.png"),
	"future": preload("res://assets/icons/zones/zone_future.png"),
	"military": preload("res://assets/icons/zones/zone_military.png"),
	"hall": preload("res://assets/icons/badges/badge_wreck_legend.png"),
}


static func cargar(ruta: String) -> Texture2D:
	if ruta == "" or not ResourceLoader.exists(ruta):
		return null
	return load(ruta) as Texture2D


static func zona(id: String) -> Texture2D:
	if GameConfig.ZONAS.has(id):
		return cargar(String(GameConfig.ZONAS[id].get("icono", "")))
	return ZONAS_BLOQUEADAS.get(id)
