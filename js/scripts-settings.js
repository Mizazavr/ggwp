document.addEventListener('DOMContentLoaded', function() {
    const settingItems = document.querySelectorAll('.setting-item');
    const resetButton = document.querySelector('.reset-button');
    const tg = window.Telegram.WebApp;

    // Expand Telegram WebApp
    tg.expand();
    tg.ready();

    // Handle setting item clicks
    settingItems.forEach(item => {
        item.addEventListener('click', function() {
            // Close other dropdowns
            settingItems.forEach(otherItem => {
                if (otherItem !== item && otherItem.classList.contains('active')) {
                    otherItem.classList.remove('active');
                }
            });
            
            // Toggle current dropdown
            this.classList.toggle('active');
        });

        // Handle dropdown item selection
        const dropdownItems = item.querySelectorAll('.dropdown-item');
        const currentValue = item.querySelector('.current-value');
        
        dropdownItems.forEach(dropdownItem => {
            dropdownItem.addEventListener('click', function(e) {
                e.stopPropagation();
                currentValue.textContent = this.textContent;
                item.classList.remove('active');
                
                // Save setting to localStorage
                const setting = item.dataset.setting;
                localStorage.setItem(setting, this.textContent);
            });
        });
    });

    // Handle reset button
    resetButton.addEventListener('click', function() {
        // Reset all settings to default
        const defaults = {
            'message-mode': 'Голосовые и текстовые',
            'speech-speed': '1.0X',
            'language-level': 'Не выбрано',
            'hints': 'Включены'
        };

        // Update UI and localStorage
        Object.entries(defaults).forEach(([setting, value]) => {
            const item = document.querySelector(`[data-setting="${setting}"]`);
            if (item) {
                const currentValue = item.querySelector('.current-value');
                if (currentValue) {
                    currentValue.textContent = value;
                }
                localStorage.setItem(setting, value);
            }
        });
    });

    // Load saved settings
    document.querySelectorAll('.setting-item').forEach(item => {
        const setting = item.dataset.setting;
        const savedValue = localStorage.getItem(setting);
        if (savedValue) {
            const currentValue = item.querySelector('.current-value');
            if (currentValue) {
                currentValue.textContent = savedValue;
            }
        }
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.setting-item')) {
            settingItems.forEach(item => {
                item.classList.remove('active');
            });
        }
    });
});
