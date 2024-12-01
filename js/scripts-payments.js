document.addEventListener('DOMContentLoaded', function() {


    const monthlyOption = document.querySelector('.payment-option:nth-child(1)');
    const yearlyOption = document.querySelector('.payment-option:nth-child(2)');
    const upgradeButton = document.querySelector('.upgrade-now-btn');

    let selectedPlan = 'monthly';

    monthlyOption.addEventListener('click', function() {
        monthlyOption.classList.add('active');
        yearlyOption.classList.remove('active');
        selectedPlan = 'monthly';
    });

    yearlyOption.addEventListener('click', function() {
        yearlyOption.classList.add('active');
        monthlyOption.classList.remove('active');
        selectedPlan = 'yearly';
    });

    upgradeButton.addEventListener('click', function() {
        const userData = {
            user_id: tg.initDataUnsafe?.user?.id || 'demo_user',
            plan: selectedPlan
        };

        fetch('/upgrade_account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Account upgraded successfully!');
                window.location.href = '/';
            } else {
                alert('Error upgrading account: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error upgrading account:', error);
            alert('An error occurred while upgrading your account. Please try again.');
        });
    });

    document.querySelector('.close-btn').addEventListener('click', function(e) {
        e.preventDefault();
        window.location.href = '/';
    });
});
