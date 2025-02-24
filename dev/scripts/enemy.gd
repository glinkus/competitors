extends CharacterBody2D
'''
Creator: Darius Rupsys
'''
const EXPERIENCE_POINTS = preload("res://nodes/experience_points.tscn")
@onready var target: CharacterBody2D = $"../../Player"
@onready var death_particles: GPUParticles2D = $DeathParticles
@onready var damage_particles: GPUParticles2D = $DamageParticles
@onready var camera_2d: Camera2D = $"../../Camera2D"
@onready var sprite_2d: Sprite2D = $Sprite2D
@onready var spawner: Node2D = $".."
@export var type: float = 0
@export var heal: float = 1.0
@export var damage: float = -1.0
@export var speed: float = 200.0
@export var max_speed: float = 200.0
@export var sin1: float = 1.0
@export var sin2: float = 1.0
var ready_to_go = false

func _ready() -> void:
	visible = false
	match type:
		1.0:
			heal = 1.0 * (spawner.time*0.1)
			damage = -1.0
			speed = 400.0
			max_speed = 400.0
			scale = Vector2(1, 1)
			var image = Image.load_from_file("res://assets/kenney_pixel-shmup/Ships/ship_0022.png")
			var texture = ImageTexture.create_from_image(image)
			sprite_2d.texture = texture
			sin1 = 8
			sin2 = 200
		2.0:
			heal = 2.0 * (spawner.time*0.1)
			damage = -1.5
			speed = 250.0
			max_speed = 250.0
			scale = Vector2(1.5, 1.5)
			var image = Image.load_from_file("res://assets/kenney_pixel-shmup/Ships/ship_0013.png")
			var texture = ImageTexture.create_from_image(image)
			sprite_2d.texture = texture
			sin1 = 1
			sin2 = 100
		3.0:
			heal = 3.0 * (spawner.time*0.1)
			damage = -2.0
			speed = 150.0
			max_speed = 150.0
			scale = Vector2(2, 2)
			var image = Image.load_from_file("res://assets/kenney_pixel-shmup/Ships/ship_0012.png")
			var texture = ImageTexture.create_from_image(image)
			sprite_2d.texture = texture
			sin1 = 0.5
			sin2 = 50
		4.0:
			heal = 1
			damage = -2.0
			speed = 300.0
			max_speed = 300.0
			scale = Vector2(1, 1)
			var image = Image.load_from_file("res://assets/kenney_pixel-shmup/Tiles/tile_0012.png")
			var texture = ImageTexture.create_from_image(image)
			sprite_2d.texture = texture
			sprite_2d.scale = Vector2(4,4)
			sin1 = 0.1
			sin2 = 600

func _process(delta: float) -> void:
	if ready_to_go and target:
		var target_direction = (target.position - position).normalized()
		velocity = target_direction * speed
		look_at(target.position)
		var local_velocity = to_local(velocity)
		local_velocity.y += sin(spawner.time*sin1)*sin2
		velocity = to_global(local_velocity)
		rotate(sin(spawner.time*sin1)*0.5)
		#1: 8
		#2: 3
		#3: 1
		move_and_slide()
		
		#velocity = (target.position - position).normalized() * speed
		#look_at(target.position)
		#velocity.x += sin(spawner.time)*velocity.x*0.5
		##rotate(sin(spawner.time))
		#move_and_slide()

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
	else:
		Punch.play()

func _on_area_2d_body_entered(body: Node2D) -> void:
	if body.is_in_group("Player"):
		body.take_damage(damage)
		death()

func death():
	camera_2d.shake_camera(10.0 * type)
	EnemyDeath.play()
	var childs = get_children()
	for child in childs:
		if child != death_particles:
			if child != damage_particles:
				child.queue_free()
	var image = Image.load_from_file("res://assets/bolt.png")
	image.resize(128, 128)
	var texture = ImageTexture.create_from_image(image)
	death_particles.texture = texture
	damage_particles.emitting = true
	death_particles.emitting = true
	await death_particles.finished
	queue_free()
	
	
func drop_xp():
	var xp = EXPERIENCE_POINTS.instantiate()
	xp.position = position
	var random_direction = Vector2(randf_range(-1, 1), randf_range(-1, 1)).normalized()
	xp.velocity = random_direction * 100
	get_parent().add_child(xp)
