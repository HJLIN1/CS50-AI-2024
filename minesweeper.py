import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines

class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells   
        # returns no mines when no conclusion possible
        return set()     
        # raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        # returns no safes when no conclusion possible
        return set()
        # raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # If cell is in the sentence, the function should update the sentence so that cell is no longer in the sentence, 
        # but still represents a logically correct sentence given that cell is known to be a mine.
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1        
        # 不用把這個cell的狀態變成true嗎(還是已經在另一個function做了)?
        # raise NotImplementedError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        # raise NotImplementedError


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
            Note that any time that you make any change to your AI's knowledge, 
            it may be possible to draw new inferences that weren't possible before. 
            Be sure that those new inferences are added to the knowledge base if it is possible to do so.
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe
        self.mark_safe(cell)    

        # 3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        # ignores known mines when adding new sentence
        # ignores known safes when adding new sentence
        neighbors = set()
        mine_count = count
        for i in range(max(0, cell[0]-1), min(self.height, cell[0]+2)):
            for j in range(max(0, cell[1]-1), min(self.width, cell[1]+2)):
                if (i, j) != cell:
                    if (i, j) in self.mines:
                        mine_count -= 1
                    elif (i, j) not in self.safes:  #將剩下未知狀態的cell加入neighbors
                        neighbors.add((i, j))
        new_sentence = Sentence(neighbors, mine_count)
        self.knowledge.append(new_sentence)
        

        while True:
            # 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
            #未做到的缺失: infer mine when given new information、infer multiple mines when given new information、
            # infer safe cells when given new information
            # 感覺可以把這個步驟移到最後，或是放在(5)迴圈中，因為這個步驟是根據新的knowledge_base來推論的

            # Iterate over all sentences in the knowledge base
            for sentence in self.knowledge:
                # If the sentence is known to be true, mark all cells in the sentence as safe
                if sentence.count == 0:
                    for cell in list(sentence.cells):  # Create a copy of sentence.cells for iteration
                        self.mark_safe(cell)
                # If the sentence is known to be false, mark all cells in the sentence as mines
                elif len(sentence.cells) == sentence.count:
                    for cell in list(sentence.cells):  # Create a copy of sentence.cells for iteration
                        self.mark_mine(cell)

            # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
            # 未做到的缺失 combines multiple sentences to draw conclusions ??(感覺有阿QQ)
            # 當存在一個sentence是另一個sentence的subset時，可以推論出新的sentence，以此建構while迴圈
            # Iterate over all pairs of sentences in the knowledge base
            new_sentences = []  # Create a new list to store new sentences
            for sentence1, sentence2 in itertools.combinations(self.knowledge, 2):
                # If one sentence is a subset of the other, create a new sentence with the difference of cells and counts
                if sentence1.cells.issubset(sentence2.cells):
                    new_cells = sentence2.cells - sentence1.cells
                    new_count = sentence2.count - sentence1.count
                    new_sentence = Sentence(new_cells, new_count)
                    # If the new sentence is not already in the knowledge base, add it
                    if new_sentence not in self.knowledge:
                        new_sentences.append(new_sentence)
                elif sentence2.cells.issubset(sentence1.cells):
                    new_cells = sentence1.cells - sentence2.cells
                    new_count = sentence1.count - sentence2.count
                    new_sentence = Sentence(new_cells, new_count)
                    # If the new sentence is not already in the knowledge base, add it
                    if new_sentence not in self.knowledge:
                        new_sentences.append(new_sentence)

            # Add new sentences to the knowledge base after the iteration
            self.knowledge.extend(new_sentences)
            
            #我的想法: 當不存在某個sentence是另一個sentence的subset時，迴圈結束
            # 或是當new_sentences為空時，迴圈結束(因為沒有新的sentence需要判斷是否有subset的關係))
            if not new_sentences:
                break


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        # If there are no safe moves, the function should return None
        return None 
        # raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
            3) If no such moves are possible, the function should return None.
        """
        possible_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                if cell not in self.moves_made and cell not in self.mines:
                    possible_moves.add(cell)
        if possible_moves:
            return random.choice(list(possible_moves))
        return None        
        # raise NotImplementedError
        #原本未考慮None的情況，所以會出現錯誤
                # Generate a random move
        # while True:
        #     i = random.randrange(self.height)
        #     j = random.randrange(self.width)
        #     move = (i, j)
        #     if move not in self.moves_made and move not in self.mines:
        #         return move
