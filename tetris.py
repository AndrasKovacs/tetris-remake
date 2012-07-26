
import libtcodpy as lt 
import os
import itertools

FPS_LIMIT = 60
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

# is_blocked = [[True] +[False]*(FIELD_WIDTH-2) + [True] for i in xrange(FIELD_HEIGHT-1)] + [[True] * FIELD_WIDTH]


is_blocked = [[True]*FIELD_HEIGHT] + [[False]*(FIELD_HEIGHT-1) + [True] for i in xrange(FIELD_WIDTH-2)] + [[True]*FIELD_HEIGHT]
cell_color = [[False] * FIELD_HEIGHT for i in xrange(FIELD_WIDTH)]
		

class O(object):
	initpos 	= ((5, 0), (6, 0), (5, 1), (6, 1))
	color  	 	= lt.blue
	rotations 	= itertools.cycle([[0, 0], [0, 0], [0, 0], [0, 0]])


#(4, 5, 6, 8, 10, 12, 15, 19, 24, 30)
#(30, 24, 19, 15, 12, 10, 8, 6, 5, 4)

SPEED = 30


def drop_piece():

	def handle_keys():
		key = lt.console_check_for_keypress(True)
		if key.vk == lt.KEY_ESCAPE:
			return "exit"
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

	piece = O  # to be extended
	pos = piece.initpos
	

	if any(is_blocked[x][y] for x, y in pos):
		return "fail"

	#wait quarter sec at top
	for i in xrange(FPS_LIMIT/4):
		if handle_keys() == "exit": return "exit"

	count = SPEED
	while True:
		count -= 1
		if not count:
			count = SPEED
			npos = tuple((x, y+1) for x, y in pos)
			if any(is_blocked[x][y] for x, y in npos):
				for x, y in pos:
					is_blocked[x][y] = True
					cell_color[x][y] = piece.color
				return "newdrop"
			else:
				pos = npos

		if handle_keys() == "exit": return "exit"


while True:

	action = drop_piece()
	print action
	if action == "exit":
		break
	elif action == "fail":
		break
	elif action == "newdrop":
		continue




			
