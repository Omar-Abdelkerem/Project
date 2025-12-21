// Delivery Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Confirm before marking as Failed
    const failButtons = document.querySelectorAll('.btn-danger');
    failButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to mark this delivery as Failed?')) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Handle form submission properly
    const forms = document.querySelectorAll('.action-form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            // Don't prevent default - let form submit normally
            const button = form.querySelector('button[type="submit"]');
            if (button) {
                // Store original values
                const originalText = button.textContent;
                const originalDisabled = button.disabled;
                
                // Show processing state
                button.disabled = true;
                button.style.opacity = '0.6';
                button.textContent = 'Processing...';
                
                // Log form data for debugging
                const formData = new FormData(form);
                console.log('Form submitting with:', {
                    delivery_id: formData.get('delivery_id'),
                    status: formData.get('status') || button.value
                });
                
                // Re-enable after 10 seconds in case of error (timeout)
                setTimeout(function() {
                    if (button.disabled) {
                        button.disabled = originalDisabled;
                        button.style.opacity = '1';
                        button.textContent = originalText;
                        console.warn('Form submission timeout - re-enabling button');
                    }
                }, 10000);
            }
            
            // Scroll to top to see flash messages
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });
});
