extends CharacterBody2D 
class_name PlayerManager

@onready var camera_2d: Camera2D = $"../Camera2D"
@onready var death_particles: GPUParticles2D = $DeathParticles
@onready var engine_sound : AudioStreamPlayer  = $EngineSound

@export var stats : Stats

@export var upgrade_array : Array[BaseUpgradeResource]

@export var screen_width: float = 1080  
@export var screen_height: float = 1920  
@export var screen_offset: float = 50  

var target_move_position: Vector2 = Vector2.ZERO
var target_look_position: Vector2 = Vector2.ZERO
var moving = false
var aiming = false
var last_tap_time = 0.0
const DOUBLE_TAP_TIME = 0.3  # Time interval for double tap detection

@export var acceleration: float = 800.0
@export var deceleration: float = 1000.0
@export var max_speed: float = 200.0
@export var start_delay: float = 0.2  # Delay before reaching max speed

var move_start_time = 0.0
var speed_factor = 0.0  # Controls gradual acceleration/deceleration

@onready var aim_indicator = $"../AimIndicator"  # Node for aim marker
@onready var move_indicator = $"../MoveIndicator"  # Node for move marker

func _ready():
	set_upgrade_ids()
	aim_indicator.hide()
	move_indicator.hide()

func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed:
			var current_time = Time.get_ticks_msec() / 1000.0
			if current_time - last_tap_time < DOUBLE_TAP_TIME:
				target_move_position = event.position
				moving = true
				move_start_time = current_time
				speed_factor = 0.0  
				move_indicator.global_position = target_move_position
				move_indicator.show()
			else:
				target_look_position = event.position
				aiming = true
				aim_indicator.global_position = target_look_position
				aim_indicator.show()
			last_tap_time = current_time

func _physics_process(delta: float) -> void:
	if moving:
		var current_time = Time.get_ticks_msec() / 1000.0
		var direction = (target_move_position - global_position).normalized()
		var distance = global_position.distance_to(target_move_position)

		# Gradual acceleration
		if current_time - move_start_time < start_delay:
			speed_factor = (current_time - move_start_time) / start_delay
		else:
			speed_factor = 1.0  # Full speed after delay

		# Slow down as the player approaches the target
		var slow_down_factor = clamp(distance / 300.0, 0.0, 1.0)
		var effective_speed = stats.max_speed * speed_factor * slow_down_factor
		velocity = velocity.move_toward(direction * effective_speed, stats.acceleration * delta)

		if distance < 10:
			moving = false  # Stop when close enough
			velocity = Vector2.ZERO
			move_indicator.hide()

	move_and_slide()
	
	# Rotate to face the aim target only
	if aiming and target_look_position != Vector2.ZERO:
		var direction_vector = (target_look_position - global_position).normalized()
		var target_angle = direction_vector.angle()
		target_angle += deg_to_rad(90)
		rotation = lerp_angle(rotation, target_angle, stats.rotation_speed * delta)
	
	wrap_around_screen()

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

func set_upgrade_ids():
	var i : int = 0
	for upgrade in upgrade_array:
			upgrade.upgrade_id = i
			i += 1

func get_upgrade_array() -> Array[BaseUpgradeResource]:
	return upgrade_array

func take_damage(damage):
	stats.health += damage
	print(stats.health)
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
