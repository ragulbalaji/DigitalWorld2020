from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.widget import Widget
from kivy.graphics import *

from kivy.config import Config
Config.set('graphics', 'resizable', False) # Fixed Size
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.write()

class GameCanvas(Widget):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		with self.canvas:
			print("HELLO")
			Rectangle(pos=(10,20),size=(100,200))

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
		return layouts

gameapp = GameApp()
gameapp.run()