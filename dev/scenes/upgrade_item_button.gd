extends Node
class_name UpgradeTextInitializer

var upgrade_id : int
@onready var icon : TextureRect = $Icon
@onready var name_label : Label = $Name
@onready var description_label : Label = $Descryption

func initialize_button(id: int, new_icon : CompressedTexture2D, name_text : String, description_text: String):
	upgrade_id = id
	name_label.text = name_text
	description_label.text = description_text
	icon.texture = new_icon


func _on_pressed() -> void:
	Globals.apply_upgrade(upgrade_id)
	Globals.resume_game()
	Click.play()
	get_parent().get_parent().queue_free()
	pass # Replace with function body.
