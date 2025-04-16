# This is the code used to generate the Firefox version

PDF_FILE_TEMPLATE = """
%PDF-1.6

% Root
1 0 obj
<<
  /AcroForm <<
    /Fields [ ###FIELD_LIST### ]
  >>
  /Pages 2 0 R
  /OpenAction 17 0 R
  /Type /Catalog
>>
endobj

2 0 obj
<<
  /Count 1
  /Kids [
    16 0 R
  ]
  /Type /Pages
>>
endobj

%% Annots Page 1 (also used as overall fields list)
21 0 obj
[
  ###FIELD_LIST###
]
endobj

###FIELDS###

%% Page 1
16 0 obj
<<
  /Annots 21 0 R
  /Contents 3 0 R
  /CropBox [
    0.0
    0.0
    612.0
    792.0
  ]
  /MediaBox [
    0.0
    0.0
    612.0
    792.0
  ]
  /Parent 2 0 R
  /Resources <<
  >>
  /Rotate 0
  /Type /Page
>>
endobj

3 0 obj
<< >>
stream
endstream
endobj

17 0 obj
<<
  /JS 42 0 R
  /S /JavaScript
>>
endobj


42 0 obj
<< >>
stream

// Hacky wrapper to work with a callback instead of a string 
function setInterval(cb, ms) {
	evalStr = "(" + cb.toString() + ")();";
	return app.setInterval(evalStr, ms);
}

// https://gist.github.com/blixt/f17b47c62508be59987b
var rand_seed = Date.now() % 2147483647;
function rand() {
	return rand_seed = rand_seed * 16807 % 2147483647;
}

var game_board = [];
var valid_moves = new Set();
var valid_jumps = new Set();

var current_selected_piece = "";

var turn_counter = 0;
var red_remaining_pieces = 12;
var white_remaining_pieces = 12;

var jump_mode = false;


//write an init function that sets up the pieces on the board
function init_board() {
  game_board = [
    [ 0, -1,  0, -1,  0, -1,  0, -1],
    [ -1, 0, -1,  0, -1,  0, -1,  0],
    [ 0, -1,  0, -1,  0, -1,  0, -1],
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 1,  0,  1,  0,  1,  0,  1,  0],
    [ 0,  1,  0,  1,  0,  1,  0,  1],
    [ 1,  0,  1,  0,  1,  0,  1,  0]
  ];
  	// because of the weird way this array of arrays is set up, its now game_board[###GRID_HEIGHT### - 1 - y][x] to look like screen
  	this.getField("T_print").value = "New game started";

	// Hide start button
	hide("B_start");
	hide("B_end_turn");

	//refreshes the board to initialize rendering
	update_board();
}

// this function is supposed to print name in the blue box on the right called T_print
function print_my_name(name) {
    // If no name is provided, use a default message
    var messageToPrint = name || "Print my name";
	this.getField("T_print").value = messageToPrint;
}


// refreshes entire board
function update_board() {
	for (var x = 0; x < ###GRID_WIDTH###; x++) {
		for (var y = 0; y < ###GRID_HEIGHT###; y++) {

			// hide the piece first
			hide(`C_white_coord_${x}_${y}`);
			hide(`C_red_coord_${x}_${y}`);
			hide(`C_king_coord_${x}_${y}`);
			
			// negative: white piece
			if (game_board[###GRID_HEIGHT### - 1 - y][x] < 0) {
				show(`C_white_coord_${x}_${y}`);
				if (game_board[###GRID_HEIGHT### - 1 - y][x] == -2) {
					show(`C_king_coord_${x}_${y}`);
				}
			}
			// positive: red piece
			else if (game_board[###GRID_HEIGHT### - 1 - y][x] > 0) {
				show(`C_red_coord_${x}_${y}`);
				if (game_board[###GRID_HEIGHT### - 1 - y][x] == 2) {
					show(`C_king_coord_${x}_${y}`);
				}
			}
		}
	}
}


// ran after a red/white checkers piece is clicked
// checks for possible moves/jumps
function select_checkers_piece(coord, multi_jump_pass) {

	// this is the most cursed bit of code here: multi_jump_pass isn't usually defined when you click a piece
	// but it's defined in the case of jumps (see the check_for_chain_jumps function), allowing multi jumps to bypass this check
	// (I could rewrite this function without this check under check_for_chain_jumps, but this works)
	if (jump_mode && typeof multi_jump_pass == "undefined") {
		this.getField("T_print").value = "Can't select another piece during jumps";
		return;
	}

	current_selected_piece = coord;

	var current_piece_coord = current_selected_piece.match(/.*_(\d+)_(\d+)/);
	var current_x = parseInt(current_piece_coord[1]);
	var current_y = parseInt(current_piece_coord[2]);

	var current_piece_id = game_board[###GRID_HEIGHT### - 1 - current_y][current_x];
	
	// prevent wrong team piece selection
	if (turn_counter % 2 == 0 && current_piece_id < 0) {
		// red's turn, and white piece is clicked
		this.getField("T_print").value = "Can't move white piece during red turn";
		current_selected_piece = "";
		return;
	}
	else if (turn_counter % 2 == 1 && current_piece_id > 0) {
		// white's turn, but red piece is selected
		this.getField("T_print").value = "Can't move red piece during white turn";
		current_selected_piece = "";
		return;
	}


	//get all 4 possible moves
	valid_moves.clear();
	valid_jumps.clear();
	valid_moves.add(`Grid_${current_x - 1}_${current_y + 1}`);
	valid_moves.add(`Grid_${current_x + 1}_${current_y + 1}`);
	valid_moves.add(`Grid_${current_x - 1}_${current_y - 1}`);
	valid_moves.add(`Grid_${current_x + 1}_${current_y - 1}`);

	// normal red pieces can't move downwards
	if (current_piece_id == 1) {
		valid_moves.delete(`Grid_${current_x - 1}_${current_y - 1}`);
		valid_moves.delete(`Grid_${current_x + 1}_${current_y - 1}`);
	}

	// normal white pieces can't move up
	if (current_piece_id == -1) {
		valid_moves.delete(`Grid_${current_x - 1}_${current_y + 1}`);
		valid_moves.delete(`Grid_${current_x + 1}_${current_y + 1}`);
	}

	//check if moves out of bound, delete if so
	for (let item of valid_moves) {

		var get_coord = item.match(/.*_(-?\d+)_(-?\d+)/);
		var x = parseInt(get_coord[1]);
		var y = parseInt(get_coord[2]);

		if (x < 0 || x >= ###GRID_WIDTH### || y < 0 || y >= ###GRID_HEIGHT###) {
			valid_moves.delete(item);
		}
	}

	//check if can jump over a piece
	for (let item of valid_moves) {

		var move_dir_coord = item.match(/.*_(\d+)_(\d+)/);
		var move_x = parseInt(move_dir_coord[1]);
		var move_y = parseInt(move_dir_coord[2]);
		var move_dir_piece_id = game_board[###GRID_HEIGHT### - 1 - move_y][move_x];


		// if there is a friendly piece in that direction: get rid from valid moves + continue
		if (Math.sign(move_dir_piece_id) == Math.sign(current_piece_id)) {
			valid_moves.delete(item);
			continue;
		}

		//if there is no pieces in that direction: this is a valid move
		if (game_board[###GRID_HEIGHT### - 1 - move_y][move_x] == 0) {
			continue; // valid move means no need to jump
		}

		//the coord one diagonal beyond (whichever direction) (epic math)
		var skipping_target_x = move_x + (move_x - current_x);
		var skipping_target_y = move_y + (move_y - current_y);

		//check if the skipping target is within bound
		if (skipping_target_x < 0 || skipping_target_x >= ###GRID_WIDTH### || skipping_target_y < 0 || skipping_target_y >= ###GRID_HEIGHT###) {
			continue; // it's out of bound, no valid jumps
		}

		var skipping_target_piece_id = game_board[###GRID_HEIGHT### - 1 - skipping_target_y][skipping_target_x];
		if (skipping_target_piece_id != 0) {
			continue; // there is another piece at the skipping target, no valid jumps
		}

		//finally, skipping target is empty, valid jumps
		valid_moves.delete(item);
		valid_jumps.add(`Grid_${skipping_target_x}_${skipping_target_y}`);

		var messageToPrint = "";
		for (let item of valid_jumps) {
			messageToPrint = messageToPrint + " " + item;
		}
		// this.getField("T_score").value = "Possible jumps:" + messageToPrint;

	}
	
	var messageToPrint = "Selected: " + current_selected_piece;
	this.getField("T_print").value = messageToPrint;
}

// runs after an empty tile is clicked
// checks if the selected piece can move/jump here. If so, do it
function check_for_valid_movement(coord) {

	if (current_selected_piece === "") {
		this.getField("T_print").value = "nothing selected: " + coord;
		return;
	}

	// else the check if current piece can move to coord
	if (valid_moves.has(coord)) {
		move_to(coord);

		//unselects the piece
		this.getField("T_print").value = "unselected: " + current_selected_piece;
		end_turn();

		valid_moves.clear();
		valid_jumps.clear();
	}
	else if (valid_jumps.has(coord)) {
		jump_to(coord);

		valid_moves.clear();
		valid_jumps.clear();

		//check for additional jumps
		check_for_chain_jumps(coord);

		//stops you from selecting other ones after checking jump
		jump_mode = true;
		
		show("B_end_turn");
	}
	else {
		this.getField("T_print").value = "invalid move";
	}
}

function check_for_chain_jumps(position) {
	// this.getField("T_print").value = "checking for chain jumps";
	select_checkers_piece(position, "cursed passing technique");
	valid_moves.clear();
}

function end_turn() {
	jump_mode = false;
	turn_counter++;
	display_turn();
	victory_check();
	current_selected_piece = "";
	hide("B_end_turn");
}


// check who's turn it is, ran after moved/jumped
function display_turn() {
	if (turn_counter % 2 == 0) {
		this.getField("T_score").value = "Red's turn";
	}
	else if (turn_counter % 2 == 1) {
		this.getField("T_score").value = "White's turn";
	}
}

// check who won, ran after move/jump
function victory_check() {
	//check if game ended
	if (red_remaining_pieces == 0) {
		this.getField("T_score").value = "White won";
		app.alert("White has won! (Refresh this page to start another game)");
		return;
	}
	else if (white_remaining_pieces == 0) {
		this.getField("T_score").value = "Red won";
		app.alert("Red has won! Refresh this page to start another game)");
		return;
	}
}


// this function handles piece movement
function move_to(target) {
	// Naming conventions: Grids: Grid_{x}_{y} || Pieces: C_red_coord_{x}_{y}

	// retrieve current & target coord from name (and their x, y)
	var current_coord = current_selected_piece.match(/.*_(\d+)_(\d+)/);
	var target_coord = target.match(/.*_(\d+)_(\d+)/);

	var current_x = parseInt(current_coord[1]);
	var current_y = parseInt(current_coord[2]);
	var target_x = parseInt(target_coord[1]);
	var target_y = parseInt(target_coord[2]);

	//getting piece location and which piece
	var piece_id = game_board[###GRID_HEIGHT### - 1 - current_y][current_x];

	// check if red piece moved all the way to top row (and white to bottom)
	if (Math.sign(piece_id) == 1 && target_y == ###GRID_HEIGHT### - 1 && piece_id != 2) {
		game_board[###GRID_HEIGHT### - 1 - current_y][current_x] = 2;
		piece_id = 2;
		// app.alert("Red piece has reached the end");
	}

	if (Math.sign(piece_id) == -1 && target_y == 0 && piece_id != -2) {
		game_board[###GRID_HEIGHT### - 1 - current_y][current_x] = -2;
		piece_id = -2;
		// app.alert("White piece has reached the end");
	}



	//move piece to new location
	game_board[###GRID_HEIGHT### - 1 - current_y][current_x] = 0;
	game_board[###GRID_HEIGHT### - 1 - target_y][target_x] = piece_id;

	//call the update function to redraw board
	update_board();

}

function jump_to(target) {
	
	//current coord and target coord
	var current_coord = current_selected_piece.match(/.*_(\d+)_(\d+)/);
	var current_x = parseInt(current_coord[1]);
	var current_y = parseInt(current_coord[2]);
	var piece_id = game_board[###GRID_HEIGHT### - 1 - current_y][current_x];

	// check piece id team to dock alive points
	if (piece_id > 0) {
		//red piece jumps over white
		white_remaining_pieces--;
	}
	else if (piece_id < 0) {
		//white pieces jumps over red
		red_remaining_pieces--;
	}

	var target_coord = target.match(/.*_(\d+)_(\d+)/);
	var target_x = parseInt(target_coord[1]);
	var target_y = parseInt(target_coord[2]);

	// check if red piece moved all the way to top row (and white to bottom)
	if (Math.sign(piece_id) == 1 && target_y == ###GRID_HEIGHT### - 1 && piece_id != 2) {
		game_board[###GRID_HEIGHT### - 1 - current_y][current_x] = 2;
		piece_id = 2;
		// app.alert("Red piece has reached the end");
	}

	if (Math.sign(piece_id) == -1 && target_y == 0 && piece_id != -2) {
		game_board[###GRID_HEIGHT### - 1 - current_y][current_x] = -2;
		piece_id = -2;
		// app.alert("White piece has reached the end");
	}


	//gets the intermediate piece coord
	var piece_between_x = (current_x + target_x) / 2;
	var piece_between_y = (current_y + target_y) / 2;

	//move piece to new location
	game_board[###GRID_HEIGHT### - 1 - current_y][current_x] = 0;
	game_board[###GRID_HEIGHT### - 1 - target_y][target_x] = piece_id;

	//get rid of skipped piece
	game_board[###GRID_HEIGHT### - 1 - piece_between_y][piece_between_x] = 0;

	//call the update function to redraw board
	update_board();
}

function hide(n) {
	this.getField(n).hidden = true;
}

function show(n) {
	this.getField(n).hidden = false;
}




// Zoom to fit (on FF)
app.execMenuItem("FitPage");

endstream
endobj


18 0 obj
<<
  /JS 43 0 R
  /S /JavaScript
>>
endobj


43 0 obj
<< >>
stream

endstream
endobj

trailer
<<
  /Root 1 0 R
>>

%%EOF
"""

# this is the gray background pixels that mark the playable area
# this entire object is un needed in checkers
PLAYING_FIELD_OBJ = """
###IDX### obj
<<
  /FT /Btn
  /Ff 1
  /MK <<
    /BG [
      0.8
    ]
    /BC [
      0 0 0
    ]
  >>
  /Border [ 0 0 1 ]
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (playing_field)
  /Type /Annot
>>
endobj
"""

#This is the actual tetris blocks, colors controlled by ###color
PIXEL_OBJ = """
###IDX### obj
<<
  /FT /Btn
  /Ff 1
  /MK <<
    /BG [
      ###COLOR###
    ]
    /BC [
      0.5 0.5 0.5
    ]
  >>
  /Border [ 0 0 1 ]
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (P_###X###_###Y###)
  /Type /Annot
>>
endobj
"""


# This is the appearance stream
BUTTON_AP_STREAM = """
###IDX### obj
<<
  /BBox [ 0.0 0.0 ###WIDTH### ###HEIGHT### ]
  /FormType 1
  /Matrix [ 1.0 0.0 0.0 1.0 0.0 0.0]
  /Resources <<
    /Font <<
      /HeBo 10 0 R
    >>
    /ProcSet [ /PDF /Text ]
  >>
  /Subtype /Form
  /Type /XObject
>>
stream
q
0.75 g
0.5 G
1 w
0 0 ###WIDTH### ###HEIGHT### re
B
Q
q
1 1 ###WIDTH### ###HEIGHT### re
W
n
BT
/HeBo 12 Tf
0 g
10 8 Td
(###TEXT###) Tj
ET
Q
endstream
endobj
"""

# for the checkers pieces, replace ###COLOR### with whatever
CHECKERS_PIECES_AP_STREAM = """
###IDX### obj
<<
  /BBox [ 0.0 0.0 ###WIDTH### ###HEIGHT### ]
  /FormType 1
  /Matrix [ 1.0 0.0 0.0 1.0 0.0 0.0]
  /Resources <<
    /Font <<
      /HeBo 10 0 R
    >>
    /ProcSet [ /PDF /Text ]
  >>
  /Subtype /Form
  /Type /XObject
>>
stream
q
###COLOR### rg
0.5 G
1 w
0 0 ###WIDTH### ###HEIGHT### re
B
Q
q
1 1 ###WIDTH### ###HEIGHT### re
W
n
BT
/HeBo 12 Tf
0 g
10 8 Td
(###TEXT###) Tj
ET
Q
endstream
endobj
"""

# for making buttons, like the checkers grid in the background (or the pieces in the og tetris game)
BUTTON_OBJ = """
###IDX### obj
<<
  /A <<
	  /JS ###SCRIPT_IDX### R
	  /S /JavaScript
	>>
  /AP <<
    /N ###AP_IDX### R
  >>
  /F 4
  /FT /Btn
  /Ff 65536
  /MK <<
    /BG [
      0.75
    ]
    /CA (###LABEL###)
  >>
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (###NAME###)
  /Type /Annot
>>
endobj
"""

# the blue text fields
TEXT_OBJ = """
###IDX### obj
<<
	/AA <<
		/K <<
			/JS ###SCRIPT_IDX### R
			/S /JavaScript
		>>
	>>
	/F 4
	/FT /Tx
	/MK <<
	>>
	/MaxLen 0
	/P 16 0 R
	/Rect [
		###RECT###
	]
	/Subtype /Widget
	/T (###NAME###)
	/V (###LABEL###)
	/Type /Annot
>>
endobj
"""

# a moldable object, good for containing the scripts for the buttons
STREAM_OBJ = """
###IDX### obj
<< >>
stream
###CONTENT###
endstream
endobj
"""

PIECE_OBJ = """
###IDX### obj
<<
  /FT /Btn
  /Ff 1
  /MK <<
    /BG [
      ###COLOR###
    ]
    /BC [
      0.5 0.5 0.5
    ]
  >>
  /Border [ 0 0 1 ]
  /P 16 0 R
  /Rect [
    ###RECT###
  ]
  /Subtype /Widget
  /T (P_###X###_###Y###)
  /Type /Annot
>>
endobj
"""


PX_SIZE = 20
GRID_WIDTH = 8
GRID_HEIGHT = 8
GRID_OFF_X = 200
GRID_OFF_Y = 350

fields_text = ""
field_indexes = []
obj_idx_ctr = 50 # starts counting the pixels/generated objects after the 50th object

#for adding each field
def add_field(field):
	global fields_text, field_indexes, obj_idx_ctr
	fields_text += field
	field_indexes.append(obj_idx_ctr)
	obj_idx_ctr += 1

# three things generated by this pdf for buttons:
# 1. A script object with the JavaScript action
# 2. An appearance stream defining the button's look
# 3. The button object itself linking the script and appearance
def add_button(label, name, x, y, width, height, js):
	script = STREAM_OBJ;
	script = script.replace("###IDX###", f"{obj_idx_ctr} 0")
	script = script.replace("###CONTENT###", js)
	add_field(script)

	ap_stream = BUTTON_AP_STREAM;
	ap_stream = ap_stream.replace("###IDX###", f"{obj_idx_ctr} 0")
	ap_stream = ap_stream.replace("###TEXT###", label)
	ap_stream = ap_stream.replace("###WIDTH###", f"{width}")
	ap_stream = ap_stream.replace("###HEIGHT###", f"{height}")
	add_field(ap_stream)

	button = BUTTON_OBJ;
	button = button.replace("###IDX###", f"{obj_idx_ctr} 0")
	button = button.replace("###SCRIPT_IDX###", f"{obj_idx_ctr-2} 0")
	button = button.replace("###AP_IDX###", f"{obj_idx_ctr-1} 0")
	#button = button.replace("###LABEL###", label)
	button = button.replace("###NAME###", name if name else f"B_{obj_idx_ctr}")
	button = button.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
	add_field(button)

# Add checkers pieces, but with special ap stream
def add_checkers_piece(label, name, x, y, width, height, js, color):
	script = STREAM_OBJ;
	script = script.replace("###IDX###", f"{obj_idx_ctr} 0")
	script = script.replace("###CONTENT###", js)
	add_field(script)

	ap_stream = CHECKERS_PIECES_AP_STREAM;
	ap_stream = ap_stream.replace("###IDX###", f"{obj_idx_ctr} 0")
	# c = [1, 0, 0] #color of red
	ap_stream = ap_stream.replace("###COLOR###", f"{color[0]} {color[1]} {color[2]}")
	ap_stream = ap_stream.replace("###TEXT###", label)
	ap_stream = ap_stream.replace("###WIDTH###", f"{width}")
	ap_stream = ap_stream.replace("###HEIGHT###", f"{height}")
	add_field(ap_stream)

	button = BUTTON_OBJ;
	button = button.replace("###IDX###", f"{obj_idx_ctr} 0")
	button = button.replace("###SCRIPT_IDX###", f"{obj_idx_ctr-2} 0")
	button = button.replace("###AP_IDX###", f"{obj_idx_ctr-1} 0")
	#button = button.replace("###LABEL###", label)
	button = button.replace("###NAME###", name if name else f"B_{obj_idx_ctr}")
	button = button.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
	add_field(button)

# Playing field outline (the big outline around the entire tetris board)
playing_field = PLAYING_FIELD_OBJ
playing_field = playing_field.replace("###IDX###", f"{obj_idx_ctr} 0")
playing_field = playing_field.replace("###RECT###", f"{GRID_OFF_X-0.5} {GRID_OFF_Y} {GRID_OFF_X+GRID_WIDTH*PX_SIZE} {GRID_OFF_Y+GRID_HEIGHT*PX_SIZE}")
add_field(playing_field) # the 0.5 is a number i pulled out of my butt so the grid shifts left for a bit

# this part builds the checkers grid
for x in range(GRID_WIDTH):
    for y in range(GRID_HEIGHT):

		# grid buttons
        grid_label = "" # the label shows up on the actual button (if large enough)
        button_name = f"Grid_{x}_{y}"
        c = [0.9, 0.9, 0.9] if (x + y) % 2 == 1 else [0.7, 0.7, 0.7]

		# Add the grid squares (abusing the add checkers piece function because that one has colors)
        add_checkers_piece(grid_label, button_name, 
                   GRID_OFF_X + x * PX_SIZE,
                   GRID_OFF_Y + y * PX_SIZE, 
                   PX_SIZE, #    GRID_OFF_X + x * PX_SIZE + PX_SIZE 
                   PX_SIZE, #    GRID_OFF_Y + y * PX_SIZE + PX_SIZE, 
                   f"check_for_valid_movement('{button_name}');", 
                   c # color
                   )


# this part builds the possible checkers positions as buttons
for x in range(GRID_WIDTH):
    for y in range(GRID_HEIGHT):
        # Create button with coordinate name
        button_label = f"" # again this label is visible
        button_name = f"C_red_coord_{x}_{y}"
        
        # Add checkers with slightly smaller size, positioned inside the grid squares
        add_checkers_piece(button_label, button_name, 
                   GRID_OFF_X + x * PX_SIZE + 5, 
                   GRID_OFF_Y + y * PX_SIZE + 5, 
                   PX_SIZE - 10, 
                   PX_SIZE - 10,
                   f"select_checkers_piece('{button_name}');", 
                   [1, 0, 0] # color (red)
                   )

        # Add white checkers
        button_label = f"White: {x},{y}"
        button_name = f"C_white_coord_{x}_{y}"
        
        # Add checkers with slightly smaller size, positioned inside the grid squares
        add_checkers_piece(button_label, button_name, 
                   GRID_OFF_X + x * PX_SIZE + 5, 
                   GRID_OFF_Y + y * PX_SIZE + 5, 
                   PX_SIZE - 10,
                   PX_SIZE - 10,
                   f"select_checkers_piece('{button_name}');",
				   [1, 1, 1] # color (white)
				   )


		# Add the black king indicators
        button_label = f"King: {x},{y}"
        button_name = f"C_king_coord_{x}_{y}"

		# Add checkers with slightly smaller size, positioned inside the grid squares
        add_checkers_piece(button_label, button_name, 
                   GRID_OFF_X + x * PX_SIZE + 8, 
                   GRID_OFF_Y + y * PX_SIZE + 8,
                   PX_SIZE - 16,
                   PX_SIZE - 16,
                   f"show('{button_name}');",
				   [0.45, 0.45, 0.45] # color
				   )


def add_text(label, name, x, y, width, height, js):
	script = STREAM_OBJ;
	script = script.replace("###IDX###", f"{obj_idx_ctr} 0")
	script = script.replace("###CONTENT###", js)
	add_field(script)

	text = TEXT_OBJ;
	text = text.replace("###IDX###", f"{obj_idx_ctr} 0")
	text = text.replace("###SCRIPT_IDX###", f"{obj_idx_ctr-1} 0")
	text = text.replace("###LABEL###", label)
	text = text.replace("###NAME###", name)
	text = text.replace("###RECT###", f"{x} {y} {x + width} {y + height}")
	add_field(text)

# maybe maybe add a image template for streaming images later (checkers, king logo)

# Start game button
add_button("Start game", "B_start", GRID_OFF_X + (GRID_WIDTH*PX_SIZE)/2-50, GRID_OFF_Y + (GRID_HEIGHT*PX_SIZE)/2-200, 100, 100, "init_board();")
# add_button("Chromium controls", "B_joystick_controls", GRID_OFF_X + (GRID_WIDTH*PX_SIZE)/2 - 250, GRID_OFF_Y + (GRID_HEIGHT*PX_SIZE)/2-400, 125, 50, "")

add_text("Red starts", "T_score", GRID_OFF_X + GRID_WIDTH*PX_SIZE+10, GRID_OFF_Y + GRID_HEIGHT*PX_SIZE-50, 100, 50, "")
add_text("Information print here", "T_print", GRID_OFF_X + GRID_WIDTH*PX_SIZE+10, GRID_OFF_Y + GRID_HEIGHT*PX_SIZE-100, 100, 50, "")
add_button("End jumps", "B_end_turn", GRID_OFF_X + GRID_WIDTH*PX_SIZE+10, GRID_OFF_Y + GRID_HEIGHT*PX_SIZE - 150, 100, 50, "end_turn();")


# print name buttons early testing
# add_button("Print my name", "B_print_my_name", GRID_OFF_X + 140, GRID_OFF_Y - 300, 50, 50, "print_my_name();")
# add_button("Print Alice", "B_print_alice", GRID_OFF_X + 200, GRID_OFF_Y - 300, 50, 50, "print_my_name('Alice');")


filled_pdf = PDF_FILE_TEMPLATE.replace("###FIELDS###", fields_text)
filled_pdf = filled_pdf.replace("###FIELD_LIST###", " ".join([f"{i} 0 R" for i in field_indexes]))
filled_pdf = filled_pdf.replace("###GRID_WIDTH###", f"{GRID_WIDTH}")
filled_pdf = filled_pdf.replace("###GRID_HEIGHT###", f"{GRID_HEIGHT}")

pdffile = open("checkers(firefox).pdf","w")
pdffile.write(filled_pdf)
pdffile.close()