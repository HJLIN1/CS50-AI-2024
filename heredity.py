import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person 
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):    #列出one_gene 所有可能的组合
            for two_genes in powerset(names - one_gene):  #列出two_genes 所有可能的组合，但須排除已經在one_gene的人

                # Update probabilities with new joint probability(依續計算出各種組合的機率，並更新至probabilities)
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV. *要馬都有 要馬都沒有
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    # 意思是返回一个集合，集合中的元素是s中的元素，集合中的元素个数是s中元素的个数加1
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)  # 从s中取r个元素
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probability = 1

    for person, data in people.items():
        # Determine the number of copies of the gene for the current person
        if person in one_gene:
            num_genes = 1
        elif person in two_genes:
            num_genes = 2
        else:
            num_genes = 0

        # Determine if the person has the trait
        has_trait = person in have_trait

        # Calculate probability based on gene distribution and trait distribution
        if data['mother'] is None and data['father'] is None:
            # No parental information available (無父母資訊時直接利用PROBS中大眾統計出的機率)
            probability *= PROBS["gene"][num_genes] * PROBS["trait"][num_genes][has_trait]
        else:
            # Parental information available
            #爸媽的基因 > 小孩的基因 > 小孩的特徵 
            mother_prob = 0.5 if data['mother'] in one_gene else 1 if data['mother'] in two_genes else 0 # 母親將基因傳給小孩的機率
            father_prob = 0.5 if data['father'] in one_gene else 1 if data['father'] in two_genes else 0
            # 窮舉父母各種可能的基因組合，計算小孩基因的機率
            if num_genes == 0:
                gene_prob = (1 - mother_prob) * (1 - father_prob) * (1 - PROBS["mutation"]) * (1 - PROBS["mutation"]) + (1 - mother_prob) * father_prob * (1 - PROBS["mutation"]) * PROBS["mutation"] + mother_prob * (1 - father_prob) * PROBS["mutation"] * (1 - PROBS["mutation"]) + mother_prob * father_prob * PROBS["mutation"] * PROBS["mutation"]
            elif num_genes == 1:
                gene_prob = (1 - mother_prob) * father_prob * ((1 - PROBS["mutation"])**2 + PROBS["mutation"]**2) + mother_prob * (1 - father_prob) * ((1 - PROBS["mutation"])**2 + PROBS["mutation"]**2) + mother_prob * father_prob * (PROBS["mutation"] * (1 - PROBS["mutation"]) + (1 - PROBS["mutation"]) * PROBS["mutation"]) + (1 - mother_prob) * (1 - father_prob) * (PROBS["mutation"] * (1 - PROBS["mutation"]) + (1 - PROBS["mutation"]) * PROBS["mutation"])
            else:
                gene_prob = mother_prob * father_prob * (1 - PROBS["mutation"]) * (1 - PROBS["mutation"]) + (1 - mother_prob) * father_prob * PROBS["mutation"] * (1 - PROBS["mutation"]) + mother_prob * (1 - father_prob) * (1 - PROBS["mutation"]) * PROBS["mutation"] + (1 - mother_prob) * (1 - father_prob) * PROBS["mutation"] * PROBS["mutation"]
            print("Gene probability:", gene_prob)
            print("Trait probability:", PROBS["trait"][num_genes][has_trait])
            probability *= gene_prob * PROBS["trait"][num_genes][has_trait]
    return probability

            # mother_prob = 0 if data['mother'] is None else 0.5 if data['mother'] in one_gene else 1 if data['mother'] in two_genes else 0
            # father_prob = 0 if data['father'] is None else 0.5 if data['father'] in one_gene else 1 if data['father'] in two_genes else 0
            # gene_prob = (1 - mother_prob) * (1 - father_prob) * (1 - PROBS["mutation"]) if num_genes == 0 else \
            #             (1 - mother_prob) * father_prob * 0.5 + mother_prob * (1 - father_prob) * 0.5 + mother_prob * father_prob * PROBS["mutation"] if num_genes == 1 else \
            #             mother_prob * father_prob * (1 - PROBS["mutation"])
            


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        num_genes = 0
        if person in one_gene:
            num_genes = 1
        elif person in two_genes:
            num_genes = 2

        # Update gene distribution
        probabilities[person]["gene"][num_genes] += p

        # Update trait distribution
        probabilities[person]["trait"][True] += p if person in have_trait else 0
        probabilities[person]["trait"][False] += p if person not in have_trait else 0


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # Normalize gene distribution
        gene_sum = sum(probabilities[person]["gene"].values())
        for num_genes in probabilities[person]["gene"]:
            probabilities[person]["gene"][num_genes] /= gene_sum

        # Normalize trait distribution
        trait_sum = sum(probabilities[person]["trait"].values())
        for has_trait in probabilities[person]["trait"]:
            probabilities[person]["trait"][has_trait] /= trait_sum


if __name__ == "__main__":
    main()
