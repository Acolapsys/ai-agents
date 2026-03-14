import Chart from 'chart.js/auto'

export function useChart(canvas, options) {
  if (!canvas || !(canvas instanceof HTMLCanvasElement)) {
    console.error('useChart: ожидается canvas элемент')
    return
  }

  const ctx = canvas.getContext('2d')
  if (!ctx) {
    console.error('useChart: не удалось получить 2D контекст')
    return
  }

  // Если на canvas уже есть график, лучше его уничтожить
  // Chart.js хранит глобальный реестр, но можно просто создать новый — он перезапишет
  // Но для красоты можно найти существующий экземпляр и вызвать destroy()
  const existingChart = Chart.getChart(canvas)
  if (existingChart) {
    existingChart.destroy()
  }

  const { type, title, x, y, labels, values } = options

  if (type === 'line' || type === 'bar') {
    new Chart(canvas, {
      type,
      data: {
        labels: x,
        datasets: [{
          label: title,
          data: y,
          backgroundColor: type === 'bar' ? '#86bbd8' : undefined,
          borderColor: '#33658a',
          tension: 0.1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        }
      }
    })
  } else if (type === 'pie') {
    new Chart(canvas, {
      type: 'pie',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: ['#33658a', '#86bbd8', '#f6ae2d', '#b0bec5', '#2f4858']
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    })
  }
}