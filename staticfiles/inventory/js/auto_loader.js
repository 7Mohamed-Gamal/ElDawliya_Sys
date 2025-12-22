/**
 * Auto Loader Script
 * Automatically loads the voucher filter loader script on every page load
 */

(function() {
    // Check if we're in the voucher form
    if (document.querySelector('#productSearchModal')) {
        // Create script tag for the filter loader
        const script = document.createElement('script');
        script.src = '/static/inventory/js/voucher_filter_loader.js';
        document.head.appendChild(script);
        console.log('Added voucher filter loader to the page');
    }
})();
