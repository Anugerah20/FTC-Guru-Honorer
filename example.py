from collections import Counter

# Contoh data klasterisasi buah-buahan
clusters = {
    'Cluster 1': ['apel', 'apel', 'apel', 'apel', 'apel', 'apel', 'apel', 'apel', 'jeruk', 'pisang'],
    'Cluster 2': ['apel', 'apel', 'jeruk', 'jeruk', 'jeruk', 'jeruk', 'jeruk', 'jeruk', 'jeruk', 'pisang'],
    'Cluster 3': ['apel', 'jeruk', 'jeruk', 'pisang', 'pisang', 'pisang', 'pisang', 'pisang', 'pisang', 'pisang']
}

def calculate_purity(clusters):
    total_items = 0  # Jumlah total buah-buahan di semua keranjang
    max_labels_sum = 0  # Jumlah buah terbanyak dalam tiap keranjang

    # Iterasi setiap klaster
    for cluster_name, fruits in clusters.items():
        # Tambahkan jumlah buah dalam keranjang ke total
        total_items += len(fruits)

        print(f'{cluster_name}: {fruits}')

        # Hitung jumlah masing-masing jenis buah
        label_counts = Counter(fruits)

        print(f'Total {cluster_name}: {total_items}')

        # Jumlah jenis buah terbanyak dalam keranjang
        max_label_count = max(label_counts.values())

        print(f'Jumlah jenis buah terbanyak dari klaster {cluster_name}: {max_label_count}')
        print(' ')


        max_labels_sum += max_label_count  # Tambahkan ke total buah terbanyak di setiap keranjang

    # Hitung purity
    purity = max_labels_sum / total_items
    return purity

# Hitung purity untuk contoh data
purity_score = calculate_purity(clusters)
print(f'Purity: {purity_score:.2f} %')