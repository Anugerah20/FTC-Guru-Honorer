document.addEventListener('DOMContentLoaded', (event) => {
     let total_positif = document.getElementById('total_positif').value;
     let total_negatif = document.getElementById('total_negatif').value;
     let total_netral = document.getElementById('total_netral').value;

     let ctx = document.getElementById('dataChart').getContext('2d');
     let dataChart = new Chart(ctx, {
          type: 'bar',
          data: {
               labels: ['Positive', 'Negative', 'Neutral'],
               datasets: [{
                    label: 'Data Chart',
                    data: [total_positif, total_negatif, total_netral],
                    backgroundColor: [
                         'rgba(75, 192, 192, 0.2)',
                         'rgba(255, 99, 132, 0.2)',
                         'rgba(255, 205, 86, 0.2)'
                    ],
                    borderColor: [
                         'rgba(75, 192, 192, 1)',
                         'rgba(255, 99, 132, 1)',
                         'rgba(255, 205, 86, 1)'
                    ],
                    borderWidth: 1
               }]
          },
          options: {
               scales: {
                    y: {
                         beginAtZero: true
                    }
               }
          }
     });
});
