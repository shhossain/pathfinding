from kivy.app import App
from kivy.uix.screenmanager import Screen,ScreenManager
from threading import Thread
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from math import sqrt
import random
import time
from re import match



# SET ANY ROWS YOU WANT (Ideal range 30-50) (ROW increase will affet your perfomence, Total Cells will be ROWS*ROWS*1.5)

#SET SPEED 

#Frist two point will be  start and end (Ctrl + S will reset Start,End)

# Tap 'c' to create random barriers (Clicking 'c' again will creeate more barriers)

# Click on any cell to create barrier

# Click on any barrier will clear the path



# After adding start and end cell anf with or without any barrier

# Tap 'a' to perform 'A(Start) Pathfinding Operation'(If no path is available program will probaly quit)

# Tap 'd' to perform 'Depth For Search'(If no path is available program will probaly quit)

# Tap 'b' to perform 'Best For Search'(If stuck just reset it)

# Tap 'q' to reset all.


#Advanced Control
# 'Ctrl + s' will reset start and end.
# 'Ctrl + [2-8]' will stope threads working with that algoritham.



#Editable
ROWS = 30
SPEED = 2

#Not this speed
SPEED = 10 * (ROWS//10) * SPEED


class Color:
	WHITE =  [1,1,1,1]
	RED = [1,0,0,1]
	GREEN = [0,1,0,1]
	BLACK = [0,0,0,1]
	YELLOW = [153/255,153/255,0,1]
	BLUE = [0,0,1,1]
	INDIGO = [128/255,0,1,1]
	PURPLE = [230/255,230/255,250/255]
	DARK_YELLOW = [102/255,102/255,0,1]


def sort_dict_star(x):
	return dict(sorted(x.items(), key=lambda item: (item[1][0],item[1][1])))


class Grid(Screen):
	error_cells = 0
	touch_down = False
	startCell = None
	auto = False
	pathFindingBFS = False
	pathFindingBBF = False
	pathFindingDFS = False

	start_end =[]

	shouldColor = []
	pathFound = False

	openSet = {}
	closeSet = {}

	#a_star
	explored_node = []
	openNodes = {}
	PathFoundAStar = False
	came_from = {}


	#bfs
	queue = []
	searched = []
	pathFound2 = False
	node = {}
	shouldColor2 = []

	parentNodeBBF = {}

	#dfs
	marked = {}
	visited = []
	visited_pos = []
	pathFoundDFS = False
	all_stack = []
	path = []
	parentNodeDFS = {}
	pathFoundDFS2 = []

	def on_enter(self):
		if ROWS%2 == 1:
			self.rows = ROWS+1
		else:
			self.rows = ROWS
		self.cols = int(self.rows*1.5)
		
		self.grid = self.ids.grid
		self.grid.rows = self.rows
		self.grid.cols = self.cols
		
		Window.bind(mouse_pos=self.on_mouse_pos)
		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)

		for _ in range(0,self.rows*self.cols):
			Thread(target=self.add_cell,daemon=True).start()	

		self.cells = self.grid.children



		self.start = False
		self.end = False

		clock1 = Clock.schedule_interval(self.update,1/SPEED)

		self.clock2 = None
		self.clock3 = None


	def create_obstacle(self):
		total_obstacle = (self.cols * self.rows)// 10
		print("total_obstacle",total_obstacle)
		obstacles = []
		n = len(self.cells) - 1
		print("total cells",n)
		for _ in range(total_obstacle):
			ran = random.randint(0,n)
			obstacles.append(self.cells[ran])
		# print(obstacles)

		for obstacle in obstacles:
			if obstacle.background_color != Color.GREEN and obstacle.background_color != Color.RED:
				obstacle.background_color = Color.BLACK





	def random_cell(self):
		start_cell = None
		n = len(self.cells) - 1
		ran1 = random.randint(0,n)
		ran_cell_1 = self.cells[ran1]
		ran_cell_pos_1 = self.get_pos(ran_cell_1)
		if not self.is_barrier(*ran_cell_pos_1):
			start_cell = ran_cell_1
		else:
			start_cell = self.cells[n//2]

		return start_cell
			




	def update(self,dt):
		if type(self.start) is tuple or type(self.end) is tuple:
			if len(self.start_end) == 0:
				self.start_end.append(((self.start),(self.end)))

			last = self.start_end[-1]
			now = (self.start,self.end)

			if now != last:
				print("start,end x,y",now)
				self.start_end.append(now)


		if self.error_cells>0:
			for _ in range(self.error_cells):
				Thread(target=self.add_cell,daemon=True).start()
			self.error_cells = 0

		if len(self.openSet)> 2:
			for cell in self.openSet.keys():
				if cell.background_color == Color.RED or cell.background_color == Color.GREEN or cell.background_color == Color.BLACK:
					pass
				else:
					cell.background_color = Color.YELLOW

		if self.pathFound:
			b = [i for i in self.closeSet.keys()]
			b.reverse()
			for cell in b:
				if cell.background_color == Color.BLACK:
					pass
				else:
					cell.background_color = Color.BLUE
			
			self.openSet = {}
			self.pathFound = False

			self.start = False
			self.end = False

			self.pathFindingBFS = False


		if len(self.queue) > 2:
			for cell in self.queue:
				if cell.background_color == Color.RED or cell.background_color == Color.GREEN or cell.background_color == Color.BLACK:
					pass
				else:
					cell.background_color = Color.YELLOW

		if self.pathFound2:
			for cell in self.shouldColor2:
				if cell.background_color == Color.BLACK:
					pass
				else:
					cell.background_color = Color.BLUE

			self.queue = []
			self.pathFound2 = False
			self.start = False
			self.end = False
			self.pathFindingBBF = False


		if self.pathFoundDFS:
			print("Start x,y",self.start,"End x,y",self.end)
			print("Node",self.parentNodeDFS)
			self.visited = []
			self.pathFoundDFS = False
			self.marked = {}

		if self.pathFoundDFS2:
			for cell_pos in self.path:
				cell = self.get_cell(*cell_pos)
				if cell.background_color == Color.BLACK:
					pass
				else:
					print("cell_pos",cell_pos)
					cell.background_color = Color.BLUE
			self.pathFoundDFS2 = False

		if len(self.explored_node) >  0:
			for cell in self.explored_node:
				if cell.background_color == Color.RED or cell.background_color == Color.GREEN or cell.background_color == Color.BLACK:
					pass
				else:
					cell.background_color = Color.YELLOW

		if self.PathFoundAStar:
			self.explored_node = []
			self.openNodes = {}
			self.PathFoundAStar = False


	def add_pos_in_btn(self):
		for cell in self.cells:
			cell_pos = self.get_pos(cell)
			cell.markup = True
			text = f"[b]{cell_pos}[/b]"
			cell.text = text
			text_len = 0
			if len(str(cell_pos))>5:
				text_len = len(text) - 5
				text_len = text_len * .25
			font_size = (10 - (self.rows/5 - 2)) - text_len + 2
			cell.font_size = font_size

	def add_cell(self):
		try:
			cell = Button(background_normal= '',background_down='',background_color= Color.WHITE,color= Color.BLACK)
			self.grid.add_widget(cell)
		except AssertionError:
			print("Assert Error")
			self.error_cells +=1


	def get_pos(self,cell):
		n = self.cells.index(cell)
		c = self.cols
		y = n//c
		x = (c-1) - (n - (c*y))

		return x,y

	def is_barrier(self,*point):
		x,y = point
		l = False
		if x == self.cols or y == self.rows:
			# print("x == self.cols or y == self.rows",x == self.cols or y == self.rows)
			l = True
		if x < 0 or y < 0:
			l = True
		if not l:
			cell = self.get_cell(*point)
			if cell.background_color == Color.BLACK:
				# print("cell.background_color != Color.BLACK",cell.background_color != Color.BLACK)
				l = True
		return l


	def get_cell(self,*point):
		x,y = point
		c = self.cols
		n = (y*c) + (c-1)-x
		cell = self.cells[n]
		return cell

	def h(self,*pos):
		x1,y1 = pos
		x2,y2 = self.end
		m = abs(x1-x2) + abs(y1-y2)
		e = sqrt(pow(x2-x1,2)+pow(y2-y1,2))
		return int(m)

	def sort_dict(self,x):
		return dict(sorted(x.items(), key=lambda item: item[1]))

	def on_click(self,cell):
		if  not self.start:
			cell.background_color = Color.GREEN
			self.start = self.get_pos(cell)
			self.startCell = cell
		elif not self.end and type(self.start) is tuple and cell.background_color != Color.GREEN:
			cell.background_color = Color.RED
			self.end = self.get_pos(cell)
			
		elif cell.background_color != Color.BLACK and cell.background_color != Color.GREEN and cell.background_color != Color.RED:
			cell.background_color = Color.BLACK

		elif cell.background_color == Color.BLACK:
			cell.background_color = Color.WHITE

		elif cell.background_color == Color.RED:
				cell.background_color = Color.WHITE
				self.end = False
		elif cell.background_color == Color.GREEN:
			cell.background_color = Color.WHITE
			self.startCell = None
			self.start = False

		pos = self.get_pos(cell)
		print(f"Pos :{self.get_pos(cell)}\n")
		# print(f"Cell :{self.get_cell(*pos)}\n")

		# self.get_cell(pos[0],pos[1])

	def neighbours(self,cell,k=1):
		start_x,start_y = self.get_pos(cell)
		x1,y1 = start_x + k,start_y
		x2,y2 = start_x - k,start_y
		x3,y3 = start_x,start_y + k
		x4,y4 = start_x,start_y - k
		x5,y5 = start_x + k,start_y + k
		x6,y6 = start_x + k,start_y - k
		x7,y7 = start_x - k,start_y + k
		x8,y8 = start_x - k,start_y - k
		# (start_x,start_y)
		return (x1,y1),(x2,y2),(x3,y3),(x4,y4),(x5,y5),(x6,y6),(x7,y7),(x8,y8)

	def h_cost(self,*point):
		x,y = point
		x2,y2 = self.end
		e = round(sqrt((x2-x)**2 + (y2-y)**2) * 10)
		return e


	def g_cost(self,own_cost,*point1):
		x1,y1,x2,y2 = point1
		# x2,y2 = point2

		e = round(sqrt((x1-x2)**2 + (y1-y2)**2) * 10) + own_cost
		return e

	def f_cost(self,g_cost,h_cost):
		return g_cost + h_cost

	def reconstract_path(self,came_from):
		self.current = [self.end]
		self.came_from = came_from
		print("Clock8 Is Starting..")
		self.clock8 = Clock.schedule_interval(self.reconstract_path_logic,1/SPEED)

	def reconstract_path_logic(self,dt):
		current = self.current[-1]
		cell = self.get_cell(*current)
		cell.background_color = Color.BLUE
		path =  self.came_from[current]
		cell = self.get_cell(*path)
		# self.path_astar.append(path)
		if path == self.start:
			self.clock8.cancel()
			cell.background_color = Color.BLUE
			self.came_from = {}
		else:
			self.current.append(path)
			cell.background_color = Color.BLUE


	def a_star(self):
		start_h_cost = self.h_cost(*self.start)
		start_f_cost =self.f_cost(0,start_h_cost)
		self.openNodes[self.startCell] = [start_f_cost,start_h_cost,0,self.start]
		print("Clock7 is starting..")
		self.clock7 = Clock.schedule_interval(self.a_star_logic,1/SPEED)

	def a_star_logic(self,dt):
		self.openNodes = sort_dict_star(self.openNodes)

		lowest_node = list(self.openNodes.items())[0]

		lowest_node_cell , lowest_node_f_cost, lowest_h_cost, lowest_g_cost = lowest_node[0],lowest_node[1][0],lowest_node[1][1],lowest_node[1][2]

		self.openNodes.pop(lowest_node_cell)
		self.explored_node.append(lowest_node_cell)


		lowest_node_pos = self.get_pos(lowest_node_cell)

		if lowest_node_pos == self.end:
			self.PathFoundAStar = True
			print("PATH FOUND Astar")
			self.clock7.cancel()
			self.reconstract_path(self.came_from)
		else:
			neighbours = self.neighbours(lowest_node_cell)

			for neighbour in neighbours:
				
				if self.is_barrier(*neighbour):
					continue

				neighbour_cell = self.get_cell(*neighbour)
				if neighbour_cell in self.explored_node:
					continue

				neighbour_g_cost = self.g_cost(lowest_g_cost,*neighbour,*lowest_node_pos)
				neighbour_h_cost = self.h_cost(*neighbour)
				neighbour_f_cost = self.f_cost(neighbour_g_cost,neighbour_h_cost)

				if neighbour_cell not in self.openNodes:
					self.came_from[neighbour] = lowest_node_pos
					self.openNodes[neighbour_cell] = [neighbour_f_cost,neighbour_h_cost,neighbour_g_cost,neighbour]


	def best_first_search(self):
		self.openSet[self.startCell] = self.h(*self.start)
		print("Clock2 Is Starting.")
		self.clock2 = Clock.schedule_interval(self.best_first_search_logic,1/SPEED)


		#plt findings
	

	def best_first_search_logic(self,dt):
		print("BFS")

		# loop
		self.openSet = self.sort_dict(self.openSet)
		# print("Open Set",self.openSet)

		if len(self.openSet) > 0:
			for k,v in self.openSet.items():
				current_cell,current_h = k,v
				break
			self.openSet.pop(current_cell)

			current_x,current_y = self.get_pos(current_cell)

			self.closeSet[current_cell] = current_h

			if current_h == 0:
				self.pathFound = True

		

			neighbours = self.neighbours(current_cell)

			for neighbour in neighbours:
				if self.is_barrier(*neighbour) or neighbour in self.closeSet:
					print("Is Barrier")
					# neighbour_cell = self.get_cell(*neighbour)
					# neighbour_cell.background_color = Color.INDIGO
					continue
				
				neighbour_h = self.h(*neighbour)
				neighbour_cell = self.get_cell(*neighbour)
				if neighbour_h < current_h or neighbour not in self.openSet:
					
 					self.openSet[neighbour_cell] = neighbour_h


			if self.pathFound:
				print("Path Found")
				self.clock2.cancel()


	def breadth_first(self):
		self.queue.append(self.startCell)
		print("Clock3 Is Starting.")
		self.clock3 = Clock.schedule_interval(self.breadth_first_logic,1/(SPEED*6)) 



	def breadth_first_logic(self,dt):
		cell = self.queue[0]
		# print("Queue",cell)
		self.queue.remove(cell)
		self.searched.append(cell)

		cell_x,cell_y = self.get_pos(cell)

		if (cell_x,cell_y) == self.end:
			self.pathFound2 = True
			print("Path Found1")
			self.clock3.cancel()
			self.reconstract_path(self.came_from)
		else:
			neighbours = self.neighbours(cell)
			for neighbour in neighbours:
				if neighbour == self.end:
					self.pathFound2 = True
					print("Path Found2")
					self.clock3.cancel()
					self.reconstract_path(self.came_from)
				else:
					if self.is_barrier(*neighbour):
						print("is_barrier")
						continue

					neighbour_cell = self.get_cell(*neighbour)
					if neighbour_cell not in self.queue and neighbour_cell != self.startCell and neighbour not in self.searched:
						self.came_from[neighbour] = (cell_x,cell_y)
						self.queue.append(neighbour_cell)

	def dfs(self):
		for cell in self.cells:
			self.marked[cell] = False
		self.all_stack = [self.startCell]
		print("Clock5 Is Starting.")
		self.clock5 = Clock.schedule_interval(self.dfs_logic,1/SPEED)


	def dfs_logic(self,dt):
		v = self.all_stack.pop()

		pos_v = self.get_pos(v)

		if pos_v == self.end:
			self.pathFoundDFS = True
			# self.add_path(self.parentNodeDFS)
			print("PATH FOUND DFS")
			self.clock5.cancel()
			self.reconstract_path(self.came_from)
		else:
			if not self.marked[v]:
				
				self.visited.append(v)
				# self.visited_pos.append(pos_v)
				self.marked[v] = True

				neighbours = self.neighbours(v)

				for neighbour in neighbours:
					if self.is_barrier(*neighbour):
						continue

					neighbour_cell = self.get_cell(*neighbour)
					neighbour_cell.background_color = Color.DARK_YELLOW
					neighbour_cell.text = f""

					if not self.marked[neighbour_cell]:
						self.came_from[neighbour] = pos_v
						self.all_stack.append(neighbour_cell)


	def on_mouse_pos(self, window, pos):
		# print("Mouse",window,pos)
		for i in self.cells:
			if i.collide_point(*pos):
				self.hover = True
				self.mouse_keyboard(i)
			else:
				self.hover = False

	def on_touch_down(self, touch):
		for i in self.cells:
			if i.collide_point(*touch.pos):
			# self.hover = True
				self.on_click(i)
		self.touch_down = True

	def on_touch_up(self, touch):
		# print('touch up',touch)
		self.touch_down = False

	def _keyboard_closed(self):
		self._keyboard.unbind(on_key_down=self._on_keyboard_down)
		self._keyboard = None

	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
		print("key down",keyboard,keycode,text,modifiers)
		if keycode[1] == 'spacebar':
			pass
		elif keycode[1] == 'q':
			self.reset()
		elif keycode[1] == 'b':
			if type(self.start) is tuple and type(self.end) is tuple and not self.pathFindingBFS:
				self.pathFindingBFS = True
				self.best_first_search()
		elif keycode[1] == 'v':
			if type(self.start) is tuple and type(self.end) is tuple and not self.pathFindingBBF:
				self.pathFindingBBF = True
				self.breadth_first()
		elif keycode[1] == 'c':
			self.create_obstacle()
		elif keycode[1] == 'a':
			self.a_star()
			# self.clock4 = Clock.schedule_interval(self.auto_test, 2*(ROWS//10))
		elif keycode[1] == 'd':
			if type(self.start) is tuple and type(self.end) is tuple and not self.pathFoundDFS:
				self.pathFindingDFS = True
				self.dfs()

		# elif 'ctrl' in modifiers:
		# 	print("Pressed ctrl")

		#to stop clock
		if 'ctrl' in modifiers:
			patNum = r"[0-9]"
			if match(patNum,keycode[1]):
				clockNo = int(keycode[1])
				self.stop_clock(clockNo)
			elif keycode[1] == 's':
				self.startCell = False
				self.end = False
				self.start = False
				self.start_end = []


	def stop_clock(self,clockNo):
		if type(clockNo) is list:
			for c in clockNo:
				self.stop_clock(c)
		if clockNo ==2:
			try:
				self.clock2.cancel()
				print("Clock2 Stoped.")
			except Exception as e:
				pass
		elif clockNo == 3:
			try:
				self.clock3.cancel()
				print("Clock3 Stoped.")
			except Exception as e:
				pass
		elif clockNo == 4:
			try:
				self.clock4.cancel()
				print("Clock4 Stoped.")
			except Exception as e:
				pass
		elif clockNo == 5:
			try:
				self.clock5.cancel()
				print("Clock5 Stoped.")
			except Exception as e:
				pass
		elif clockNo == 6:
			try:
				self.clock6.cancel()
				print("Clock6 Stoped.")
			except Exception as e:
				pass
		elif clockNo == 7:
			try:
				self.clock7.cancel()
				print("Clock7 Stoped.")
			except Exception as e:
				pass
		elif clockNo == 8:
			try:
				self.clock8.cancel()
				print("Clock8 Stoped.")
			except Exception as e:
				pass


	def mouse_keyboard(self,cell):
		if self.touch_down:
			if cell.background_color != Color.BLACK and cell.background_color != Color.GREEN and cell.background_color != Color.RED:
				cell.background_color = Color.BLACK
			# elif cell.background_color == Color.BLACK and cell.background_color != Color.GREEN and cell.background_color != Color.RED:
			# 	cell.background_color = Color.WHITE



	def reset(self):
		for i in self.cells:
			i.background_color = Color.WHITE
		print("Total CELLS",self.cols*self.rows)
		print("Self cells",len(self.cells))
		self.start = False
		self.end = False
		self.shouldColor = {}
		self.touch_down = False
		self.startCell = None
		self.pathFound = False
		self.pathFound2 = False
		self.openSet = {}
		self.closeSet = {}
		self.queue = []
		self.searched = []
		self.marked = {}
		self.visited = []
		self.pathFoundDFS = False
		self.all_stack = [] 

		self.stop_clock([2,3,4,5,6,7,8])



class AstarApp(App):
	def build(self):
		sm = ScreenManager()
		sm.add_widget(Grid(name='grid'))
		return sm


AstarApp().run()