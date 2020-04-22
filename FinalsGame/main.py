from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.core.text import Label as CoreLabel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import *
from kivy.metrics import *
import time
import random

GAME_FPS = 1.0/60.0
GAME_WIDTH = 1200
GAME_HEIGHT = 900
GAME_DIM = (GAME_WIDTH, GAME_HEIGHT)
GAME_OBJS = []
KEYS_ACTIVE = set()
TOUCH_ACTIVE = None

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
		kwargs.setdefault('pos', (0,0))
		kwargs.setdefault('rot', 0)
		kwargs.setdefault('size', (10,10))
		kwargs.setdefault('velocity', (0,0))
		kwargs.setdefault('accleration', (0,0))

		self.pos = Vector(kwargs['pos'])
		self.rot = kwargs['rot']
		self.size = Vector(kwargs['size'])
		self.velocity = Vector(kwargs['velocity'])
		self.accleration = Vector(kwargs['accleration'])
	def update(self, dt):
		pass
	def render(self, canvas):
		with canvas:
			PushMatrix()
			PopMatrix()
			pass

class myBox(Entity):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
	def update(self, dt):
		#self.velocity += self.accleration * dt
		self.pos += self.velocity * dt
		self.velocity *= 0.9
		print(self.pos, self.velocity, self.accleration)
	def render(self, canvas):
		with canvas:
			Color(*CLR_RED)
			Rectangle(pos=self.pos, size=self.size)

class Bullet(Entity):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.startpos = self.pos[:]
		self.size = Vector(dp(10), dp(10))
		self.range = dp(GAME_HEIGHT/2)
		snd_shoot.play()
	def update(self, dt):
		self.pos += self.velocity
		if self.pos.distance(self.startpos) > self.range:
			GAME_OBJS.remove(self)
	def render(self, canvas):
		with canvas:
			PushMatrix()
			Color(1, 0.149, 0.463, 1)
			Ellipse(pos=self.pos-self.size/2, size=self.size)
			PopMatrix()

class EnemyTank(Entity):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.speed = dp(100)
		self.rotspd = 120
		self.size = Vector(dp(46), dp(100))
		self.turretangle = 0
		self.turretsize = Vector(dp(60), dp(15))
		self.turretcorrection = Vector(0, dp(7.5))
		self.capsize = Vector(dp(44), dp(44))
		self.nextshottime = 0
		self.reloadtime = 1.0 / 2.5
	def update(self, dt):
		global KEYS_ACTIVE, TOUCH_ACTIVE
		if 'a' in KEYS_ACTIVE: self.rot += self.rotspd * dt
		if 'd' in KEYS_ACTIVE: self.rot -= self.rotspd * dt
		
		movedir = Vector(0, self.speed).rotate(self.rot)
		if 'w' in KEYS_ACTIVE: self.velocity = movedir
		if 's' in KEYS_ACTIVE: self.velocity = -0.5 * movedir

		if 'left' in KEYS_ACTIVE: self.turretangle += self.rotspd * dt
		if 'right' in KEYS_ACTIVE: self.turretangle -= self.rotspd * dt

		if TOUCH_ACTIVE != None: self.turretangle = -Vector(1,0).angle(Vector(TOUCH_ACTIVE.pos)-self.pos)

		if (TOUCH_ACTIVE != None or 'up' in KEYS_ACTIVE) and time.time() > self.nextshottime:
			self.nextshottime = time.time() + self.reloadtime
			bulletvel = Vector(dp(10),0).rotate(self.turretangle)
			GAME_OBJS.append(Bullet(pos=self.pos+Vector(dp(60), 0).rotate(self.turretangle), velocity=bulletvel))
			self.velocity -= 10 * bulletvel # knockback

		self.pos += self.velocity * dt
		self.velocity *= 0.9
		self.lowerleftpos = self.pos - self.size / 2
	def render(self, canvas):
		with canvas:
			PushMatrix()
			Color(1,1,1,1)
			Rotate(origin=self.pos, angle=self.rot)
			Rectangle(pos=self.lowerleftpos, size=self.size, source='assets/img/tank.png')
			PopMatrix()
			PushMatrix()
			Color(*CLR_RED)
			Ellipse(pos=self.pos-self.capsize/2, size=self.capsize)
			Rotate(origin=self.pos, angle=self.turretangle)
			Rectangle(pos=self.pos-self.turretcorrection, size=self.turretsize)
			PopMatrix()

class PlayerTank(Entity):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.health = 10
		self.speed = dp(100)
		self.rotspd = 120
		self.size = Vector(dp(46), dp(100))
		self.turretangle = 0
		self.turretsize = Vector(dp(60), dp(15))
		self.turretcorrection = Vector(0, dp(7.5))
		self.capsize = Vector(dp(44), dp(44))
		self.nextshottime = 0
		self.reloadtime = 1.0 / 3
	def update(self, dt):
		global KEYS_ACTIVE, TOUCH_ACTIVE
		if 'a' in KEYS_ACTIVE: self.rot += self.rotspd * dt
		if 'd' in KEYS_ACTIVE: self.rot -= self.rotspd * dt
		
		movedir = Vector(0, self.speed).rotate(self.rot)
		if 'w' in KEYS_ACTIVE: self.velocity = movedir
		if 's' in KEYS_ACTIVE: self.velocity = -0.5 * movedir

		if 'left' in KEYS_ACTIVE: self.turretangle += self.rotspd * dt
		if 'right' in KEYS_ACTIVE: self.turretangle -= self.rotspd * dt

		if TOUCH_ACTIVE != None: self.turretangle = -Vector(1,0).angle(Vector(TOUCH_ACTIVE.pos)-self.pos)

		if (TOUCH_ACTIVE != None or 'up' in KEYS_ACTIVE) and time.time() > self.nextshottime:
			self.nextshottime = time.time() + self.reloadtime
			bulletvel = Vector(dp(10),0).rotate(self.turretangle)
			GAME_OBJS.append(Bullet(pos=self.pos+Vector(dp(60), 0).rotate(self.turretangle), velocity=bulletvel))
			self.velocity -= 10 * bulletvel # knockback

		self.pos += self.velocity * dt
		self.velocity *= 0.9
		self.lowerleftpos = self.pos - self.size / 2
	def render(self, canvas):
		with canvas:
			PushMatrix()
			Color(1,1,1,1)
			Rotate(origin=self.pos, angle=self.rot)
			Rectangle(pos=self.lowerleftpos, size=self.size, source='assets/img/tank.png')
			PopMatrix()
			PushMatrix()
			Color(*CLR_BLU)
			Ellipse(pos=self.pos-self.capsize/2, size=self.capsize)
			Rotate(origin=self.pos, angle=self.turretangle)
			Rectangle(pos=self.pos-self.turretcorrection, size=self.turretsize)
			PopMatrix()
			PushMatrix()
			Color(1,1,1,1)
			for i in range(self.health): Rectangle(pos=(100+i*dp(50), 10), size=(dp(50),dp(50)), source='assets/img/heart.png')
			PopMatrix()

class GameCanvas(Widget):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.touchpos = None
		self.focused = False
		self.keys_active = set()
		self.keyboard = Window.request_keyboard(self.on_kb_close, self, 'text')
		self.keyboard.bind(on_key_down=self.key_down)
		self.keyboard.bind(on_key_up=self.key_up)

		# init objs
		GAME_OBJS.append(PlayerTank(pos=(dp(GAME_WIDTH/2), dp(GAME_HEIGHT/2))))

		for i in range(random.randint(2, 5)):
			GAME_OBJS.append(EnemyTank(pos=(dp(random.randint(0,GAME_WIDTH/2)), dp(random.randint(0,GAME_WIDTH/2)))))
		
		Clock.schedule_interval(self.tick, GAME_FPS)
	
	def on_touch_down(self, touch):
		global TOUCH_ACTIVE
		self.focused = True
		self.touchpos = touch
		TOUCH_ACTIVE = touch

	def on_touch_move(self, touch):
		global TOUCH_ACTIVE
		self.focused = True
		self.touchpos = touch
		TOUCH_ACTIVE = touch

	def on_touch_up(self, touch):
		global TOUCH_ACTIVE
		self.touchpos = None
		TOUCH_ACTIVE = None

	def on_kb_close(self):
		print('Keyboard Failed')
		self.keyboard.unbind(on_key_down=self.key_down)
		self.keyboard = None

	def key_down(self, keyboard, keycode, text, modifiers):
		global KEYS_ACTIVE
		self.focused = True
		code, word = keycode
		self.keys_active.add(word)
		KEYS_ACTIVE.add(word)

	def key_up(self, keyboard, keycode):
		global KEYS_ACTIVE
		code, word = keycode
		self.keys_active.remove(word)
		KEYS_ACTIVE.remove(word)

	def tick(self, dt):
		if not self.focused:
			self.canvas.clear() # Clear
			self.canvas.add(texLabel("Click to focus", 100, (0,0), CLR_RED))
			return
		print('Tick', dt, len(GAME_OBJS))
		
		# update
		for obj in GAME_OBJS:
			obj.update(dt)

		# render
		self.canvas.clear() # Clear
		for obj in GAME_OBJS:
			obj.render(self.canvas)

class MainMenu(Screen):
	pass
class GameScreen(Screen):
	pass
class HelpScreen(Screen):
	pass
class ScreenMgr(ScreenManager):
	pass
layouts = Builder.load_file('layouts.kv')
class GameApp(App):
	title = 'Tanks! | Ragul Balaji 2020 | Digital World 10.009'
	def build(self):
		print(self.title)
		snd_pickup.play()
		return layouts

gameapp = GameApp()
gameapp.run()