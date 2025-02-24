extends Node
class_name UpgradeTextInitializer

var upgrade_id : int
@onready var name_label : Label = $MarginContainer/VBoxContainer/Name
@onready var description_label : Label = $MarginContainer/VBoxContainer/Descryption

func initialize_button(id: int, name_text : String, description_text: String):
	upgrade_id = id
	name_label.text = name_text
	description_label.text = description_text


func _on_pressed() -> void:
	Globals.apply_upgrade(upgrade_id)
	Globals.resume_game()
	Click.play()
	get_parent().get_parent().get_parent().queue_free()
	pass # Replace with function body.
