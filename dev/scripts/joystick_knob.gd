extends Sprite2D

@onready var parent = $".."

var pressing = false
var touch_position

@export var maxLength = 50
var deadzone = 15

func _ready():
	deadzone = parent.deadzone
	maxLength *= parent.scale.x
	# Ensure the joystick starts at a reasonable initial position (relative to the parent)
	global_position = parent.global_position  # Set joystick's initial position based on parent
	# Initially hide the joystick or set it to an inactive state
	parent.visible = false

func _process(delta):
	if pressing:
		# Update joystick position based on touch, but limit movement within maxLength
		if touch_position.distance_to(parent.global_position) <= maxLength:
			global_position = touch_position
			pass
		else:
			var angle = parent.global_position.angle_to_point(touch_position)
			global_position.x = parent.global_position.x + cos(angle)*maxLength
			global_position.y = parent.global_position.y + sin(angle)*maxLength
		calculateVector()
	else:
		# Smoothly move joystick back to parent if touch is released
		global_position = lerp(global_position, parent.global_position, delta * 50)
		parent.posVector = Vector2(0, 0)
		
func calculateVector():
	# Calculate the joystick's direction vector based on its position relative to the parent
	if abs((global_position.x - parent.global_position.x)) >= deadzone:
		parent.posVector.x = (global_position.x - parent.global_position.x) / maxLength
	if abs((global_position.y - parent.global_position.y)) >= deadzone:
		parent.posVector.y = (global_position.y - parent.global_position.y) / maxLength

func _input(event):
	
	if event is InputEventScreenDrag:
		touch_position = event.position
		
	if event is InputEventScreenTouch:
		if event.pressed:
			# When touch starts, set the joystick's position to the touch position
			global_position = event.position
			touch_position = event.position
			parent.global_position = event.position  # Set the center point of the joystick to the touch position
			pressing = true
			parent.visible = true  # Show the joystick when pressed
		else:
			# When touch ends, hide the joystick and stop movement
			pressing = false
			parent.visible = false  # Hide the joystick when not pressing
