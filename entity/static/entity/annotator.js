
var queue = new Array();
var spanCounter = 0;

function enableSelectable() {
    // set the paragraphs to selectable
    var pars = document.getElementsByTagName('div');
    for (var i=0;i<pars.length; i++) {
	if (pars[i].id != null && pars[i].id.startsWith("text")) {
	    pars[i].setAttribute("onkeypress", "select_text(event, this)");
	    pars[i].setAttribute("tabindex", i);
            pars[i].style.cursor = "default";
	}
    }
}
       
function select_text(e, div) {
    // store the span text in the queue for undo
    var span;
    var html = div.innerHTML;
    queue.push(html);
            
    // translate the key event to the key code
    var obj = window.event ? event : e;
    var unicode = obj.charCode ? obj.charCode : obj.keyCode;
    var key = String.fromCharCode(unicode).toLowerCase();

    // delete the selected span
    if (key == 'd') {
	var span = document.getElementsByTagName('span');
	for (var i=0; i<span.length; i++) {
	    if (span[i].getAttribute("class") == null
		|| !span[i].getAttribute("class").match('selected')) {
		continue;
	    }
	    var text = document.createTextNode(span[i].innerHTML);
	    span[i].parentNode.replaceChild(text, span[i]);
	}
	return;
    }
    
    // else, check for new selection.
    if (key != 's') {
        return;
    }
            
    // Firefox and Safari
    if (typeof window.getSelection != "undefined") {
        var sel = window.getSelection();
        if (sel.rangeCount) {
            var range = sel.getRangeAt(0);
                    
            // select the start and end nodes to check for overlapping spans
            var start_node = range.startContainer.parentNode;
            var end_node = range.endContainer.parentNode;
                    
            // if the selection extends outside the statement, then deselect
            if (!validContainer(start_node) || !validContainer(end_node)) {
                if (typeof document.selection == "undefined") {
                    sel.removeAllRanges();
                }
                else {
                    document.selection.empty();
                }
		console.log("error: selection extends beyond div");
                return;
            }
                    
            // if not contained in existing span, then add new span container
            if (start_node.localName != "span" && start_node == end_node) {
                // adjust the range to fit word boundaries
                adjustStartOffset(range);
                adjustEndOffset(range);
                        
                // construct the span from the range, remove embedded spans
                var text = extractText(range.cloneContents());
                var node = document.createTextNode(text);
                span = document.createElement("span");
                span.appendChild(node);
                span.setAttribute("class", "coded_i_new");
                range.deleteContents();
                range.insertNode(span);
            }
            else if (start_node.localName == "div") {
                // adjust the range to fit starting word boundary
                adjustStartOffset(range);
                        
                // expand span to include the start node
                range.setEndBefore(end_node);
                end_node.insertBefore(range.cloneContents(), end_node.firstChild);
                range.deleteContents();
            }
            else if (end_node.localName == "div") {
                // adjust the range to fit end word boundary
                adjustEndOffset(range);
                        
                // expand span to include the end node
                range.setStartAfter(start_node);
                start_node.appendChild(range.cloneContents());
                range.deleteContents();
            }
            else if (start_node != end_node) {
                // join two adjacent spans by merging contents into start span
                var node = start_node.nextSibling;
                while (node != null) {
                    if (node.localName == "span") {
                        var child = node.removeChild(node.firstChild);
                        var parent = node.parentNode;
                        parent.removeChild(node);
                        start_node.appendChild(child);
                    }
                    else {
                        start_node.appendChild(node);
                    }
                    if (node == end_node) {
                        break;
                    }
                    else {
                        node = start_node.nextSibling;
                    }
                }
            }
            else {
                // do nothing, one outer span contains selection
            }
                    
            // deselect the selected text
            if (typeof document.selection == "undefined") {
                sel.removeAllRanges();
            }
            else {
                document.selection.empty();
            }
        }
    }
    // Internet Explorer
    else if (typeof document.selection != "undefined") {
        if (document.selection.type == "Text") {
            var range = document.selection.createRange();
            var text = range.text;
                    
            // span the text and remove duplicates
            span = formatSpan(text);
            range.pasteHTML(span);
                    
            // deselect the selected text
            document.selection.empty();
        }
    }

    if (span != null) {
	// add alt text based on span content
	span.setAttribute("alt", span.innerHTML);

	// enable draggableness for ontology
	enableDraggableSpan(span);
    }
}
        
function validContainer(node) {
    while (node != null) {
        if (node.id.startsWith("text")) {
            return true;
        }
        node = node.parentNode;
    }
    return false;
}
        
function adjustStartOffset(range) {
    var text = range.startContainer.data;
    var i = range.startOffset - 1;
            
    // if in a word, move the start offset backwards
    if (text.charAt(i).match(/\S/)) {
        while (i >= 0 && text.charAt(i).match(/\S/)) {
            i--;
        }
        i++; // advance to start of first character
    }
    else {
        // if in a space, move the start offset forwards
        while (i < text.length - 1 && text.charAt(i).match(/\s/)) {
            i++;
        }
    }
    // sanity check the bounds
    if (i > text.length) { i = text.length; }
    if (i < 0) { i = 0; }
            
    if (i != range.startOffset) {
        range.setStart(range.startContainer, i);
    }
}
        
function adjustEndOffset(range) {
    var text = range.endContainer.data;
    var i = range.endOffset - 1;
            
    // if in a word, move the end offset forwards
    if (text.charAt(i).match(/\S/)) {
        while (i < text.length - 1 && text.charAt(i).match(/\S/)) {
            i++;
        }
    }
    else {
        // if in a space, move the end offset backwards
        while (i > 0 && text.charAt(i).match(/\s/)) {
            i--;
        }
        i++;
    }
    // sanity check the bounds
    if (i > text.length) { i = text.length; }
    if (i < 0) { i = 0; }
        
    if (i != range.endOffset) {
        range.setEnd(range.endContainer, i);
    }
}
        
function extractText(frag) {
    // walk the fragment tree and select text nodes
    var node, text = "";
    var walk = document.createTreeWalker(frag, NodeFilter.SHOW_TEXT, null, false);
    while (node = walk.nextNode()) {
        text += " " + node.data;
    }
    return text.trim();
}
        
function formatSpan(text) {
    var span_o ='<span class="coded_i_new">';
    var span_c = '</span>';
    var regex = /(<([^>]+)>)/ig;

    var clean = text.replace(regex, "");
    var diff = (text.length - clean.length) % (span_o.length + span_c.length);
            
    if (diff == 0) {
        return span_o + clean + span_c;
    }
    else if (diff == span_o.length) {
        return span_o + clean;
    }
    else if (diff == spac_c.length) {
        return clean + span_c;
    }
    return clean;
}
        
function clearLast() {
    if (queue.length == 0) {
        return;
    }
    var span = document.getElementById('stmt');
    span.innerHTML = queue.pop();
}
        
function clearAll() {
    if (queue.length == 0) {
        return;
    }
            
    // clear the queue including the last element
    for (i = queue.length; i > 1; i--) {
        queue.pop();
    }
    var span = document.getElementById('stmt');
    span.innerHTML = queue.pop();
}

function enableDraggableSpan(span) {
    if (span == null) {
	return;
    }
    span.setAttribute("id", 't' + spanCounter);
    span.setAttribute("ondragstart", "dragSpan(event)");
    span.setAttribute("ondrop", "dropSpan(event)");
    span.setAttribute("ondragover", "allowDropSpan(event)");
    span.setAttribute("draggable", "true");
    span.setAttribute("onclick", "selectSpan(this)");
}
