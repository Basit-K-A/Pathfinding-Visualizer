"""
------------------------------------------------------------------------
Algorithm Visualizer in a 2D Grid
------------------------------------------------------------------------
Author: Basit Khan
Email:  khan8019@mylaurier.ca
__updated__ = "2/13/2025"
------------------------------------------------------------------------
"""

import sys
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QGridLayout
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import Qt,QTimer
import heapq

GRIDSIZE = 25
grid = []
start_square = None
end_square = None

def valid_node(node):
    if node.ind < 0 or node.ind >= GRIDSIZE * GRIDSIZE:
        return False
    return True

def up(node):
    return grid[node.ind - GRIDSIZE] if node.ind - GRIDSIZE >= 0 else None

def down(node):
    return grid[node.ind + GRIDSIZE] if node.ind + GRIDSIZE < GRIDSIZE * GRIDSIZE else None

def left(node):
    return grid[node.ind - 1] if node.ind % GRIDSIZE != 0 else None

def right(node):
    return grid[node.ind + 1] if (node.ind + 1) % GRIDSIZE != 0 else None

class Square(QGraphicsRectItem):
    def __init__(self, x, y, ind):
        super().__init__(0, 0, 24, 24)
        self.setPos(x, y)
        self.setBrush(Qt.white)
        self.ind = ind
        self.is_start = False
        self.is_end = False
        self.is_wall = False
        self.distance = float('inf')  # For Dijkstra
        self.previous = None  # To reconstruct path

    def __lt__(self, other):
        return self.distance < other.distance


    def mousePressEvent(self, event):
        global start_square, end_square

        if self.is_start:
            self.setBrush(Qt.white)
            self.is_start = False
            start_square = None
            return

        # If clicking on the end square, deselect it
        if self.is_end:
            self.setBrush(Qt.white)
            self.is_end = False
            end_square = None
            return

        # If no start exists, set this as start
        if not start_square:
            self.setBrush(Qt.green)
            self.is_start = True
            start_square = self
            return

        # If no end exists and this isn't the start, set as end
        if not end_square and self != start_square:
            self.setBrush(Qt.red)
            self.is_end = True
            end_square = self
            return

class PathfindingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        global scene, grid, start_square, end_square
        self.setWindowTitle("Pathfinding Visualizer")

        main_layout = QVBoxLayout()
        title = QLabel("Pathfinding Visualizer")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)

        instructions = QLabel("Select a start and end square, then click 'Run Dijkstra' to visualize the algorithm.")
        instructions.setStyleSheet("font-size: 14px;")
        main_layout.addWidget(instructions)

        layout = QGridLayout()

        scene = QGraphicsScene(0, 0, 600, 600)
        count = 0
        for i in range(GRIDSIZE):
            for j in range(GRIDSIZE):
                square = Square(j * GRIDSIZE, i * GRIDSIZE, count)
                scene.addItem(square)
                grid.append(square)
                count += 1

        self.grid = grid  # Store in class for later use
        self.view = QGraphicsView(scene)
        layout.addWidget(self.view, 0, 0, 1, 2)

        # Add Start Button
        self.start_button = QPushButton("Run Dijkstra")
        self.start_button.clicked.connect(self.runDijkstra)
        layout.addWidget(self.start_button, 1, 0)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear)
        layout.addWidget(self.clear_button, 1, 1)

        main_layout.addLayout(layout)
        self.setLayout(main_layout)

        # Apply stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color:rgb(188, 206, 167);
            }
            QPushButton {
                font-size: 12px;
                padding: 10px;
            }
            QGraphicsView {
                border: 1px solid #ccc;
            }
        """)

    def runDijkstra(self):
        if not start_square or not end_square:
            print("please select a start and end square")
            return

        start_square.distance = 0
        self.priority_queue = [(0, start_square)]
        self.timer = QTimer()
        self.timer.timeout.connect(self.stepDijkstra)
        self.timer.start(10)

    def stepDijkstra(self):
        if not self.priority_queue:
            self.timer.stop()
            self.reconstructPath()
            return

        current_distance, current_node = heapq.heappop(self.priority_queue)

        if current_node == end_square:
            self.timer.stop()
            self.reconstructPath()
            return

        if current_distance > current_node.distance:
            return

        directions = [up, down, left, right]
        for direction in directions:
            neighbor = direction(current_node)
            if neighbor and valid_node(neighbor):
                distance = current_distance + 1  # Assuming uniform cost for each move
                if distance < neighbor.distance:
                    neighbor.distance = distance
                    neighbor.previous = current_node
                    heapq.heappush(self.priority_queue, (distance, neighbor))
                    if neighbor is not end_square: neighbor.setBrush(Qt.blue)

    def reconstructPath(self):
        node = end_square
        while node.previous:
            node.setBrush(Qt.yellow)
            node = node.previous
        start_square.setBrush(Qt.green)
        end_square.setBrush(Qt.red)

    def clear(self):
        global start_square, end_square
        start_square = None
        end_square = None
        for i in range(GRIDSIZE):
            for j in range(GRIDSIZE):
                grid[i * GRIDSIZE + j].setBrush(Qt.white)
                grid[i * GRIDSIZE + j].is_start = False
                grid[i * GRIDSIZE + j].is_end = False
                grid[i * GRIDSIZE + j].is_wall = False
                grid[i * GRIDSIZE + j].distance = float('inf')
                grid[i * GRIDSIZE + j].previous = None
                

# Main execution
app = QApplication(sys.argv)
window = PathfindingApp()
window.show()
sys.exit(app.exec_())