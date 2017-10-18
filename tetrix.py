from PyQt5.QtWidgets import QMainWindow, QFrame, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont
import sys, random

#========CONSTANTS==========#
TITLE_OF_PROGRAM = "PyQtTetrix"
TILE_SIZE = 30
WELL_X = 10
WELL_Y = 20
WINDOW_WIDTH = WELL_X * TILE_SIZE + 180
WINDOW_HEIGHT = WELL_Y * TILE_SIZE
NUM_BLOCKS_IN_PIECE = 4
ScoreTable = [ 300, 500, 700, 1500 ]

class Window( QMainWindow ):
    
    def __init__( self ):
        super().__init__()
        self.init_UI()
        

    def init_UI( self ):
        self.canvas = Canvas( self )
        self.setCentralWidget( self.canvas )
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.centralize()
        self.setWindowTitle(TITLE_OF_PROGRAM)
        self.show()


    def centralize( self ):
        screen_rect = QDesktopWidget().screenGeometry()
        window_rect = self.geometry()
        dx = ( screen_rect.width() - window_rect.width() ) / 2
        dy = ( screen_rect.height() - window_rect.height() ) / 2
        self.move( dx, dy)        


class Canvas( QFrame ):

    def __init__( self, parent = None ):
        super().__init__( parent )
        self.setFocusPolicy(Qt.StrongFocus)
        self.is_game_over = False
        self.score = 0
        self.num_of_removed_lines = 0
        self.level = 1
        self.well = Well( WELL_X, WELL_Y + 1, TILE_SIZE )
        self.active_tetramino = Tetramino(4, 0, random.choice( range(len(Shape.table))))
        self.next_tetramino = Tetramino(11, 1, random.choice( range(len(Shape.table))))
        self.timer = QBasicTimer()
        self.timer.start(1000.0 / self.level , self)
        

    def start_new_game( self ):
        self.is_game_over = False
        self.score = 0
        self.num_of_removed_lines = 0
        self.level = 1
        self.well.clear_grid()
        self.active_tetramino = Tetramino(4, 0, random.choice(
            range(len(Shape.table))))
        self.next_tetramino = Tetramino(11, 2, random.choice(
            range(len(Shape.table))))
        self.timer.start(1000.0 / self.level , self)
        pass

    
    def __is_touching_ground_( self, tetramino ):
        blocks = tetramino.get_blocks()
        for block in blocks:
            if self.well.is_tile_solid( block.get_x(), block.get_y() + 1 ):
                return True
        return False
    

    def __is_colliding_wall_( self, tetramino ):
        blocks = tetramino.get_blocks()
        for block in blocks:
            if block.get_x() < 0 or block.get_x() >= WELL_X:
                return True
            if self.well.is_tile_solid( block.get_x(), block.get_y() ):
                return True
        return False


    def __unite_( self, tetramino ):
        blocks = tetramino.get_blocks()
        for block in blocks:
            self.well.set_tile( block.get_x(), block.get_y() )
        

    def timerEvent( self, event ):
        if event.timerId() == self.timer.timerId():
            if self.__is_touching_ground_( self.active_tetramino ):
                self.__unite_( self.active_tetramino )
                self.next_tetramino.set_pos(4, 0)
                self.active_tetramino = self.next_tetramino
                self.next_tetramino = Tetramino(11, 2, random.choice(
                    range(len(Shape.table))))
                if self.__is_colliding_wall_( self.active_tetramino ):
                    self.is_game_over = True
                    self.timer.stop()
                self.update()
            else:
                self.active_tetramino.step_down()
                self.update()
                num_lines = self.well.remove_filled_lines()
                if num_lines > 0:
                    self.score += ScoreTable[ num_lines - 1 ]
                    self.num_of_removed_lines += num_lines
                    if self.score > self.level * 500:
                        self.level += 1
                        self.timer.start(1000.0 / self.level , self )                
        else:
            super( Canvas, self ).timerEvent( event )

        
    def keyPressEvent( self, event ):
        key = event.key()

        if key == Qt.Key_Up:
            copy = self.active_tetramino.get_copy()
            copy.rotate_left()
            if not self.__is_colliding_wall_( copy ):
                self.active_tetramino.rotate_left()
                self.update()
        elif key == Qt.Key_Down:
            copy = self.active_tetramino.get_copy()
            copy.rotate_right()
            if not self.__is_colliding_wall_( copy ):
                self.active_tetramino.rotate_right()
                self.update()
        elif key == Qt.Key_Left:
            copy = self.active_tetramino.get_copy()
            copy.move_left()
            if not self.__is_colliding_wall_( copy ):
                self.active_tetramino.move_left()
                self.update()
        elif key == Qt.Key_Right:
            copy = self.active_tetramino.get_copy()
            copy.move_right()
            if not self.__is_colliding_wall_( copy ):
                self.active_tetramino.move_right()
                self.update()
        elif key == Qt.Key_Space:
            while not self.__is_touching_ground_( self.active_tetramino ):                
                self.active_tetramino.step_down()
                self.update()
        elif key == Qt.Key_N:
            self.start_new_game()
        elif key == Qt.Key_P:
            if not self.timer.isActive():
                self.timer.start(2000.0 / self.level , self )
            else:
                self.timer.stop()
            self.update()


    def paintEvent(self, event):
        painter = QPainter( self )
        self.well.draw( painter )
        if not self.is_game_over:
            self.active_tetramino.draw( painter )
        self.next_tetramino.draw( painter )
        self.__draw_game_info_( painter )


    def __draw_game_info_( self, painter ):
        font = QFont ( "Tahoma" )
        font.setPointSize( 14 )
        painter.setFont( font )
        painter.setPen(QColor(0,0,255))
        painter.drawText(310, 20, "Next piece:")
        painter.setPen(QColor(0,127,0))
        painter.drawText(310, 180, "Score:" + str(self.score))
        painter.setPen(QColor(0,148,255))
        painter.drawText(310, 230, "Lines:" + str(self.num_of_removed_lines))
        status = "Status: "
        if self.is_game_over:
            painter.setPen(QColor(255,0,0))
            status += "GAME OVER"
        else:
            if self.timer.isActive():
                painter.setPen(QColor(0,127,0))
                status += "PLAYING"
            else:
                painter.setPen(QColor(255,255,0))
                status += "PAUSED"
        painter.drawText(310, 290, status )
        pass
                

class Well():
    def __init__( self, width, height, tile_size):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.grid = []
        self.clear_grid()

    def clear_grid( self ):
        self.grid = []
        for y in range( self.height ):
            row = []
            for x in range( self.width ):
                row.append(False)                
            self.grid.append( row )

        for x in range( self.width ):
            self.grid[ self.height - 1 ][ x ] = True
            
        
    def __is_coords_valid_( self, x, y ):
        return x >= 0 and x < self.width and y >= 0 and y < self.height


    def is_tile_solid( self, x, y):
        return self.grid[y][x] if self.__is_coords_valid_( x, y ) else False


    def set_tile( self, x, y, is_solid = True):
        if self.__is_coords_valid_( x, y ):
            self.grid[y][x] = is_solid


    def __is_line_filled_( self, y ):
        for x in range( WELL_X ):
            if not self.grid[ y ][ x ]:
                return False
        return True
    
        
    def remove_filled_lines( self ):
        num_of_removed_lines = 0
        for yy in range( WELL_Y ):
            if self.__is_line_filled_( yy ):
                num_of_removed_lines += 1
                for y in range( yy, 0, -1 ):
                    for x in range ( WELL_X ):
                        self.grid[ y ][ x ] = self.grid[ y - 1 ][ x ]
                for x in range ( WELL_X ):
                    self.grid[ 0 ][ x ] = False
            else:
                continue
        return num_of_removed_lines                    
        

    def draw( self, painter ):
        for y in range( self.height - 1):
            for x in range( self.width ):
                color = QColor(160,160,160) if self.grid[y][x] else QColor(0,0,0)
                painter.fillRect(x * self.tile_size + 1, y * self.tile_size + 1,
                                 self.tile_size - 1, self.tile_size - 1, color)    


class Block():

    def __init__( self, x, y, color ):
        self.__x = x
        self.__y = y
        self.__color = color


    def set_pos( self, x, y ):
        self.__x = x
        self.__y =  y


    def get_x( self ):
        return self.__x


    def get_y( self ):
        return self.__y


    def draw( self, painter ):        
        painter.fillRect(self.__x * TILE_SIZE + 1, self.__y * TILE_SIZE + 1,
                         TILE_SIZE - 1, TILE_SIZE - 1, self.__color)

    
class Tetramino():
    
    def __init__( self, x, y, shape_index, angle = 0 ):
        self.__x = x
        self.__y = y        
        self.__angle = angle
        self.__shape_index = shape_index
        self.__shape = Shape.table[ shape_index ][ 0 ][ self.__angle ]
        self.__color = QColor(Shape.table[ shape_index ][ 1 ] )
        self.__blocks = []
       
        for y in range( len( self.__shape ) ):
            for x in range( len( self.__shape[y] ) ):
                if self.__shape[y][x] == 'X':
                    block = Block( self.__x + x, self.__y + y, self.__color )
                    self.__blocks.append( block )


    def get_blocks( self ):
        return self.__blocks

    
    def get_copy( self ):
        copy = Tetramino( self.__x, self.__y, self.__shape_index, self.__angle )
        return copy
    

    def set_pos( self, x, y ):
        self.__x = x
        self.__y = y
        self.__update_blocks_()

        
    def step_down( self ):
        self.__y += 1
        for block in self.__blocks:
            block.set_pos(block.get_x(), block.get_y() + 1)

        
    def move_left( self ):
        self.__x -= 1
        for block in self.__blocks:
            block.set_pos(block.get_x() - 1, block.get_y())


    def move_right( self ):
        self.__x += 1
        for block in self.__blocks:
            block.set_pos(block.get_x() + 1, block.get_y())
            

    def rotate_left( self ):
        if self.__shape_index == 4:
            return
        self.__angle -= 1
        if self.__angle < 0:
            self.__angle = NUM_BLOCKS_IN_PIECE - 1
        self.__update_blocks_()
        

    def rotate_right( self ):
        if self.__shape_index == 4:
            return
        self.__angle += 1
        self.__angle %= NUM_BLOCKS_IN_PIECE
        self.__update_blocks_()


    def draw( self, painter ):
        for block in self.__blocks:
            block.draw( painter )


    def __update_blocks_( self ):
        counter = 0
        self.__shape = Shape.table[ self.__shape_index ][ 0 ][ self.__angle ]
        for y in range( len( self.__shape ) ):
            for x in range( len( self.__shape[y] ) ):
                if self.__shape[y][x] == 'X':
                    self.__blocks[counter].set_pos( self.__x + x, self.__y + y )
                    counter += 1 


class Shape:
    table = (
                #Z-shape
                (
                    (
                        ("XX ",
                         " XX",
                         "   "),
                        ("  X",
                         " XX",
                         " X "),
                        ("   ",
                         "XX ",
                         " XX"),
                        (" X ",
                         "XX ",
                         "X  ")
                    ),
                    0xCC6666
                ),
                #S-shape
                (
                    (
                        (" XX",
                         "XX ",
                         "   "),
                        (" X ",
                         " XX",
                         "  X"),
                        ("   ",
                         " XX",
                         "XX "),
                        ("X  ",
                         "XX ",
                         " X ")
                    ),
                    0x66CC66
                ),
                #I-shape
                (
                    (
                        ("    ",
                         "XXXX",
                         "    ",
                         "    "),
                        (" X  ",
                         " X  ",
                         " X  ",
                         " X  "),
                        ("    ",
                         "XXXX",
                         "    ",
                         "    "),
                        (" X  ",
                         " X  ",
                         " X  ",
                         " X  "),
                    ),
                    0x6666CC
                ),
                #T-shape
                (
                    (
                        ("XXX",
                         " X ",
                         "   "),
                        ("  X",
                         " XX",
                         "  X"),
                        ("   ",
                         " X ",
                         "XXX"),
                        ("X  ",
                         "XX ",
                         "X  ")
                    ),
                    0xCCCC66
                ),
                #O-shape
                (
                    (
                        ("XX",
                         "XX"),
                    ),
                    0xCC66CC
                ),
                #L-shape
                (
                    (
                        (" X ",
                         " X ",
                         " XX"),
                        ("   ",
                         "XXX",
                         "X  "),
                        ("XX ",
                         " X ",
                         " X "),
                        ("  X",
                         "XXX",
                         "   ")
                    ),
                    0x66CCCC
                 ),
                #J-shape
                (
                    (
                        (" X ",
                         " X ",
                         "XX "),
                        ("X  ",
                         "XXX",
                         "   "),
                        (" XX",
                         " X ",
                         " X "),
                        ("   ",
                         "XXX",
                         "  X")
                    ),
                    0xDAAA00
                )
            )


if __name__ == '__main__':
    app = QApplication([])
    window = Window()
    sys.exit(app.exec_())   
