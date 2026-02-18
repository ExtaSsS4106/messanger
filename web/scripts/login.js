class Login_page {
    get_data() {
        const username = document.getElementById('username')?.value || '';
        const password = document.getElementById('password')?.value || '';
        
        return { username, password };
    }

    init_page() {
        const btn = document.getElementById('submit-btn');
        
        btn.addEventListener('click', () => {
            const data = this.get_data();
            const response = eel.login(data.username, data.password)();
            if (response){
                loadPage("main");
            }
        });
    }
}