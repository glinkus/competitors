extends BaseUpgradeResource
class_name BulletCountUpgradeResource

@export var bullet_increase_amout : int
@export var damage_decrease_amout : float

func apply_upgrade(stats : Stats):
	stats.bullet_count += bullet_increase_amout
	stats.damage += damage_decrease_amout
