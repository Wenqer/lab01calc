/**
 * Created with PyCharm.
 * User: Yarik
 * Date: 01.06.12
 * Time: 13:14
 * To change this template use File | Settings | File Templates.
 */
jQuery(document).ready(function($){
	var paper = Raphael("layout",<%= layout.wid_a3 %>, <%= layout.hei_a3 %>);
	// Creates canvas 320 × 200 at 10, 50
	//var paper = Raphael("layout", 320, 200);

            for (var i = 1; i < <%= layout.rows%>;i++){

            }
            // Creates circle at x = 50, y = 40, with radius 10
            //var circle = paper.circle(50, 40, 10);
            // Sets the fill attribute of the circle to red (#f00)
            circle.attr("fill", "#f00");

            // Sets the stroke attribute of the circle to white
            circle.attr("stroke", "#fff");
});