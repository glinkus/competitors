extends CharacterBody2D
'''
Creator: Darius Rupsys
'''
const EXPERIENCE_POINTS = preload("res://nodes/experience_points.tscn")
@onready var target: CharacterBody2D = $"../../Player"
@onready var death_particles: GPUParticles2D = $DeathParticles
@onready var camera_2d: Camera2D = $"../../Camera2D"

@export var type: float = 0
@export var heal: float = 1.0
@export var damage: float = -1.0
@export var speed: float = 200.0
@export var max_speed: float = 200.0
var ready_to_go = false

func _ready() -> void:
	visible = false
	match type:
		1.0:
			heal = 1.0
			damage = -1.0
			speed = 400.0
			max_speed = 400.0
			scale = Vector2(1, 1)
		2.0:
			heal = 2.0
			damage = -1.5
			speed = 250.0
			max_speed = 250.0
			scale = Vector2(1.5, 1.5)
		3.0:
			heal = 3.0
			damage = -2.0
			speed = 150.0
			max_speed = 150.0
			scale = Vector2(2, 2)

func _process(delta: float) -> void:
	if ready_to_go and target:
		velocity = (target.position - position).normalized() * speed
		look_at(target.position)
		move_and_slide()

func _on_timer_timeout() -> void:
	ready_to_go = true
	visible = true

func take_damage(dmg):
	heal += dmg
	if heal <= 0:
		drop_xp()
		drop_xp()
		drop_xp()
		death()

func _on_area_2d_body_entered(body: Node2D) -> void:
	if body.is_in_group("Player"):
		body.take_damage(damage)
		death()

func death():
	camera_2d.shake_camera(10.0 * type)
	var childs = get_children()
	for child in childs:
		if child != death_particles:
			child.queue_free()
	death_particles.emitting = true
	await death_particles.finished
	queue_free()
	
func drop_xp():
	var xp = EXPERIENCE_POINTS.instantiate()
	xp.position = position
	var random_direction = Vector2(randf_range(-1, 1), randf_range(-1, 1)).normalized()
	xp.velocity = random_direction * 100
	get_parent().add_child(xp)
