(function ($) {
  if ($(window).width() > Drupal.settings.backstretchMinWidth) {
    $.backstretch(Drupal.settings.backstretchURL);
    
    $(document).ready(function () { 
      if (Drupal.settings.backstretchScroller) {
        var height = $(window).height() + parseInt(Drupal.settings.backstretchScrollerAdj);
        if ($('#toolbar').length > 0) { var height = height - $('#toolbar').height(); }
        if (Drupal.settings.backstretchScrollerAdj != 0) {
          $('body').append('<div id="backstretchmargin"></div>');
        }
        $('#backstretchmargin').css('margin-bottom', height);
      }

      if (Drupal.settings.backstretchScrollTo) {

        $("#footer").waypoint(function(){
          $("#backstretch-scrollto").text("Back to Top").attr("href", "#page");
        });

        $("#main-menu").waypoint(function(){
          $("#backstretch-scrollto").text("View Photo").attr("href", "#backstretchmargin");
        });
        
        // Scroll to right place on click.
        $("#backstretch-scrollto").click(function(e){
          var s = $(this).attr("href");
          console.log(s);
          if (s == '#backstretchmargin') {
            var s = 'max';
            console.log('hi');
          }
          $.scrollTo(s, 1000);
          e.preventDefault();
          return false;
        });
      }
    });
  }
})(jQuery);
;
(function ($) {
  // innerLabel
  $.fn.innerLabel = function( default_text ){
    var element = this;
    // prevent non-existant elements from being processed
    if( $(element).length <= 0 ) {
      return;
    }

      // If element val() isset, use that as default text.
      var text = (element.find('input[type=text]').val()) ? element.find('input[type=text]').val() : default_text;

      // Set the default text.
      //var text = (default_text) ? default_text : element.find('label').text().trim();

      // add a class to be able to target processed form items
      $(element).addClass('inner-label-processed');

      // set the default value for the input text
      $(element).find('input[type=text]')[0].defaultValue = text;

      // Add focus/blur event handlers

      $(element)
        .find('input[type=text]')
        .val(text)
        .focus( function() {
          // when user clicks, remove the default text
          if ($(this).val() == $(this)[0].defaultValue) {
            $(this).val('');
            $(this).addClass('focus');
          }
        })
        .blur( function() {
          // when user moves away from text,
          // replace the text with default if input is empty
          if ($(this).val().trim() == '') {
            $(this).val($(this)[0].defaultValue);
            $(this).removeClass('focus');
          }
       });
  };
  $(window).load(function(){
    // Put innerLabel on to search field in the header.
    $('#block-google-appliance-ga-block-search-form form .form-item-search-keys').innerLabel('Search this site');
  });
}(jQuery));
;
/*! track-focus v 1.0.0 | Author: Jeremy Fields [jeremy.fields@vget.com], 2015 | License: MIT */
// inspired by: http://irama.org/pkg/keyboard-focus-0.3/jquery.keyboard-focus.js

(function(body) {

	var usingMouse;

	var preFocus = function(event) {
		usingMouse = (event.type === 'mousedown');
	};

	var addFocus = function(event) {
		if (usingMouse)
			event.target.classList.add('focus--mouse');
	};

	var removeFocus = function(event) {
		event.target.classList.remove('focus--mouse');
	};

	var bindEvents = function() {
		body.addEventListener('keydown', preFocus);
		body.addEventListener('mousedown', preFocus);
		body.addEventListener('focusin', addFocus);
		body.addEventListener('focusout', removeFocus);
	};

	bindEvents();

})(document.body);
;
(function( $ ){
  $(document).ready(function(){
  
  $(".ui-accordion").bind("accordionchange", function(event, ui) {
     if ($(ui.newHeader).offset() != null) {
          ui.newHeader, // $ object, activated header
          $("html, body").animate({scrollTop: ($(ui.newHeader).offset().top)-100}, 500);
     }
  });
  
  
  
  });
})( jQuery );;
jQuery(window).scroll(function() {
  if (jQuery(this).scrollTop() > 300) {
      jQuery('#cu_back_to_top').fadeIn('slow');
  } else {
      jQuery('#cu_back_to_top').fadeOut('slow');
  }
});
jQuery('#cu_back_to_top a').click(function(){
  jQuery("html, body").animate({ scrollTop: 0 }, 600);
  jQuery("#page").focus();
  return false;
});;
jQuery(window).scroll(function() {
  if (jQuery(this).scrollTop() > 160) {
      jQuery('#sticky-menu').fadeIn('slow');
  } else {
      jQuery('#sticky-menu').fadeOut('slow');
  }
});;
