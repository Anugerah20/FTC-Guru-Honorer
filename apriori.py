import itertools
import time

def extract_terms(documents):
    """
    Mengambil semua istilah unik dari dokumen.
    Args:
        documents (list of str): Daftar dokumen, setiap dokumen berupa string.
    Returns:
        list: Daftar istilah unik yang sudah diurutkan.
    """
    terms = set()
    for doc in documents:
        terms.update(doc.split())
    return sorted(terms)

def preprocess_documents(documents):
    """
    Memproses dokumen dengan memecah setiap dokumen menjadi set istilah.
    Args:
        documents (list of str): Daftar dokumen, setiap dokumen berupa string.
    Returns:
        list of set: Daftar set istilah untuk setiap dokumen.
    """
    return [set(doc.split()) for doc in documents]

def generate_candidates(itemset_number, last_frequent_itemsets):
    """
    Menghasilkan kandidat itemset dengan ukuran tertentu dari itemset frekuensi terakhir.
    Args:
        itemset_number (int): Ukuran itemset yang akan dihasilkan.
        last_frequent_itemsets (list of tuple): Daftar itemset frekuensi terakhir.
    Returns:
        list of tuple: Daftar kandidat itemset.
    """
    if itemset_number == 1:
        raise Exception(
            "This function should not be called for the first itemset generation.")
    else:
        temp_candidates = set()
        # Lakukan perulangan terhadap pasangan dari set item yang sering muncul terakhir
        for i in range(len(last_frequent_itemsets)):
            for j in range(i + 1, len(last_frequent_itemsets)):
                # Mengubah tupel menjadi set untuk memudahkan penggabungan
                set1, set2 = set(last_frequent_itemsets[i]), set(
                    last_frequent_itemsets[j])
                # Gabungkan set hanya jika mereka memiliki kesamaan persis dengan itemset_number - 2 item yang sama
                if len(set1.intersection(set2)) == itemset_number - 2:
                    new_candidate = tuple(sorted(set1.union(set2)))
                    # Memastikan kandidat baru memiliki jumlah item yang benar
                    if len(new_candidate) == itemset_number:
                        temp_candidates.add(new_candidate)
        return list(temp_candidates)

def calculate_frequent_itemsets(documents, candidates, min_sup):
    """
    Menghitung itemset frekuensi dan dokumen yang mengandung itemset tersebut.
    Args:
        documents (list of set): Daftar set istilah untuk setiap dokumen.
        candidates (list of tuple): Daftar kandidat itemset.
        min_sup (float): Ambang batas dukungan minimum.
    Returns:
        list of tuple: Daftar itemset frekuensi beserta dokumen yang mengandung itemset tersebut.
    """
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

def apriori(documents, min_sup):
    """
    Implementasi algoritma Apriori untuk menemukan itemset frekuensi.
    Args:
        documents (list of str): Daftar dokumen, setiap dokumen berupa string.
        min_sup (float): Ambang batas dukungan minimum.
        time (float): Waktu eksekusi algoritma apriori.
    """
    start = time.time()
    terms = extract_terms(documents)
    processed_docs = preprocess_documents(documents)
    all_frequent_itemsets = []  # List to store all frequent itemsets

    # Generate initial frequent itemsets directly from terms
    last_frequent_itemsets = calculate_frequent_itemsets(
        processed_docs, [tuple([term]) for term in terms], min_sup)

    # Store initial frequent itemsets
    all_frequent_itemsets.extend(last_frequent_itemsets)

    print("Frequent 1-itemsets:")
    for itemset, docs in last_frequent_itemsets:
        print(f"{' '.join(itemset)} = {sorted(list(docs))}")

    itemset_number = 1

    while True:
        itemset_number += 1
        candidates = generate_candidates(
            itemset_number, [itemset for itemset, _ in last_frequent_itemsets])

        last_frequent_itemsets = calculate_frequent_itemsets(
            processed_docs, candidates, min_sup)

        if not last_frequent_itemsets:
            break

        # Store all subsequent frequent itemsets
        all_frequent_itemsets.extend(last_frequent_itemsets)

        print()
        print(f"Frequent {itemset_number}-itemsets:")
        for itemset, docs in last_frequent_itemsets:
            print(f"{' '.join(itemset)} = {sorted(list(docs))}")

        if itemset_number > 10:  # Safety check to prevent infinite loops
            break

    # Display all frequent itemsets collected
    print("\nAll Frequent Itemsets:")
    for itemset, docs in all_frequent_itemsets:
        print(f"{' '.join(itemset)} = {sorted(list(docs))}")

    end = time.time()
    print(f"Execution time is: {(end - start):.2f} seconds.")

if __name__ == "__main__":
    documents = [
       "honorer jokowi sd tes",
       "owi jokowi",
       "guru honorer sd tes",
       "honorer jokowi sd tes",
       "guru gaji wowo",
       "wowo gaji guru",
       "honorer jokowi sd prima",
       "kebijakan jokowi sd prima",
       "pasal jokowi sd prima",
    ]
    # min_sup = 0.4  # Minimum support (40%)
    # min_sup = 0.3  # Minimum support (30%)
    # min_sup = 0.2  # Minimum support (20%)
    min_sup = 0.1  # Minimum support (10%)

    apriori(documents, min_sup)
