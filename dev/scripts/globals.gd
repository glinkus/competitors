extends Node

var high_score = 0
var score = 0
var is_game_over = false

func _ready() -> void:
	start_game()
	
func start_game():
	score = 0
	is_game_over = false

func game_over():
	is_game_over = true
	if high_score < score:
		high_score = score
