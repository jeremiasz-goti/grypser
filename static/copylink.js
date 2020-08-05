function copyGryps() {

  var elm = document.getElementById("copy-gryps");
  // for Internet Explorer

  if(document.body.createTextRange) {
    var range = document.body.createTextRange();
    range.moveToElementText(elm);
    range.select();
    document.execCommand("Copy");
    alert("Link do grypsa skopiowany!");
  }
  else if(window.getSelection) {
    // other browsers

    var selection = window.getSelection();
    var range = document.createRange();
    range.selectNodeContents(elm);
    selection.removeAllRanges();
    selection.addRange(range);
    document.execCommand("Copy");
    alert("Link do grypsa skopiowany!");
  }
}

function alarm() {
    alert("kliknieto");
}
