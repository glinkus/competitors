extends CharacterBody2D
'''
Creator: Darius Rupsys
'''

@onready var target: CharacterBody2D = $"../../Player"

@export var type: float = 0
@export var heal: float = 1.0
@export var damage: float = -1.0
@export var speed: float = 200.0
@export var max_speed: float = 200.0
var ready_to_go = false

func _ready() -> void:
	visible = false
	match type:
		0:
			heal = 1.0
			damage = -1.0
			speed = 400.0
			max_speed = 400.0
			scale = Vector2(1, 1)
		1:
			heal = 2.0
			damage = -1.5
			speed = 250.0
			max_speed = 250.0
			scale = Vector2(1.5, 1.5)
		2:
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
		#drop_xp()
		Globals.score += 1
		queue_free()

func _on_area_2d_body_entered(body: Node2D) -> void:
	if body.is_in_group("Player"):
		body.take_damage(damage)
