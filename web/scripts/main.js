    let activeChatId = null;
    function getChatIdFromUrl() {
        const params = new URLSearchParams(window.location.search);
        return params.get('user');
    }

        let messages=[]
        let currentUser = '';
        let usr_email = '';

        function renderMessages(messages) {
            const container = document.getElementById('messagesContainer');
            container.innerHTML = '';

            messages.forEach(msg => {
                const div = document.createElement('div');
                div.className = msg.user === currentUser
                    ? 'message-right'
                    : 'message-left';
                div.innerHTML = `
                    <div>${msg.user}</div>
                    <div class="message-text">${msg.text}</div>
                `;
                container.appendChild(div);
            });
            container.scrollTop = container.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            if (!input.value || !activeChatId) return;
            
            const mess = ({
                count: messages.length + 1,
                chat: activeChatId,
                user: currentUser,
                email: usr_email,
                text: input.value,
                type: 'text',
                file: ''
            });

            console.log(mess);
            messages.push(mess);

            await eel.send_message(mess)();

            input.value = '';
            loadMessages(activeChatId);
        }

        async function openChat(chat) {
            activeChatId = chat.chat_id;
            document.getElementById('chatUserAvatar');
            document.getElementById('chatUserName').textContent = chat.name;
            const friendsList = await eel.get_messages(activeChatId)();
            console.log(friendsList)
            messages = friendsList;
            console.log(messages)
            renderMessages(messages);
            loadMessages(activeChatId);
        }

        function loadMessages(chatId) {
            console.log("Загружаем чат:", chatId);
            const data = messages.filter(m => m.chat == chatId);
            console.log("Найдено сообщений:", data);

            renderMessages(data);
        }

        //открытие контекcт менюшки
        function threemenuBtn(userId) {
            console.log('Получен userId:', userId, typeof userId);
            const chat = data.find(item => item.id === (userId));
            if (!chat) {
                console.error('Чат с ID', userId, 'не найден');
                return;
            }
            const menu = document.getElementById('contextMenu');
            if (menu.style.display === 'block') {
                menu.style.display = 'none';
                return;
            }

            menu.innerHTML = '';
            let contexthtml = '';

            if (chat.type === 'private') {
                contexthtml = `
                    <button class="menu-item" data-action="addFriend">Добавить в друзья</button>
                    <button class="menu-item" data-action="removeFriend">Удалить из друзей</button>
                    <button class="menu-item" data-action="deleteChat">Удалить чат</button>
                `;
            } 
            else if (chat.type === 'group') {
                contexthtml = `
                    <button class="menu-item" data-action="copyLink">Скопировать ссылку</button>
                    <button class="menu-item danger" data-action="leaveChannel">Выйти из канала</button>
                `;
            }
            menu.innerHTML = contexthtml;

            const menuButtons = menu.querySelectorAll('.menu-item');
            menuButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const action = this.getAttribute('data-action');
                    handleMenuAction(action);
                });
            });
            console.log('Тип', chat.type, 'чат', chat.type === 'private');
            menu.style.display = 'block';
            console.log('Тип', chat.type, 'группа', chat.type === 'group');
            menu.style.display = 'block';
        }

        function handleMenuAction(action) {
            switch(action) {
                case 'addFriend':
                    alert('Добавить в друзья');
                    break;
                case 'removeFriend':
                    alert('Удалить из друзей');
                    break;
                case 'deleteChat':
                    alert('Удалить чат');
                    break;
                case 'copyLink':
                    alert('Скопировать ссылку');
                    break;
                case 'leaveChannel':
                    alert('Выйти из канала');
                    break;
            }
            document.getElementById('contextMenu').style.display = 'none';
        }
        //типы данных: private, group, addfriend(может быть), friend(может быть)
        // Данные пользователей
        let data = [];
        let friends = [];
        
        // Отображение друзей
        async function displayFriends(filter = '') {
            const container = document.getElementById('chatsList');
            container.innerHTML = '<div class="loading">Загрузка...</div>';
            
            try {
                const friendsList = await eel.select_friends()();  
                friends = friendsList;
                
                container.innerHTML = '';
                
                // Фильтруем по имени
                const filteredFriends = friendsList.filter(friend => 
                    friend.name.toLowerCase().includes(filter.toLowerCase())
                );
                
                if (filteredFriends.length === 0) {
                    container.innerHTML = '<div class="no-data">Нет друзей</div>';
                    return;
                }
                
                filteredFriends.forEach(friend => {
                    const friendDiv = document.createElement('div');
                    friendDiv.className = 'user-item';
                    friendDiv.onclick = () => openChat({
                        id: friend.id,
                        name: friend.name,
                        type: 'private',  
                        chat_id: friend.chat_id
                    });
                    

                    friendDiv.innerHTML = `
                    <div class="user-avatar"></div>
                    <span class="user-name">${friend.name}</span>
                    <button onclick="eel.remove_friend_api(${friend.id})();" 
                            style="background: #ff4444; 
                                color: white; 
                                border: none; 
                                border-radius: 4px; 
                                padding: 5px 10px; 
                                margin-left: 10px;
                                cursor: pointer;
                                font-size: 12px;
                                transition: background 0.2s;
                                hover: {background: #ff6666;}"
                            onmouseover="this.style.background='#ff6666'"
                            onmouseout="this.style.background='#ff4444'">
                        ✕ Удалить
                    </button>
                `;
                    container.appendChild(friendDiv);
                });
                
            } catch (error) {
                console.error('Ошибка загрузки друзей:', error);
                container.innerHTML = '<div class="error">Ошибка загрузки</div>';
            }
        }

        // Отображение запросов с фильтром
        async function displayFriendRequests(filter = '') {
            const container = document.getElementById('chatsList');
            container.innerHTML = '<div class="loading">Загрузка...</div>';
            
            try {
                const fr_requests = await eel.chek_for_friends_requests()();  
                
                container.innerHTML = '';
                
                // Фильтруем по имени отправителя
                const filteredRequests = fr_requests.filter(req => 
                    req.friend_name.toLowerCase().includes(filter.toLowerCase())
                );
                
                if (filteredRequests.length === 0) {
                    container.innerHTML = '<div class="no-data">Нет заявок</div>';
                    return;
                }
                
                filteredRequests.forEach(data => {
                    const friendreqDiv = document.createElement('div');
                    friendreqDiv.className = 'user-item';
                    friendreqDiv.onclick = () => accept_friend_request(data);
                    friendreqDiv.innerHTML = `
                        <div class="user-avatar"></div>
                        <span class="user-name">${data.friend_name}</span>
                    `;
                    container.appendChild(friendreqDiv);
                });
                
            } catch (error) {
                console.error('Ошибка загрузки заявок:', error);
                container.innerHTML = '<div class="error">Ошибка загрузки</div>';
            }
        }

        async function accept_friend_request(data) {
            await eel.accept_friend_request(data.id)();
        }

//отображение групп
//            function displayGroups(filter = '') {
//                const container = document.getElementById('chatsList');
//                container.innerHTML = '';
//
//                let filteredGroups = Groups.filter(f => f.type === 'group');
//                filteredGroups.forEach(data => {
//                    const GroupsDiv = document.createElement('div');
//                    document.getElementById('sendmessage');
//                    GroupsDiv.className = 'user-item';
//                    GroupsDiv.onclick = (sendMessage) => openChat(data);
//                    GroupsDiv.innerHTML = `
//                        <div class="user-avatar"></div>
//                        <span class="user-name">${data.title}</span>
//                    `;
//                    container.appendChild(GroupsDiv);
//                });
//            }

        // Отображение чатов с фильтром
        async function displayChats(filter = '') {
            const container = document.getElementById('chatsList');
            container.innerHTML = '<div class="loading">Загрузка...</div>';
            
            try {
                const chats = await eel.select_chats()();  
                data = chats;
                
                container.innerHTML = '';
                
                // Фильтруем по названию чата
                const filteredChats = chats.filter(chat => 
                    chat.name.toLowerCase().includes(filter.toLowerCase())
                );
                
                if (filteredChats.length === 0) {
                    container.innerHTML = '<div class="no-data">Нет чатов</div>';
                    return;
                }
                
                filteredChats.forEach(chat => {
                    const div = document.createElement('div');
                    div.className = 'user-item';
                    div.onclick = () => openChat(chat);

                    div.innerHTML = `
                        <div class="user-avatar"></div>
                        <span class="user-name">${chat.name}</span>
                    `;

                    container.appendChild(div);
                });
                
            } catch (error) {
                console.error('Ошибка загрузки чатов:', error);
                container.innerHTML = '<div class="error">Ошибка загрузки</div>';
            }
        }

        function switchTab(tab) {
            console.log('perem', switchTab);
            const chatsTab = document.getElementById('chatsTab');
            const friendsTab = document.getElementById('friendsTab');
            const friendreqtab = document.getElementById('friendreqtab');
            const chatsList = document.getElementById('chatsList');

            chatsTab.classList.remove('active');
            friendsTab.classList.remove('active');
            friendreqtab.classList.remove('active');

            chatsList.style.display = 'none';

            if (tab === 'chats') {
                chatsTab.classList.add('active');
                chatsList.style.display = 'block';
                displayChats();

            } else if (tab === 'friends') {
                friendsTab.classList.add('active');
                chatsList.style.display = 'block';
                displayFriends();

            } else if (tab === 'friends_request') {
                friendreqtab.classList.add('active');
                chatsList.style.display = 'block';
                displayFriendRequests();
            }
        }
        
        // Поиск
    function searchUsers() {
        const filter = document.getElementById('searchInput').value;
        const chatsTab = document.getElementById('chatsTab');
        const friendsTab = document.getElementById('friendsTab');
        const friendreqtab = document.getElementById('friendreqtab');
        
        // Определяем, какая вкладка активна
        if (chatsTab.classList.contains('active')) {
            displayChats(filter);
        } else if (friendsTab.classList.contains('active')) {
            displayFriends(filter);
        } else if (friendreqtab.classList.contains('active')) {
            displayFriendRequests(filter);
        }
    }




        function set_user_name(data) {
            const username = data.user.username;
            usr_email = data.user.email;
            currentUser = username;
            document.getElementById('user#id').textContent = username;
        }

        function start_main_page(){

            switchTab('chats');
            const messageInput = document.getElementById('messageInput');

            messageInput.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    sendMessage();
                }
            });
        }
        
        