#!/usr/bin/env python

import gc
import math
import clutter
import gtk
import cairo
import cluttercairo

class BehaviourSpin(clutter.Behaviour):
	# This is a simple Clutter behaviour which spins any actor it is applied to
	__gtype_name__ = 'BehaviourSpin'

	def __init__(self, alpha):
		clutter.Behaviour.__init__(self)
		self.set_alpha(alpha)
		# The start and end angles can be changed to suit the desired rotation
		self.angle_start = 359.0
		self.angle_end = 0.0

	def do_alpha_notify (self, alpha_value):
		# This is run when Clutter updates. alpha_value is the progress of the
		# behaviour, running from 0 to clutter.MAX_ALPHA, therefore alpha_value
		# divided by clutter.MAX_ALPHA gives progress from 0.0 to 1.0
		angle = alpha_value \
			* (self.angle_end - self.angle_start) \
			/ clutter.MAX_ALPHA
		# Apply the new angle to any actors we have been applied to
		for actor in self.get_actors():
			actor.set_rotation(clutter.Z_AXIS, angle,
				0,
				0,
				0)

class BehaviourGrow(clutter.Behaviour):
	# This is a simple Clutter behaviour which changes the size of actors it is
	# applied to from 0 x 0 to normal size x normal size
	__gtype_name__ = 'BehaviourGrow'

	def __init__(self, alpha):
		clutter.Behaviour.__init__(self)
		self.set_alpha(alpha)

	def do_alpha_notify(self, alpha_value):
		# This is run when Clutter updates. alpha_value is the progress of the
		# behaviour, running from 0 to clutter.MAX_ALPHA, therefore alpha_value
		# divided by clutter.MAX_ALPHA gives progress from 0.0 to 1.0
		scale = (alpha_value + 0.0) / (clutter.MAX_ALPHA + 0.0)		# 0.0 is added to make the numbers floats as int/int would equal 0
		for actor in self.get_actors():
			# Apply the new scale to any actors we have been applied to
			actor.set_scale(scale, scale)

class BehaviourFade(clutter.Behaviour):
	# This is a simple Clutter behaviour which changes the opacity of actors it
	# is applied to from zero opacity to full opacity
	__gtype_name__ = 'BehaviourFade'

	def __init__(self, alpha):
		clutter.Behaviour.__init__(self)
		self.set_alpha(alpha)

	def do_alpha_notify(self, alpha_value):
		# This is run when Clutter updates. alpha_value is the progress of the
		# behaviour, running from 0 to clutter.MAX_ALPHA, therefore alpha_value
		# divided by clutter.MAX_ALPHA gives progress from 0.0 to 1.0
		opacity = (alpha_value + 0.0) / (clutter.MAX_ALPHA + 0.0)		# 0.0 is added to make the numbers floats as int/int would equal 0
		for actor in self.get_actors():
			# Apply the new opacity to any actors we have been applied to
			actor.set_opacity(255 * opacity)		# Opacity goes from 0-255

class BehaviourOrbit(clutter.Behaviour):
	# This is a more complex Clutter behaviour which works out the trigonometry needed to
	# send any actors it is applied to around an elliptical path. This behaviour does not
	# spin the actors as they move around. It does change their scale to appear as if the
	# actors are moving forwards and backwards in space, and changes their stacking to
	# ensure that actors in the 'back' of their orbit are drawn behind everything else
	__gtype_name__ = 'BehaviourOrbit'

	def __init__(self, alpha, width, height, tilt, (offset_x, offset_y), start_angle = 0):
		"""width is the width of the elliptical path, height is the height. Tilt specifies
		how many degrees the ellipse is from being straight (ie. width and height are turned
		away from the screen coordinate system by tilt). Offset x and y give the position of
		the centre of the ellipse (in the coordinate system the actor is in). Start angle is the
		angular displacemrnt around the ellipse at the start."""
		clutter.Behaviour.__init__(self)		# Call the superclass constructor
		self.set_alpha(alpha)		# Set the tick of the animation
		self.angle_start = start_angle		# Where abouts on the ellipse we start
		self.angle_end = start_angle - 359.0		# Where abouts on the ellipse we are aiming for
		self.angle = self.angle_start		# This stores the angle traversed around the ellipse
		self.width = width		# The width of the ellipse
		self.height = height		# The height of the ellipse
		self.tilt = tilt		# The angle in degrees to tilt the ellipse anticlockwise
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
		# This is run when Clutter updates. alpha_value is the progress of the
		# behaviour, running from 0 to clutter.MAX_ALPHA, therefore alpha_value
		# divided by clutter.MAX_ALPHA gives progress from 0.0 to 1.0
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
			# Update the position and size of actors based on the new angle
			scale = math.cos(math.radians((self.angle / 2) - 45))**2 + 0.25
			actor.set_position(self.x_position(self.angle), self.y_position(self.angle))
			# Actors must be given a property 'scale_factor' which is their standard scale
			actor.set_scale(actor.scale_factor * scale, actor.scale_factor * scale)
			# Adjust the rendering order for things 'in front' or 'behind'
			#if scale - 0.25 > 0.9:
			#	actor.raise_top()
			#elif scale - 0.25 < 0.1:
			#	actor.lower_bottom()

	def turn(self, angle):
		"""This tilts the ellipse anticlockwise by the given number of degrees"""
		self.tilt += angle

	def stretch(self, amount):
		"""This adds the given number onto the ellipse height"""
		self.height += amount

class ClutterDisplay:
	# This is the screen where everything happens

	def __init__(self, (size_x, size_y), (grid_x, grid_y), background):
		self.x = size_x		# This is our horizontal size
		self.y = size_y		# Vertical size
		# Make a Grid which fills the display
		# grid_x and grid_y are the numbers of columns and rows
		self.grid = Grid((self.x, self.y), (grid_x, grid_y))
		self.grid.set_position(0, 0)
		self.grid.set_size(self.x, self.y)
		self.grid.show()
		# The stage is the top-level actor in Clutter, where everything
		# else lives
		self.stage = clutter.Stage()
		self.stage.set_size(size_x, size_y)
		self.stage.set_color(clutter.color_parse(background))
		self.stage.add(self.grid)
		# This makes sure events are reacted to
		self.stage.set_reactive(True)
		# If the window is closed run "main_quit"
		self.stage.connect("destroy", self.main_quit)

	# Not needed at the moment so doesn't do anything
	def input_keys(self, arg2, arg3):
		pass

	def main_quit(self, event):
		"""Quits the clutter main loop."""
		clutter.main_quit

	def main(self):
		"""Runs the clutter main loop which does the actual work."""
		self.stage.show_all()
		clutter.main()

class Grid(clutter.Group):
	# A Grid is a way to keep track of all of the Squares. It is a
	# type of clutter.Group, ie. a container for actors

	def __init__(self, (size_x, size_y), (squares_x, squares_y)):
		# Standard setting up stuff
		super(Grid, self).__init__()
		self.set_size(size_x, size_y)
		self.set_position(0, 0)
		# This makes sure events are reacted to
		self.set_reactive(True)
		# This stores the number of turns taken, since declaring a player
		# dead is not fair if they have yet to make their first move!
		self.turns = 0
		# self.grid stores the squares in a matrix
		self.grid = []
		self.square_size = (size_x / squares_x, size_y / squares_y)
		# Recursively add squares to each column, then add each column to
		# the self.grid matrix.
		# IMPORTANT: Left is -, right is +, up is -, down is +
		# So (0, 0) is the top left, (1, 1) is one right and one down from
		# the top left, etc.
		for column in range(0, squares_x):
			new_column = []
			# column_type keeps track of where we are on the grid, so that
			# the explosion limits of the square are set correctly
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
		# Now that the squares are in self.grid we want to add them to
		# self, the actual Grid container being drawn on the stage
		for x in self.grid:
			for y in x:
				self.add(y)
				y.show()

	def add_particle(self, (column, row)):
		"""Add a particle to the square at (column, row)"""
		global current_colour
		self.grid[column][row].add_particle(current_colour, True)

	def explode(self, (column, row)):
		"""Run the explode function of the square at (column, row)"""
		self.grid[column][row].explode()

	def add_turn(self):
		"""Increment the turns taken by 1."""
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
	# Square is a clutter.Group which holds the actors for the atoms

	def __init__(self, (size_x, size_y), (position_x, position_y), type):
		global electron_alpha		# This makes all electrons stay in sync
		super(Square, self).__init__()
		# This makes the Square respond to events
		self.set_reactive(True)
		# This tells the program to run "clicked", "on_enter" and "on_leave"
		# when the Square is clicked on, has the cursor enter and has the
		# cursor leave respectively
		self.connect("button-press-event", self.clicked, self)
		self.connect("enter-event", self.on_enter, self)
		self.connect("leave-event", self.on_leave, self)
		# Squares start out without an owner/colour
		self.colour = None
		# Store and set the Square size
		self.size_x = size_x
		self.size_y = size_y
		self.set_size(self.size_x, self.size_y)
		self.column = position_x
		self.row = position_y
		# The position can be calculated as the size of a square multiplied
		# by the number of squares along/down it is
		self.set_position(size_x * position_x, size_y * position_y)
		# self.rectangle makes the nice blue square appear
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

		# self.flash is the explosion animation
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

		# Start out with no nucleons or electrons
		self.nucleons = []
		self.electrons = []
		# These are the electrons' orbits and spin
		self.electron_behaviours = {'horizontal_orbit':BehaviourOrbit(electron_alpha, size_x / 2, size_y / 8, 0, (size_x / 2, size_y / 2)),\
		                            'vertical_orbit':BehaviourOrbit(electron_alpha, size_x / 8.0, size_y / 2, 0, (size_x / 2, size_y / 2)),\
   		                            'diagonal_orbit':BehaviourOrbit(electron_alpha, size_x / 8.0, size_y / 2, -45, (size_x / 2, size_y / 2)),\
		                            'antidiagonal_orbit':BehaviourOrbit(electron_alpha, size_x / 2, size_y / 8, -45, (size_x / 2, size_y / 2)),\
		                            'spin':BehaviourSpin(electron_alpha)}
		# Calculate the explosion size for this atom
		# It must be at least 2, so start with that
		self.limit = 2
		self.type = type
		# corner will stay as 2
		if self.type[0] is not 'c':
			# Everything else goes up to 3
			self.limit += 1
			# edge will stay as 3
			if self.type[0] is not 'e':
				# Everything else will go up to 4
				self.limit += 1

	def on_enter(self, action, event, widget):
		"""Display a blue square on mouse-over."""
		# We use one timeline for going forwards and backwards, switching
		# direction. This stops any jumping around if the leave animation
		# starts before the enter animation has finished
		self.rectangle_timeline.set_direction(clutter.TIMELINE_FORWARD)
		self.rectangle_timeline.start()

	def on_leave(self, action, event, widget):
		"""Fade the blue square when the cursor leaves the square."""
		# We use one timeline for going forwards and backwards, switching
		# direction. This stops any jumping around if the leave animation
		# starts before the enter animation has finished
		self.rectangle_timeline.set_direction(clutter.TIMELINE_BACKWARD)
		self.rectangle_timeline.start()

	# This only exists to remind me how to draw circles with Cairo
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
		"""Do stuff needed when clicked."""
		global current_colour
		global colours
		# added will be True if a particle gets added (ie. the move is
		# valid) and False if not (ie. that is an illegal move)
		added = self.add_particle(current_colour)
		if added:
			# If the move is legal then a particle was added. Now check
			# if we should explode
			self.explode()
			# Increment the turn counter of the Grid by 1
			self.get_parent().add_turn()
			# Eliminate anyone taken out by that move
			self.get_parent().check_players()
			# Next player's turn
			# If we are the last player then go back to the first player
			if colours.index(current_colour) == len(colours) - 1:
				current_colour = colours[0]
			# Otherwise go to the next player
			else:
				current_colour = colours[colours.index(current_colour) + 1]


	def add_electron(self):
		"""Add an electron to the atom."""
		# This is meant to keep memory use down by using small images if the
		# image on screen is small anyway. Doesn't work at the moment since
		# using the small image only displays a corner, so always use big one
		#if min((self.size_x, self.size_y)) / 18.0 > 25:
		pixbuf = gtk.gdk.pixbuf_new_from_file('images/electron_big.png')
		#else:
		#pixbuf = gtk.gdk.pixbuf_new_from_file('images/electron_small.png')
		# Set up a clutter.Texture with the electron image. This is our actor
		texture = clutter.Texture(pixbuf)
		texture.set_anchor_point(texture.get_width() / 2, texture.get_height() / 2)		# Manipulate via the centre
		texture.set_position(0, 0)
		# The scale factor makes the electron 1/18th of the smallest dimension
		# of the Square
		texture.scale_factor = min(((self.size_x + 0.0) / (18.0 * texture.get_width()), ((self.size_y + 0.0) / 18.0 * texture.get_height())))
		texture.set_scale(texture.scale_factor, texture.scale_factor)
		# Add to our list of electrons
		self.electrons.append(texture)
		# Make the electron spin
		self.electron_behaviours['spin'].apply(texture)
		# Depending on which electron we are, choose an orbit
		if len(self.electrons) == 1:
			self.electron_behaviours['horizontal_orbit'].apply(texture)
		elif len(self.electrons) == 2:
			self.electron_behaviours['vertical_orbit'].apply(texture)
		elif len(self.electrons) == 3:
			self.electron_behaviours['diagonal_orbit'].apply(texture)
		elif len(self.electrons) == 4:
			self.electron_behaviours['antidiagonal_orbit'].apply(texture)
		# Display the electron and add to the Square (which is a clutter.Group)
		texture.show()
		self.add(texture)

	def add_nucleon(self, colour):
		"""Add a nucleon to the current atom."""
		# This is meant to keep memory use down by using small images if the
		# image on screen is small anyway. Doesn't work at the moment since
		# using the small image only displays a corner, so always use big one
		#if (min((self.size_x, self.size_y)) + 0.0) / 4.0 > 25:
		pixbuf = gtk.gdk.pixbuf_new_from_file('images/' + colour + 'proton_big.png')
		#else:
		#	pixbuf = gtk.gdk.pixbuf_new_from_file('images/' + colour + 'proton_small.png')
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
		# FIXME: This may be causing memory leaks (are the particles
		# still referenced by their behaviours, thus not getting garbage
		# collected?)
		for electron in self.electrons:
			self.remove(electron)
			for behaviour in self.electron_behaviours:
				try:
					behaviour.remove(electron)
				except:
					pass
		self.electrons = []
		for nucleon in self.nucleons:
			self.remove(nucleon)
		self.nucleons = []
		self.remove_all()
		print self.get_children
		#while gc.collect():
		#	pass

	def remove_particle(self):
		global current_colour
		# Remove an electron and a nucleon pair from the lists, the Square
		# and any behaviours they have applied.
		# FIXME: This may be causing memory leaks (are the particles
		# still referenced by their behaviours, thus not getting garbage
		# collected?)
		to_remove = self.electrons.pop()
		self.remove(to_remove)
		for behaviour in self.electron_behaviours.keys():
			try:
				self.electron_behaviours[behaviour].remove(to_remove)
			except:
				pass
		to_remove = self.nucleons.pop()
		self.remove(to_remove)
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
		#while gc.collect():
		#	pass

	def send_left(self):
		"""Remove a nucleon from the current Square and add one to the
		Square on the left."""
		clutter.redraw()
		self.remove_particle()
		self.get_parent().add_particle((self.column - 1, self.row))

	def send_right(self):
		"""Remove a nucleon from the current Square and add one to the
		Square on the right."""
		clutter.redraw()
		self.remove_particle()
		self.get_parent().add_particle((self.column + 1, self.row))

	def send_up(self):
		"""Remove a nucleon from the current Square and add one to the
		Square above."""
		clutter.redraw()
		self.remove_particle()
		self.get_parent().add_particle((self.column, self.row - 1))

	def send_down(self):
		"""Remove a nucleon from the current Square and add one to the
		Square below."""
		clutter.redraw()
		self.remove_particle()
		self.get_parent().add_particle((self.column, self.row + 1))

	def explode(self):
		"""If the limit of the current Square has been reached then
		remove the nucleons from this Square and send them to neighbours."""
		# Chain reactions are implemented so that atoms explode followed
		# by their neighbours. A more elegant solution follows the
		# reaction to the end and works back, however this can go over
		# the maximum recursion depth, plus a critical/supercritical
		# mass in play wouldn't work as explosions would never end
		# Only explode if the atom has too many nucleons
		if len(self.electrons) >= self.limit:
			# Start the flash animation for an explosion effect
			self.flash_timeline.start()
			if self.type == 'corner_top_left':
				self.send_right()
				self.send_down()
				# Check if the atoms just added to need to explode
				self.get_parent().explode((self.column + 1, self.row))
				self.get_parent().explode((self.column, self.row + 1))
			elif self.type == 'corner_top_right':
				self.send_left()
				self.send_down()
				# Check if the atoms just added to need to explode
				self.get_parent().explode((self.column + -1, self.row))
				self.get_parent().explode((self.column, self.row + 1))
			elif self.type == 'corner_bottom_left':
				self.send_right()
				self.send_up()
				# Check if the atoms just added to need to explode
				self.get_parent().explode((self.column, self.row - 1))
				self.get_parent().explode((self.column + 1, self.row))
			elif self.type == 'corner_bottom_right':
				self.send_left()
				self.send_up()
				# Check if the atoms just added to need to explode
				self.get_parent().explode((self.column + -1, self.row))
				self.get_parent().explode((self.column, self.row - 1))
			elif self.type == 'edge_left':
				self.send_up()
				self.send_down()
				self.send_right()
				# Check if the atoms just added to need to explode
				self.get_parent().explode((self.column, self.row - 1))
				self.get_parent().explode((self.column, self.row + 1))
				self.get_parent().explode((self.column + 1, self.row))
			elif self.type == 'edge_right':
				self.send_up()
				self.send_down()
				self.send_left()
				# Check if the atoms just added to need to explode
				self.get_parent().explode((self.column, self.row - 1))
				self.get_parent().explode((self.column, self.row + 1))
				self.get_parent().explode((self.column + -1, self.row))
			elif self.type == 'edge_top':
				self.send_left()
				self.send_right()
				self.send_down()
				# Check if the atoms just added to need to explode
				self.get_parent().explode((self.column + -1, self.row))
				self.get_parent().explode((self.column + 1, self.row))
				self.get_parent().explode((self.column, self.row + 1))
			elif self.type == 'edge_bottom':
				self.send_left()
				self.send_right()
				self.send_up()
				# Check if the atoms just added to need to explode
				self.get_parent().explode((self.column + -1, self.row))
				self.get_parent().explode((self.column + 1, self.row))
				self.get_parent().explode((self.column, self.row - 1))
			else:
				self.send_up()
				self.send_down()
				self.send_left()
				self.send_right()
				# Check if the atoms just added to need to explode
				self.get_parent().explode((self.column, self.row - 1))
				self.get_parent().explode((self.column, self.row + 1))
				self.get_parent().explode((self.column + -1, self.row))
				self.get_parent().explode((self.column + 1, self.row))

# This is where execution starts
if __name__ == '__main__':
	# Keep all electrons in sync
	global electron_alpha
	electron_timeline = clutter.Timeline(fps=50, duration=1500)
	electron_timeline.set_loop(True)
	electron_alpha = clutter.Alpha(electron_timeline, clutter.ramp_inc_func)
	electron_timeline.start()

	# Define the players. Each colour must have a corresponding image
	# called colourproton_big.png in the images folder
	# Players are cycled through in the list order
	global colours
	global current_colour
	#colours = ['green', 'yellow', 'red', 'blue']
	colours = ['green']
	current_colour = 'green'

	# Set the board size
	columns = 8
	rows = 6

	# Set up the board
	display = ClutterDisplay((800, 600), (columns, rows), "#000000")

	# Run the game
	display.main()
