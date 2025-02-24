extends Node2D

@export var player : PlayerManager

@onready var stats : Stats = player.stats
@export var shoot_logic: ShootLogicResource

@export var rate_of_fire = 0.5
@export var bullet_speed = 800
@export var shoot_spot_array : Array[Node2D]
@onready var bullet_scene = preload("res://scenes/bullet.tscn")
@onready var bullet_sound = $ShootSound


var shoot_cd := false

func _ready() -> void:
	pass 

func _process(delta):
	if !shoot_cd:
		shoot_cd = true
		shoot_logic.shoot(self, shoot_spot_array, bullet_scene, stats, bullet_sound)
		await get_tree().create_timer(stats.fire_rate).timeout
		shoot_cd = false
			
			
func shoot():
	if shoot_spot_array.size() > 0:
		for shoot_spot in shoot_spot_array:
			var bullet = bullet_scene.instantiate()
			get_parent().get_parent().add_child(bullet)
			bullet.global_position = shoot_spot.global_position
			var player_rotation = get_parent().rotation
			var bullet_direction = Vector2(0, -1).rotated(player_rotation).normalized()
			bullet.initialize_bullet(player_rotation, bullet_direction, stats.bullet_speed, stats.damage)
			bullet_sound.play()
