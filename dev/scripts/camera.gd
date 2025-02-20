extends Camera2D

var rng = RandomNumberGenerator.new()
var shake_streangth: float = 0.0
var shake_fade: float = 5.0

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	if shake_streangth > 0:
		shake_streangth = lerpf(shake_streangth, 0, shake_fade * delta)
		offset = randomOffset()

func shake_camera(streangth):
	shake_streangth = streangth

func randomOffset() -> Vector2:
	return Vector2(rng.randf_range(-shake_streangth,shake_streangth),rng.randf_range(-shake_streangth,shake_streangth))
