document.getElementById("liveToastBtn").onclick = function() {
  var myAlert =document.getElementById('liveToast');//select id of toast
  var bsAlert = new bootstrap.Toast(myAlert);//inizialize it
  bsAlert.show();//show it
  }

