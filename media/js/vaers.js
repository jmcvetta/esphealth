function postAndNextScreen(url, elem){
    $.post(url, 
	   function(data){
	       elem.html(data);
	   });
}
