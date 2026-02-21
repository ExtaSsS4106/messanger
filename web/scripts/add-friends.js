// Отображение запросов с фильтром
        async function all_users_() {
            const container = document.getElementById('user-card');
            container.innerHTML = '<div class="loading">Загрузка...</div>';
            
                const users = await eel.select_users_for_add()();  
                
                container.innerHTML = '';
                
                
                if (users.length === 0) {
                    container.innerHTML = '<div class="no-data">Нет заявок</div>';
                    return;
                }
                
                users.forEach(data => {
                    const friendreqDiv = document.createElement('div');
                    friendreqDiv.className = 'user-item';
                    friendreqDiv.onclick = () => eel.send_friend_request(data.id)();
                    friendreqDiv.innerHTML = `
                        <div class="user-avatar"></div>
                        <span class="user-name">${data.username}</span>
                    `;
                    container.appendChild(friendreqDiv);
                });
                

        }