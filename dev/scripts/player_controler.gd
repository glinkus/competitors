extends CharacterBody2D

@onready var joystick = $"../Camera2D/Joystick"

# Movement variables
@export var heal: float = 10.0
@export var max_speed: float = 100.0
@export var acceleration: float = 800.0
@export var deceleration: float = 1000.0
@export var rotation_speed: float = 10.0  # Speed of rotation

# Screen boundaries (set these to your screen or map size)
@export var screen_width: float = 1080  # Width of the screen/map
@export var screen_height: float = 1920  # Height of the screen/map
@export var screen_offset: float = 50  # Height of the screen/map

func _physics_process(delta: float) -> void:
	# Get input for movement
	#var direction: Vector2 = Vector2.ZERO
	#direction.x = Input.get_axis("ui_left", "ui_right")
	#direction.y = Input.get_axis("ui_up", "ui_down")
	
	var direction = joystick.posVector

	# Normalize the direction to prevent faster diagonal movement
	if direction.length() > 0:
		direction = direction.normalized()

	# Apply acceleration
	if direction != Vector2.ZERO:
		velocity = velocity.move_toward(direction * max_speed, acceleration * delta)
	else:
		# Apply deceleration when no input is pressed
		velocity = velocity.move_toward(Vector2.ZERO, deceleration * delta)

	# Move the character
	move_and_slide()

	# Rotate the triangle to face the input direction
	if direction.length() > 0:
		var target_angle = direction.angle()  # Get the angle of the input direction
		# Adjust the angle to make the triangle point in the input direction
		target_angle += deg_to_rad(90)  # Add 90 degrees offset to align the triangle's point
		rotation = lerp_angle(rotation, target_angle, rotation_speed * delta)
		
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

func take_damage(damage):
	heal += damage
	#if heal <= 0:
		#game_over()
