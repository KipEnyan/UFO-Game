import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject

class Missile(DirectObject):
	def __init__(self):
		self.model = loader.loadModel("Art/missile.egg")
		self.acc = .01
		self.speed = .2

	def seek (self, player):
		self.speed += self.acc
		self.model.lookAt(player)
		self.model.setY(self.model, self.speed)