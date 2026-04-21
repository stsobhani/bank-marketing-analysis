const NAVY = '#0B1D3A';
const ACC  = '#C4380D';
const GOLD = '#B8860B';
const GRAY = '#B4B2A9';

const base = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false } },
    y: { grid: { color: 'rgba(0,0,0,0.05)' } }
  }
};

//groupby job, response rate descending
new Chart('jobChart', {
  type: 'bar',
  data: {
    labels: ['student','retired','unemployed','admin.','management','technician','self-empl.','housemaid','entrepreneur','services','blue-collar'],
    datasets: [{
      data: [31.43, 25.23, 14.20, 12.97, 11.22, 10.83, 10.49, 10.00, 8.52, 8.14, 6.89],
      backgroundColor: [ACC, ACC, GOLD, GOLD, GRAY, GRAY, GRAY, GRAY, GRAY, GRAY, GRAY],
      borderRadius: 3
    }]
  },
  options: {
    ...base,
    indexAxis: 'y',
    scales: {
      x: { grid: { color: 'rgba(0,0,0,0.05)' }, title: { display: true, text: 'Subscription Rate (%)' } },
      y: { grid: { display: false } }
    }
  }
});

// Age band
new Chart('ageChart', {
  type: 'bar',
  data: {
    labels: ['18-24\n(n=1,068)', '25-34\n(n=13,686)', '35-44\n(n=13,500)', '45-54\n(n=8,704)', '55-64\n(n=3,567)', '65+\n(n=663)'],
    datasets: [{
      data: [23.97, 12.17, 8.65, 8.65, 13.57, 47.21],
      backgroundColor: [GOLD, GRAY, GRAY, GRAY, GOLD, ACC],
      borderRadius: 3
    }]
  },
  options: {
    ...base,
    scales: {
      x: { grid: { display: false }, ticks: { autoSkip: false } },
      y: { grid: { color: 'rgba(0,0,0,0.05)' }, title: { display: true, text: 'Subscription Rate (%)' } }
    }
  }
});

// Month, sorted by rate descending
new Chart('monthChart', {
  type: 'bar',
  data: {
    labels: ['mar', 'dec', 'sep', 'oct', 'apr', 'aug', 'jun', 'nov', 'jul', 'may'],
    datasets: [{
      data: [50.55, 48.90, 44.91, 43.87, 20.48, 10.60, 10.51, 10.14, 9.05, 6.43],
      backgroundColor: [ACC, ACC, ACC, ACC, GOLD, GRAY, GRAY, GRAY, GRAY, GRAY],
      borderRadius: 3
    }]
  },
  options: {
    ...base,
    scales: {
      x: { grid: { display: false }, ticks: { autoSkip: false } },
      y: { grid: { color: 'rgba(0,0,0,0.05)' }, title: { display: true, text: 'Subscription Rate (%)' } }
    }
  }
});

// Prior campaign outcome
new Chart('poutcomeChart', {
  type: 'bar',
  data: {
    labels: ['success\n(n=1,373)', 'failure\n(n=4,252)', 'nonexistent\n(n=35,563)'],
    datasets: [{
      data: [65.11, 14.23, 8.83],
      backgroundColor: [ACC, GOLD, GRAY],
      borderRadius: 3,
      barThickness: 80
    }]
  },
  options: {
    ...base,
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: 'rgba(0,0,0,0.05)' }, title: { display: true, text: 'Subscription Rate (%)' } }
    }
  }
});

// Contact channel
new Chart('contactChart', {
  type: 'bar',
  data: {
    labels: ['cellular\n(n=26,144)', 'telephone\n(n=15,044)'],
    datasets: [{
      data: [14.74, 5.23],
      backgroundColor: [ACC, GRAY],
      borderRadius: 3,
      barThickness: 80
    }]
  },
  options: {
    ...base,
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: 'rgba(0,0,0,0.05)' }, title: { display: true, text: 'Subscription Rate (%)' } }
    }
  }
});

// Campaign bucket
new Chart('campaignChart', {
  type: 'bar',
  data: {
    labels: ['1 contact', '2 contacts', '3 contacts', '4-5 contacts', '6+ contacts'],
    datasets: [{
      data: [13.04, 11.46, 10.75, 8.68, 5.49],
      backgroundColor: [ACC, GOLD, GOLD, GRAY, GRAY],
      borderRadius: 3
    }]
  },
  options: {
    ...base,
    scales: {
      x: { grid: { display: false }, ticks: { autoSkip: false } },
      y: { grid: { color: 'rgba(0,0,0,0.05)' }, title: { display: true, text: 'Subscription Rate (%)' } }
    }
  }
});

// Euribor by outcome
new Chart('euriborChart', {
  type: 'bar',
  data: {
    labels: ['Subscribed — yes (n=4,640)', 'Did Not Subscribe — no (n=36,548)'],
    datasets: [{
      data: [2.123, 3.811],
      backgroundColor: [ACC, GRAY],
      borderRadius: 3,
      barThickness: 100
    }]
  },
  options: {
    ...base,
    scales: {
      x: { grid: { display: false } },
      y: {
        min: 0, max: 5,
        grid: { color: 'rgba(0,0,0,0.05)' },
        title: { display: true, text: 'Average Euribor 3-Month Rate (%)' }
      }
    }
  }
});

// Model comparison
new Chart('modelCompareChart', {
  type: 'bar',
  data: {
    labels: ['Logistic Regression', 'Random Forest', 'XGBoost'],
    datasets: [{
      data: [0.7806, 0.7736, 0.8003],
      backgroundColor: [GRAY, GRAY, ACC],
      borderRadius: 3,
      barThickness: 60
    }]
  },
  options: {
    ...base,
    scales: {
      x: { grid: { display: false } },
      y: {
        min: 0.72, max: 0.82,
        grid: { color: 'rgba(0,0,0,0.05)' },
        title: { display: true, text: 'AUC-ROC (5-Fold CV)' }
      }
    }
  }
});

// Feature importance, lists the top 8 from XGBoost
new Chart('featureChart', {
  type: 'bar',
  data: {
    labels: ['cons.price.idx', 'is_cellular', 'cons.conf.idx', 'pdays', 'poutcome_ord', 'was_prev_contacted', 'emp.var.rate', 'nr.employed'],
    datasets: [{
      data: [0.0194, 0.0177, 0.0312, 0.0336, 0.0348, 0.0471, 0.0555, 0.6757],
      backgroundColor: [GRAY, GRAY, GRAY, GRAY, GRAY, GOLD, GOLD, ACC],
      borderRadius: 3
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { color: 'rgba(0,0,0,0.05)' }, title: { display: true, text: 'Importance Score' } },
      y: { grid: { display: false } }
    }
  }
});

// Cumulative gain curve
new Chart('liftChart', {
  type: 'line',
  data: {
    labels: ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'],
    datasets: [
      {
        label: 'XGBoost Model',
        data: [0, 51.4, 66.8, 76.3, 83.3, 88.4, 92.0, 95.0, 97.2, 99.2, 100],
        borderColor: ACC,
        backgroundColor: 'rgba(196,56,13,0.08)',
        fill: true,
        borderWidth: 2.5,
        pointRadius: 4,
        pointBackgroundColor: ACC,
        tension: 0.3
      },
      {
        label: 'Random Baseline',
        data: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        borderColor: GRAY,
        borderWidth: 1.5,
        borderDash: [6, 4],
        pointRadius: 0,
        fill: false
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: true, position: 'bottom' } },
    scales: {
      x: { grid: { display: false }, title: { display: true, text: '% of File Contacted (top-scored first)' } },
      y: { grid: { color: 'rgba(0,0,0,0.05)' }, title: { display: true, text: '% of All Subscribers Captured' } }
    }
  }
});

// Decile bar
new Chart('decileBarChart', {
  type: 'bar',
  data: {
    labels: ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10'],
    datasets: [{
      data: [57.93, 17.33, 10.73, 7.89, 5.68, 4.13, 3.33, 2.48, 2.21, 0.95],
      backgroundColor: [ACC, ACC, ACC, GOLD, GOLD, GRAY, GRAY, GRAY, GRAY, GRAY],
      borderRadius: 3
    }]
  },
  options: {
    ...base,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: 'rgba(0,0,0,0.05)' }, title: { display: true, text: 'Subscription Rate (%)' } }
    }
  }
});