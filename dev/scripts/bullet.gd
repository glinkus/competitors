extends Area2D

@export var speed = 100
@export var damage = -1
@onready var death_particles: GPUParticles2D = $DeathParticles
var direction = Vector2.RIGHT  # Default direction (right)

# Method to set the bullet's rotation and direction
func initialize_bullet(new_rotation: float, new_direction: Vector2, bullet_speed: float):
	rotation = new_rotation  # Set the bullet's rotation
	direction = new_direction.normalized()  # Normalize the direction vector to ensure consistent speed
	speed = bullet_speed

func _physics_process(delta):
	# Move the bullet in the specified direction
	global_position += direction * speed * delta

func _on_visible_on_screen_notifier_2d_screen_exited():
	queue_free()  # Remove the bullet when it exits the screen

func _on_area_entered(area):
	pass
	#if area is Enemy:
	#	area.take_damage(damage)
	#	queue_free()

func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("Enemy"):
		body.take_damage(damage)
		var childs = get_children()
		for child in childs:
			if child != death_particles:
				child.queue_free()
		death_particles.emitting = true
		death_particles.scale = Vector2(0.2, 0.2)
		await death_particles.finished
		queue_free()
