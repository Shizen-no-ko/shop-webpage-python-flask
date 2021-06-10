
window.onload = function(e){
    buttons = document.getElementsByClassName('button');
    title = document.getElementById('lalala');
    backdrop = document.getElementById('backdrop');
    modal = document.getElementById('modal-card');
    title.innerHTML="wow";
    var i;
    for (i = 0; i < buttons.length; i++) {
    buttons[i].onclick = function(e){
    var id = this.id;
    var num = id.split('-')[1];
    var titleText = document.getElementById('full-title-' + num).innerHTML;
    var descriptionText = document.getElementById('description-' + num).innerHTML;
    title.innerHTML= backdrop.id;
    document.documentElement.scrollTop = 0;
    backdrop.classList.toggle('show');
    modal.classList.toggle('show');
    document.getElementById('modal-title').innerHTML = titleText;
    document.getElementById('modal-description').innerHTML = descriptionText;
    current = 0;
  };
    buttons[i].style.backgroundColor="red";
    }
    }


