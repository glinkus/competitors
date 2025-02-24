extends CharacterBody2D

@onready var joystick = $"../Camera2D/Joystick"
@onready var camera_2d: Camera2D = $"../Camera2D"
@onready var death_particles: GPUParticles2D = $DeathParticles
@onready var health_ui = $"../HealthUI" 
@export var stats : Stats

@export var upgrade_array : Array[BaseUpgradeResource]

@export var screen_width: float = 1080  
@export var screen_height: float = 1920  
@export var screen_offset: float = 50  

var target_look_position: Vector2 = Vector2.ZERO

var tap_start_time = 0.0
var tap_start_position = Vector2()
const TAP_THRESHOLD = 0.2  
var move_direction


func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed:
			tap_start_time = Time.get_ticks_msec() / 1000.0  # Convert to seconds
			tap_start_position = event.position
		else:
			var current_time = Time.get_ticks_msec() / 1000.0
			var touch_duration = current_time - tap_start_time
			if touch_duration < TAP_THRESHOLD:
				if tap_start_position.distance_to(event.position) < 10:
					target_look_position = event.position

func _physics_process(delta: float) -> void:
	var direction = joystick.posVector
	move_direction = direction
	if direction.length() > 0:
		direction = direction.normalized()

	if direction != Vector2.ZERO:
		velocity = velocity.move_toward(direction * stats.max_speed, stats.acceleration * delta)
	else:
		velocity = velocity.move_toward(Vector2.ZERO, stats.deceleration * delta)

	move_and_slide()
	rotate_to_movement_direction(delta)

	rotate_to_tapped_position(delta)

	wrap_around_screen()

func rotate_to_movement_direction(delta: float) -> void:
	if velocity.length() > 0:
		#var move_direction = velocity.normalized()
		var move_angle = move_direction.angle()
		move_angle += deg_to_rad(90)
		rotation = lerp_angle(rotation, move_angle, stats.rotation_speed * delta)

func rotate_to_tapped_position(delta: float) -> void:
	if target_look_position != Vector2.ZERO:
		var direction_to_target = (target_look_position - global_position).normalized()
		var target_angle = direction_to_target.angle()
		target_angle += deg_to_rad(90)
		rotation = lerp_angle(rotation, target_angle, stats.rotation_speed * delta)

func wrap_around_screen():
	# Get the player's global position
	var position = global_position

	# Wrap horizontally
	if position.x > screen_width + screen_offset:
		position.x = 0
	elif position.x < -screen_offset:
		position.x = screen_width + screen_offset

	# Wrap vertically
	if position.y > screen_height + screen_offset:
		position.y = 0
	elif position.y < -screen_offset:
		position.y = screen_height + screen_offset

	# Update the player's global position
	global_position = position
	
func apply_upgrade(upgrade_id: int):
	for upgrade in upgrade_array:
		if upgrade.upgrade_id == upgrade_id:
			upgrade.apply_upgrade(stats)
			print("damage %s" % stats.damage)
			print("speed %s" % stats.max_speed)
			print("firerate %s" % stats.fire_rate)

func take_damage(damage):
	health_ui.set_max(stats.health)
	stats.health += damage
	print(stats.health)
	health_ui.current_health = stats.health
	health_ui.update_health_bar()
	if stats.health  <= 0:
		DeathSoundPlayer.play()
		await get_tree().create_timer(0.1).timeout
		camera_2d.shake_camera(40.0)
		var childs = get_children()
		for child in childs:
			if child != death_particles:
				child.queue_free()
		death_particles.emitting = true
		await death_particles.finished  
		Globals.game_over()

func _on_shoot_sound_finished() -> void:
	pass # Replace with function body.
