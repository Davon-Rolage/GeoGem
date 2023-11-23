// Block mastery doughnut chart
let ctx = document.getElementById('doughnut').getContext('2d');
let bmlDoughnutFractional = JSON.parse(document.getElementById("bml-doughnut-fractional").textContent);
bmlDoughnutFractional *= 100;

let doughnutChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        datasets: [{
            data: [bmlDoughnutFractional, 100 - bmlDoughnutFractional],
            backgroundColor: ['#50C878', '#D3D3D3'],
        }],
    },
});

// Block mastery chart
let ctx2 = document.getElementById("mastery-level-chart").getContext("2d");
const mlChartData = JSON.parse(document.getElementById("ml-chart-data").textContent);

let chart = new Chart(ctx2, {
type: "bar",
data: {
    labels: mlChartData["x"],
    datasets: [
        {
        label: "Number of words",
        backgroundColor: "#79AEC8",
        borderColor: "#417690",
        data: mlChartData["y"]
        }
    ]
},
options: {
    scales: {
        x: {
            title: {
                display: true,
                text: "Mastery level"
            }
        },
        y: {
            title: {
                display: true,
                text: "Number of words"
            }
        }
    }
}
});
