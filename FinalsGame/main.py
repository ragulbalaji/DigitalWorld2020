from kivy.app import App
from kivy.lang import Builder
from kivy.core.audio import SoundLoader
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.core.text import Label as CoreLabel
from kivy.clock import Clock
from kivy.graphics import *
from kivy.metrics import *

GAME_FPS = 1.0/60.0
GAME_WIDTH = 800
GAME_HEIGHT = 600
GAME_DIM = (GAME_WIDTH, GAME_HEIGHT)

from kivy.config import Config
Config.set('graphics', 'resizable', False) # Fixed Size
Config.set('graphics', 'width', str(GAME_WIDTH))
Config.set('graphics', 'height', str(GAME_HEIGHT))
Config.write()

snd_hit = SoundLoader.load('assets/snd/Hit.wav')
snd_pickup = SoundLoader.load('assets/snd/Pickup.wav')
snd_shoot = SoundLoader.load('assets/snd/Shoot.wav')

CLR_RED = (1,0,0,1)
CLR_GRN = (0,1,0,1)
CLR_BLU = (0,0,1,1)
CLR_WHI = (1,1,1,1)
CLR_GRY = (0.5,0.5,0.5,1)
CLR_BLK = (0,0,0,1)
def texLabel(msg, sz, pos, clr):
	tlabel = CoreLabel(text=msg, font_size=sp(sz), color=clr)
	tlabel.refresh()
	return Rectangle(pos=(dp(pos[0]), dp(pos[1])), texture=tlabel.texture, size=list(tlabel.texture.size))

curid = 0
def getNextId():
	global curid
	curid += 1
	return curid

class Entity():
	def __init__(self, **kwargs):
		self.id = getNextId()
		self.pos = kwargs['pos']
		self.size = kwargs['size']
	def update(self, dt):
		pass
	def render(self, dt):
		pass

class myBox(Entity):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
	def update(self, dt):
		xp, yp = self.pos
		self.pos = (xp, yp + self.id * 50 * dt)

	def render(self, dt):
		return Rectangle(pos=self.pos, size=self.size)

class GameCanvas(FocusBehavior, Widget):
	gameobjects = []
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		
		# init objs
		for i in range(10):
			self.gameobjects.append(myBox(pos=(dp(i*50),dp(0)), size=(dp(50),dp(50))))
		
		Clock.schedule_interval(self.tick, GAME_FPS)

	def tick(self, dt):
		if not self.focused:
			self.canvas.clear() # Clear
			self.canvas.add(texLabel("Click to focus", 100, (0,0), CLR_RED))
			return
		#print('Tick', dt)
		
		# update
		for obj in self.gameobjects:
			obj.update(dt)
		
		# render
		self.canvas.clear() # Clear
		for obj in self.gameobjects:
			self.canvas.add(obj.render(dt)) 

class MainMenu(Screen):
	pass
class GameScreen(Screen):
	pass
class ScreenMgr(ScreenManager):
	pass
layouts = Builder.load_file('layouts.kv')
class GameApp(App):
	title = 'Tanks! | Ragul Balaji 2020 | Digital World 10.009'
	def build(self):
		print(self.title)
		#snd_pickup.play()
		return layouts

gameapp = GameApp()
gameapp.run()