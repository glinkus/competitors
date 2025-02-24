extends Control

@onready var health_bar = $TextureProgressBar

var max_health = 0
var current_health = 100
var count = 0

func set_max(value :float):
	if(count == 0):
		health_bar.max_value = value
	count = count + 1
	
func _ready():
	update_health_bar()

func update_health_bar():
	health_bar.value = health_bar.max_value - current_health
	
