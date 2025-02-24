extends BaseUpgradeResource
class_name BulletSpeedUpgradeResource

@export var bullet_speed_increase_amout : int

func apply_upgrade(stats : Stats):
	stats.bullet_speed += bullet_speed_increase_amout
