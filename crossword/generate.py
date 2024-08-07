import sys

from crossword import *


class CrosswordCreator:

    def __init__(self, crossword: Crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
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
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
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
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable, domain in self.domains.items():
            self.domains[variable] = set(
                word for word in domain if len(word) == variable.length
            )
        pass

    def revise(self, x: Variable, y: Variable):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False
        (i, j) = overlap
        revised = False
        for word_x in list(self.domains[x]):
            if any(word_x[i] == word_y[j] for word_y in self.domains[y]):
                continue
            self.domains[x].remove(word_x)
            revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = arcs
        if arcs is None:
            queue = set()
            for var in self.domains:
                for neighbour in self.crossword.neighbors(var):
                    queue.add((var, neighbour))
            queue = list(queue)
            pass
        while len(queue) > 0:
            (x, y) = queue.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))
            pass
        return True

    def assignment_complete(self, assignment: dict[Variable, str]):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.domains:
            if variable in assignment:
                continue
            return False
        return True

    def consistent(self, assignment: dict[Variable, str]):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        assigned_words: set[str] = set()
        for variable, assigned_word in assignment.items():
            if assigned_word in assigned_words:
                return False
            if len(assigned_word) != variable.length:
                return False
            for neighbour in self.crossword.neighbors(variable):
                if neighbour not in assignment:
                    continue
                overlap = self.crossword.overlaps[variable, neighbour]
                if overlap is None:
                    continue
                (i, j) = overlap
                neighbour_assigned_word = assignment[neighbour]
                if assigned_word[i] == neighbour_assigned_word[j]:
                    continue
                return False
            assigned_words.add(assigned_word)
            pass
        return True

    def order_domain_values(self, var: Variable, assignment: dict[Variable, str]):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        heuristics: list[tuple[str, int]] = []
        for word in self.domains[var]:
            heuristic = 0
            for neighbour in self.crossword.neighbors(var):
                if neighbour in assignment:
                    continue
                overlap = self.crossword.overlaps[var, neighbour]
                if overlap is None:
                    continue
                (i, j) = overlap
                heuristic += sum(
                    word[i] == word_neighbour[j]
                    for word_neighbour in self.domains[neighbour]
                )
            heuristics.append((word, heuristic))
            pass
        heuristics.sort(key=lambda heuristic: heuristic[1], reverse=True)
        domain_values = [heuristic[0] for heuristic in heuristics]
        return domain_values

    def select_unassigned_variable(self, assignment: dict[Variable, str]):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        domain_size_var_map: dict[int, Variable] = dict()
        for var in self.domains:
            if var in assignment:
                continue
            domain_size = len(self.domains[var])
            if domain_size not in domain_size_var_map:
                domain_size_var_map[domain_size] = []
            domain_size_var_map[domain_size].append(var)
            pass
        min_domain_size = min(domain_size_var_map)
        remaining = domain_size_var_map[min_domain_size]
        if len(remaining) == 1:
            return remaining[0]
        remaining = [[var, len(self.crossword.neighbors(var))] for var in remaining]
        remaining.sort(key=lambda var: var[1])
        return remaining[0][0]

    def backtrack(self, assignment: dict[Variable, str]):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        variable = self.select_unassigned_variable(assignment)
        for word in self.domains[variable]:
            new_assignment = dict(assignment)
            new_assignment[variable] = word
            if not self.consistent(new_assignment):
                continue
            result = self.backtrack(new_assignment)
            if result is None:
                continue
            return result
        return None


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
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
