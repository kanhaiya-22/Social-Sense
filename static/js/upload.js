// Upload functionality for Social Media Content Analyzer

document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const fileInfo = document.getElementById('fileInfo');
    const processingStatus = document.getElementById('processingStatus');
    
    let selectedFile = null;

    // File type icons mapping
    const fileIcons = {
        'pdf': 'fas fa-file-pdf text-danger',
        'png': 'fas fa-file-image text-success',
        'jpg': 'fas fa-file-image text-success',
        'jpeg': 'fas fa-file-image text-success'
    };

    // Initialize drag and drop
    initializeDragAndDrop();
    
    // File input change handler
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    // Form submit handler
    uploadForm.addEventListener('submit', function(e) {
        if (!selectedFile) {
            e.preventDefault();
            showAlert('Please select a file first.', 'warning');
            return;
        }
        
        showProcessingStatus();
    });

    function initializeDragAndDrop() {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        // Handle dropped files
        dropZone.addEventListener('drop', handleDrop, false);
        
        // Click to select file
        dropZone.addEventListener('click', function() {
            fileInput.click();
        });
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        dropZone.classList.add('drag-over');
    }

    function unhighlight() {
        dropZone.classList.remove('drag-over');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    }

    function handleFileSelection(file) {
        // Validate file type
        const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
        if (!allowedTypes.includes(file.type)) {
            showAlert('Invalid file type. Please select a PDF, PNG, or JPG file.', 'danger');
            return;
        }

        // Validate file size (16MB limit)
        const maxSize = 16 * 1024 * 1024; // 16MB in bytes
        if (file.size > maxSize) {
            showAlert('File is too large. Maximum size is 16MB.', 'danger');
            return;
        }

        selectedFile = file;
        displayFileInfo(file);
        enableAnalyzeButton();
    }

    function displayFileInfo(file) {
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const fileIcon = document.getElementById('fileIcon');
        
        // Update file info
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        
        // Update file icon based on extension
        const extension = file.name.split('.').pop().toLowerCase();
        const iconClass = fileIcons[extension] || 'fas fa-file text-secondary';
        fileIcon.className = iconClass + ' fa-2x me-3';
        
        // Show file info and hide drop zone content
        fileInfo.classList.remove('d-none');
        dropZone.querySelector('.drop-zone-content').style.display = 'none';
        dropZone.style.padding = '0';
        dropZone.style.border = 'none';
        dropZone.appendChild(fileInfo);
    }

    function clearFile() {
        selectedFile = null;
        fileInput.value = '';
        
        // Reset UI
        fileInfo.classList.add('d-none');
        dropZone.querySelector('.drop-zone-content').style.display = 'block';
        dropZone.style.padding = '3rem 2rem';
        dropZone.style.border = '2px dashed var(--bs-border-color)';
        document.querySelector('.card-body').appendChild(fileInfo);
        
        disableAnalyzeButton();
    }

    function enableAnalyzeButton() {
        analyzeBtn.disabled = false;
        analyzeBtn.classList.remove('btn-secondary');
        analyzeBtn.classList.add('btn-info');
    }

    function disableAnalyzeButton() {
        analyzeBtn.disabled = true;
        analyzeBtn.classList.remove('btn-info');
        analyzeBtn.classList.add('btn-secondary');
    }

    function showProcessingStatus() {
        // Hide form and show processing status
        uploadForm.style.display = 'none';
        processingStatus.classList.remove('d-none');
        
        // Scroll to processing status
        processingStatus.scrollIntoView({ behavior: 'smooth' });
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'danger' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert alert at the top of the container
        const container = document.querySelector('.container');
        const firstRow = container.querySelector('.row');
        container.insertBefore(alertDiv, firstRow);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // Make clearFile function globally available
    window.clearFile = clearFile;

    // Progress simulation for better UX
    function simulateProgress() {
        const progressBar = document.querySelector('.progress-bar');
        if (!progressBar) return;

        let width = 0;
        const interval = setInterval(() => {
            width += Math.random() * 15;
            if (width >= 90) {
                clearInterval(interval);
                width = 90; // Stop at 90% to show actual processing
            }
            progressBar.style.width = width + '%';
        }, 500);
    }

    // Start progress simulation when form is submitted
    uploadForm.addEventListener('submit', function() {
        setTimeout(simulateProgress, 100);
    });
});

// Utility function to copy text to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function() {
            showCopyFeedback('Text copied to clipboard!');
        }).catch(function(err) {
            console.error('Failed to copy text: ', err);
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

// Fallback for older browsers or non-HTTPS contexts
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopyFeedback('Text copied to clipboard!');
    } catch (err) {
        console.error('Fallback copy failed: ', err);
        showCopyFeedback('Failed to copy text', 'danger');
    } finally {
        textArea.remove();
    }
}

// Show copy feedback
function showCopyFeedback(message, type = 'success') {
    // Create toast or alert for feedback
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 250px;';
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : 'exclamation-circle'} me-2"></i>
        ${message}
    `;
    
    document.body.appendChild(toast);
    
    // Add fade in animation
    setTimeout(() => toast.classList.add('fade-in'), 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
