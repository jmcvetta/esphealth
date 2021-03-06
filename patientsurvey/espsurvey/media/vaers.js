var DemoNotificationEmail = null;

function makeGrid(elem, page_url){
    elem.flexigrid({
	striped:true,
	width: 700,
	height: 'auto',
	url: page_url,
	dataType: 'json',
	colModel: [
	    {display:"Provider", name:"provider", sortable:false},
	    {display:"Event Date", name:"date", sortable:true},
	    {display:"Event Description", name:"description"},
	    {display:"Action", name:"action", sortable:true},
	    {display:"Details", name:"details"}
	],
	usepager:true,
	title: "Cases",

    });
}


function Paginator(elem, page_url){
    var currentPage = 1;
    var getPage = function(page){
	$(elem).load(page_url, {page:page});
	
    }
	
    this.getPreviousPage = function(){
	if (currentPage > 1){
	    getPage(currentPage-1);
	    currentPage -= 1;
	}
    }

    this.getNextPage = function(){
	getPage(currentPage+1);
	currentPage += 1;
    }
}
	

function postAndNextScreen(url, elem){
    $.post(url, 
	   function(data){
	       elem.html(data);
	   });
}

function notify(elem, case_url){
    if (DemoNotificationEmail){
	jQuery.post(
		    case_url, { email:DemoNotificationEmail },
		    function(data){
			$(elem.parentNode).html(data);
			$("#banner_content").html(data);
			$("#banner").fadeIn("fast");

		    }, "text");
    }
    else {
	promptEmail('Which email address should be used?');
	notify(elem, case_url);
    }
}

function hideDemoWarning(){
    $("#banner").fadeOut();
}


function hideEmailPrompt(){
    $("#banner_no_email").fadeOut("fast");
}

function showCurrentEmail(){
    if (DemoNotificationEmail){
	$("#email_address").html(DemoNotificationEmail);
	$("#banner_info_email").fadeIn("slow");
    }
}
 
 $(document).ready(function() {

    $('.css_state').click(function() {
        var container = $(this);

        $.get( container.attr('alt'), {'com': 1}, function() {
            container.find('.togcomment').toggle();
        });

    });
});

function promptEmail(message){
    msg = message || 'Please set up the email address to send detailed reports.';
    var email = prompt(msg);
    DemoNotificationEmail = email;
    if (!DemoNotificationEmail) { 
	    alert ("Invalid Input.");
	}
    else {
	hideEmailPrompt();
	showCurrentEmail();
    }
}

function togglecomment()
{
    var com1 = document.getElementById("first");
    var com2 = document.getElementById("second");
    var com3 = document.getElementById("third");
	var vals = document.getElementsByName("state");
	for(var val in vals)
	{
		if(vals[val].checked)
		{
			if(vals[val].value=="confirm") {
				com1.style.display="none";
				com2.style.display="block";
				com3.style.display="none"; }
			else if(vals[val].value=="false_positive") {
				com1.style.display="none";
				com2.style.display="none";
				com3.style.display="block"; }
		}
	}
}
