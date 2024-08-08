import itertools
import time
from collections import defaultdict
from math import log


def extract_terms(documents):
    terms = set()
    for doc in documents:
        terms.update(doc.split())
    return sorted(terms)

def preprocess_documents(documents):
    return [set(doc.split()) for doc in documents]

def generate_candidates(itemset_number, last_frequent_itemsets):
    if itemset_number == 1:
        raise Exception("This function should not be called for the first itemset generation.")
    else:
        temp_candidates = set()
        for i in range(len(last_frequent_itemsets)):
            for j in range(i + 1, len(last_frequent_itemsets)):
                set1, set2 = set(last_frequent_itemsets[i]), set(last_frequent_itemsets[j])
                if len(set1.intersection(set2)) == itemset_number - 2:
                    new_candidate = tuple(sorted(set1.union(set2)))
                    if len(new_candidate) == itemset_number:
                        temp_candidates.add(new_candidate)
        return list(temp_candidates)

def calculate_frequent_itemsets(documents, candidates, min_sup):
    num_documents = len(documents)
    frequent_itemsets = []
    itemset_counts = [0] * len(candidates)
    itemset_documents = [set() for _ in range(len(candidates))]

    for i, candidate in enumerate(candidates):
        for doc_id, document in enumerate(documents):
            if set(candidate).issubset(document):
                itemset_counts[i] += 1
                itemset_documents[i].add(f"D{doc_id+1}")

    return [(candidates[i], itemset_documents[i]) for i in range(len(candidates)) if itemset_counts[i] / num_documents >= min_sup]

def generate_frequent_term_set(documents, min_sup):
    terms = extract_terms(documents)
    processed_docs = preprocess_documents(documents)
    all_frequent_itemsets = []

    # Debug: Cetak terms dan dokumen yang telah diproses
    # print("Extracted terms:", terms)
    # print("Processed documents:", processed_docs)

    last_frequent_itemsets = calculate_frequent_itemsets(processed_docs, [tuple([term]) for term in terms], min_sup)
    all_frequent_itemsets.extend(last_frequent_itemsets)

    print("Frequent 1-itemsets:")
    for itemset, docs in last_frequent_itemsets:
        print(f"{' '.join(itemset)} = {sorted(list(docs))}")

    itemset_number = 1

    while True:
        itemset_number += 1
        candidates = generate_candidates(itemset_number, [itemset for itemset, _ in last_frequent_itemsets])

        # Cetak kandidat yang dihasilkan
        # print(f"Candidates for itemset {itemset_number}:", candidates)

        last_frequent_itemsets = calculate_frequent_itemsets(processed_docs, candidates, min_sup)

        if not last_frequent_itemsets:
            break

        all_frequent_itemsets.extend(last_frequent_itemsets)

        print()
        print(f"Frequent {itemset_number}-itemsets:")
        for itemset, docs in last_frequent_itemsets:
            print(f"{' '.join(itemset)} = {sorted(list(docs))}")

        if itemset_number > 10:
            break

    print("\nAll Frequent Itemsets:")
    for itemset, docs in all_frequent_itemsets:
        print(f"{' '.join(itemset)} = {sorted(list(docs))}")

    frequent_term_set = {tuple(itemset): docs for itemset, docs in all_frequent_itemsets}
    return frequent_term_set

def calculate_entropy_overlap(frequent_term_set, data):
    entropy_overlap_results = {}

    for term_set, documents in frequent_term_set.items():
        entropy_overlap_sum = 0
        for document in documents:
            frequency = sum(document in documents for documents in frequent_term_set.values())
            entropy_overlap = (-1/frequency) * log(1/frequency)
            entropy_overlap_sum += entropy_overlap

        entropy_overlap_results[term_set] = (documents, round(entropy_overlap_sum, 2))

    return entropy_overlap_results

def remove_document(entropy_overlap_results, min_support):
    removed_docs = []
    lowest_dicts = []
    keys_to_remove = []
    lowest_value = float('inf')

    for term_set, document in entropy_overlap_results.items():
        frequency = document[1]
        if frequency < lowest_value:
            lowest_value = frequency
            lowest_dicts = [{term_set: document}]
        elif frequency == lowest_value:
            lowest_dicts.append({term_set: document})

    for lowest_dict in lowest_dicts:
        removed_docs.extend(lowest_dict[list(lowest_dict.keys())[0]][0])

    updated_results = {}
    for term_set, document in entropy_overlap_results.items():
        remaining_docs = [doc for doc in document[0] if doc not in removed_docs]
        if remaining_docs:
            updated_results[term_set] = (remaining_docs, document[1])

    for term_set, document in updated_results.items():
        if len(document[0]) < min_support:
            keys_to_remove.append(term_set)

    for key in keys_to_remove:
        del updated_results[key]

    return updated_results

# def ftc(data, min_support):

#     # Time start
#     start = time.time()

#     cluster = {}

#     frequent_term_set = generate_frequent_term_set(data, min_support)

#     # i = 0
#     # while len(frequent_term_set) > 1:
#     #     eo_frequent_term_set = calculate_entropy_overlap(frequent_term_set, data)

#     #     removed = remove_document(eo_frequent_term_set, min_support)

#     #     for term_set, (documents, entropy_overlap) in eo_frequent_term_set.items():
#     #         cluster[term_set] = (documents, entropy_overlap)

#     #     frequent_term_set = {term_set: document[0] for term_set, document in removed.items()}
#     #     i += 1


#     iterations = []
#     i = 0

#     while len(frequent_term_set) > 1:
#         eo_frequent_term_set = calculate_entropy_overlap(frequent_term_set, data)
#         removed = remove_document(eo_frequent_term_set, min_support)

#         iteration_results = {
#             'iteration': i + 1,
#             'frequent_term_set': eo_frequent_term_set
#         }
#         iterations.append(iteration_results)

#         for term_set, (documents, entropy_overlap) in eo_frequent_term_set.items():
#             cluster[term_set] = (documents, entropy_overlap)

#         frequent_term_set = {term_set: document[0] for term_set, document in removed.items()}
#         i += 1

#     # Hasil klaster setelah FTC
#     print(" ")
#     print("Cluster results after FTC:")

#     for term_set, (documents, entropy_overlap) in cluster.items():
#         print(f"Term Set: {' '.join(term_set)}, Documents: {sorted(list(documents))}, Entropy Overlap: {entropy_overlap}")

#     # Time end
#     end = time.time()

#     print(f"Waktu eksekusi: {(end - start):.2f} detik")

#     return cluster


# NEW NEW
def ftc(data, min_support):
    start = time.time()
    cluster = {}
    iterations = []

    frequent_term_set = generate_frequent_term_set(data, min_support)
    i = 0

    while len(frequent_term_set) > 1:
        eo_frequent_term_set = calculate_entropy_overlap(frequent_term_set, data)
        removed = remove_document(eo_frequent_term_set, min_support)

        iteration_results = {
            'iteration': i + 1,
            'frequent_term_set': eo_frequent_term_set
        }
        iterations.append(iteration_results)

        for term_set, (documents, entropy_overlap) in eo_frequent_term_set.items():
            cluster[term_set] = (documents, entropy_overlap)

        frequent_term_set = {term_set: document[0] for term_set, document in removed.items()}
        i += 1

    end = time.time()
    print(f"Waktu eksekusi: {(end - start):.2f} detik")

    return iterations


def main():

    # Minumum support 40%
    min_support = 0.4

    data = [
       "honorer jokowi sd tes",
       "owi jokowi",
       "guru honorer sd tes",
       "guru jokowi sd gaji",
       "honorer owi tes sd",
       "wowo gaji"
    ]

    cluster = ftc(data, min_support)

    print(" ")
    # print(cluster)

    print(f"Klaster yang dihasilkan: {cluster}")

    for iteration in cluster:
        print(f"Iteration {iteration['iteration']}:")
        for term_set, (documents, entropy_overlap) in iteration['frequent_term_set'].items():
            # Menentukan format output untuk term_set
            if len(term_set) == 1:
                terms_display = term_set[0]  # Jika hanya satu term, tampilkan tanpa koma
            else:
                terms_display = ', '.join(term_set)  # Jika lebih dari satu term, pisahkan dengan koma
            print(f"Term Set: {terms_display}, Documents: {sorted(list(documents))}, Entropy Overlap: {entropy_overlap}")

if __name__ == "__main__":
    main()
