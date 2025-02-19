extends CharacterBody2D
'''
Creator: Darius Rupsys
'''

@onready var target: CharacterBody2D = $"../../Player"

@export var type = 0
@export var heal = 1.0
@export var speed = 200.0
var ready_to_go = false

func _ready() -> void:
	visible = false
	match type:
		0:
			heal = 1.0
			speed = 400.0
		1:
			heal = 2.0
			speed = 250.0
		2:
			heal = 3.0
			speed = 150.0

func _process(delta: float) -> void:
	if ready_to_go:
		velocity = (target.position - position).normalized() * speed
		look_at(target.position)
		move_and_slide()

func _on_timer_timeout() -> void:
	ready_to_go = true
	visible = true

func take_damage(damage):
	heal += damage
