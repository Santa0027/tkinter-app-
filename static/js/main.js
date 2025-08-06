// Main JavaScript for Folder Structure Manager

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Confirm delete actions
    $('.btn-delete').on('click', function(e) {
        e.preventDefault();
        var url = $(this).attr('href');
        var itemName = $(this).data('item-name') || 'this item';
        
        if (confirm('Are you sure you want to delete ' + itemName + '? This action cannot be undone.')) {
            window.location.href = url;
        }
    });

    // Form validation
    $('form').on('submit', function(e) {
        var form = $(this);
        var isValid = true;

        // Check required fields
        form.find('input[required], select[required], textarea[required]').each(function() {
            var field = $(this);
            if (!field.val().trim()) {
                field.addClass('is-invalid');
                isValid = false;
            } else {
                field.removeClass('is-invalid');
            }
        });

        if (!isValid) {
            e.preventDefault();
            showAlert('Please fill in all required fields.', 'danger');
        }
    });

    // Clear validation errors on input
    $('input, select, textarea').on('input change', function() {
        $(this).removeClass('is-invalid');
    });

    // Search functionality
    $('#searchInput').on('keyup', function() {
        var value = $(this).val().toLowerCase();
        $('#searchResults tbody tr').filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
    });

    // Loading spinner
    function showSpinner() {
        $('body').append('<div class="spinner-overlay"><div class="spinner-border spinner-border-lg text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>');
    }

    function hideSpinner() {
        $('.spinner-overlay').remove();
    }

    // AJAX form submission
    $('.ajax-form').on('submit', function(e) {
        e.preventDefault();
        var form = $(this);
        var url = form.attr('action');
        var method = form.attr('method') || 'POST';
        var data = form.serialize();

        showSpinner();

        $.ajax({
            url: url,
            method: method,
            data: data,
            success: function(response) {
                hideSpinner();
                if (response.success) {
                    showAlert(response.message || 'Operation completed successfully!', 'success');
                    if (response.redirect) {
                        setTimeout(function() {
                            window.location.href = response.redirect;
                        }, 1000);
                    }
                } else {
                    showAlert(response.message || 'An error occurred.', 'danger');
                }
            },
            error: function(xhr, status, error) {
                hideSpinner();
                showAlert('An error occurred: ' + error, 'danger');
            }
        });
    });

    // Show alert function
    function showAlert(message, type) {
        var alertHtml = '<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert">' +
                       message +
                       '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
                       '</div>';
        
        $('.container-fluid').prepend(alertHtml);
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            $('.alert').fadeOut('slow');
        }, 5000);
    }

    // Copy to clipboard functionality
    $('.copy-btn').on('click', function() {
        var text = $(this).data('copy-text');
        navigator.clipboard.writeText(text).then(function() {
            showAlert('Copied to clipboard!', 'success');
        });
    });

    // Dynamic form fields
    $('.add-field-btn').on('click', function() {
        var container = $(this).data('container');
        var template = $(this).data('template');
        var newField = $(template).clone();
        $(container).append(newField);
    });

    $('.remove-field-btn').on('click', function() {
        $(this).closest('.dynamic-field').remove();
    });

    // File upload preview
    $('input[type="file"]').on('change', function() {
        var file = this.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                var preview = $(this).siblings('.file-preview');
                if (file.type.startsWith('image/')) {
                    preview.html('<img src="' + e.target.result + '" class="img-thumbnail" style="max-width: 200px;">');
                } else {
                    preview.html('<p>File selected: ' + file.name + '</p>');
                }
            }.bind(this);
            reader.readAsDataURL(file);
        }
    });

    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        var target = $($(this).attr('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 100
            }, 500);
        }
    });

    // Back to top button
    $(window).scroll(function() {
        if ($(this).scrollTop() > 100) {
            $('#backToTop').fadeIn();
        } else {
            $('#backToTop').fadeOut();
        }
    });

    $('#backToTop').on('click', function() {
        $('html, body').animate({scrollTop: 0}, 500);
    });

    // Table row selection
    $('.selectable-row').on('click', function() {
        $(this).toggleClass('table-active');
        var checkbox = $(this).find('input[type="checkbox"]');
        checkbox.prop('checked', !checkbox.prop('checked'));
    });

    // Bulk actions
    $('#selectAll').on('change', function() {
        var isChecked = $(this).prop('checked');
        $('.row-checkbox').prop('checked', isChecked);
        $('.selectable-row').toggleClass('table-active', isChecked);
    });

    $('.row-checkbox').on('change', function() {
        var totalCheckboxes = $('.row-checkbox').length;
        var checkedCheckboxes = $('.row-checkbox:checked').length;
        $('#selectAll').prop('checked', totalCheckboxes === checkedCheckboxes);
    });

    // Responsive table wrapper
    $('.table-responsive').each(function() {
        if ($(this).find('table').width() > $(this).width()) {
            $(this).addClass('table-scroll');
        }
    });

    // Initialize any additional components
    initializeComponents();
});

// Initialize additional components
function initializeComponents() {
    // Add any additional initialization code here
    console.log('Folder Structure Manager initialized');
}

// Utility functions
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}
