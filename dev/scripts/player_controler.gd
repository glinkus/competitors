extends CharacterBody2D

@onready var joystick = $"../Camera2D/Joystick"


@export var heal: float = 10.0
@export var max_speed: float = 100.0
@export var acceleration: float = 800.0
@export var deceleration: float = 1000.0
@export var rotation_speed: float = 10.0 

@export var screen_width: float = 1080  
@export var screen_height: float = 1920  
@export var screen_offset: float = 50  

var target_look_position: Vector2 = Vector2.ZERO

var tap_start_time = 0.0
var tap_start_position = Vector2()
const TAP_THRESHOLD = 0.2  

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

	if direction.length() > 0:
		direction = direction.normalized()

	if direction != Vector2.ZERO:
		velocity = velocity.move_toward(direction * max_speed, acceleration * delta)
	else:
		velocity = velocity.move_toward(Vector2.ZERO, deceleration * delta)

	move_and_slide()
	
	rotate_to_tapped_position(delta)
	wrap_around_screen()
	
func rotate_to_tapped_position(delta : float):
	if target_look_position != Vector2.ZERO:
		var direction_to_target = (target_look_position - global_position).normalized()
		var target_angle = direction_to_target.angle()  # Get the angle to the target
		# Adjust the angle to make the triangle point in the correct direction
		target_angle += deg_to_rad(90)  # Add 90 degrees offset to align the triangle's point
		rotation = lerp_angle(rotation, target_angle, rotation_speed * delta)

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

func take_damage(damage):
	heal += damage
	#if heal <= 0:
		#game_over()
