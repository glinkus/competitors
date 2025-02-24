extends Node2D
'''
Creator: Darius Rupsys
'''

var danger_sprite = preload("res://nodes/danger_sprite.tscn")

@export var mob_scene: PackedScene
@onready var timer: Timer = $Timer
@onready var sprite_2d: Sprite2D = $Sprite2D

var rng: RandomNumberGenerator = RandomNumberGenerator.new()
var time: float = 0.0

var very_fast_probability = 0.3
var fast_probability = 0.2
var slow_probability = 0.3
var rocket_probability = 0.2

func _ready() -> void:
	pass # Replace with function body.


func _process(delta: float) -> void:
	time += delta
	timer.wait_time -= delta/60
	#print(timer.wait_time)


func _on_timer_timeout() -> void:
	var danger = danger_sprite.instantiate()
	#var screen_size = DisplayServer.screen_get_size()
	var screen_size = Vector2(1080, 1920)
	var side = rng.randi_range(0, 4)
	var mob_spawn_location = Vector2()
	var danger_sprite_location = Vector2()
	match side:
		0:  # Kairysis šonas
			mob_spawn_location.x = rng.randf_range(0, screen_size.x)
			mob_spawn_location.y = 0
			danger_sprite_location.x = mob_spawn_location.x
			danger_sprite_location.y = 60
		1:  # Dešinysis šonas
			mob_spawn_location.x = rng.randf_range(0, screen_size.x)
			mob_spawn_location.y = screen_size.y
			danger_sprite_location.x = mob_spawn_location.x
			danger_sprite_location.y = screen_size.y-60
		2:  # Viršutinė dalis
			mob_spawn_location.x = 0
			mob_spawn_location.y = rng.randf_range(0, screen_size.y)
			danger_sprite_location.x = 25
			danger_sprite_location.y = mob_spawn_location.y
		3:  # Apatinė dalis
			mob_spawn_location.x = screen_size.x
			mob_spawn_location.y = rng.randf_range(0, screen_size.y)
			danger_sprite_location.x = screen_size.x-25
			danger_sprite_location.y = mob_spawn_location.y
	danger_sprite_location.x = max(25, min(danger_sprite_location.x, screen_size.x-25))
	danger_sprite_location.y = max(60, min(danger_sprite_location.y, screen_size.y-60))
	danger.position = danger_sprite_location
	#var type = rng.randi_range(1, 4)
	var type = get_enemy_type_based_on_probabilities()
	add_child(danger)
	await get_tree().create_timer(2).timeout
	var mob = mob_scene.instantiate()
	mob.type = type
	mob.position = mob_spawn_location
	add_child(mob)

func update_enemy_probabilities():
	var time_factor = time/60
	#slow_probability = max(0.1, 0.7 - time_factor * 0.1)
	#fast_probability = min(0.2, 0.2 + time_factor * 0.1)
	#very_fast_probability = min(0.4, 0.1 + time_factor * 0.1)
	#rocket_probability = min(0.4, 0.1 + time_factor * 0.1)

func get_enemy_type_based_on_probabilities():
	update_enemy_probabilities()
	var rand_val = rng.randf()
	if rand_val < slow_probability:
		return 1
	elif rand_val < slow_probability + fast_probability:
		return 2
	elif rand_val < slow_probability + fast_probability + very_fast_probability:
		return 3
	else:
		return 4
