extends Control

const LEADERBOARD_ITEM = preload("res://nodes/leaderboard_item.tscn")
@onready var label_3: Label = $Label3
@onready var label_4: Label = $Label4
@onready var leaderboard: Control = $Leaderboard
@onready var v_box_container: VBoxContainer = $VBoxContainer

var label_theme: LabelSettings
var label_theme_head: LabelSettings

func _ready() -> void:
	label_3.text = str(Globals.score)
	label_theme = load("res://assets/the_end.tres")
	label_theme_head = load("res://assets/the_end_head.tres")
	

	var header_row = HBoxContainer.new()
	header_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL

	var rank_header = Label.new()
	rank_header.text = "Vieta"
	rank_header.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	rank_header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	
	var score_header = Label.new()
	score_header.text = "Taškai"
	score_header.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	score_header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	
	var time_header = Label.new()
	time_header.text = "Laikas"
	time_header.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	time_header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

	rank_header.label_settings = label_theme_head
	score_header.label_settings = label_theme_head
	time_header.label_settings = label_theme_head

	header_row.add_child(rank_header)
	header_row.add_child(score_header)
	header_row.add_child(time_header)

	v_box_container.add_child(header_row)

	var count = 0
	for score in Globals.leaderboard:
		count += 1

		var row = HBoxContainer.new()
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL

		var rank_label = Label.new()
		rank_label.text = str(count)
		rank_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		rank_label.label_settings = label_theme
		rank_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		
		var score_label = Label.new()
		score_label.text = str(score.total_score)
		score_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		score_label.label_settings = label_theme
		score_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

		var time_label = Label.new()
		time_label.text = str(score.time["hour"]) + ":" + str(score.time["minute"]) + ":" + str(score.time["second"])
		time_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		time_label.label_settings = label_theme
		time_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER

		row.add_child(rank_label)
		row.add_child(score_label)
		row.add_child(time_label)

		v_box_container.add_child(row) 

		if count >= 10:
			break




# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass

func _on_button_to_main_menu_pressed() -> void:
	Click.play()
	get_tree().create_timer(0.3)
	Globals.main_menu()
