$.widget( "readmore.dummy", {
	// Default options
	options: {
		controlwidget: "articleviewer"
	},
	_create: function(){
		var _self = this
		// Find any instance of the controlwidget and
		// bind to the `wordclick' event
		$(":readmore-"+this.options.controlwidget).bind(
			this.options.controlwidget+"wordclick",
			function(event, data){
				_self.load(data['word']);
			}
		)
	},
    load: function(word){
		var _self = this
		api_call(
			"/widgets/dummy/?word="+word,
			{},
			'GET',
			function(data, xhr){
				_self.element.html(data['word']);
			}
		);
	}
})
