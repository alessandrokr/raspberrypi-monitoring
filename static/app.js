const DEFAULT_INTERVAL = 2000;
let interval = localStorage.getItem('updateInterval') ? parseInt(localStorage.getItem('updateInterval'), 10) : DEFAULT_INTERVAL;
let timer = null;

const tempEl = document.getElementById('tempValue');
const freqEl = document.getElementById('freqValue');
const thrEl = document.getElementById('throttleValue');
const intervalInput = document.getElementById('intervalInput');
const saveBtn = document.getElementById('saveBtn');

// Chart setup
const ctx = document.getElementById('tempChart').getContext('2d');
const maxPoints = 60;
const chartData = {
  labels: [],
  datasets: [{
    label: 'CPU °C',
    backgroundColor: 'rgba(255,99,132,0.2)',
    borderColor: 'rgba(255,99,132,1)',
    tension: 0.25,
    data: []
  }]
};

const tempChart = new Chart(ctx, {
  type: 'line',
  data: chartData,
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {display: false},
      y: {beginAtZero: false}
    }
  }
});

async function fetchStats(){
  try{
    const [tRes,fRes,thRes] = await Promise.all([
      fetch('/cpu-temp'),
      fetch('/cpu-freq'),
      fetch('/throttle')
    ]);
    const t = await tRes.json();
    const f = await fRes.json();
    const th = await thRes.json();

    const temp = (t.temperature||0).toFixed(2);
    tempEl.textContent = `${temp} °C`;
    freqEl.textContent = `${f.frequency} Hz`;
    thrEl.textContent = `0x${(th.throttled||0).toString(16)}`;

    // update chart
    const now = new Date().toLocaleTimeString();
    chartData.labels.push(now);
    chartData.datasets[0].data.push(parseFloat(temp));
    if(chartData.labels.length > maxPoints){
      chartData.labels.shift();
      chartData.datasets[0].data.shift();
    }
    tempChart.update();
  }catch(e){
    console.error('fetchStats', e);
  }
}

function startPolling(){
  if(timer) clearInterval(timer);
  fetchStats();
  timer = setInterval(fetchStats, interval);
}

saveBtn.addEventListener('click', ()=>{
  const v = parseInt(intervalInput.value, 10);
  if(!isNaN(v) && v >= 250){
    interval = v;
    localStorage.setItem('updateInterval', String(interval));
    startPolling();
  }
});

// init
intervalInput.value = interval;
startPolling();
