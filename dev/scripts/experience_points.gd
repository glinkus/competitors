extends Area2D

var velocity = Vector2()
var friction = 0.1 
# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if velocity.length() > 0.1:
		position += velocity * delta
		velocity.x = lerp(velocity.x, 0.0, 0.1)
		if abs(velocity.x) < 0.01:
			velocity.x = 0
		velocity.y = lerp(velocity.y, 0.0, 0.1)
		if abs(velocity.y) < 0.01:
			velocity.y = 0
	else:
		velocity = Vector2(0, 0)


func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("Player"):
		Globals.take_xp()
		queue_free()
