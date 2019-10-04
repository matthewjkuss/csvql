function addRow(table, string) {
    var cell = document.createElement("TD");
    var row = document.createElement("TR");
    var text = document.createTextNode(string);
    cell.appendChild(text);       
    row.appendChild(cell);       
    table.appendChild(row);       
}

function drawTable(tablename, table) {
    var tableNode = document.getElementById(tablename);
    tableNode.innerHTML = ""
    var rowNode = document.createElement("TR");
    table.columns.forEach(header => {
            var cellNode = document.createElement("TH");
            var textNode = document.createTextNode(header);
            cellNode.appendChild(textNode);
            rowNode.appendChild(cellNode);
    })
    tableNode.appendChild(rowNode)
    table.rows.forEach(row => {
        var rowNode = document.createElement("TR");
        row.forEach(cell => {
            var cellNode = document.createElement("TD");
            var textNode = document.createTextNode(cell);
            cellNode.appendChild(textNode);
            rowNode.appendChild(cellNode);

        })
        tableNode.appendChild(rowNode); 
    })
}

function reqListener() {
  console.log(this.response);
  var table = document.getElementById('messages')
  table.innerHTML = ""
  var rowNode = document.createElement("TR");
  var cellNode = document.createElement("TH");
  var textNode = document.createTextNode("Messages");
  cellNode.appendChild(textNode);
  rowNode.appendChild(cellNode);
  table.appendChild(rowNode)
  this.response.messages.forEach(message => {
    addRow(table, message);
  });
  drawTable("result", this.response.value);
}

function sendRequest(str) {
    console.log(str);
    oReq.open("GET", "http://localhost:8080/" + str);
    oReq.send();
}

var oReq = new XMLHttpRequest();
oReq.addEventListener("load", reqListener);
oReq.responseType = "json";