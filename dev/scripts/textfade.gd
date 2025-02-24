extends Label

@onready var timer: Timer = $Timer

func _ready():
	timer.wait_time = 5
	timer.start()

func _on_timer_timeout() -> void:
	visible = false
