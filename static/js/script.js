//var buttons = document.getElementById('lalala');
//buttons.innerHTML="Woolaaah";
//buttons.onclick = function(){
//    buttons.innerHTML="Ploppy"
//}
window.onload = function(){
    buttons = document.getElementsByClassName('button');
    title = document.getElementById('lalala');
    title.innerHTML="purple";
    var i;
    for (i = 0; i < buttons.length; i++) {
    buttons[i].onclick = function(e){
    title.innerHTML="MobblyBoo";
    current = 0;
  };
    buttons[i].style.backgroundColor="red";
    }
    }
//    for (i = 0; i < buttons.length; i++) {
//   buttons[i].style.backgroundColor = "red";
//    }
//buttons = document.getElementsByClassName('card');
//title = document.getElementById('lalala');
////var i;
//title.innerHTML="purple";
//buttons[0].style.backgroundColor = "red";
//for (i = 0; i < buttons.length; i++) {
//    buttons[i].onclick = function(){
//    title.innerHTML="MobblyBoo";
//  }


