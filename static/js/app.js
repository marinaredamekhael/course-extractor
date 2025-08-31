// Course Extractor Frontend Application



class CourseExtractorApp {
    constructor() {
        this.currentResults = null;
        this.processingHistory = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadHistory();
        this.setupNavigation();
    }

    bindEvents() {
        // Form submission
        document.getElementById('extractForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.extractCourses();
        });

        // Multiple URLs functionality
        document.getElementById('addMultipleUrlsBtn').addEventListener('click', () => {
            this.toggleMultipleUrls();
        });

        // Export buttons
        document.getElementById('exportCsvBtn').addEventListener('click', () => {
            this.exportData('csv');
        });

        document.getElementById('exportExcelBtn').addEventListener('click', () => {
            this.exportData('excel');
        });

        // URL input changes
        document.getElementById('urlInput').addEventListener('input', (e) => {
            this.validateUrl(e.target.value);
        });
    }

    setupNavigation() {
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getHash());
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Active navigation highlighting
        window.addEventListener('scroll', () => {
            this.updateActiveNavigation();
        });
    }

    getHash() {
        return this.getAttribute('href');
    }

    updateActiveNavigation() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.nav-link');

        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    }

    validateUrl(url) {
        const urlInput = document.getElementById('urlInput');
        const extractBtn = document.getElementById('extractBtn');
        
        try {
            new URL(url);
            urlInput.classList.remove('is-invalid');
            urlInput.classList.add('is-valid');
            extractBtn.disabled = false;
        } catch {
            if (url.length > 0) {
                urlInput.classList.remove('is-valid');
                urlInput.classList.add('is-invalid');
                extractBtn.disabled = true;
            } else {
                urlInput.classList.remove('is-valid', 'is-invalid');
                extractBtn.disabled = false;
            }
        }
    }

    toggleMultipleUrls() {
        const container = document.getElementById('multipleUrlsContainer');
        const btn = document.getElementById('addMultipleUrlsBtn');
        
        if (container.style.display === 'none') {
            container.style.display = 'block';
            btn.innerHTML = '<i class="fas fa-minus me-2"></i>Hide Multiple URLs';
            this.addUrlInputRow();
        } else {
            container.style.display = 'none';
            btn.innerHTML = '<i class="fas fa-plus me-2"></i>Add Multiple URLs';
        }
    }

    addUrlInputRow() {
        const container = document.getElementById('multipleUrlsContainer');
        const row = document.createElement('div');
        row.className = 'url-input-row mb-2';
        row.innerHTML = `
            <div class="input-group">
                <input type="url" class="form-control url-input" placeholder="Enter URL">
                <button class="btn btn-outline-danger remove-url-btn" type="button">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        // Add remove button functionality
        row.querySelector('.remove-url-btn').addEventListener('click', () => {
            row.remove();
        });

        container.appendChild(row);
    }

    async extractCourses() {
        const urlInput = document.getElementById('urlInput');
        const mainUrl = urlInput.value.trim();
        
        if (!mainUrl) {
            this.showError('Please enter a valid URL');
            return;
        }

        // Collect all URLs (main + multiple)
        const urls = [mainUrl];
        const multipleInputs = document.querySelectorAll('.url-input');
        multipleInputs.forEach(input => {
            if (input.value.trim()) {
                urls.push(input.value.trim());
            }
        });

        // Show loading modal
        this.showLoadingModal();

        try {
            const response = await fetch('/api/extract', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ urls: urls })
            });

            const data = await response.json();

            if (response.ok) {
                this.handleExtractionSuccess(data);
            } else {
                this.showError(data.error || 'Failed to extract courses');
            }
        } catch (error) {
            console.error('Extraction error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.hideLoadingModal();
        }
    }

    handleExtractionSuccess(data) {
        this.currentResults = data;
        
        // Update statistics
        this.updateStatistics(data);
        
        // Display results
        this.displayResults(data);
        
        // Add to history
        this.addToHistory(data);
        
        // Show results section
        document.getElementById('results').style.display = 'block';
        
        // Scroll to results
        document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        
        // Show success message
        this.showSuccessMessage(`Successfully extracted ${data.total_courses} courses from ${data.results.length} website(s)`);
    }

    updateStatistics(data) {
        const courses = this.flattenCourses(data.results);
        
        // Count unique values
        const institutes = new Set(courses.map(c => c.institute_name).filter(name => name !== 'Not Available'));
        const locations = new Set(courses.map(c => c.location).filter(loc => loc !== 'Not Available'));
        const formats = new Set(courses.map(c => c.format).filter(fmt => fmt !== 'Not Available'));

        document.getElementById('totalCourses').textContent = data.total_courses;
        document.getElementById('totalInstitutes').textContent = institutes.size;
        document.getElementById('totalLocations').textContent = locations.size;
        document.getElementById('totalFormats').textContent = formats.size;
    }

    flattenCourses(results) {
        const courses = [];
        results.forEach(result => {
            if (result.success && result.courses) {
                courses.push(...result.courses);
            }
        });
        return courses;
    }

    displayResults(data) {
        const tableBody = document.getElementById('resultsTableBody');
        const noResultsMessage = document.getElementById('noResultsMessage');
        
        if (data.total_courses === 0) {
            tableBody.innerHTML = '';
            noResultsMessage.style.display = 'block';
            return;
        }

        noResultsMessage.style.display = 'none';
        tableBody.innerHTML = '';

        data.results.forEach(result => {
            if (result.success && result.courses) {
                result.courses.forEach(course => {
                    const row = this.createCourseRow(course, result.url);
                    tableBody.appendChild(row);
                });
            }
        });
    }

    createCourseRow(course, sourceUrl) {
        const row = document.createElement('tr');
        row.className = 'fade-in';
        
        row.innerHTML = `
            <td><strong>${this.escapeHtml(course.course_name)}</strong></td>
            <td>${this.escapeHtml(course.institute_name)}</td>
            <td>${this.escapeHtml(course.location)}</td>
            <td><span class="badge bg-info">${this.escapeHtml(course.format)}</span></td>
            <td>${this.escapeHtml(course.faculty)}</td>
            <td>${this.escapeHtml(course.language)}</td>
            <td>${this.escapeHtml(course.dates)}</td>
            <td>${this.escapeHtml(course.duration)}</td>
            <td>${this.escapeHtml(course.suitable_for)}</td>
            <td><span class="badge bg-success">${this.escapeHtml(course.fees)}</span></td>
            <td><span class="badge bg-warning">${this.escapeHtml(course.availability)}</span></td>
            <td><a href="${sourceUrl}" target="_blank" class="text-truncate d-inline-block" style="max-width: 150px;" title="${sourceUrl}">${this.escapeHtml(sourceUrl)}</a></td>
            <td>
                <button class="btn btn-sm btn-outline-primary" type="button">Details</button>
            </td>
        `;

        // Bind details button
        row.querySelector('button').addEventListener('click', () => {
            this.showDetailsModal(course, sourceUrl);
        });

        return row;
    }

    showDetailsModal(course, sourceUrl) {
        const content = document.getElementById('detailsContent');
        const fields = [
            ['Course Name', course.course_name],
            ['Institute', course.institute_name],
            ['Location', course.location],
            ['Format', course.format],
            ['Faculty', course.faculty],
            ['Language', course.language],
            ['Dates', course.dates],
            ['Duration', course.duration],
            ['Suitable For', course.suitable_for],
            ['Fees', course.fees],
            ['Availability', course.availability],
            ['Source URL', `<a href="${sourceUrl}" target="_blank">${this.escapeHtml(sourceUrl)}</a>`]
        ];
        content.innerHTML = `
            <div class="table-responsive">
                <table class="table table-bordered">
                    <tbody>
                        ${fields.map(([k,v]) => `
                            <tr>
                                <th style="width: 180px;">${k}</th>
                                <td>${v || 'Not Available'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        new bootstrap.Modal(document.getElementById('detailsModal')).show();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    addToHistory(data) {
        const historyItem = {
            timestamp: new Date().toISOString(),
            urls: data.results.map(r => r.url),
            totalCourses: data.total_courses,
            success: data.total_courses > 0
        };

        this.processingHistory.unshift(historyItem);
        
        // Keep only last 10 items
        if (this.processingHistory.length > 10) {
            this.processingHistory = this.processingHistory.slice(0, 10);
        }

        this.saveHistory();
        this.updateHistoryDisplay();
    }

    updateHistoryDisplay() {
        const container = document.getElementById('historyContainer');
        
        if (this.processingHistory.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-clock fa-3x mb-3"></i>
                    <p>No processing history yet. Start by extracting courses from a website.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.processingHistory.map(item => `
            <div class="history-item slide-in">
                <div class="row align-items-center">
                    <div class="col-md-6">
                        <div class="d-flex align-items-center mb-2">
                            <span class="status ${item.success ? 'success' : 'error'} me-2">
                                ${item.success ? 'Success' : 'No Courses Found'}
                            </span>
                            <span class="timestamp">${this.formatTimestamp(item.timestamp)}</span>
                        </div>
                        <div class="urls">
                            ${item.urls.map(url => `
                                <a href="${url}" target="_blank" class="url d-block mb-1">
                                    <i class="fas fa-external-link-alt me-1"></i>
                                    ${this.truncateUrl(url)}
                                </a>
                            `).join('')}
                        </div>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <div class="course-count">
                            <strong>${item.totalCourses}</strong> courses extracted
                        </div>
                        <button class="btn btn-sm btn-outline-primary mt-2" onclick="app.reprocessHistoryItem('${item.timestamp}')">
                            <i class="fas fa-redo me-1"></i>
                            Reprocess
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    truncateUrl(url) {
        try {
            const urlObj = new URL(url);
            return urlObj.hostname + urlObj.pathname.substring(0, 30) + (urlObj.pathname.length > 30 ? '...' : '');
        } catch {
            return url.length > 50 ? url.substring(0, 50) + '...' : url;
        }
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        
        return date.toLocaleDateString();
    }

    async reprocessHistoryItem(timestamp) {
        const item = this.processingHistory.find(h => h.timestamp === timestamp);
        if (!item) return;

        // Set URLs in the form
        document.getElementById('urlInput').value = item.urls[0] || '';
        
        // Clear multiple URLs
        document.getElementById('multipleUrlsContainer').innerHTML = '';
        document.getElementById('multipleUrlsContainer').style.display = 'none';
        document.getElementById('addMultipleUrlsBtn').innerHTML = '<i class="fas fa-plus me-2"></i>Add Multiple URLs';

        // Add additional URLs if any
        item.urls.slice(1).forEach(url => {
            this.toggleMultipleUrls();
            const lastInput = document.querySelector('.url-input:last-child');
            if (lastInput) lastInput.value = url;
        });

        // Extract courses
        await this.extractCourses();
    }

    async exportData(format) {
        if (!this.currentResults) {
            this.showError('No data to export. Please extract courses first.');
            return;
        }

        try {
            const response = await fetch(`/api/export/${format}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ results: this.currentResults.results })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `courses_export_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showSuccessMessage(`${format.toUpperCase()} export completed successfully!`);
            } else {
                const error = await response.json();
                this.showError(error.error || `Failed to export ${format.toUpperCase()}`);
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showError(`Failed to export ${format.toUpperCase()}. Please try again.`);
        }
    }

    showLoadingModal() {
        const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
        modal.show();
    }

    hideLoadingModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
        if (modal) modal.hide();
    }

    showError(message) {
        document.getElementById('errorMessage').textContent = message;
        const modal = new bootstrap.Modal(document.getElementById('errorModal'));
        modal.show();
    }

    showSuccessMessage(message) {
        // Create a temporary success toast
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0 position-fixed';
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check-circle me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            document.body.removeChild(toast);
        });
    }

    saveHistory() {
        try {
            localStorage.setItem('courseExtractorHistory', JSON.stringify(this.processingHistory));
        } catch (error) {
            console.warn('Failed to save history to localStorage:', error);
        }
    }

    loadHistory() {
        try {
            const saved = localStorage.getItem('courseExtractorHistory');
            if (saved) {
                this.processingHistory = JSON.parse(saved);
                this.updateHistoryDisplay();
            }
        } catch (error) {
            console.warn('Failed to load history from localStorage:', error);
        }
    }

    // Utility method to clear history
    clearHistory() {
        this.processingHistory = [];
        this.saveHistory();
        this.updateHistoryDisplay();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CourseExtractorApp();
});

// Add some utility functions to the global scope
window.utils = {
    // Format currency
    formatCurrency: (amount) => {
        if (!amount || amount === 'Not Available') return amount;
        const num = parseFloat(amount.replace(/[^\d.-]/g, ''));
        if (isNaN(num)) return amount;
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(num);
    },

    // Format duration
    formatDuration: (duration) => {
        if (!duration || duration === 'Not Available') return duration;
        return duration.replace(/(\d+)\s*(\w+)/g, '$1 $2');
    },

    // Copy to clipboard
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (error) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return true;
        }
    }
};

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.getElementById('extractForm');
        if (form) {
            e.preventDefault();
            form.dispatchEvent(new Event('submit'));
        }
    }

    // Escape to close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();
        });
    }
});

// Add service worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
