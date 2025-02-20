extends Sprite2D
'''
Creator: Darius Rupsys
'''
var blink_interval: float = 0.3
var current_time: float = 0.3
var alpha: float = 1.0

func _ready():
	set_visible(true)

func _process(delta: float):
	current_time -= delta
	if current_time <= 0:
		current_time = blink_interval
		if alpha == 0.0:
			alpha = 1.0
		else:
			alpha = 0.0

	modulate.a = alpha

func _on_timer_timeout() -> void:
	queue_free()
