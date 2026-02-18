       // Данные пользователей
        let users = [
            {id: 1234, name: 'User#1234', lastMessage: 'Привет!', time: '12:05'},
            {id: 4321, name: 'User#4321', lastMessage: 'Как дела?', time: '11:30'},
            {id: 1243, name: 'User#1243', lastMessage: 'Го в встречу', time: 'Вчера'},
            {id: 2134, name: 'User#2134', lastMessage: 'Ок', time: 'Вчера'},
            {id: 3142, name: 'User#3142', lastMessage: 'Привет', time: '20 янв'},
            {id: 3142, name: 'User#3142', lastMessage: 'Привет', time: '20 янв'},
            {id: 3142, name: 'User#3142', lastMessage: 'Привет', time: '20 янв'},
            {id: 3142, name: 'User#3142', lastMessage: 'Привет', time: '20 янв'},
            {id: 3142, name: 'User#3142', lastMessage: 'Привет', time: '20 янв'},
            {id: 3142, name: 'User#3142', lastMessage: 'Привет', time: '20 янв'},
            {id: 3142, name: 'User#3142', lastMessage: 'Привет', time: '20 янв'},
            {id: 3142, name: 'User#3142', lastMessage: 'Привет', time: '20 янв'},
            {id: 3142, name: 'User#3142', lastMessage: 'Привет', time: '20 янв'},
            {id: 3142, name: 'User#3142', lastMessage: 'Привет', time: '20 янв'},
            {id: 3142, name: 'User#3142', lastMessage: 'Привет', time: '20 янв'},
            {id: 123456, name: 'Exti'},
            {id: 654321, name: 'kitro'},
            {id: 789012, name: 'Exti4106'}
        ];
        
        let friends = [
            {id: 123456, name: 'Exti'},
            {id: 654321, name: 'kitro'},
            {id: 789012, name: 'Exti4106'}
        ];
        
        // Отображение чатов
        function displayChats(filter = '') {
            const container = document.getElementById('chatsList');
            container.innerHTML = '';
            
            let filteredUsers = users.filter(u => u.name.toLowerCase().includes(filter.toLowerCase()));
            
            filteredUsers.forEach(user => {
                const userDiv = document.createElement('div');
                userDiv.className = 'user-item';
                userDiv.onclick = () => window.location.href = `chat.html?user=${user.id}`;
                userDiv.innerHTML = `
                    <div class="user-avatar"></div>
                    <span class="user-name">${user.name}</span>
                `;
                container.appendChild(userDiv);
            });
        }
        
        // Отображение друзей
        function displayFriends(filter = '') {
            const container = document.getElementById('chatsList');
            container.innerHTML = '';
            
            let filteredFriends = friends.filter(f => f.name.toLowerCase().includes(filter.toLowerCase()));
            
            filteredFriends.forEach(friend => {
                const friendDiv = document.createElement('div');
                friendDiv.className = 'user-item';
                friendDiv.onclick = () => window.location.href = `chat.html?user=${friend.id}`;
                friendDiv.innerHTML = `
                    <div class="user-avatar"></div>
                    <span class="user-name">${friend.name}</span>
                `;
                container.appendChild(friendDiv);
            });
        }
        
        // Переключение между вкладками
        function switchTab(tab) {
            const chatsTab = document.getElementById('chatsTab');
            const friendsTab = document.getElementById('friendsTab');
            const chatsList = document.getElementById('chatsList');
            
            if (tab === 'chats') {
                chatsTab.classList.add('active');
                friendsTab.classList.remove('active');
                chatsList.style.display = 'block';
                displayChats();
            } else {
                friendsTab.classList.add('active');
                chatsTab.classList.remove('active');
                displayFriends();
            }
        }
        
        // Поиск
        function searchUsers() {
            const filter = document.getElementById('searchInput').value;
            const friendsTab = document.getElementById('friendsTab');
            const chatsList = document.getElementById('chatsList');
            friendsTab.classList.remove('active');
            chatsTab.classList.remove('active');
            displayChats(filter);
        }
        
