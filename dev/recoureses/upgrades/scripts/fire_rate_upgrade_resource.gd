extends BaseUpgradeResource
class_name FireRateUpgradeResource

@export var fire_rate_increase_amout : float

func apply_upgrade(stats : Stats):
	if stats.fire_rate > 0.2:
		stats.fire_rate -= fire_rate_increase_amout
