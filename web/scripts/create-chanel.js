        let friends = JSON.parse(localStorage.getItem('friends')) || [
            {id: 123456, name: 'User#123456', selected: false},
            {id: 654321, name: 'User#654321', selected: false},
            {id: 789012, name: 'User#789012', selected: false}
        ];

        function displayFriends() {
            const container = document.getElementById('friendsList');
            container.innerHTML = '';
            friends.forEach((friend, index) => {
                const row = document.createElement('div');
                row.className = 'friend-row';
                row.innerHTML = `
                    <div class="friend-info">
                        <div class="friend-avatar"></div>
                        <span class="friend-name">${friend.name}</span>
                    </div>
                    <button class="add-btn" onclick="toggleFriend(${index})">${friend.selected ? 'Добавлен' : 'Добавить'}</button>
                `;
                container.appendChild(row);
            });
        }

        function toggleFriend(index) {
            friends[index].selected = !friends[index].selected;
            displayFriends();
        }

        function createChannel() {
            const channelName = document.getElementById('channelName').value.trim();
            if (!channelName) {
                alert('Введите название канала');
                return;
            }

            const selectedFriends = friends.filter(f => f.selected);
            if (selectedFriends.length === 0) {
                alert('Выберите хотя бы одного друга');
                return;
            }

            const channels = JSON.parse(localStorage.getItem('channels')) || [];
            const newChannel = {
                id: 'channel_' + Date.now(),
                name: channelName,
                members: selectedFriends,
                createdAt: new Date().toISOString()
            };
            channels.push(newChannel);
            localStorage.setItem('channels', JSON.stringify(channels));

            alert(`Канал "${channelName}" создан!`);
            window.location.href = 'chats.html';
        }

        displayFriends();