/**
 * Created with PyCharm.
 * User: РосLab01
 * Date: 14.06.12
 * Time: 17:33
 * To change this template use File | Settings | File Templates.
 */
(function($) {
    $(document).ready(function($) {
        // you can now use jquery / javascript here...
        //alert('It worked.');
		var json = $('#id_layout').val();
		$('#id_layout').before("<div id='canvas' style='margin-left: 100px'></div>");
		$('#id_layout').remove();
		paper = Raphael('canvas');

		paper.fromJSON(json);
    });
})(django.jQuery);