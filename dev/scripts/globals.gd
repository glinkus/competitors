extends Node

const POWER_UP_SCENE = preload("res://scenes/power_up_scene.tscn")

var high_score = 0
var score = 0
var is_game_over = false

func _ready() -> void:
	main_menu()

func main_menu():
	score = 0
	is_game_over = false
	get_tree().change_scene_to_file("res://scenes/start_menu.tscn")

func start_game():
	score = 0
	is_game_over = false
	get_tree().change_scene_to_file("res://scenes/main_map.tscn")

func pause_game():
	get_tree().paused = true
	var power_up_scene = POWER_UP_SCENE.instantiate()
	get_tree().root.add_child(power_up_scene)

func game_over():
	is_game_over = true
	if high_score < score:
		high_score = score
	get_tree().change_scene_to_file("res://scenes/the_end.tscn")
