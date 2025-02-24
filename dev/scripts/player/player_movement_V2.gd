extends CharacterBody2D
#@onready var joystick = $"../Camera2D/Joystick"

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

# Variable to store the tapped position
var target_look_position: Vector2 = Vector2.ZERO
var target_move_position: Vector2 = Vector2.ZERO
var moved_by_touch = false

func _input(event: InputEvent) -> void:
	# Check for touch input
	if event is InputEventScreenTouch:
		if event.pressed:
			target_look_position = event.position
			if moved_by_touch:
				target_move_position = event.position
		else:
			moved_by_touch = false
			print("No touch")
	elif event is InputEventScreenDrag:
		if moved_by_touch:
			target_move_position = event.position

func _physics_process(delta: float) -> void:
	# Get input for movement
	#var direction = joystick.posVector
#
	## Normalize the direction to prevent faster diagonal movement
	#if direction.length() > 0:
		#direction = direction.normalized()
#
	## Apply acceleration
	#if direction != Vector2.ZERO:
		#velocity = velocity.move_toward(direction * max_speed, acceleration * delta)
	#else:
		## Apply deceleration when no input is pressed
		#velocity = velocity.move_toward(Vector2.ZERO, deceleration * delta)

	if moved_by_touch:
		global_position = global_position.lerp(target_move_position, 0.1)	# Move the character

	#print(target_move_position)
	move_and_slide()

	# Rotate towards the tapped position
	if target_look_position != Vector2.ZERO:
		var direction_to_target = (target_look_position - global_position).normalized()
		var target_angle = direction_to_target.angle()  # Get the angle to the target
		# Adjust the angle to make the triangle point in the correct direction
		target_angle += deg_to_rad(90)  # Add 90 degrees offset to align the triangle's point
		rotation = lerp_angle(rotation, target_angle, rotation_speed * delta)
	
	if moved_by_touch:
		if target_move_position.length() > 0:
			var direction_to_target = (target_move_position - global_position).normalized()
			var target_angle = direction_to_target.angle()  # Get the angle to the target
			# Adjust the angle to make the triangle point in the correct direction
			target_angle += deg_to_rad(90)  # Add 90 degrees offset to align the triangle's point
			rotation = target_angle
	
	# Wrap around the screen
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


func _on_area_2d_input_event(viewport: Node, event: InputEvent, shape_idx: int) -> void:
	if event is InputEventScreenTouch:
		if event.pressed:
			moved_by_touch = true
		else:
			moved_by_touch = false
			

func take_damage(damage):
	heal += damage
	#if heal <= 0:
	#game_over()
