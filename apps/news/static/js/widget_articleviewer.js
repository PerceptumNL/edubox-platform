$.widget( "readmore.articleviewer", {
	// Default options
	options: {
		article: undefined
	},
	_create: function(){
		var _self = this
		api_call(
			this.options.article,
			{'format':'json'},
			'GET',
			function(data, xhr){
				title = $("<header>").html(data['title']);
				title.append($("<h6>").html(data['date']));
				_self.element.html(data['body']);
				_self.element.prepend(title);
				_self.postprocess()
			}
		);
	},
	postprocess: function(){
		/* Make all words clickable.
		 * This is done by the following steps:
		 *   1. All textnodes (in all depths) are collected breadth-first.
		 *   2. From the text in each textnode, a new string is extracted where
		 *      each word is wrapped by a <span> element with the class ".word"
		 *   3. The new string is placed in a new <span> element, which is inserted
         *      in the DOM just before the textnode
         *   4. The textnode itself is removed
         *   5. Each element with the ".word" class gets an onClick event
		 *
		 * Clicking a word triggers the "wordclick" event, containing data["word"].
		 */
		var _self = this
		textnodes = []

		// Set traverse list to  toplevel child nodes
		nodes = $.makeArray($(this.element).contents())

		// While there are still nodes to traverse
		while(nodes.length > 0){
			// Pick the first node
			node = nodes.shift();
			if(node.nodeType == 3){
				// If it's a textnode, save
				textnodes.push(node);
			}else{
				// Else, add child nodes to traverse list
				nodes = nodes.concat($.makeArray($(node).contents()))
			}
		}
		// Replace each word
		$(textnodes).each(function(){
			// Create string containing new HTML
			content = this.textContent.replace(
				/([^\s.,;:'\"`~!@#\$%\^&*()_\+\-=\[\]\{\}\\\|\?\/<>]+)/g,
				"<span class='word'>$1</span>");
			// Add new HTML to DOM
			$("<span>"+content+"</span>").insertBefore(this)
			// Remove old textnode
			$(this).remove()
		})
		// Add onclick events on each word
		$(".word").click(function(e){
			//Remove selected link feedback, if any
			$('.neutral').children().unwrap();
			//Remove linked image, if any
			$(".linkimg").remove();
			//Remove #selected from previously clicked word
			$('#selected').attr('id', '');
			//Add #selected to current clicked word
			this.setAttribute('id', 'selected');
			// Trigger wordclick event, providing the word that was clicked on.
			_self._trigger("wordclick", e, {"word": $(this).text()})
		})

		$(".wikiBlueLink").click(function(e){
			//Prevent triggering url
			e.preventDefault();
			//Save article url
			var link = this.getAttribute('href');
			//Wrap link in container span
			$(this).wrap("<span class='neutral'></span>")
			//Append linked image to article
			$("<a class='linkimg' href='" + link + "''><img src='/static/img/layout/link_nobg.png'></a>").appendTo($(this).parent());
		})

	    $('#article img').load(function(){
			if($(this).innerHeight() > 1){
				$('#imageHolder').append(this);
			}
        });
	}
})
