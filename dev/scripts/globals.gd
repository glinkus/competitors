extends Node

#const POWER_UP_SCENE = preload("res://scenes/power_up_scene.tscn")
const POWER_UP_SCENE = preload("res://scenes/level_up_gui.tscn")
const CHAR_SELECT_SCENE = preload("res://scenes/character_select_gui.tscn")

var high_score = 0
var score = 0
var is_game_over = false
var is_first_upgrade : bool
var leaderboard : Array[LeaderboardData]

class LeaderboardData:
	var total_score : int
	var time : Dictionary
	func _init(_total_score : int) -> void:
		total_score = _total_score
		time = Time.get_time_dict_from_system()

func _ready() -> void:
	is_first_upgrade = true
	main_menu()

func main_menu():
	score = 0
	is_game_over = false
	is_first_upgrade = true
	get_tree().change_scene_to_file("res://scenes/start_menu.tscn")

func start_game():
	score = 0
	is_game_over = false
	is_first_upgrade = true
	get_tree().change_scene_to_file("res://scenes/main_map.tscn")

func pause_game():
	get_tree().paused = true
	
	if(is_first_upgrade):
		var char_select = CHAR_SELECT_SCENE.instantiate()
		get_tree().root.add_child(char_select)
		is_first_upgrade = false
	else:
		var power_up_scene = POWER_UP_SCENE.instantiate()
		get_tree().root.add_child(power_up_scene)
		
func resume_game():
	get_tree().paused = false

func game_over():
	is_game_over = true
	if high_score < score:
		high_score = score
	var _data = LeaderboardData.new(
		score
	)
	leaderboard.append(_data)
	leaderboard.sort_custom(func(a, b): return a.total_score > b.total_score)
	get_tree().change_scene_to_file("res://scenes/the_end.tscn")

func take_xp():
	score += 2
	if score % 20 == 0:
		pause_game()

func apply_upgrade(upgrade_id: int):
	var player = get_tree().get_first_node_in_group("Player")
	player.apply_upgrade(upgrade_id)
