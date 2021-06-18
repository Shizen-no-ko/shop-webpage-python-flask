 function toggleModal() {
            backdrop.classList.toggle('show');
            modalCard.classList.toggle('show');
            modalClose.classList.toggle('show');
 };

function setButtons(){
    buttons = document.getElementsByClassName('button');
    backdrop = document.getElementById('backdrop');
    modalCard = document.getElementById('modal-card');
    var i;
    for (i = 0; i < buttons.length; i++) {
        buttons[i].onclick = function(){
            var id = this.id;
            var num = id.split('-')[1];
            var titleText = document.getElementById('full-title-' + num).innerHTML;
            var descriptionText = document.getElementById('description-' + num).innerHTML;
            var priceText = document.getElementById('price-' + num).innerHTML;
            var imageUrl = document.getElementById('img-' + num).src;
            document.documentElement.scrollTop = 0;
            modalClose = document.getElementById('close-modal-button');
            modalClose.onclick = toggleModal;
            toggleModal()
            document.getElementById('modal-title').innerHTML = titleText;
            document.getElementById('modal-image').src = imageUrl;
            document.getElementById('modal-description').innerHTML = descriptionText;
            document.getElementById('modal-price').innerHTML = priceText;
            current = 0;
        };
    };
};

window.onload = function(){
 setButtons()
};
