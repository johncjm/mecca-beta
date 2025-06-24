def load_custom_styles():
    """Load custom CSS and JavaScript for MECCA interface"""
    return """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .about-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #1f77b4;
    }
    .learn-more-inline {
        display: inline-block;
        margin-left: 10px;
        vertical-align: top;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
        margin-top: 1rem;
    }
    .radio-group {
        font-size: 0.9rem;
        color: #666;
    }
    .custom-context-container {
        margin-top: 1rem;
    }
    .fact-check-warning {
        font-style: italic;
        color: #d63384;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }
    .word-limit-notice {
        background-color: #e7f3ff;
        padding: 0.8rem;
        border-radius: 6px;
        border-left: 3px solid #1f77b4;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
    .eic-summary {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    .dialogue-section {
        background-color: #e8f5e8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    .ai-disclaimer {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
    .chat-message {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .user-message {
        background-color: #e3f2fd;
        text-align: right;
    }
    .eic-message {
        background-color: #f1f8e9;
    }
    .specialist-columns {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 20px;
        max-height: 600px;
    }
    .specialist-column {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        overflow-y: auto;
        background-color: #ffffff;
    }
    .specialist-column h4 {
        margin-top: 0;
        color: #1f77b4;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 0.5rem;
    }
    .search-bar {
        width: 100%;
        padding: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #ced4da;
        border-radius: 4px;
    }
    /* Improve tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border-bottom: 3px solid #1f77b4;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }
    
    /* EiC Toggle Styles */
    .eic-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e9ecef;
    }
    
    .eic-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin: 0;
    }
    
    .eic-toggle {
        display: flex;
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 4px;
        border: 1px solid #dee2e6;
    }
    
    .eic-toggle-btn {
        padding: 8px 16px;
        border: none;
        background: transparent;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #6c757d;
    }
    
    .eic-toggle-btn.active {
        background-color: #ffffff;
        color: #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .eic-toggle-btn:hover:not(.active) {
        color: #495057;
        background-color: #e9ecef;
    }
    
    /* Content visibility classes */
    .eic-full-content {
        display: block;
    }
    
    .eic-condensed-content {
        display: none;
    }
    
    .view-quick-fixes .eic-full-content {
        display: none;
    }
    
    .view-quick-fixes .eic-condensed-content {
        display: block;
    }
    
    /* Quick fixes styling */
    .quick-fixes-summary {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    
    .error-count-overview {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
    
    .quick-fix-item {
        padding: 0.5rem 0;
        border-bottom: 1px solid #e9ecef;
    }
    
    .quick-fix-item:last-child {
        border-bottom: none;
    }
    
    .fix-severity {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 8px;
    }
    
    .severity-critical {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    .severity-high {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .severity-medium {
        background-color: #d1ecf1;
        color: #0c5460;
    }
</style>

<script>
function toggleEiCView(mode) {
    const container = document.querySelector('.eic-container');
    const buttons = document.querySelectorAll('.eic-toggle-btn');
    
    // Remove active class from all buttons
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Add active class to clicked button
    const targetBtn = document.querySelector(`[data-mode="${mode}"]`);
    if (targetBtn) {
        targetBtn.classList.add('active');
    }
    
    // Toggle container class
    if (mode === 'quick') {
        container.classList.add('view-quick-fixes');
    } else {
        container.classList.remove('view-quick-fixes');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Set default view to full analysis
    setTimeout(function() {
        const fullBtn = document.querySelector('[data-mode="full"]');
        if (fullBtn) {
            fullBtn.classList.add('active');
        }
    }, 100);
});
</script>
"""
