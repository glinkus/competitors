extends Control

const LEADERBOARD_ITEM = preload("res://nodes/leaderboard_item.tscn")
@onready var label_3: Label = $Label3
@onready var label_4: Label = $Label4
@onready var leaderboard: Control = $Leaderboard
@onready var v_box_container: VBoxContainer = $VBoxContainer

func _ready() -> void:
	label_3.text = str(Globals.score)
	var count = 0
	for score in Globals.leaderboard:
		count += 1
		var item = LEADERBOARD_ITEM.instantiate()
		item.get_node("Label").text = str(count) + ". "
		item.get_node("Score").text = str(score.total_score)
		item.get_node("Time").text = str(score.time["hour"]) + ":" + str(score.time["minute"]) + ":" + str(score.time["second"])
		v_box_container.add_child(item)
		if count >= 10:
			break

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass

func _on_button_to_main_menu_pressed() -> void:
	Click.play()
	get_tree().create_timer(0.3)
	Globals.main_menu()
