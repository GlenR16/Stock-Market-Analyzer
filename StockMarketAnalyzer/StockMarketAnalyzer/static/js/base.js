//Graphs
textcolor = 'aqua';

function getRandomInt(min=2, max=20) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min) + min);
}
const ctx = document.getElementById('myChart');
if (ctx){
    const myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['1', '2', '3', '4', '5', '6'],
            datasets: [{label: 'Random Data',data: [2, 19, 3, 5, 2, 20],borderColor: textcolor,borderWidth: 3}]
        },
        options: {
            plugins: {legend: {display: false},},
            scales: {y: {beginAtZero: true,grid:{display:true,color:textcolor},ticks:{color:textcolor}},x:{grid:{display:true,color:'#ffffff'},ticks:{color:textcolor}}},
            elements:{line:{tension: 0.4}}
        }
    });
    setInterval( function () {                        
        myChart.data.datasets[0].data = [2, getRandomInt(), getRandomInt(), getRandomInt(), getRandomInt(), 20];
        myChart.update();
    },2000);
}
const stock = document.getElementById("stockgraph");
if (stock){
    const chart = new Chart(stock,{
        type: 'line',
        data:{
            labels: [" "," "," "," "," "," "],
            datasets:[{label:'Price',data: [2, 4, 6, 8, 10, 20],borderColor: textcolor,borderWidth: 3}]
        },
        options: {
            scales: {y: {beginAtZero: true,grid:{display:true,color:'#ffffff'},ticks:{color:textcolor}},x:{grid:{display:true,color:'#ffffff'},ticks:{color:'#7efed4'}}}
        }
    });
    setInterval( function () {
        $.ajax({
            url: "../api/",
            type: 'GET',
            dataType: 'json',
            success: function(res) {
                console.log(res);
            }

        });
        chart.data.datasets[0].data = [2, getRandomInt(), getRandomInt(), getRandomInt(), getRandomInt(), 20];
        chart.update();
    },120000);
}