function noteToSelf() {
  var x = document.getElementById("note");
  if (x.style.display === "none") {
    x.style.display = "";
  } else {
    x.style.display = "none";
  }
}

function Get(url){
  var Httpreq = new XMLHttpRequest(); // a new request
  Httpreq.open("GET",url,false);
  Httpreq.send(null);
  return Httpreq.responseText;          
}

var x = ""
var json_obj = JSON.parse(Get("/books/titles.json"));

for (i in json_obj.books){
x = `${x}<div class=" m-4 mx-3 bd-highlight"><a href="book-details.html" ><img class="book-cover shadow rounded" src="${json_obj.books[i].thumbnail}"></a><h6 class="pt-3 text-left text-wrap">${json_obj.books[i].title}</h6></div>`;
}

document.getElementById("book-store").innerHTML = x;

