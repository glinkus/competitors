extends Button


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass


func _on_pressed() -> void:
	Click.play()
	get_tree().create_timer(0.3)
	Globals.start_game()
	#get_tree().change_scene_to_file("res://scenes/main_map.tscn")
