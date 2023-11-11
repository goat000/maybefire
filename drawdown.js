$(document).ready(function() {
    populateFormData();

    $('#drawdownForm').submit(function(event) {
        event.preventDefault(); // Prevent the form from submitting the traditional way
        compute();
        saveFormData();
    });
});

// Function to save form data to localStorage using jQuery
function saveFormData() {
    $('#drawdownForm').find(':input').each(function() {
        var element = $(this);
        if (element.attr('name')) {
            localStorage.setItem(element.attr('name'), element.val());
        }
    });
}

// Function to populate form with data from localStorage using jQuery
function populateFormData() {
    $('#drawdownForm').find(':input').each(function() {
        var element = $(this);
        if (element.attr('name')) {
            element.val(localStorage.getItem(element.attr('name')));
        }
    });
}

function compute() {
    // Placeholder for your calculation logic to populate this data
    const data = {
        labels: Array.from(new Array(50), (val, index) => index + 1), // Years 1 through 50
        datasets: [
            {
                label: 'Roth Withdrawal',
                backgroundColor: 'rgb(255, 99, 132)',
                data: new Array(50).fill(10000), // Replace zeros with actual computed data
            },
            {
                label: 'Traditional Withdrawal',
                backgroundColor: 'rgb(54, 162, 235)',
                data: new Array(50).fill(20000), // Replace zeros with actual computed data
            },
            {
                label: 'Taxable Withdrawal',
                backgroundColor: 'rgb(75, 192, 192)',
                data: new Array(50).fill(30000), // Replace zeros with actual computed data
            },
            {
                label: 'HSA Withdrawal',
                backgroundColor: 'rgb(153, 102, 255)',
                data: new Array(50).fill(40000), // Replace zeros with actual computed data
            }
        ]
    };

    // Configuration options
    const config = {
        type: 'line',
        data: data,
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        },
    };

    // Render the chart
    const myChart = new Chart(
        document.getElementById('myChart'),
        config
    );
}

// Remember to call `compute` when appropriate, e.g., after a form submission.
