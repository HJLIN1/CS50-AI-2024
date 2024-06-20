import nltk
nltk.download('punkt')
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

# S表示句子，NP表示名词短语，VP表示动词短语，PP表示介词短语，AdjP表示形容词短语，AdvP表示副词短语，DetP表示限定词短语。
NONTERMINALS = """
S -> NP VP | S Conj S | S P S | S Adv | S AdvP | S PP
NP -> N | Det NP | Adj NP | NP PP | NP AdvP | NP Conj NP
VP -> V | V NP | V NP PP | V PP | VP AdvP | VP Conj VP
PP -> P NP | P NP PP | P DetP
AdjP -> Adj | Adj AdjP
AdvP -> Adv | Adv AdvP
DetP -> Det | Det DetP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    #使用nltk.word_tokenize()函数将句子分割成单词，而不是简单地使用.split()方法，因为nltk.word_tokenize()函数可以处理标点符号。
    # 并且只保留至少包含一个字母的单词，将其换为小写。
    words = nltk.word_tokenize(sentence)
    words = [word.lower() for word in words if any(char.isalpha() for char in word)]
    return words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    #遍历树中的所有子树，找到标签为NP的子树，然后检查该子树是否包含其他NP子树，如果不包含，则将其添加到列表中。
    np_chunks = []
    for subtree in tree.subtrees():
        if subtree.label() == "NP" and not list(subtree.subtrees(lambda t: t.label() == "NP" and t != subtree)):
            np_chunks.append(subtree)
    return np_chunks


if __name__ == "__main__":
    main()
