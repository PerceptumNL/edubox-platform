$( function(){
    var $cardcontainer = $('#cards').isotope({
        itemSelector: '.element-item',
        getSortData: {
            order: '[data-order] parseInt'
        },
        sortBy: 'order'
    });
});

$( function(){
    var $cardcontainer = $('.cards').isotope({
        itemSelector: '.element-item',
        getSortData: {
            order: '[data-order] parseInt'
        },
        sortBy: 'order'
    });
});

var $container = $('#articles');
$( function() {
    // init Isotope
    var qsRegex;
    $container.isotope({
        layoutMode: 'masonry',
        masonryHorizontal: {
            columnWidth: 256
        },
        itemSelector: '.articleTile',
        transitionDuration: 0,
        //filter: function() {
        //   var variable = qsRegex ? $(this).text().match( qsRegex ) : true;
        //    return variable ;
        //}
    });
    $(window).load(function(){
        $container.isotope();
    });
    // use value of search field to filter
//    var $quicksearch = $('#quicksearch').keyup( debounce( function() {
//        qsRegex = new RegExp( $quicksearch.val(), 'gi' );
//        $container.isotope();
//    }, 200 ) );
});
// debounce so filtering doesn't happen every millisecond
function debounce( fn, threshold ) {
    var timeout;
    return function debounced() {
        if ( timeout ) {
            clearTimeout( timeout );
        }
        function delayed() {
            fn();
        timeout = null;
    }
    timeout = setTimeout( delayed, threshold || 100 );
    }
}
/*
$container.isotope({
		filter: function () {
		  if(filterValue=='*'){
			return true
		  };
		  var cat = $(this).find('.articleInfo').text();
		  return cat.match( filterValue );
		}
	});

  // change is-checked class on buttons
  $('.button-group').each( function( i, buttonGroup ) {
    var $buttonGroup = $( buttonGroup );
    $buttonGroup.on( 'click', 'button', function() {
      $buttonGroup.find('.is-checked').removeClass('is-checked');
      $( this ).addClass('is-checked');
    });
  });
	*/
