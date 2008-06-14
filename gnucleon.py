#!/usr/bin/env python

import math
import clutter
import gtk
import cairo
from clutter import cluttercairo

class BehaviourSpin(clutter.Behaviour):
	__gtype_name__ = 'BehaviourSpin'
	def __init__(self, alpha):
		clutter.Behaviour.__init__(self)
		self.set_alpha(alpha)
		self.angle_start = 359.0
		self.angle_end = 0.0

	def do_alpha_notify (self, alpha_value):
		angle = alpha_value \
			* (self.angle_end - self.angle_start) \
			/ clutter.MAX_ALPHA

		for actor in self.get_actors():
			actor.set_rotation(clutter.Z_AXIS, angle,
				0,
				0,
				0)

class BehaviourGrow(clutter.Behaviour):

	__gtype_name__ = 'BehaviourGrow'

	def __init__(self, alpha):
		clutter.Behaviour.__init__(self)
		self.set_alpha(alpha)

	def do_alpha_notify(self, alpha_value):
		scale = (alpha_value + 0.0) / (clutter.MAX_ALPHA + 0.0)
		for actor in self.get_actors():
			actor.set_scale(scale, scale)

class BehaviourFade(clutter.Behaviour):

	__gtype_name__ = 'BehaviourFade'

	def __init__(self, alpha):
		clutter.Behaviour.__init__(self)
		self.set_alpha(alpha)

	def do_alpha_notify(self, alpha_value):
		opacity = (alpha_value + 0.0) / (clutter.MAX_ALPHA + 0.0)
		for actor in self.get_actors():
			actor.set_opacity(255 * opacity)

class BehaviourOrbit(clutter.Behaviour):

	__gtype_name__ = 'BehaviourOrbit'

	def __init__(self, alpha, width, height, tilt, (offset_x, offset_y), start_angle = 0):
		clutter.Behaviour.__init__(self)		# Call the superclass constructor
		self.set_alpha(alpha)		# Set the tick of the animation
		self.angle_start = start_angle		# Where abouts on the ellipse we start
		self.angle_end = start_angle - 359.0		# Where abouts on the ellipse we are aiming for
		self.angle = self.angle_start		# This stores the angle traversed around the ellipse
		self.width = width		# The width of the ellipse
		self.height = height		# The height of the ellipse (can be changed with Up/Down)
		self.tilt = tilt		# The angle in degrees to tile the ellipse anticlockwise
		self.offset = (offset_x, offset_y)		# Where the centre of the ellipse should be
		self.phase = 0.0		# Initialise this to zero for comparisons later

	def x_position(self, angle):
		"""Calculates the horizontal position on the screen at a given angle around the ellipse"""
		# This is a standard mathematical description of a tilted ellipse
		return self.width * math.cos(math.radians(angle)) * math.cos(math.radians(self.tilt)) - self.height * math.sin(math.radians(angle)) * math.sin(math.radians(self.tilt)) + self.offset[0]

	def y_position(self, angle):
		"""Calculates the vertical position on the screen at a given angle around the ellipse"""
		# This is a standard mathematical description of a tilted ellipse
		return self.width * math.cos(math.radians(angle)) * math.sin(math.radians(self.tilt)) + self.height * math.sin(math.radians(angle)) * math.cos(math.radians(self.tilt)) + self.offset[1]

	def do_alpha_notify (self, alpha_value):
		phase = (alpha_value + 0.0) / (clutter.MAX_ALPHA + 0.0)		# Get a value from 0.0 - 1.0 of our progress
		delta = self.phase - phase		# Calculate the difference since the last time
		self.phase = phase		# Update our last known position
		increment = delta * (((self.angle_end - self.angle_start)))		# Calculate how much angle we should move
		self.angle += increment		# Add it to the current angle

		# This prevents the values becoming too large by making every turn the first one
		if self.angle > 360:
			self.angle -= 360
		elif self.angle < -360:
			self.angle += 360

		for actor in self.get_actors():
			# Update the position and size based on the new angle
			scale = math.cos(math.radians((self.angle / 2) - 45))**2 + 0.25
			actor.set_position(self.x_position(self.angle), self.y_position(self.angle))
			actor.set_scale(actor.scale_factor * scale, actor.scale_factor * scale)
			if scale - 0.25 > 0.9:
				actor.raise_top()
			elif scale - 0.25 < 0.1:
				actor.lower_bottom()

	def turn(self, angle):
		"""This tilts the ellipse anticlockwise by the given number of degrees"""
		self.tilt += angle

	def stretch(self, amount):
		"""This adds the given number onto the ellipse height"""
		self.height += amount

class ClutterDisplay:

	def __init__(self, (size_x, size_y), (grid_x, grid_y), background):
		self.x = size_x
		self.y = size_y
		self.grid = Grid((self.x, self.y), (grid_x, grid_y))
		self.grid.set_position(0, 0)
		self.grid.set_size(self.x, self.y)
		self.grid.show()
		self.stage = clutter.Stage()
		self.stage.set_size(size_x, size_y)
		self.stage.set_color(clutter.color_parse(background))
		self.stage.add(self.grid)
		self.stage.set_reactive(True)
		self.stage.connect("destroy", self.main_quit)

	def input_keys(self, arg2, arg3):
		pass

	def main_quit(self, event):
		clutter.main_quit

	def main(self):
		self.stage.show_all()
		clutter.main()

class Grid(clutter.Group):

	def __init__(self, (size_x, size_y), (squares_x, squares_y)):
		super(Grid, self).__init__()
		self.set_size(size_x, size_y)
		self.set_position(0, 0)
		self.set_reactive(True)
		self.grid = []
		self.turns = 0
		self.square_size = (size_x / squares_x, size_y / squares_y)
		for column in range(0, squares_x):
			new_column = []
			column_type = ''
			if column == 0:
				column_type = 'left'
			elif column == squares_x - 1:
				column_type = 'right'
			else:
				column_type = 'middle'
			for square in range(0, squares_y):
				if column_type == 'left':
					if square == 0:
						new_column.append(Square(self.square_size, (column, square), 'corner_top_left'))
					elif square == squares_y - 1:
						new_column.append(Square(self.square_size, (column, square), 'corner_bottom_left'))
					else:
						new_column.append(Square(self.square_size, (column, square), 'edge_left'))
				elif column_type == 'right':
					if square == 0:
						new_column.append(Square(self.square_size, (column, square), 'corner_top_right'))
					elif square == squares_y - 1:
						new_column.append(Square(self.square_size, (column, square), 'corner_bottom_right'))
					else:
						new_column.append(Square(self.square_size, (column, square), 'edge_right'))
				elif column_type == 'middle':
					if square == 0 and not square == squares_y - 1:
						new_column.append(Square(self.square_size, (column, square), 'edge_top'))
					elif square == squares_y - 1:
						new_column.append(Square(self.square_size, (column, square), 'edge_bottom'))
					else:
						new_column.append(Square(self.square_size, (column, square), 'middle'))
			self.grid.append(new_column)
		for x in self.grid:
			for y in x:
				self.add(y)
				y.show()

	def add_particle(self, (column, row)):
		global current_colour
		self.grid[column][row].add_particle(current_colour, True)

	def explode(self, (column, row)):
		self.grid[column][row].explode()

	def add_turn(self):
		self.turns += 1

	def check_players(self):
		'''Check whether any players have been eliminated.'''
		global colours
		global current_colour
		# Only check if every player has had at least one turn
		if self.turns > len(colours):
			new_colours = []		# This will store the colours still in play
			# Not very efficient here, but the colour order must be preserved
			for colour in colours:
				alive = False		# Assume this colour is gone
				# Check the colour of every square, if it matches then mark it alive
				for row in self.grid:
					for square in row:
						if square.colour == colour:
							alive = True
				# Add the colour to those still in play if it was found
				if alive:
					new_colours.append(colour)
			colours = new_colours

class Square(clutter.Group):

	def __init__(self, (size_x, size_y), (position_x, position_y), type):
		global electron_alpha
		super(Square, self).__init__()
		self.set_reactive(True)
		self.connect("button-press-event", self.clicked, self)
		self.connect("enter-event", self.on_enter, self)
		self.connect("leave-event", self.on_leave, self)
		self.size_x = size_x
		self.size_y = size_y
		self.colour = None
		self.set_size(self.size_x, self.size_y)
		self.column = position_x
		self.row = position_y
		self.set_position(size_x * position_x, size_y * position_y)

		self.rectangle = clutter.Rectangle()
		self.add(self.rectangle)
		#self.rectangle.set_position(size_x * position_x, size_y * position_y)
		self.rectangle.set_position(0, 0)
		self.rectangle.set_size(self.size_x, self.size_y)
		self.rectangle.set_color(clutter.color_parse('#0099FF'))
		self.rectangle.set_opacity(0)

		self.rectangle.show()
		self.rectangle_timeline = clutter.Timeline(fps=30, duration=500)
		self.rectangle_alpha = clutter.Alpha(self.rectangle_timeline, clutter.sine_inc_func)
		self.rectangle_behaviour = BehaviourFade(self.rectangle_alpha)
		self.rectangle_behaviour.apply(self.rectangle)

		self.flash_pixmap = gtk.gdk.pixbuf_new_from_file('images/electron_big.png')
		self.flash = clutter.Texture(self.flash_pixmap)
		self.flash.set_opacity(0)
		self.add(self.flash)
		self.flash.set_size(min((self.size_x, self.size_y)), min((self.size_x, self.size_y)))
		self.flash.set_anchor_point(self.flash.get_width() / 2, self.get_height() / 2)
		self.flash.set_position(self.flash.get_width() / 2, self.flash.get_height() / 2)
		self.flash.show()
		self.flash_timeline = clutter.Timeline(fps=30, duration=200)
		self.flash_sine_alpha = clutter.Alpha(self.flash_timeline, clutter.sine_func)
		self.flash_ramp_alpha = clutter.Alpha(self.flash_timeline, clutter.ramp_inc_func)
		self.flash_behaviours = [BehaviourGrow(self.flash_ramp_alpha), BehaviourFade(self.flash_sine_alpha)]
		for behaviour in self.flash_behaviours:
			behaviour.apply(self.flash)

		self.nucleons = []

		self.electrons = []
		self.electron_behaviours = {'horizontal_orbit':BehaviourOrbit(electron_alpha, size_x / 2, size_y / 8, 0, (size_x / 2, size_y / 2)),\
		                            'vertical_orbit':BehaviourOrbit(electron_alpha, size_x / 8.0, size_y / 2, 0, (size_x / 2, size_y / 2)),\
   		                            'diagonal_orbit':BehaviourOrbit(electron_alpha, size_x / 8.0, size_y / 2, -45, (size_x / 2, size_y / 2)),\
		                            'antidiagonal_orbit':BehaviourOrbit(electron_alpha, size_x / 2, size_y / 8, -45, (size_x / 2, size_y / 2)),\
		                            'spin':BehaviourSpin(electron_alpha)}
		self.limit = 2
		self.type = type
		if self.type[0] is not 'c':
			self.limit += 1
			if self.type[0] is not 'e':
				self.limit += 1

	def on_enter(self, action, event, widget):
		self.rectangle_timeline.set_direction(clutter.TIMELINE_FORWARD)
		self.rectangle_timeline.start()

	def on_leave(self, action, event, widget):
		self.rectangle_timeline.set_direction(clutter.TIMELINE_BACKWARD)
		self.rectangle_timeline.start()

	def commented(self):
		pass
		#def add_circle(self, (position_x, position_y), (size_x, size_y), color, border = 0, border_color = "#FFFFFF"):
		#	cairo_tex = cluttercairo.CairoTexture(width=50, height=50)

		#	context = cairo_tex.cairo_create()

		#	# we scale the context to the size of the surface
		#	context.scale(50, 50)
		#	context.set_line_width(0.01)
		#	context.translate(0.5, 0.5)
		#	context.arc(0, 0, 0.25, 0, math.pi * 2)
		#	context.stroke()

		#	del(context) # we need to destroy the context so that the
                 # texture gets properly updated with the result
                 # of our operations; you can either move all the
                 # drawing operations into their own function and
                 # let the context go out of scope or you can
                 # explicitly destroy it

		#	cairo_tex.set_anchor_point(25, 25)
		#	cairo_tex.set_position(25, 25)
		#	self.stage.add(cairo_tex)
		#	for behaviour in behaviours:
		#		behaviour.apply(cairo_tex)
		#	cairo_tex.show()

	def clicked(self, action, event, widget):
		global current_colour
		global colours
		added = self.add_particle(current_colour)
		if added:
			self.explode()
			self.get_parent().add_turn()
			self.get_parent().check_players()
			if colours.index(current_colour) == len(colours) - 1:
				current_colour = colours[0]
			else:
				current_colour = colours[colours.index(current_colour) + 1]


	def add_electron(self):
		#if min((self.size_x, self.size_y)) / 18.0 > 25:
		#pixbuf = gtk.gdk.pixbuf_new_from_file('images/electron_big.png')
		#else:
		pixbuf = gtk.gdk.pixbuf_new_from_file('images/electron_small.png')
		texture = clutter.Texture(pixbuf)
		texture.set_anchor_point(texture.get_width() / 2, texture.get_height() / 2)
		texture.set_position(0, 0)
		texture.scale_factor = min(((self.size_x + 0.0) / (18.0 * texture.get_width()), ((self.size_y + 0.0) / 18.0 * texture.get_height())))
		texture.set_scale(texture.scale_factor, texture.scale_factor)
		self.electrons.append(texture)
		self.electron_behaviours['spin'].apply(texture)
		if len(self.electrons) == 1:
			self.electron_behaviours['horizontal_orbit'].apply(texture)
		elif len(self.electrons) == 2:
			self.electron_behaviours['vertical_orbit'].apply(texture)
		elif len(self.electrons) == 3:
			self.electron_behaviours['diagonal_orbit'].apply(texture)
		elif len(self.electrons) == 4:
			self.electron_behaviours['antidiagonal_orbit'].apply(texture)
		texture.show()
		self.add(texture)

	def add_nucleon(self, colour):
		if (min((self.size_x, self.size_y)) + 0.0) / 4.0 > 25:
			pixbuf = gtk.gdk.pixbuf_new_from_file('images/' + colour + 'proton_big.png')
		else:
			pixbuf = gtk.gdk.pixbuf_new_from_file('images/' + colour + 'proton_small.png')
		texture = clutter.Texture(pixbuf)
		#texture.set_position(0, 0)
		texture.set_anchor_point(texture.get_width() / 2, texture.get_height() / 2)
		self.nucleons.append(texture)
		radius = min(((self.size_x + 0.0) / 4.0) / (texture.get_width() + 0.0), ((self.size_y + 0.0) / 4.0) / (texture.get_height() + 0.0))
		texture.scale_factor = radius
		texture.set_scale(radius, radius)

		if len(self.nucleons) == 1:
			texture.set_position(self.size_x / 2, self.size_y / 2)
		elif len(self.nucleons) == 2:
			texture.set_position(self.size_x / 2 - self.size_x / 8, self.size_y / 2)
			self.nucleons[0].set_position(self.size_x / 2 + self.size_x / 8, self.size_y / 2)
		elif len(self.nucleons) == 3:
			texture.set_position(self.size_x / 2, self.size_y / 2 - self.size_y / 8)
			self.nucleons[0].set_position(self.size_x / 2 - self.size_x / 8, self.size_y / 2 + self.size_y / 8)
			self.nucleons[1].set_position(self.size_x / 2 + self.size_x / 8, self.size_y / 2 + self.size_y / 8)
		elif len(self.nucleons) == 4:
			texture.set_position(self.size_x / 2 - self.size_x / 8, self.size_y / 2 - self.size_y / 8)
			self.nucleons[1].set_position(self.size_x / 2 + self.size_x / 8, self.size_y / 2 - self.size_y / 8)
			self.nucleons[0].set_position(self.size_x / 2 - self.size_x / 8, self.size_y / 2 + self.size_y / 8)
			self.nucleons[2].set_position(self.size_x / 2 + self.size_x / 8, self.size_y / 2 + self.size_y / 8)
		#texture.set_scale(radius, radius)
		self.add(texture)
		texture.show()

	def add_particle(self, colour, explosion=False):
		if explosion:
			self.colour = colour
			self.change_colour()
		if self.colour is None or self.colour == colour:
			self.add_nucleon(colour)
			self.add_electron()
			self.colour = colour
			#if len(self.electrons) >= self.limit:
			#	self.explode()
			return True
		else:
			return False

	def change_colour(self):
		number = len(self.electrons)
		self.clear()
		for particle in range(0, number):
			self.add_particle(self.colour)

	def clear(self):
		self.electrons = []
		self.nucleons = []
		self.remove_all()

	def remove_particle(self):
		global current_colour
		# Remove an electron and a nucleon pair from the lists and the Group
		self.remove(self.electrons.pop())
		self.remove(self.nucleons.pop())
		# Check to see if we need to rearrange any left behind
		if len(self.electrons) > 0:
			# If so remove one
			self.remove(self.electrons.pop())
			self.remove(self.nucleons.pop())
			# Then add it back since the layout is set during add
			self.add_nucleon(current_colour)
			self.add_electron()
		else:
			# If there aren't any left behind then the atom has no owner
			self.colour = None

	def send_left(self):
		clutter.redraw()
		self.remove_particle()
		self.get_parent().add_particle((self.column - 1, self.row))

	def send_right(self):
		clutter.redraw()
		self.remove_particle()
		self.get_parent().add_particle((self.column + 1, self.row))

	def send_up(self):
		clutter.redraw()
		self.remove_particle()
		self.get_parent().add_particle((self.column, self.row - 1))

	def send_down(self):
		clutter.redraw()
		self.remove_particle()
		self.get_parent().add_particle((self.column, self.row + 1))

	def explode(self):
		if len(self.electrons) >= self.limit:
			self.flash_timeline.start()
			if self.type == 'corner_top_left':
				self.send_right()
				self.send_down()
				self.get_parent().explode((self.column + 1, self.row))
				self.get_parent().explode((self.column, self.row + 1))
			elif self.type == 'corner_top_right':
				self.send_left()
				self.send_down()
				self.get_parent().explode((self.column + -1, self.row))
				self.get_parent().explode((self.column, self.row + 1))
			elif self.type == 'corner_bottom_left':
				self.send_right()
				self.send_up()
				self.get_parent().explode((self.column, self.row - 1))
				self.get_parent().explode((self.column + 1, self.row))
			elif self.type == 'corner_bottom_right':
				self.send_left()
				self.send_up()
				self.get_parent().explode((self.column + -1, self.row))
				self.get_parent().explode((self.column, self.row - 1))
			elif self.type == 'edge_left':
				self.send_up()
				self.send_down()
				self.send_right()
				self.get_parent().explode((self.column, self.row - 1))
				self.get_parent().explode((self.column, self.row + 1))
				self.get_parent().explode((self.column + 1, self.row))
			elif self.type == 'edge_right':
				self.send_up()
				self.send_down()
				self.send_left()
				self.get_parent().explode((self.column, self.row - 1))
				self.get_parent().explode((self.column, self.row + 1))
				self.get_parent().explode((self.column + -1, self.row))
			elif self.type == 'edge_top':
				self.send_left()
				self.send_right()
				self.send_down()
				self.get_parent().explode((self.column + -1, self.row))
				self.get_parent().explode((self.column + 1, self.row))
				self.get_parent().explode((self.column, self.row + 1))
			elif self.type == 'edge_bottom':
				self.send_left()
				self.send_right()
				self.send_up()
				self.get_parent().explode((self.column + -1, self.row))
				self.get_parent().explode((self.column + 1, self.row))
				self.get_parent().explode((self.column, self.row - 1))
			else:
				self.send_up()
				self.send_down()
				self.send_left()
				self.send_right()
				self.get_parent().explode((self.column, self.row - 1))
				self.get_parent().explode((self.column, self.row + 1))
				self.get_parent().explode((self.column + -1, self.row))
				self.get_parent().explode((self.column + 1, self.row))

if __name__ == '__main__':
	global electron_alpha
	electron_timeline = clutter.Timeline(fps=50, duration=1500)
	electron_timeline.set_loop(True)
	electron_alpha = clutter.Alpha(electron_timeline, clutter.ramp_inc_func)
	electron_timeline.start()

	global colours
	global current_colour
	colours = ['green', 'yellow']
	current_colour = 'green'

	columns = 4
	rows = 3

	display = ClutterDisplay((800, 600), (columns, rows), "#000000")

	display.main()
