extends BaseUpgradeResource
class_name SpeedUpgradeResource

@export var speed_increase_amout : int

func apply_upgrade(stats : Stats):
	stats.max_speed += speed_increase_amout
