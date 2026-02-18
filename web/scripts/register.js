class Register_page {
    get_data() {
        const username = document.getElementById('username')?.value || '';
        const email = document.getElementById('email')?.value || '';
        const password1 = document.getElementById('password1')?.value || '';
        const password2 = document.getElementById('password2')?.value || '';
        
        return { username, email, password1, password2 };
    }

    init_page() {
        const btn = document.getElementById('submit-btn');
        
        btn.addEventListener('click', () => {
            const data = this.get_data();
            eel.sign_up(data.username, data.email, data.password1, data.password2)();
        });
    }
}