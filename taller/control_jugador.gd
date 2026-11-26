class_name ControlJugador
extends CharacterBody3D
## Coordina las piezas. Va en "Jugador", que desde la Sesión 3 es un CharacterBody3D.
## Corre en _physics_process: el cuerpo se mueve en el paso fijo de física (1/60 s).

@export var mostrar_rapidez := false

@onready var lector: LectorEntrada = $LectorEntrada
@onready var motor: Motor = $Motor
@onready var orientador: Orientador = $Orientador
@onready var empujador: Empujador = $Empujador

var posicion_anterior := Vector3.ZERO


func _ready() -> void:
	posicion_anterior = position


func _physics_process(delta: float) -> void:
	var direccion := lector.leer_direccion()
	motor.avanzar(direccion, delta)
	empujador.empujar(self, motor.velocidad)
	orientador.mirar(direccion, delta)

	if mostrar_rapidez and delta > 0.0:
		print("rapidez: %.2f m/s" % (Vectores.longitud(position - posicion_anterior) / delta))
	posicion_anterior = position
