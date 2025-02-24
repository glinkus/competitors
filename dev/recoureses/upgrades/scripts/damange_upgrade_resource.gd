extends BaseUpgradeResource
class_name DamageUpgradeResource

@export var damage_increase_amout : float

func apply_upgrade(stats : Stats):
	stats.damage -= damage_increase_amout
