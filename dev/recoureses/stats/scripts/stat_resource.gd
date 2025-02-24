extends Resource
class_name Stats

@export var health : int

@export var max_speed : int
@export var acceleration : int
@export var deceleration : int

@export var rotation_speed : int

@export var fire_rate : float
@export var bullet_speed: float
@export var bullet_count: int
@export var damage : float

func reset(stats: Stats):
	# Set the current stats to the values provided in the 'stats' parameter
	self.health = stats.health
	self.max_speed = stats.max_speed
	self.acceleration = stats.acceleration
	self.deceleration = stats.deceleration
	self.rotation_speed = stats.rotation_speed
	self.fire_rate = stats.fire_rate
	self.bullet_speed = stats.bullet_speed
	self.bullet_count = stats.bullet_count
	self.damage = stats.damage
	
