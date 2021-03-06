###############################################################################
#            Object Chaser Controller | Template v 1.0 | UPBGE 0.2.3          #
###############################################################################
#                      Created by: Guilherme Teres Nunes                      #
#                       Access: youtube.com/UnidayStudio                      #
#                               github.com/UnidayStudio                       #
###############################################################################
# This component will make the object chase another object with certain
# distance.
# You can change the Target object by calling the function setTarget()
# 	It's very simple to configure:
#	-> Activate: Activate or deactivate the logic
#	-> Navmesh Name: The name of your navmesh
#	-> Target Object: The name of your target
#	-> Min Distance: The minimum distance that you want the object from the
#                    target
#	-> Tolerance Distance: Once the object is already near the target, the
#                          extra tolerance distance that they can have before
#                          it starts chasing again.
#	-> Speed: The speed of the object while chasing the target
#	-> Front Axis: The front Axis (put Y axis if you don't know)
#	-> Up Axis: The up Axis (put Z if you don't know)
#	-> Smooth Turn: To smooth the path following turns.
###############################################################################
import bge
from mathutils import Vector

class ObjectChaser(bge.types.KX_PythonComponent):
	args = {
		"Activate"          : True,
		"Navmesh Name"      : "",
		"Target Object"     : "",
		"Min Distance"      : 2.0,
		"Tolerance Distance": 1.0,
		"Speed"             : 0.1,
		"Front Axis"        : {"Z Axis", "Y Axis", "X Axis"},
		"Up Axis"           : {"Z Axis", "Y Axis", "X Axis"},
		"Smooth Turn"       : 0.5,
	}

	# Start Function
	def start(self, args):
		scene = bge.logic.getCurrentScene()

		self.active 	= args["Activate"]
		self.navmesh	= scene.objects[args["Navmesh Name"]]
		self.target 	= scene.objects[args["Target Object"]]

		self.minDist    = args["Min Distance"]
		if self.minDist < 1:
			self.minDist = 1
		self.tolerance  = args["Tolerance Distance"]
		self.speed      = args["Speed"]

		self.upAxis    = {"X Axis":0, "Y Axis":1, "Z Axis":2}[args["Up Axis"]]
		self.frontAxis = {"X Axis":0, "Y Axis":1, "Z Axis":2}[args["Front Axis"]]
		self.smoothTurn = args["Smooth Turn"]

		self.__stopped   = True
		self.__targetPos = None
		self.__path 	 = None

	# Public function to allow changing the Target Object in realtime.
	# You can pass the new object by name (string) or by reference (GameObject)
	def setTarget(self, obj):
		scene = bge.logic.getCurrentScene()

		if type(obj) == type(""):
			self.target = scene.objects[obj]
		else:
			self.target = obj

	# Makes the object chase the target
	def chaseTarget(self):
		# Calculating the path only when the target object moves.
		# This will avoid unecessary logic consuming.
		if self.__targetPos != self.target.worldPosition:
			self.__targetPos = self.target.worldPosition.copy()
			self.__path = self.navmesh.findPath(self.object.worldPosition, self.__targetPos)

		if len(self.__path) > 0:
			vec = self.object.getVectTo(self.__path[0])
			if vec[0] < 0.5 + self.minDist/2.0:
				self.__path = self.__path[1:]
				vec = self.object.getVectTo(self.__path[0])

			self.object.alignAxisToVect(vec[1], self.frontAxis, self.smoothTurn)
			self.object.alignAxisToVect([0,0,1],self.upAxis, 1)

			self.object.applyMovement([0,self.speed,0], True)

	# Update Function
	def update(self):
		if self.active:
			#print(self.__stopped)
			if self.__stopped:
				# The object isn't chasing the Target.
				maxDist = self.minDist + self.tolerance
				if self.object.getDistanceTo(self.target) > maxDist:
					self.__stopped = False
					self.__targetPos = None
			else:
				# The object needs to chase the Target
				self.chaseTarget()
				if self.object.getDistanceTo(self.target) < self.minDist:
					self.__stopped = True