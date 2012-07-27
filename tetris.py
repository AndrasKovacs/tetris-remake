
import libtcodpy as lt 
import os
import random







FPS_LIMIT = 60 #level speeds are calibrated to 60 fps!
SCREEN_WIDTH = 40
SCREEN_HEIGHT = 25
FIELD_WIDTH = 12
FIELD_HEIGHT = 21


def help_color_rect_foreground(con, a, b, c, d, color):
	for i in xrange(a, a+c):
		for j in xrange(b, b+d):
			lt.console_set_char_foreground(con, i, j, color)


lt.console_set_custom_font(os.path.join('data', 'fonts','terminal16x16_gs_ro.png'), lt.FONT_TYPE_GREYSCALE | lt.FONT_LAYOUT_ASCII_INROW)
lt.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'KuttaTetris', fullscreen=False)

lt.sys_set_fps(FPS_LIMIT)

playfield_bg = lt.console_new(FIELD_WIDTH, FIELD_HEIGHT)
playfield    = lt.console_new(FIELD_WIDTH, FIELD_HEIGHT)

######################## render playfield_bg ########################

lt.console_set_default_foreground(playfield_bg, lt.light_blue)
for i in xrange(0, FIELD_HEIGHT-1):
	lt.console_print(playfield_bg, 0, i, chr(178) + ' . . . . .'  + chr(178))
lt.console_print(playfield_bg, 0, FIELD_HEIGHT-1, chr(178) * FIELD_WIDTH)
help_color_rect_foreground(playfield_bg, 1, 0, FIELD_WIDTH-2, FIELD_HEIGHT-1, lt.blue)

################## initialize non-changing window elements ###########

left_text = """
Your level: 
Full lines:

Score


   H E L P

F1:Pause
 7:Left
 9:Right
 8:Rotate
 1:Draw next
 6:Speed up
 4:Drop
  SPACE:Drop


    Next:



              Play TETRIS !
"""

right_text = """


   STATISTICS

  xxx    -
  x
    xxxx -

  xxx    -
   x
      xx -
     xx
  xx     -
   xx
      xx -
      xx
  xxx    -
    x
  ------------
  Sum    :  
""".replace('x', chr(219))

lt.console_print(0, 0, 0, left_text)
lt.console_print(0, 26, 0, right_text)

################## coloring ###################################

for i in xrange(14, 27):
	lt.console_set_char_foreground(0, i, 23, lt.red)

stat_colors = (lt.purple, lt.red, lt.orange, lt.green, lt.cyan, lt.blue, lt.silver)
for i,color in zip(xrange(5, 20, 2), stat_colors):
	help_color_rect_foreground(0, 28, i, 8, 2, color)


################# playfield mechanics ###########################


is_blocked = [[True]*FIELD_HEIGHT] + [[False]*(FIELD_HEIGHT-1) + [True] for i in xrange(FIELD_WIDTH-2)] + [[True]*FIELD_HEIGHT]
cell_color = [[False] * FIELD_HEIGHT for i in xrange(FIELD_WIDTH)]
		

class O(object):
	initpos 	= ((5, 0), (6, 0), (5, 1), (6, 1))
	color  	 	= lt.blue
	rotations 	= [((0, 0), (0, 0), (0, 0), (0, 0))]

class I(object):
	initpos 	= ((4, 0), (5, 0), (6, 0), (7, 0))
	color  	 	= lt.red
	rotations 	= [(( 2, -1), ( 1, 0), (0,  1), (-1,  2)), 
				   ((-2,  1), (-1, 0), (0, -1), ( 1, -2))]

class T(object):
	initpos 	= ((5, 0), (6, 0), (7, 0), (6, 1))
	color  	 	= lt.orange
	rotations 	=  [(( 1, 1), (0, 0), (-1, -1), ( 1, -1)),
					(( 1,-1), (0, 0), (-1,  1), (-1, -1)),
					((-1,-1), (0, 0), ( 1,  1), ( -1, 1)),
					((-1, 1), (0, 0), ( 1, -1), ( 1,  1))]

class L(object):
	initpos 	= ((5, 0), (6, 0), (7, 0), (5, 1))
	color  	 	= lt.purple
	rotations 	=  [(( 1, 1), (0, 0), (-1, -1), ( 2,  0)),
					(( 1,-1), (0, 0), (-1,  1), ( 0, -2)),
					((-1,-1), (0, 0), ( 1,  1), (-2,  0)),
					((-1, 1), (0, 0), ( 1, -1), ( 0,  2))]
		
class J(object):
	initpos 	= ((5, 0), (6, 0), (7, 0), (7, 1))
	color  	 	= lt.silver
	rotations 	=  [(( 1, 1), (0, 0), (-1, -1), ( 0, -2)),
					(( 1,-1), (0, 0), (-1,  1), (-2,  0)),
					((-1,-1), (0, 0), ( 1,  1), ( 0,  2)),
					((-1, 1), (0, 0), ( 1, -1), ( 2,  0))]

class S(object):
	initpos 	= ((5, 1), (6, 1), (6, 0), (7, 0))
	color  	 	= lt.green
	rotations 	=  [(( 2,  0), ( 1, -1), (0, 0), ( -1, -1)),
					((-2,  0), (-1,  1), (0, 0), (  1,  1))]

class Z(object):
	initpos 	= ((5, 0), (6, 0), (6, 1), (7, 1))
	color  	 	= lt.cyan
	rotations 	=  [(( 1,  1), (0, 0), ( 1, -1), (0, -2)),
					((-1, -1), (0, 0), (-1,  1), (0,  2))]

	



#(30, 24, 19, 15, 12, 10, 8, 6, 5, 4)

MOVE_SPEED = 30




def drop_piece(piece):

	global pos, rotation_state

	rotation_state = 0
	pos = piece.initpos[:]


	def handle_keys():
		global pos, move_count, rotation_state

		# handle keys

		key = lt.console_check_for_keypress(True) # exit
		if key.vk == lt.KEY_ESCAPE:
			return "exit"

		elif key.vk == lt.KEY_LEFT:  #move left
			npos = tuple((w-1, h) for w, h in pos)
			if not any(is_blocked[x][y] for x, y in npos):
				pos = npos

		elif key.vk == lt.KEY_RIGHT: # move right
			npos = tuple((w+1, h) for w, h in pos)
			if not any(is_blocked[x][y] for x, y in npos):
				pos = npos

		elif key.vk == lt.KEY_SPACE: # drop
			while not any(is_blocked[x][y+1] for x, y in pos):
				pos = tuple((w, h+1) for w, h in pos)
			move_count = 1 # makes moving after drop impossible

		elif key.vk == lt.KEY_UP: # rotate
			npos = tuple((w + dw, h + dh) for (w, h), (dw, dh) in zip(pos, piece.rotations[rotation_state]))
			if not any(is_blocked[x][y] for x, y in npos):
				pos = npos
				rotation_state += 1
				if rotation_state == len(piece.rotations):
					rotation_state = 0

		#render

		lt.console_blit(playfield_bg, 0, 0, FIELD_WIDTH, FIELD_HEIGHT, playfield, 0, 0)

		lt.console_set_default_foreground(playfield, piece.color)
		for x, y in pos: 
			lt.console_put_char(playfield, x, y , 219)

		for x in xrange(FIELD_WIDTH):
			for y in xrange(FIELD_HEIGHT):
				if cell_color[x][y]:
					lt.console_set_default_foreground(playfield, cell_color[x][y])
					lt.console_put_char(playfield, x, y , 219)

		lt.console_blit(playfield, 0, 0, FIELD_WIDTH, FIELD_HEIGHT, 0, 14, 1)
		lt.console_flush()

	def update_lines():
		for h in xrange(FIELD_HEIGHT-1):
			if all(is_blocked[w][h] for w in xrange(1, FIELD_WIDTH-1)):
				for w in xrange(1, FIELD_WIDTH-1):
					is_blocked[w][h] = False
					cell_color[w][h] = False
				for hn in reversed(xrange(h)):
					for wn in xrange(1, FIELD_WIDTH-1):
						is_blocked[wn][hn], is_blocked[wn][hn+1] =  is_blocked[wn][hn+1], is_blocked[wn][hn]
						cell_color[wn][hn], cell_color[wn][hn+1] =  cell_color[wn][hn+1], cell_color[wn][hn]

	
	if any(is_blocked[x][y] for x, y in pos):
		return "fail"  #game is over if initial position is already filled

	#wait quarter sec at top regardless of speed (seems to be the case in Tetris 3.12)
	for i in xrange(FPS_LIMIT/4):
		if handle_keys() == "exit": return "exit"

	global move_count
	move_count = MOVE_SPEED
	while True:
		move_count -= 1
		if not move_count:
			move_count = MOVE_SPEED
			npos = tuple((x, y+1) for x, y in pos)
			if any(is_blocked[x][y] for x, y in npos):
				for x, y in pos:
					is_blocked[x][y] = True
					cell_color[x][y] = piece.color
				update_lines()
				return "newdrop"
			else:
				pos = npos

		if handle_keys() == "exit": return "exit"



curr_piece = random.choice((O, I, T, L, J, S, Z))
while True:

	next_piece = random.choice((O, I, T, L, J, S, Z))
	action = drop_piece(curr_piece)
	if action == "exit":
		break
	elif action == "fail":
		break
	elif action == "newdrop":
		pass

	curr_piece = next_piece 








			
