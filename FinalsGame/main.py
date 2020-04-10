from kivy.app import App
from kivy.lang import Builder
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.graphics import *
from kivy.metrics import *

from kivy.config import Config
Config.set('graphics', 'resizable', False) # Fixed Size
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.write()

snd_hit = SoundLoader.load('assets/snd/Hit.wav')
snd_pickup = SoundLoader.load('assets/snd/Pickup.wav')
snd_shoot = SoundLoader.load('assets/snd/Shoot.wav')

class GameCanvas(Widget):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		with self.canvas:
			Rectangle(pos=(0,0),size=(dp(750),dp(550)))

class MainMenu(Screen):
	pass
class GameScreen(Screen):
	pass
class ScreenMgr(ScreenManager):
	pass
layouts = Builder.load_file('layouts.kv')
class GameApp(App):
	title="Tanks! | Ragul Balaji 2020 | Digital World 10.009"
	def build(self):
		print(self.title)
		snd_pickup.play()
		return layouts

gameapp = GameApp()
gameapp.run()