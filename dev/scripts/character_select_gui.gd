extends Panel

const TANK_PLAYER = preload("res://nodes/tank_player.tscn")
const SCOUT_PLAYER = preload("res://nodes/scout_player.tscn")
const SOlDIER_PLAYER = preload("res://nodes/player.tscn")

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass
	
	
func _on_char_item_button_3_pressed() -> void:
	swap_player(SOlDIER_PLAYER)
	Globals.resume_game()
	Click.play()
	queue_free()

func _on_char_item_button_2_pressed() -> void:
		# Scout char swap
	swap_player(SOlDIER_PLAYER)
	Globals.resume_game()
	Click.play()
	queue_free()


func _on_char_item_button_pressed() -> void:
	# Tank char swap
	swap_player(TANK_PLAYER)
	Globals.resume_game()
	Click.play()
	queue_free()


func swap_player(new_player_scene: PackedScene) -> void:
	var current_player = get_tree().get_nodes_in_group("Player")

	if current_player.size() == 0:
		print("Error: No player with the 'Player' tag found!")
		return

	var player = current_player[0]
	
	var player_parent = player.get_parent()
	
	var player_position = player.global_position
	var player_rotation = player.rotation

	player.queue_free()

	var new_player = new_player_scene.instantiate()
	player_parent.add_child(new_player)

	new_player.global_position = player_position
	new_player.rotation = player_rotation
	new_player.name = "Player"
