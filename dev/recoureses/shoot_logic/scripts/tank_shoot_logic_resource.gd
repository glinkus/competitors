extends ShootLogicResource
class_name  TankShootLogicResource

func shoot(shoot_manager: Node2D, shoot_spot_array: Array[Node2D], bullet_scene: PackedScene, stats: Stats, bullet_sound: AudioStreamPlayer):
	var player = shoot_manager.get_parent()
	var center_position = player.global_position 
	
	for i in range(stats.bullet_count):
		# Adds player rotation and -90 deg to shoot from the nose of the plane
		var angle = (2 * PI / stats.bullet_count) * i + player.rotation + deg_to_rad(-90)
		var bullet_direction = Vector2(cos(angle), sin(angle)).normalized()
		
		var bullet = bullet_scene.instantiate()
		shoot_manager.get_parent().get_parent().add_child(bullet)
		bullet.global_position = center_position
		bullet.initialize_bullet(angle, bullet_direction, stats.bullet_speed, stats.damage)
		bullet.rotation += deg_to_rad(90)
		
	bullet_sound.play()
