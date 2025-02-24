extends ShootLogicResource
class_name  DefaultShootLogicResource

@export var spread_angle: float = 45  

func shoot(shoot_manager: Node2D, shoot_spot_array: Array[Node2D], bullet_scene: PackedScene, stats: Stats, bullet_sound: AudioStreamPlayer):
	var player = shoot_manager.get_parent()
	var center_position = shoot_spot_array[0].global_position  
	
	var angle_step = deg_to_rad(spread_angle) / (stats.bullet_count - 1)
	var start_angle = -deg_to_rad(spread_angle) / 2  

	for i in range(stats.bullet_count):
		
		var bullet_angle = start_angle + (angle_step * i) + player.rotation + deg_to_rad(-90)
		var bullet_direction = Vector2(cos(bullet_angle), sin(bullet_angle)).normalized()
		
		var bullet = bullet_scene.instantiate()
		shoot_manager.get_parent().get_parent().add_child(bullet)
		bullet.global_position = center_position
		bullet.initialize_bullet(bullet_angle, bullet_direction, stats.bullet_speed, stats.damage)
		bullet.rotation += deg_to_rad(90)
		
	bullet_sound.play()
