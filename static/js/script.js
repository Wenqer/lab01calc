/* Author: 

*/

jQuery(document).ready(function($){
	$('#send').button('reset');
	$('form[name=recount]').submit(function(e){

		e.preventDefault();
		$('#send').button('loading');
		$form = $(this);
		senddata='';
		$result=$('#result');
		$result.html('');
		$.each($form.find('input'),function(){
			if ($(this).val() != '') senddata+= $(this).attr('name') + '=' + $(this).val() + '&';
		});
		$.ajax({
			url: '/recounter/',
			data: senddata,
			dataType: 'json',
			beforeSend: function(){},
			success: function(data, textStatus){
				$('#send').button('reset');
				$.each(data, function(i, val){
					$('#result').append(i+' '+val+'<br/>');
				})
			}
		});
	});
	$('#send').click(function(e){



	});
});



