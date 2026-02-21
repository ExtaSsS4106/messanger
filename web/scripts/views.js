console.log("views.js inited")



async function loadPage(value) {
    let content;
    let data;
    switch(value) {
        case "homepage":
            console.log("homepage")
            content = await eel.start_page()();
            document.querySelector('body').innerHTML = content;
            break;
        case "login":
            let loginPage = new Login_page();
            content = await eel.login()();
            document.querySelector('body').innerHTML = content;
            loginPage.init_page();
            break;
        case "register":
            let RegPage = new Register_page();
            content = await eel.sign_up()();
            document.querySelector('body').innerHTML = content;
            RegPage.init_page();
            break;
        case "main":
            [content, data] = await eel.main()(); 
            document.querySelector('body').innerHTML = content;
            set_user_name(data)
            start_main_page();
            
            break;
        case "createChannel":
            content= await eel.create_channel()(); 
            document.querySelector('body').innerHTML = content;
            displayFriendsForCCpage();
            break;
        case "addFriends":
            content= await eel.add_friends()(); 
            document.querySelector('body').innerHTML = content;
            all_users_()
            break;
        default:
            console.log("nothing to show");
            document.querySelector('body').innerHTML = '<h1>Такой страницы не существует</h1>';
            break;
    }
}