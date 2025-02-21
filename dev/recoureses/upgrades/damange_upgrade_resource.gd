extends BaseUpgradeResource
class_name DamageUpgradeResource

@export var damage_increase_amout : int

func apply_upgrade(stats : Stats):
	stats.damage -= damage_increase_amout
