extends Control

@export var upgrade_array : Array[BaseUpgradeResource]

@export var button_array : Array[Button]

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	
	var current_player = get_tree().get_nodes_in_group("Player")
	
	if current_player.size() == 0:
		print("Error: No player with the 'Player' tag found!")
		return
		
	upgrade_array = current_player[0].get_upgrade_array()
		
	for button in button_array:
		var index = randi_range(0,  upgrade_array.size()-1)
		button.initialize_button(upgrade_array[index].upgrade_id,
								upgrade_array[index].upgrade_name, 
								upgrade_array[index].upgrade_decription)


func _on_button_pressed() -> void:
	Click.play()
	get_tree().create_timer(0.3)
	Globals.resume_game()
	queue_free()
	pass # Replace with function body.


func _on_button_2_pressed() -> void:
	Click.play()
	get_tree().create_timer(0.3)

func _on_upgrade_item_button_button_up() -> void:
	Click.play()
	get_tree().create_timer(0.3)
	Globals.resume_game()
	queue_free()
	pass # Replace with function body.
