import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject

class Missile(DirectObject):
	def __init__(self, x, y, z):
		self.model = loader.loadModel("missile")
		self.speed = 10
		self.model.reparentTo(render)
		self.model.setPos(x,y,z)

	def seek (self, player):
		self.model.lookAt(player)
		if self.model.getX() < player.getX():
			self.model.setX(self.model, self.speed)
		elif self.model.getX() > player.getX():
			self.model.setX(self.model, -self.speed)

		if self.model.getY() < player.getY():
			self.model.setY(self.model, self.speed)
		elif self.model.getY() > player.getY():
			self.model.setY(self.model, -self.speed)

		if self.model.getZ() < player.getZ():
			self.model.setZ(self.model, self.speed)
		elif self.model.getZ() > player.getZ():
			self.model.setZ(self.model, -self.speed)