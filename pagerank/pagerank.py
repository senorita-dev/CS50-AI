import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    # ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    # print(f"PageRank Results from Sampling (n = {SAMPLES})")
    # for page in sorted(ranks):
    #     print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
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
        pages[filename] = set(link for link in pages[filename] if link in pages)

    return pages


def transition_model(corpus: dict[str, set[str]], page: str, damping_factor: float):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    linked_pages = corpus[page]
    if len(linked_pages) == 0:
        return dict.fromkeys(corpus.keys(), 1 / len(corpus))
    # with probability `1 - damping_factor`, choose a link at random chosen from all pages in the corpus.
    probability_distribution = dict.fromkeys(
        corpus.keys(), (1 - damping_factor) / len(corpus)
    )
    # with probability `damping_factor`, choose a link at random linked to by `page`.
    for linked_page in linked_pages:
        probability_distribution[linked_page] = damping_factor / len(linked_pages)
        pass
    return probability_distribution


def sample_pagerank(corpus: dict[str, set[str]], damping_factor: float, n: int):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    probability_distribution = dict.fromkeys(corpus.keys(), 0)
    sample_page = random.choice(list(corpus.keys()))
    probability_distribution[sample_page] += 1 / n
    for _ in range(n - 1):
        transition_distribution = transition_model(corpus, sample_page, damping_factor)
        choices = list(transition_distribution.keys())
        weights = list(transition_distribution.values())
        sample_page = random.choices(choices, weights)[0]
        probability_distribution[sample_page] += 1 / n
        pass
    return probability_distribution


def iterate_pagerank(corpus: dict[str, set[str]], damping_factor: float):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # A page that has no links at all should be interpreted as having one link for every page in the corpus (including itself).
    for page, linked_pages in corpus.items():
        if len(linked_pages) == 0:
            corpus[page] = set(corpus.keys())
    reverse_corpus: dict[str, set[str]] = {page: set() for page in corpus}
    for page, linked_pages in corpus.items():
        for linked_page in linked_pages:
            reverse_corpus[linked_page].add(page)
        pass
    max_difference = 1
    new_dist = dict.fromkeys(corpus.keys(), 1 / len(corpus))
    while max_difference > 0.001:
        max_difference = 0
        current_dist = new_dist
        new_dist = dict.fromkeys(corpus.keys(), 0)
        for page in corpus:
            linking_pages = reverse_corpus[page]
            # 2) With probability d, the surfer followed a link from a page i to page p.
            for linking_page in linking_pages:
                new_dist[page] += current_dist[linking_page] / len(corpus[linking_page])
            new_dist[page] *= damping_factor
            # 1) With probability 1 - d, the surfer chose a page at random and ended up on page p.
            new_dist[page] += (1 - damping_factor) / len(corpus)
            max_difference = max(
                max_difference, abs(new_dist[page] - current_dist[page])
            )
            pass
        pass
    return new_dist


if __name__ == "__main__":
    main()
