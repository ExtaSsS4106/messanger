console.log("views.js inited")



async function loadPage(value) {
    switch(value) {
        case "homepage":
            content = await eel.start_page()();
            document.querySelector('body').innerHTML = content;
            break;
        case "login":
            content = await eel.login()();
            document.querySelector('body').innerHTML = content;
            break;
        case "register":
            content = await eel.register()();
            document.querySelector('body').innerHTML = content;
            break;
        case "main":
            content = await eel.main()();
            document.querySelector('body').innerHTML = content;
            displayChats();
            break;
        default:
            console.log("nothing to show");
            document.querySelector('body').innerHTML = '<h1>Такой страницы не существует</h1>';
            break;
    }
}