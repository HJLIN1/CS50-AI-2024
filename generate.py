import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword): 
        """
        Create new CSP crossword generate.
        """
        # 初始設定，將crossword和domain設定好；domain是字典結構(key是變數，value是變數的候選字詞)
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):  # 依照變數的方向，將變數的字詞填入letters(初始時為None)
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        # 把目前的assignment印出來，若是空格則印出"█"
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        # 解決crossword問題的主要函數，先檢查node consistency，再檢查arc consistency，最後使用backtrack解決
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # 確保變數符合unary constraints(變數與填入字的長度相符)，先將不符合長度的字詞從domain中移除
        # Iterate over all variables in the crossword, and remove any words from the domain that do not have the same length as the variable.
        for var in self.crossword.variables:
            for word in self.crossword.words:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # 此函數確保單一變數x與變數y的domain是arc consistent(變數x的domain中的字詞與變數y的domain中的字詞在重疊處有相同字元)
        # 會被應用在AC3函數中，用來檢查變數之間的相容性
        revised = False
        # Find the overlap between the variables x and y
        overlap = self.crossword.overlaps[x, y]
        # If there is no overlap, return False(若兩變數無重疊處，則互不影響)
        if overlap is None:
            return False
        # Iterate over all words in the domain of variable x(其餘有重疊處的變數x的所有字詞)
        # 如果變數y的domain中沒有任何一個字詞有相同的字元在重疊處，則從變數x的domain中移除該字詞
        # 若變數x的domain中每個字詞都有y的候選字詞，則不做更動，revised維持初始值False
        for word_x in self.domains[x].copy():
            # If there is no word in the domain of variable y that has the same character at the overlap, remove the word from the domain of variable x
            # any(): 當有一個元素是True時，就會回傳True
            if not any(word_x[overlap[0]] == word_y[overlap[1]] for word_y in self.domains[y]):
                self.domains[x].remove(word_x)
                revised = True
        return revised

    def ac3(self, arcs=None):  # 此函數是用來檢查變數之間的相容性，
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Initialize the queue of arcs
        if arcs is None:
            arcs = [(x, y) for x in self.crossword.variables for y in self.crossword.neighbors(x)]
        # While the queue of arcs is not empty
        while arcs:
            # Pop the first arc from the queue (移除並回傳列表中的第一個元素)
            x, y = arcs.pop(0)
            # If the variable x is revised, add all neighbors of x to the queue of arcs
            if self.revise(x, y):
                # If the domain of variable x is empty, return False
                if not self.domains[x]:
                    return False
                # Add all neighbors of x to the queue of arcs except for y
                # since X’s domain was changed, we need to see if all the arcs associated with X are still consistent.
                # 不需要再檢查(y, x)，因為已經檢查過revise(x, y)
                for z in self.crossword.neighbors(x) - {y}:
                    arcs.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Check if the assignment is complete(檢查assignment是否完成)
        # 檢查assignment中的變數是否與crossword中的所有變數相同
        return set(assignment.keys()) == set(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """           
        # 需檢查3個條件確認此變數的賦值是否符合條件:
        # Check if all values are distinct
        if len(set(assignment.values())) != len(assignment):
            return False
        # Check if all values are the correct length(檢查所有的值是否為正確的長度)
        # Check if there are no conflicts between neighboring variables
        for x, word_x in assignment.items():
            if x.length != len(word_x):
                return False
            for y in self.crossword.neighbors(x):
                if y in assignment:
                    overlap = self.crossword.overlaps[x, y]
                    if word_x[overlap[0]] != assignment[y][overlap[1]]:
                        return False
        return True        

    def order_domain_values(self, var, assignment):  # 這個函數是用來選擇一個變數的領域值，以便在搜索過程中優先選擇最有希望的值(限縮其他變數最少的值)；hard!
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        counts = []  # list of tuples (value, count)

        for value in self.domains[var]:
            count = 0
            # 程式碼邏輯: 若var的Domain中的value與neighbor的Domain中的v在重疊處的字母不相同，則count += 1
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    var_index, neighbor_index = self.crossword.overlaps[var, neighbor]
                    count += sum(1 for v in self.domains[neighbor] if v[neighbor_index] != value[var_index])
            counts.append((value, count))
        # sort by count, extract values，此處是將counts中的值按照count的大小排序(lambda x: x[1]表示按照counts中的第二個元素(即count)排序)，並將value取出
        return [value for value, count in sorted(counts, key=lambda x: x[1])]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # 目的是選擇一個未分配的變數，該變數在其域中具有最少的剩餘值，如果有平手，則選擇具有做多變數連接的變數
        # Initialize the list of unassigned variables
        unassigned = [var for var in self.crossword.variables if var not in assignment]
        # Sort the list of unassigned variables by the number of remaining values in their domain
        # If there is a tie, sort by the number of neighbors
        return min(unassigned, key=lambda var: (len(self.domains[var]), -len(self.crossword.neighbors(var))))
        # 想法: min 函數會選出使這個函數返回的元組最小的變數。 匿名函數（也稱為 lambda 函數）接受一個變數var並返回tuple
        # 元組的比較是按照字典序進行的，所以首先會比較第一個元素(Domain剩餘值的數量)
        # 如果有平手的情況，則會比較第二個元素(鄰居數量的相反數)

        # # 法二
        # unassigned = [var for var in self.crossword.variables if var not in assignment]
        # unassigned.sort(key=lambda var: len(self.domains[var]))
        # min_domain_size = len(self.domains[unassigned[0]])
        # candidates = [var for var in unassigned if len(self.domains[var]) == min_domain_size]
        # candidates.sort(key=lambda var: len(self.crossword.neighbors(var)), reverse=True)
        # return candidates[0]
    

    def backtrack(self, assignment):  #目前只使用較簡單的backtrack，並未結合
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If the assignment is complete, return the assignment
        if self.assignment_complete(assignment):
            return assignment
        # Select an unassigned variable
        var = self.select_unassigned_variable(assignment)
        # Iterate over all values in the domain of the variable
        for value in self.order_domain_values(var, assignment):
            # Add the variable and value to the assignment
            assignment[var] = value
            # If the assignment is consistent, recursively call backtrack；以遞迴方式調用backtrack
            if self.consistent(assignment):
                result = self.backtrack(assignment)  #如果一直順利就會繼續下去，每次呼叫的函數做到這裡就又重新呼叫自己，直到所有變數都被分配到值(成功!)
                if result is not None:
                    return result
            # Remove the variable and value from the assignment
            del assignment[var]  # 若在遞迴賦值的過程中遇到不符合條件的狀況，則移除此變數和值
        return None  #若遇到某格變數的domain為空，則返回None(無解)
        

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    #紀錄解題時間
    import time
    start = time.time()
    assignment = creator.solve()
    end = time.time()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        print("Time:", end - start)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
