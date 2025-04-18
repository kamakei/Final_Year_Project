document.addEventListener('DOMContentLoaded', function() {
    // Get the "Get Started" button on home page
    const getStartedBtn = document.getElementById('get-started');
    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', function() {
            window.location.href = 'register.html';
        });
    }

    // Handle logout functionality
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Clear user data from localStorage
            localStorage.removeItem('user');
            // Redirect to login page
            window.location.href = 'login.html';
        });
    }

    // Check if user is logged in and handle page access
    function checkAuth() {
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
        const currentPage = window.location.pathname.split('/').pop();
        
        // Pages that require authentication
        const authPages = ['farmer_dashboard.html', 'trader_dashboard.html', 'admin_dashboard.html'];
        
        // If user tries to access dashboard without being logged in
        if (authPages.includes(currentPage) && !currentUser.id) {
            window.location.href = 'login.html';
            return;
        }

        // If logged-in user tries to access login/register pages
        if ((currentPage === 'login.html' || currentPage === 'register.html') && currentUser.id) {
            // Redirect to appropriate dashboard based on role
            switch(currentUser.role) {
                case 'farmer':
                    window.location.href = 'farmer_dashboard.html';
                    break;
                case 'trader':
                    window.location.href = 'trader_dashboard.html';
                    break;
                case 'admin':
                    window.location.href = 'admin_dashboard.html';
                    break;
            }
        }
    }

    // Run authentication check
    checkAuth();

    // Handle registration form
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate passwords match
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            
            if (password !== confirmPassword) {
                alert('Passwords do not match');
                return;
            }
            
            const formData = {
                username: document.getElementById('username').value,
                email: document.getElementById('email').value,
                password: password,
                role: document.getElementById('role').value,
                phone: document.getElementById('phone').value
            };
            
            fetch('http://localhost:5000/api/users/register', {
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
                    window.location.href = 'login.html';
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
            
            fetch('http://localhost:5000/api/users/login', {
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
                            window.location.href = 'farmer_dashboard.html';
                            break;
                        case 'trader':
                            window.location.href = 'trader_dashboard.html';
                            break;
                        case 'admin':
                            window.location.href = 'admin_dashboard.html';
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
});