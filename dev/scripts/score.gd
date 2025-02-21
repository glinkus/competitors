extends Control
@onready var label_3: Label = $Label3
@onready var label_4: Label = $Label4


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	label_3.text = str(Globals.score)
	label_4.text = "Didžiausias pasiektas rezultatas: " + str(Globals.high_score)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass


func _on_button_to_main_menu_pressed() -> void:
	Globals.main_menu()
