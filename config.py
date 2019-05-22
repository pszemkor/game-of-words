BOARD_SIZE = 15
TILEBOX_SIZE = 7

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

FIELD_RECTANGLE = (34, 34)
FIELD_RECTANGLE_WIDTH = FIELD_RECTANGLE[0] + 2
LEFT_EDGE_BOARD_OFFSET = (WINDOW_WIDTH - FIELD_RECTANGLE_WIDTH * BOARD_SIZE) // 2
TOP_EDGE_BOARD_OFFSET = 100
BOARD_WIDTH = BOARD_SIZE * FIELD_RECTANGLE_WIDTH

TOP_EDGE_TILEBOX_OFFSET = 650
LEFT_EDGE_TILEBOX_OFFSET = (WINDOW_WIDTH - FIELD_RECTANGLE_WIDTH * TILEBOX_SIZE) // 2
TILEBOX_WIDTH = TILEBOX_SIZE * FIELD_RECTANGLE_WIDTH

ACTIVE_FIELD_BORDER_SIZE = 2

SCOREBOARD_SHAPE = (200, 50)