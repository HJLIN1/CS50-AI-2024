import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])  #corpus是一個dictionary，key是頁面名稱，value是一個set，裡面是這個頁面連結到的頁面
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES) #sample_pagerank是一個重要函數，利用sampling的方式計算pagerank
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks): #將ranks裡的頁面按照名稱排序? 注意sorted()函數的用法: sorted(iterable, key, reverse)表示對iterable進行排序，key是排序的依據，reverse是排序的方向
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING) # 利用迭代的方式、以經驗函數?計算pagerank，直到收斂
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory): # 將directory裡的html檔案讀取，並找出每個頁面連結到的頁面
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    transition_probabilities = {}

    # If the current page has outgoing links
    if corpus[page]:
        for linked_page in corpus:
            # Probability of choosing a linked page
            linked_probability = (1 - damping_factor) / len(corpus)
            # If the linked page is in the outgoing links of the current page
            if linked_page in corpus[page]:
                linked_probability += damping_factor / len(corpus[page])
            transition_probabilities[linked_page] = linked_probability
    # If the current page has no outgoing links
    else:
        for linked_page in corpus:
            # Probability of choosing any page
            transition_probabilities[linked_page] = 1 / len(corpus)

    return transition_probabilities
    # raise NotImplementedError


def sample_pagerank(corpus, damping_factor, n): #重要函數，利用sampling的方式計算pagerank
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank = {page: 0 for page in corpus}
    # Start with a random page
    current_page = random.choice(list(corpus.keys()))   

    for _ in range(n):
        # Update the pagerank of the current page
        pagerank[current_page] += 1 / n
        # Get the transition model for the current page
        transition_model_probabilities = transition_model(corpus, current_page, damping_factor)
        # Choose the next page based on the transition model
        current_page = random.choices(list(transition_model_probabilities.keys()), weights=transition_model_probabilities.values(), k=1)[0]
    return pagerank
    # raise NotImplementedError

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    pagerank = {page: 1 / N for page in corpus}
    convergence_threshold = 0.001

    while True:
        new_pagerank = {}
        # Calculate new rank values based on the PageRank formula
        # 依序計算每個頁面的新rank值，動態更新pagerank直到收斂
        for page in corpus: 
            # 第一種情況: 在一定的機率下，需利用隨機挑選進入下個頁面，避免遇到繞不出去的情況
            new_rank = (1 - damping_factor) / N
            # 第二種情況: 大部分狀況下，計算此網頁被其他網頁連結的多寡來決定rank值
            # A page that has no links at all should be interpreted as having one link for every page in the corpus (including itself).
            for linking_page, links in corpus.items():
                if page in links:
                    new_rank += damping_factor * pagerank[linking_page] / len(links)
                if not links:
                    new_rank += damping_factor * pagerank[linking_page] / N
            new_pagerank[page] = new_rank
        # iterate_pagerank returns correct results for corpus with pages without links

        # Check for convergence 
        # check if the difference between the new rank values and the old rank values is less than the convergence threshold
        max_diff = max(abs(new_pagerank[page] - pagerank[page]) for page in corpus)
        if max_diff < convergence_threshold:
            break
        pagerank = new_pagerank
    return pagerank



    raise NotImplementedError


if __name__ == "__main__":
    main()
