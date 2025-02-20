extends Sprite2D

@onready var parent = $".."
var pressing = false
var touch_position
@export var maxLength = 50
var deadzone = 15
var hold_timer = -1.0
const HOLD_THRESHOLD = 0.2 
var touch_start_position = Vector2()  

func _ready():
	deadzone = parent.deadzone
	maxLength *= parent.scale.x
	global_position = parent.global_position
	parent.visible = false

func _process(delta):
	if hold_timer >= 0.0: 
		hold_timer += delta
		if hold_timer >= HOLD_THRESHOLD:
			pressing = true
			parent.visible = true
			global_position = touch_start_position
			touch_position = touch_start_position
			parent.global_position = touch_start_position
			hold_timer = -1.0 
	if pressing:
		if touch_position.distance_to(parent.global_position) <= maxLength:
			global_position = touch_position
		else:
			var angle = parent.global_position.angle_to_point(touch_position)
			global_position.x = parent.global_position.x + cos(angle)*maxLength
			global_position.y = parent.global_position.y + sin(angle)*maxLength
		calculateVector()
	else:
		global_position = lerp(global_position, parent.global_position, delta * 50)
		parent.posVector = Vector2(0, 0)

func calculateVector():
	if abs((global_position.x - parent.global_position.x)) >= deadzone:
		parent.posVector.x = (global_position.x - parent.global_position.x) / maxLength
	if abs((global_position.y - parent.global_position.y)) >= deadzone:
		parent.posVector.y = (global_position.y - parent.global_position.y) / maxLength

func _input(event):
	if event is InputEventScreenDrag:
		if pressing:  
			touch_position = event.position
	
	if event is InputEventScreenTouch:
		if event.pressed:

			hold_timer = 0.0
			touch_start_position = event.position
		else:
			pressing = false
			parent.visible = false
			hold_timer = -1.0  
