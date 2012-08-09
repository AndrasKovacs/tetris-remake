
import libtcodpy as lt 
import os
import time
import random


#TODO
	# Main menu: starting difficulty, manual difficulty, progressive difficulty



#constants
LEVEL_SPEEDS = (30, 24, 19, 15, 12, 10, 8, 6, 5, 4)
FPS_LIMIT = 60 #level speeds are calibrated for 60 fps!
SCREEN_WIDTH = 40
SCREEN_HEIGHT = 25
FIELD_WIDTH = 12
FIELD_HEIGHT = 21


#initialize windows
lt.console_set_custom_font(os.path.join('data', 'fonts','terminal16x16_gs_ro.png'), lt.FONT_TYPE_GREYSCALE | lt.FONT_LAYOUT_ASCII_INROW)
lt.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'KuttaTetris', fullscreen=False)
lt.sys_set_fps(FPS_LIMIT)
lt.console_set_keyboard_repeat(75, 40)

playfield_bg = lt.console_new(FIELD_WIDTH, FIELD_HEIGHT)
playfield    = lt.console_new(FIELD_WIDTH, FIELD_HEIGHT)


#pieces
class L(object):
	image		= " xxx\n x".replace('x', chr(219))
	initpos 	= ((5, 0), (6, 0), (7, 0), (5, 1))
	color  	 	= lt.purple
	rotations 	=  [(( 1, 1), (0, 0), (-1, -1), ( 2,  0)),
					(( 1,-1), (0, 0), (-1,  1), ( 0, -2)),
					((-1,-1), (0, 0), ( 1,  1), (-2,  0)),
					((-1, 1), (0, 0), ( 1, -1), ( 0,  2))]

class I(object):
	image		= "xxxx".replace('x', chr(219))
	initpos 	= ((4, 0), (5, 0), (6, 0), (7, 0))
	color  	 	= lt.red
	rotations 	= [(( 2, -1), ( 1, 0), (0,  1), (-1,  2)), 
				   ((-2,  1), (-1, 0), (0, -1), ( 1, -2))]

class T(object):
	image		= " xxx\n  x".replace('x', chr(219))
	initpos 	= ((5, 0), (6, 0), (7, 0), (6, 1))
	color  	 	= lt.orange
	rotations 	=  [(( 1, 1), (0, 0), (-1, -1), ( 1, -1)),
					(( 1,-1), (0, 0), (-1,  1), (-1, -1)),
					((-1,-1), (0, 0), ( 1,  1), ( -1, 1)),
					((-1, 1), (0, 0), ( 1, -1), ( 1,  1))]

class S(object):
	image		= " xx\nxx".replace('x', chr(219))
	initpos 	= ((5, 1), (6, 1), (6, 0), (7, 0))
	color  	 	= lt.green
	rotations 	=  [(( 2,  0), ( 1, -1), (0, 0), ( -1, -1)),
					((-2,  0), (-1,  1), (0, 0), (  1,  1))]

class Z(object):
	image		= " xx\n  xx".replace('x', chr(219))
	initpos 	= ((5, 0), (6, 0), (6, 1), (7, 1))
	color  	 	= lt.cyan
	rotations 	=  [(( 1,  1), (0, 0), ( 1, -1), (0, -2)),
					((-1, -1), (0, 0), (-1,  1), (0,  2))]
				
class O(object):
	image		= " xx\n xx".replace('x', chr(219))
	initpos 	= ((5, 0), (6, 0), (5, 1), (6, 1))
	color  	 	= lt.blue
	rotations 	= [((0, 0), (0, 0), (0, 0), (0, 0))]
		
class J(object):
	image		= " xxx\n   x".replace('x', chr(219))
	initpos 	= ((5, 0), (6, 0), (7, 0), (7, 1))
	color  	 	= lt.silver
	rotations 	=  [(( 1, 1), (0, 0), (-1, -1), ( 0, -2)),
					(( 1,-1), (0, 0), (-1,  1), (-2,  0)),
					((-1,-1), (0, 0), ( 1,  1), ( 0,  2)),
					((-1, 1), (0, 0), ( 1, -1), ( 2,  0))]


#Helpers
def help_color_rect_foreground(con, a, b, c, d, color):
	for i in xrange(a, a+c):
		for j in xrange(b, b+d):
			lt.console_set_char_foreground(con, i, j, color)

def help_color_print(con, w, h, string, color):
	defcolor = lt.console_get_default_foreground(con)
	lt.console_set_default_foreground(0, color)
	lt.console_print(con, w, h, string)
	lt.console_set_default_foreground(0, defcolor)


def get_textinput(w, h, message, fps, cursor, blink_speed, color, max_length, forbidden = tuple()):
    def_color = lt.console_get_default_foreground(0)
    lt.console_set_default_foreground(0, color)
    current_cursor = cursor
    inp = ""
    blink_toggle = int(fps*blink_speed)
    count = blink_toggle
    lt.console_print(0, w, h, " "*(len(message)+max_length))
    lt.console_print(0, w, h, message)
    w += len(message)
    inp_w = 0
    while True:
        count -= 1
        k = lt.console_check_for_keypress(True)
        if k.vk == lt.KEY_ESCAPE:
            break
        elif k.vk == lt.KEY_ENTER:
            lt.console_set_default_foreground(0, def_color)
            return inp
        elif k.vk == lt.KEY_BACKSPACE:
            if inp_w: 
                inp = inp[:-1]
                lt.console_print(0, w + inp_w, h, " ")
                inp_w -= 1
        elif k.vk == lt.KEY_NONE:
            pass
        elif k.vk == lt.KEY_SHIFT or not k.c:
            pass
        elif chr(k.c) in forbidden:
            pass
        else:
            if inp_w != max_length: 
                inp += chr(k.c)
                lt.console_print(0, w + inp_w, h, chr(k.c))
                inp_w += 1
        if not count:
            count = blink_toggle
            current_cursor = cursor if current_cursor == " " else " "
            lt.console_print(0, w + inp_w, h, current_cursor)
        lt.console_flush()


# the game of Tetris
def game_session():

	#initialize variables
	global show_next, level, full_lines, score, curr_piece, next_piece, move_speed, piece_stats, stats_sum
	show_next = True
	level = 0
	full_lines = 0
	score = 0
	curr_piece = random.choice((L, I, T, S, Z, O, J))
	next_piece = random.choice((L, I, T, S, Z, O, J))
	move_speed = LEVEL_SPEEDS[level]
	piece_stats = {L:0, I:0, T:0, S:0, Z:0, O:0, J:0}
	stats_sum = 0

	#panel texts
	pause_text = """
xxxxxxxxxxxx
xxxPAUSEDxxx
xxxxxxxxxxxx""".replace("x", chr(219))

	game_over_text = """
xxxxxxxxxxxx
xGAME  OVERx
xxxxxxxxxxxx""".replace("x", chr(219))


	left_text = """
Your level: 
Full lines:

Score


   H E L P

 p:Pause
 <:Left
 >:Right
 ^:Rotate
 1:Draw next
 6:Speed up
  SPACE:Drop



    Next:



              Play TETRIS !""".replace('<', chr(27)).replace('>', chr(26)).replace('^', chr(24))

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
  Sum    :  """.replace('x', chr(219))


	# renderers
	def render_panels():
		lt.console_print(0, 0, 0, left_text)
		lt.console_print(0, 26, 0, right_text)
		for i in xrange(14, 27):
			lt.console_set_char_foreground(0, i, 23, lt.red)

	def render_piece_stats():
		for i, piece in zip(xrange(5, 20, 2), (L, I, T, S, Z, O, J)):
			lt.console_print(0, 37, i, str(piece_stats[piece]).rjust(3))
			help_color_rect_foreground(0, 28, i, 12, 2, piece.color)

	def render_level():
		lt.console_print(0, 12, 1, str(level))

	def render_full_lines():
		lt.console_print(0, 11, 2, str(full_lines).center(3))

	def render_score():
		lt.console_set_default_foreground(0, lt.yellow)
		lt.console_print(0, 8, 4, str(score).rjust(4))
		lt.console_set_default_foreground(0, lt.white)

	def render_next():
		if not show_next: return
		lt.console_print(0, 4, 21, '    \n    ')
		lt.console_print(0, 4, 21, next_piece.image)
		help_color_rect_foreground(0, 4, 21, 10, 10, next_piece.color)

	def render_stats_sum():
		lt.console_print(0, 37, 20, str(stats_sum).rjust(3))

	def render_playfield_bg():
		lt.console_set_default_foreground(playfield_bg, lt.light_blue)
		for i in xrange(0, FIELD_HEIGHT-1):
			lt.console_print(playfield_bg, 0, i, chr(178) + ' . . . . .'  + chr(178))
		lt.console_print(playfield_bg, 0, FIELD_HEIGHT-1, chr(178) * FIELD_WIDTH)
		help_color_rect_foreground(playfield_bg, 1, 0, FIELD_WIDTH-2, FIELD_HEIGHT-1, lt.blue)

	def render_all():
		render_panels()
		render_piece_stats()
		render_level()
		render_full_lines()
		render_score()
		render_next()
		render_stats_sum()
		render_playfield_bg()


	#playfield mechanics 
	is_blocked = [[True]*FIELD_HEIGHT] + [[False]*(FIELD_HEIGHT-1) + [True] for i in xrange(FIELD_WIDTH-2)] + [[True]*FIELD_HEIGHT]
	cell_color = [[False] * FIELD_HEIGHT for i in xrange(FIELD_WIDTH)]
			

	def drop_piece(piece):

		global pos, rotation_state, stats_sum, score, show_next
		rotation_state = 0
		pos = piece.initpos[:]


		def render_playfield():
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


		def handle_keys():
			global pos, move_count, rotation_state, level, move_speed, show_next

			key = lt.console_check_for_keypress(True) 

			if key.vk == lt.KEY_ESCAPE:
				return "exit"

			if key.c == ord('p'): #pause
				lt.console_print(0, 14, 9, pause_text)
				lt.console_flush()
				while True:
					time.sleep(0.1)
					k = lt.console_check_for_keypress(True)
					if k.c == ord('p'): break
					if k.vk == lt.KEY_ESCAPE: return "exit"

			if key.vk == lt.KEY_1: #toggle show next
				if show_next: 
					show_next = False
					lt.console_print(0, 4, 21, '    \n    ')
				else:
					show_next = True
					render_next()

			if key.vk == lt.KEY_6: #increase level
				if level != len (LEVEL_SPEEDS) - 1:
					level += 1
					move_speed = LEVEL_SPEEDS[level]
					render_level()

			if key.vk == lt.KEY_LEFT:  #move left
				npos = tuple((w-1, h) for w, h in pos)
				if not any(is_blocked[x][y] for x, y in npos):
					pos = npos

			if key.vk == lt.KEY_RIGHT: # move right
				npos = tuple((w+1, h) for w, h in pos)
				if not any(is_blocked[x][y] for x, y in npos):
					pos = npos

			if key.vk == lt.KEY_UP: # rotate
				npos = tuple((w + dw, h + dh) for (w, h), (dw, dh) in zip(pos, piece.rotations[rotation_state]))
				if not any(is_blocked[x][y] for x, y in npos):
					pos = npos
					rotation_state += 1
					if rotation_state == len(piece.rotations):
						rotation_state = 0

			if key.vk == lt.KEY_SPACE: # drop
				while not any(is_blocked[x][y+1] for x, y in pos):
					pos = tuple((w, h+1) for w, h in pos)
				move_count = 1 # makes moving after drop impossible


		def update_lines():
			global full_lines
			for h in xrange(FIELD_HEIGHT-1):
				if all(is_blocked[w][h] for w in xrange(1, FIELD_WIDTH-1)):
					full_lines += 1
					for w in xrange(1, FIELD_WIDTH-1):
						is_blocked[w][h] = False
						cell_color[w][h] = False
					for hn in reversed(xrange(h)):
						for wn in xrange(1, FIELD_WIDTH-1):
							is_blocked[wn][hn], is_blocked[wn][hn+1] =  is_blocked[wn][hn+1], is_blocked[wn][hn]
							cell_color[wn][hn], cell_color[wn][hn+1] =  cell_color[wn][hn+1], cell_color[wn][hn]
			render_full_lines()

		#game is over if initial position is already filled
		if any(is_blocked[x][y] for x, y in pos):
			return "fail"  
		
		for i in xrange(FPS_LIMIT/4): #wait quarter sec at top regardless of speed (seems to be the case in Tetris 3.12)
			if handle_keys() == "exit": return "exit"
			render_playfield()

		global move_count
		move_count = move_speed
		rows_fallen = 0 
		while True:
			move_count -= 1
			if not move_count:
				move_count = move_speed
				npos = tuple((x, y+1) for x, y in pos)
				if any(is_blocked[x][y] for x, y in npos):
					for x, y in pos:
						is_blocked[x][y] = True
						cell_color[x][y] = piece.color

					piece_stats[curr_piece] += 1
					stats_sum += 1
					score += 19 - rows_fallen + level*3 + (5, 0)[show_next]

					update_lines()
					render_stats_sum() 
					render_score()
					render_piece_stats()
					return "newdrop"
				else:
					pos = npos
					rows_fallen += 1
			if handle_keys() == "exit": return "exit"
			render_playfield()


	def handle_high_scores(level, score):

		name_length = 10

		lt.console_clear(0)
		lt.console_flush()
		name = get_textinput(0, SCREEN_HEIGHT-1, "Enter name: ", FPS_LIMIT, chr(220), 0.33, lt.red, name_length, forbidden = (','))

		try:
			f = open("high_scores.txt", "a+") 
			hiscores = [tuple(line.rstrip().split(",")) for line in f]
			f.write(",".join((name, str(level), str(score))) + "\n")
		except IOError:
			f = open("high_scores.txt", "w")
			hiscores = []

		hiscores.append((name, level, score))
		hiscores = enumerate(sorted(hiscores, key = lambda x: int(x[2]), reverse=True)[:10], start=1)
		hiscores =  "\n".join(str(i).rjust(2) + "." + name.ljust(name_length+1) + str(level).ljust(7) + str(score).ljust(5) 
							      for (i, (name, level, score)) in hiscores)

		lt.console_clear(0)
		help_color_print(0, 14, 3, "HIGH SCORES", lt.red)
		lt.console_print(0, 7, 6, "  Name       Level  Score")
		lt.console_print(0, 6, 8, hiscores)

		while True:
			action = get_textinput(0, SCREEN_HEIGHT-1, "Play again? y/n: ", FPS_LIMIT, chr(220), 0.33, lt.red, name_length)
			if action in ("y", "Y"):
				lt.console_clear(0)
				return "restart"
			elif action in ("n", "N"):
				return "exit"

	render_all()
	action = "newdrop"

	while True:
		
		if action == "exit":
			return

		elif action == "restart":
			level = 0
			full_lines = 0
			score = 0
			move_speed = LEVEL_SPEEDS[level]
			piece_stats = {L:0, I:0, T:0, S:0, Z:0, O:0, J:0}
			stats_sum = 0
			is_blocked = [[True]*FIELD_HEIGHT] + [[False]*(FIELD_HEIGHT-1) + [True] for i in xrange(FIELD_WIDTH-2)] + [[True]*FIELD_HEIGHT]
			cell_color = [[False] * FIELD_HEIGHT for i in xrange(FIELD_WIDTH)]
			render_all()

		action = drop_piece(curr_piece)

		if action == "fail":
			lt.console_print(0, 14, 9, game_over_text)
			lt.console_print(0, 2, 15, "R: RESTART")
			help_color_rect_foreground(0, 2, 15, 10, 1, lt.red)
			lt.console_flush()

			k = lt.console_wait_for_keypress(True)
			if k.c == ord('r'):
				action = "restart"
			else: 
				action = handle_high_scores(level, score)

		elif action == "newdrop":
			curr_piece = next_piece 
			next_piece = random.choice((L, I, T, S, Z, O, J))
			render_next()
			lt.console_flush()


game_session()





			
