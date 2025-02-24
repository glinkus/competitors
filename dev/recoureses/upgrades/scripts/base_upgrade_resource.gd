extends Resource
class_name BaseUpgradeResource

@export var upgrade_id : int
@export var upgrade_icon : CompressedTexture2D
@export var upgrade_name : String
@export var upgrade_decription : String
	
func apply_upgrade(stats : Stats):
	pass
