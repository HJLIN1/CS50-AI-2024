from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")
#Rules:
#(v) In each of the above puzzles, each character is either a knight or a knave. 
#Every sentence spoken by a knight is true, and every sentence spoken by a knave is false.
#等同於 knight>True or knave>False，但應如何表示為邏輯公式呢？(需對照fact決定true or false，刪除例外(自稱knave))
# 老師建議: 可設計兩個函數，分別處理該句話在knight/knave的情況，如果與KB交集符合，則回傳True

# Puzzle 0(我判斷: AKnave)
# A says "I am both a knight and a knave."
#TODO

knowledge0 = And(
    Or(AKnight, AKnave), # A is either a knight or a knave
    Not(And(AKnight, AKnave)), # A cannot be both a knight and a knave
    #不知道這樣算不算"most direct translation"  If A is a knight, then A is both a knight and a knave
    Implication(AKnight, And(AKnight, AKnave)), 
    # If A is a knave, then A is not both a knight and a knave
    Implication(AKnave, Not(And(AKnight, AKnave))) 
    # Biconditional(AKnight, And(AKnight, AKnave)) #用雙箭頭好像也可以，但不知道這樣是否加入了人的邏輯思考
)    

# Puzzle 1  (我判斷: AKnave, BKnight)
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Or(AKnight, AKnave), # A is either a knight or a knave
    Not(And(AKnight, AKnave)), # A cannot be both a knight and a knave
    Or(BKnight, BKnave), # B is either a knight or a knave
    Not(And(BKnight, BKnave)), # B cannot be both a knight and a knave
    Implication(AKnight, And(AKnave, BKnave)), # If A is a knight, then A and B are both knaves
    Implication(AKnave, Not(And(AKnave, BKnave)))
    # TODO
)

# Puzzle 2 (我判斷: AKnave, BKnight)
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Or(AKnight, AKnave), # A is either a knight or a knave
    Not(And(AKnight, AKnave)), # A cannot be both a knight and a knave
    Or(BKnight, BKnave), # B is either a knight or a knave
    Not(And(BKnight, BKnave)), # B cannot be both a knight and a knave
    # If A is a knight, then A and B are the same kind
    Implication(AKnight, And(AKnight, BKnight)), 
    # If A is a knave, then A and B are not the same kind
    Implication(AKnave, Not(And(AKnave, BKnave))), 
    Implication(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight))),
    Implication(BKnave, Not(Or(And(AKnight, BKnave), And(AKnave, BKnight))))
    # TODO
)

# Puzzle 3 (我判斷: AKnight, BKnave, CKnight) 好好玩ㄎㄎ
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(AKnight, AKnave), # A is either a knight or a knave
    Not(And(AKnight, AKnave)), # A cannot be both a knight and a knave
    Or(BKnight, BKnave), # B is either a knight or a knave
    Not(And(BKnight, BKnave)), # B cannot be both a knight and a knave
    Or(CKnight, CKnave), # C is either a knight or a knave
    Not(And(CKnight, CKnave)), # C cannot be both a knight and a knave
    # A says either "I am a knight." or "I am a knave.", but you don't know which. If A is a knave, then
    Implication(AKnight, Or(AKnight, AKnave)), 
    Implication(AKnave, Not(Or(AKnight, AKnave))), 
    # B says "A said 'I am a knave'."  
    Implication(BKnight, Or(And(AKnight, AKnave), And(AKnave, Not(AKnave)))), 
    Implication(BKnave, Not(Or(And(AKnight, AKnave), And(AKnave, Not(AKnave))))), 
    Implication(BKnight, CKnave), # B says "C is a knave."
    Implication(BKnave, Not(CKnave)),
    Implication(CKnight, AKnight), # C says "A is a knight."
    Implication(CKnave, Not(AKnight))
    # TODO
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
