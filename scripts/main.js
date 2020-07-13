function noteToSelf() {
  var x = document.getElementById("note");
  if (x.style.display === "none") {
    x.style.display = "";
  } else {
    x.style.display = "none";
  }
}

function getUrl(url){
  var Httpreq = new XMLHttpRequest(); // a new request
  Httpreq.open("GET",url,false);
  Httpreq.send(null);
  return Httpreq.responseText;          
}


if (window.location.pathname == /kindle-notes-reader/){ 
var x = "";
var json_obj = JSON.parse(getUrl("books/titles.json"));
for (i in json_obj.books){
// x = `${x}<div class="m-4 mx-3"><a href="book-details.html"><img id=${i} onerror="onerrFunction();" class="book-cover shadow rounded" src="${json_obj.books[i].thumbnail}"><h6 class="pt-3 text-left text-wrap">${json_obj.books[i].title}</h6></a></div>`;
x = `${x}<div class="m-4 mx-3"><a href="book-details.html"><img id=${i} class="book-cover shadow rounded" src="${json_obj.books[i].thumbnail}" onError="this.onerror=null;this.src='images/noimage.jpg';"></a><h6 class="pt-3 text-left text-wrap">${json_obj.books[i].title}</h6></div>`;

} 
document.getElementById("book-store").innerHTML = x;
}


document.querySelectorAll('.book-cover').forEach(item => {
  item.addEventListener('click', event => {
    sessionStorage.setItem("selfLink",json_obj.books[event.target.id].selfLink);
    console.log(selfLink);
  })
})


if (window.location.pathname == "/kindle-notes-reader/book-details.html"){
  
  if (sessionStorage.getItem("selfLink") == null){
    console.log("hello");
    console.log(selfLink);
    alert("Empty");
    window.location.replace("https://vimalav.github.io/kindle-notes-reader/");
  }

  var bookPath = sessionStorage.getItem('selfLink');
  document.getElementById("book-img").src = bookPath + "/thumbnail.jpg";

  var y = "";
  var json_obj2 = JSON.parse(getUrl(bookPath + "highlights.json"));
  
  document.getElementById("title").innerHTML = json_obj2.meta_data.title;
  document.getElementById("authors").innerHTML = json_obj2.meta_data.authors;

  for (j in json_obj2.highlights){
    y = `${y}<div class="row"><p>${json_obj2.highlights[j].text}</p></div>`
  }
  document.getElementById("annotations").innerHTML = y; 
  sessionStorage.removeItem("selfLink");
}
