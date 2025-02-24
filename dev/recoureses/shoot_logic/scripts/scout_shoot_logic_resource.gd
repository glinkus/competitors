extends ShootLogicResource
class_name  ScoutShootLogicResource


func shoot(shoot_manager: Node2D, shoot_spot_array: Array[Node2D], bullet_scene: PackedScene, 
			stats: Stats, bullet_sound: AudioStreamPlayer):
	if shoot_spot_array.size() > 0:
		for shoot_spot in shoot_spot_array:
			var bullet = bullet_scene.instantiate()
			shoot_manager.get_parent().get_parent().add_child(bullet)
			bullet.global_position = shoot_spot.global_position
			var player_rotation = shoot_manager.get_parent().rotation
			var bullet_direction = Vector2(0, -1).rotated(player_rotation).normalized()
			bullet.initialize_bullet(player_rotation, bullet_direction, stats.bullet_speed, stats.damage)
			bullet_sound.play()
