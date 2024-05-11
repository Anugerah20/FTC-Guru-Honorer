import seaborn as sns
import matplotlib.pyplot as plt

# Mengatur seaborn untuk tampilan
sns.set_theme()

def show_bar_chart(labels, counts, title):

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(labels, counts, color=['#2394f7', '#f72323', '#fac343'])

    # Menambahkan keterangan persentase
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax.annotate(f'{count}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), # 3 points vertical offset
                    textcoords='offset points',
                    ha='center', va='bottom')

    # Menambahkan grid
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Menambahkan label sumbu dan judul
    ax.set_xlabel('Text Mining')
    ax.set_ylabel('Jumlah')
    ax.set_title(title)

    plt.savefig('static/bar_chart.png')