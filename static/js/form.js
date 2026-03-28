// Clear form inputs when page loads with a result displayed
document.addEventListener('DOMContentLoaded', function() {
    const resultContainer = document.querySelector('.result-container');
    if (resultContainer && resultContainer.classList.contains('show')) {
        // Clear all form inputs
        document.querySelectorAll('input[type="number"], input[type="text"], select').forEach(input => {
            input.value = '';
        });
        
        // Scroll to result
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});
