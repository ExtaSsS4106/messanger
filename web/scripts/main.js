    let activeChatId = null;
    function getChatIdFromUrl() {
        const params = new URLSearchParams(window.location.search);
        return params.get('user');
    }

        let messages=[]
        let currentUser = '';

        function renderMessages(messages) {
            const container = document.getElementById('messagesContainer');
            container.innerHTML = '';

            messages.forEach(msg => {
                const div = document.createElement('div');
                div.className = msg.user === 'User#228'
                    ? 'message-right'
                    : 'message-left';
                div.innerHTML = `
                    <div>${msg.user}</div>
                    <div class="user-avatar-small"></div>
                    <div class="message-text">${msg.text}</div>
                `;
                container.appendChild(div);
            });
            container.scrollTop = container.scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            if (!input.value || !activeChatId) return;
            let lastCount = messages.length > 0
            ? messages[messages.length - 1].count
            : 0;
                messages.push({
                count: messages.length + 1,
                chat: activeChatId,
                user: 'User#228',
                text: input.value,
                type: 'text',
                file: ''
            });

            input.value = '';
            loadMessages(activeChatId);
        }

        async function openChat(user) {
            activeChatId = user.chat_id;
            document.getElementById('chatUserAvatar');
            document.getElementById('chatUserName').textContent = user.title;
            const friendsList = await eel.get_messages(user.id)();
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
            container.innerHTML = '';
            
            const friendsList = await eel.select_friends()();  
            friends=friendsList;
            let filteredFriends = friendsList.filter(f => 
                f.username.toLowerCase().includes(filter.toLowerCase())
            );
            
            filteredFriends.forEach(friend => {
                const friendDiv = document.createElement('div');
                friendDiv.className = 'user-item';
                friendDiv.onclick = () => openChat({
                    id: friend.id,
                    title: friend.username,
                    type: 'private',  
                    chat_id: friend.chat_id
                });
                
                friendDiv.innerHTML = `
                    <div class="user-avatar"></div>
                    <span class="user-name">${friend.username}</span>
                `;
                container.appendChild(friendDiv);
            });
        }

        //отображение запросов в друзья //пока отображает группы
            function displayFriendRequests(filter = '') {
                const container = document.getElementById('chatsList');
                container.innerHTML = '';

                let filteredFriendRequests = data.filter(f => f.type === 'group');

                filteredFriendRequests.forEach(data => {
                    const friendreqDiv = document.createElement('div');
                    document.getElementById('sendmessage');
                    friendreqDiv.className = 'user-item';
                    friendreqDiv.onclick = (sendMessage) => openChat(data);
                    friendreqDiv.innerHTML = `
                        <div class="user-avatar"></div>
                        <span class="user-name">${data.title}</span>
                    `;
                    container.appendChild(friendreqDiv);
                });
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

        function displayChats(filter = '') {
            const container = document.getElementById('chatsList');
            container.innerHTML = '';

            data
                .filter(u => u.title.toLowerCase().includes(filter.toLowerCase()))
                .forEach(user => {
                    const div = document.createElement('div');
                    div.className = 'user-item';
                    div.onclick = (sendMessage) => openChat(user);

                    div.innerHTML = `
                        <div class="user-avatar"></div>
                        <span class="user-name">${user.title}</span>
                    `;

                    container.appendChild(div);
                });
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
            const friendsTab = document.getElementById('friendsTab');
            const chatsList = document.getElementById('chatsList');
            friendsTab.classList.remove('active');
            chatsTab.classList.remove('active');
            displayChats(filter);
        }

        const messageInput = document.getElementById('messageInput');

        messageInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        });

        function set_user_name(data) {
            const username = data.user.username;
            currentUser = username;
            document.getElementById('user#id').textContent = username;
        }
        
        