function postAndNextScreen(url, elem){
    $.post(url, 
	   function(data){
	       elem.html(data);
	   });
}

function notify(case_url){
    jQuery.post(case_url);
}
