        function sendFriendRequest() {
            alert('Запрос на дружбу отправлен!');
            // Сохраняем нового друга (для теста)
            let friends = JSON.parse(localStorage.getItem('friends')) || [];
            friends.push({id: Date.now(), name: 'User#New', selected: false});
            localStorage.setItem('friends', JSON.stringify(friends));
        }