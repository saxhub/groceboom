//checks to see if every checkbox in an aisle is checked
function AisleIsClosed(aisle_id){
	var no_more_items = 1;
	$('#aisle-' + aisle_id).children('.item-wrap').each(function(){

		if ($(this).find('.item-check').prop('checked') == false){
			no_more_items = 0;
		}
	})
	if (no_more_items == 1){
		return true;
	}
	else {
		return false;
	}
}

//swaps out the related select box for a text input, for a checked select-or-add box
function AddNewIsChecked(){
	if($(this).prop('checked') == true){
		$(this).parent().siblings('.select-or-add.choose').children('.select').fadeOut('fast',function(){
			$(this).siblings('.new').fadeIn('fast');
		});
		
	}
	else{
		$(this).parent().siblings('.select-or-add.choose').children('.new').fadeOut('fast',function(){
			$(this).siblings('.select').fadeIn('fast');
		});
	}
}

$(document).ready(function() {
	var csrftoken = $.cookie('csrftoken');
	function csrfSafeMethod(method) {
	    // these HTTP methods do not require CSRF protection
	    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	}
	$.ajaxSetup({
	    crossDomain: false, // obviates need for sameOrigin test
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type)) {
	            xhr.setRequestHeader("X-CSRFToken", csrftoken);
	        }
	    }
	});

	$('#in-store .aisle-wrap').each(function(){
		if (AisleIsClosed($(this).data('aisleid'))){
			$(this).hide();
		}
	});


	$('.select-or-add .check').each(AddNewIsChecked);
	$('.select-or-add .check').click(AddNewIsChecked);
	




	$('.item-check').click(function(){
  	
	  	if($(this).prop('checked') == true){
	  		itemid = $(this).data('itemid');
	  		$.post('/item-check/', {item_id : itemid})
	  		.done(function(data) {
			  $('#item-wrap-' + itemid).addClass('strike').delay(1000).slideUp(400);
			  	if (AisleIsClosed($('#item-wrap-' + itemid).parent('.aisle-wrap').data('aisleid'))){
			  		$('#item-wrap-' + itemid).parent('.aisle-wrap').delay(1000).slideUp(400);
			  	}
			});
			  
			
	  	}
  	
  	});

  	$("#in-store").sortable({
		update: function(event, ui) {
		  	$.post('/serialize-aisles/', $('#in-store').sortable('serialize'));	
		},
    }).disableSelection();


    $('#glist-form').submit(function() { 
    	// catch the form's submit event
    		$('#submit-wrap').addClass('loading').html('loading');
            $.ajax({ // create an AJAX call...
                data: $(this).serialize(), // get the form data
                type: $(this).attr('method'), // GET or POST
                url: $(this).attr('action'), // the file to call
                success: function(response) { // on success..
                    $('body').html(response); // update the DIV
            
                }
            });
            return false;
        });


	


});

