import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject

class Missile(DirectObject):
	def __init__(self):
		self.model = loader.loadModel("Art/missile.egg")
		self.acc = .005
		self.speed = .1

	def seek (self, player):
		self.speed += self.acc
		self.model.lookAt(player)
		self.model.setY(self.model, self.speed)