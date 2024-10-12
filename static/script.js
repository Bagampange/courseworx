
// Function for timing out success messages
window.setTimeout(function() {
    const alerts = document.querySelectorAll('.flash-success');
    alerts.forEach(alert => alert.style.display = 'none');
}, 1500);

// Function for auto-filling input fields
function updateInputFields() {
    const selectElement = document.getElementById('courseSelect');
    const inputField1 = document.getElementById('courseName');
    const inputField2 = document.getElementById('assignmentNumber');


    // Get the selected value
    const selectedValue = selectElement.value;

    // Find the corresponding option
    const selectedOption = assignmentsData.find(option => option.course_code === selectedValue);

    // Update the input fields based on the selected value
    if (selectedOption) {
        inputField1.value = selectedOption.course_name;
        inputField2.value = selectedOption.assignment_number;

    } else {
        inputField1.value = '';
        inputField2.value = '';

    }
};

