extends Node2D

signal laser_shot(laser_scene, location)

@export var rate_of_fire = 1
@export var bullet_speed = 800
@onready var laser_container = $"."
@onready var shoot_spot = $ShootSpot
@onready var bullet_scene = preload("res://scenes/bullet.tscn")
var shoot_cd := false
# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


func _process(delta):
		if !shoot_cd:
			shoot_cd = true
			shoot()
			await get_tree().create_timer(rate_of_fire).timeout
			shoot_cd = false
			
			
func shoot():
	var bullet = bullet_scene.instantiate()
	get_parent().get_parent().add_child(bullet)
	bullet.global_position = shoot_spot.global_position
	# Get the player's rotation
	var player_rotation = get_parent().rotation
	# Calculate the bullet's direction based on the player's rotation
	var bullet_direction = Vector2(0, -1).rotated(player_rotation).normalized()
	# Set the bullet's rotation and direction
	bullet.initialize_bullet(player_rotation, bullet_direction, bullet_speed)
	# Calculate the movement direction based on the player's rotation
