document.addEventListener('DOMContentLoaded', function() {
    // Get the "Get Started" button on home page
    const getStartedBtn = document.getElementById('get-started');
    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', function() {
            window.location.href = '/register';
        });
    }

    // Handle registration form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate passwords match
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password')?.value;
            
            if (confirmPassword && password !== confirmPassword) {
                alert('Passwords do not match');
                return;
            }
            
            const formData = {
                username: document.getElementById('username').value,
                email: document.getElementById('email').value,
                password: password,
                role: document.getElementById('role').value,
                phone: document.getElementById('phone')?.value || '0000000000'
            };
            
            fetch('/api/users/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Registration successful! Please log in.');
                    window.location.href = '/login';
                } else {
                    alert('Registration failed: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred during registration.');
            });
        });
    }

    // Handle login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                username: document.getElementById('username').value,
                password: document.getElementById('password').value,
                role: document.getElementById('role').value
            };
            
            fetch('/api/users/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    localStorage.setItem('user', JSON.stringify(data.user));
                    
                    switch(data.user.role) {
                        case 'farmer':
                            window.location.href = '/farmer-dashboard';
                            break;
                        case 'trader':
                            window.location.href = '/trader-dashboard';
                            break;
                        case 'admin':
                            window.location.href = '/admin-dashboard';
                            break;
                    }
                } else {
                    alert('Login failed: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred during login.');
            });
        });
    }

    // Logout functionality
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            localStorage.removeItem('user');
            window.location.href = '/login';
        });
    }
    
    // Check if user is logged in and redirect appropriately
    function checkAuth() {
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
        const path = window.location.pathname;
        
        if (path === '/farmer-dashboard' && (!currentUser.id || currentUser.role !== 'farmer')) {
            window.location.href = '/login';
        }
        else if (path === '/trader-dashboard' && (!currentUser.id || currentUser.role !== 'trader')) {
            window.location.href = '/login';
        }
        else if (path === '/admin-dashboard' && (!currentUser.id || currentUser.role !== 'admin')) {
            window.location.href = '/login';
        }
        else if ((path === '/login' || path === '/register') && currentUser.id) {
            // Redirect to appropriate dashboard if already logged in
            switch(currentUser.role) {
                case 'farmer':
                    window.location.href = '/farmer-dashboard';
                    break;
                case 'trader':
                    window.location.href = '/trader-dashboard';
                    break;
                case 'admin':
                    window.location.href = '/admin-dashboard';
                    break;
            }
        }
    }
    
    // Run auth check
    checkAuth();
});