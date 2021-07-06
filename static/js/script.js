// toggle modal on or off
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
//        apply onclick function to artwork buttons to trigger modal
        buttons[i].onclick = function(){
//        obtain id number from button id
            var id = this.id;
            var num = id.split('-')[1];
//            grab infos for display in modal
            var titleText = document.getElementById('full-title-' + num).innerHTML;
            var descriptionText = document.getElementById('description-' + num).innerHTML;
            var priceText = document.getElementById('price-' + num).innerHTML;
            var imageUrl = document.getElementById('img-' + num).src;
//            scroll to page top for displaying modal
            document.documentElement.scrollTop = 0;
//            set modal close button to toggleModal function
            modalClose = document.getElementById('close-modal-button');
            modalClose.onclick = toggleModal;
//            display modal
            toggleModal()
//            set modal details to infos gathered above from artwork card
            document.getElementById('modal-title').innerHTML = titleText;
            document.getElementById('modal-image').src = imageUrl;
            document.getElementById('modal-description').innerHTML = descriptionText;
            document.getElementById('modal-price').innerHTML = priceText;
            document.getElementById('buy-button').value = num;
            current = 0;
        };
    };
};

//only display cart number if greater than 0
function setCartNumber(){
    cartNumber = document.getElementById("cart-count");
    if (cartNumber.innerHTML != "0"){
        cartNumber.classList.add('show');
    } else {
        cartNumber.classList.remove("show");
    };

}

//run after page has loaded
window.onload = function(){
 setButtons()
 setCartNumber()
};
