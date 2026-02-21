
        let selectedFriends = [];
        async function displayFriendsForCCpage() {
            const container = document.getElementById('friendsList');
            container.innerHTML = '';
            const friends = await eel.select_friends()();
            console.log(friends)
            friends.forEach((friend) => {
                const row = document.createElement('div');
                row.className = 'friend-row';
                row.innerHTML = `
                    <div class="friend-info">
                        <div class="friend-avatar"></div>
                        <span class="friend-name">${friend.name}</span>
                    </div>
                    <input type="checkbox" id="scales" name="scales" checked />
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

        }

        