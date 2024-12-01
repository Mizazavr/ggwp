const tg = window.Telegram.WebApp;

function getTelegramId() {
    // First try to get ID from Telegram WebApp
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user) {
        return window.Telegram.WebApp.initDataUnsafe.user.id.toString();
    }
    
    // Then try URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const telegramId = urlParams.get('telegram_id');
    if (telegramId) {
        return telegramId;
    }
    
    // For development/testing, return a demo ID
    if (window.location.hostname === 'localhost' || window.location.hostname.includes('replit')) {
        const demoId = '12345';
        console.info('Using demo telegram_id for development:', demoId);
        return demoId;
    }
    
    // If we reach here, we couldn't get the telegram_id
    console.info('No telegram user data available, waiting for WebApp initialization');
    return null;
}

async function fetchUserStats() {
    try {
        const telegramId = getTelegramId();
        if (!telegramId) {
            console.error('No telegram_id provided');
            return;
        }
        const response = await fetch(`/api/stats?telegram_id=${telegramId}`);
        const stats = await response.json();
        updateStatsDisplay(stats);
        updateReferralLink(telegramId);
    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

async function fetchUserProfile() {
    try {
        const telegramId = getTelegramId();
        if (!telegramId) {
            console.error('No telegram_id provided');
            return;
        }
        const response = await fetch(`/api/profile?telegram_id=${telegramId}`);
        const profile = await response.json();
        updateProfileDisplay(profile);
    } catch (error) {
        console.error('Error fetching profile:', error);
    }
}

function updateReferralLink(telegramId) {
    const inviteLink = document.getElementById('invite-link');
    if (!inviteLink) return;
    
    if (!telegramId) {
        inviteLink.textContent = 'Please open the application through Telegram';
        return;
    }
    
    const botUsername = 'Speakadora_bot';
    const botLink = `https://t.me/${botUsername}?start=ref${telegramId}`;
    inviteLink.href = botLink;
    inviteLink.textContent = 'Click to copy your referral link';
    
    // Copy link on click
    inviteLink.addEventListener('click', function(e) {
        e.preventDefault();
        navigator.clipboard.writeText(botLink).then(() => {
            tg.showPopup({
                title: 'Link Copied!',
                message: 'Share this link with your friends to invite them'
            });
        }).catch(() => {
            // Fallback if clipboard API fails
            inviteLink.select();
            document.execCommand('copy');
            tg.showPopup({
                title: 'Link Copied!',
                message: 'Share this link with your friends to invite them'
            });
        });
    });
}

function updateStatsDisplay(stats) {
    document.querySelector('[data-stats="talk-today"]').textContent = `- Today: ${stats.talk_time.today} min.`;
    document.querySelector('[data-stats="talk-weekly"]').textContent = `- Weekly: ${stats.talk_time.weekly} min.`;
    document.querySelector('[data-stats="talk-total"]').textContent = `- Total: ${stats.talk_time.total} min.`;
    document.querySelector('[data-stats="listened"]').textContent = `🎯 Listened Time: ${stats.listened_time} min. of English speech`;
    document.querySelector('[data-stats="days"]').textContent = `⏰ Total Days Engaged: ${stats.days_engaged} days`;
    document.querySelector('.level').textContent = `lvl ${stats.level} ⭐`;
    document.querySelector('.account-status').textContent = `ACCOUNT STATUS ${stats.account_status}`;
    
    // Update referral count
    const invitedFriendsText = document.querySelector('.gift-section div:last-child');
    invitedFriendsText.textContent = `👥 You have invited ${stats.invited_friends} friends`;
    
    // Update premium progress
    const premiumProgress = document.querySelector('.gift-section div:nth-child(2)');
    const remainingInvites = 10 - stats.invited_friends;
    if (stats.account_status === 'PREMIUM') {
        premiumProgress.textContent = '🎉 Congratulations! You have earned Premium status! 🎉';
    } else {
        premiumProgress.textContent = `Invite ${remainingInvites} more friend${remainingInvites !== 1 ? 's' : ''} who reach level 5 to get Premium subscription`;
    }

    // Update achievements page if it exists
    const achievementsGrid = document.querySelector('.achievements-grid');
    if (achievementsGrid) {
        const referralMilestones = [1, 5, 10, 20];
        const referralCards = achievementsGrid.querySelectorAll('.achievement-card');
        
        referralCards.forEach((card, index) => {
            if (index < referralMilestones.length) {
                const milestone = referralMilestones[index];
                const progress = card.querySelector('.progress');
                if (progress) {
                    progress.textContent = `${Math.min(stats.invited_friends, milestone)}/${milestone}`;
                    if (stats.invited_friends >= milestone) {
                        card.classList.add('completed');
                    }
                }
            }
        });
    }
}

function updateProfileDisplay(profile) {
    const userNameElement = document.getElementById('user-name');
    if (!userNameElement) return;
    
    // Получаем имя из Telegram WebApp если доступно
    const telegramUser = window.Telegram.WebApp.initDataUnsafe.user;
    const userName = telegramUser?.username || profile.name || 'Student';
    
    userNameElement.textContent = userName;
    
    const profilePic = document.querySelector('.profile-pic');
    if (profilePic && profile.avatar) {
        profilePic.src = profile.avatar;
    }
}

// Initialize Telegram WebApp
tg.expand();
tg.ready();

function addTelegramIdToLinks() {
    const telegramId = getTelegramId();
    if (!telegramId) return;
    
    const premiumLinks = document.querySelectorAll('.premium-button a');
    premiumLinks.forEach(link => {
        const currentHref = link.getAttribute('href');
        link.href = `${currentHref}?telegram_id=${telegramId}`;
    });
}

// Load data when page loads
document.addEventListener('DOMContentLoaded', () => {
    fetchUserStats();
    fetchUserProfile();
    addTelegramIdToLinks();
    
    // Get telegram_id from URL
    const telegramId = getTelegramId();
    if (telegramId) {
        // Update profile on achievements page
        const userNameElement = document.getElementById('user-name');
        if (userNameElement) {
            const telegramUser = window.Telegram.WebApp.initDataUnsafe.user;
            const userName = telegramUser?.username || 'Student';
            userNameElement.textContent = userName;
        }
    }
});
