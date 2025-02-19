extends Node2D
'''
Creator: Darius Rupsys
'''

@export var mob_scene: PackedScene
var danger_sprite = preload("res://nodes/danger_sprite.tscn")

var rng: RandomNumberGenerator = RandomNumberGenerator.new()

func _ready() -> void:
	pass # Replace with function body.


func _process(delta: float) -> void:
	pass


func _on_timer_timeout() -> void:
	var mob = mob_scene.instantiate()
	var danger = danger_sprite.instantiate()
	var screen_size = DisplayServer.screen_get_size()
	var side = rng.randi_range(0, 4)
	var mob_spawn_location = Vector2()
	var danger_sprite_location = Vector2()
	match side:
		0:  # Kairysis šonas
			mob_spawn_location.x = rng.randf_range(0, screen_size.y)
			mob_spawn_location.y = 0
			danger_sprite_location.x = mob_spawn_location.x
			danger_sprite_location.y = 60
		1:  # Dešinysis šonas
			mob_spawn_location.x = rng.randf_range(0, screen_size.y)
			mob_spawn_location.y = screen_size.x
			danger_sprite_location.x = mob_spawn_location.x
			danger_sprite_location.y = screen_size.x-60
		2:  # Viršutinė dalis
			mob_spawn_location.x = 0
			mob_spawn_location.y = rng.randf_range(0, screen_size.x)
			danger_sprite_location.x = 25
			danger_sprite_location.y = mob_spawn_location.y
		3:  # Apatinė dalis
			mob_spawn_location.x = screen_size.y
			mob_spawn_location.y = rng.randf_range(0, screen_size.x)
			danger_sprite_location.x = screen_size.y-25
			danger_sprite_location.y = mob_spawn_location.y
	mob.position = mob_spawn_location
	danger_sprite_location.x = max(25, min(danger_sprite_location.x, screen_size.y-25))
	danger_sprite_location.y = max(60, min(danger_sprite_location.y, screen_size.x-60))
	danger.position = danger_sprite_location
	var type = rng.randi_range(0, 3)
	mob.type = type
	add_child(mob)
	add_child(danger)
