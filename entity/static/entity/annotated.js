/* Entity Library Functions, Travis Breaux, 6 NOV 2015 */

function allowDropSpan(ev) {
    ev.preventDefault();
}

function dragSpan(ev) {
    var list = [];
    
    // compile list from selected spans, if any
    var spans = document.getElementsByTagName("span");
    for (var i=0; i<spans.length; i++) {
	if (spans[i].className.indexOf("selected ") >= 0) {
	    list.push(spans[i].getAttribute("id"));
	}
    }
    
    // if no selected spans, drag the target span by default
    if (list.length == 0) {
	list.push(ev.target.getAttribute("id"));
    }
    //console.log("Dragging: ", list);
    ev.dataTransfer.setData("text", list.join());
}

function dropSpan(ev) {
    ev.preventDefault();
    
    // find target div, create if none exists
    var iframe = window.parent.document.getElementById("ontology_frame");
    var if_doc = iframe.contentDocument || iframe.contentWindow.document;

    var top = if_doc.getElementById("top");
    var targetName = ev.target.getAttribute("alt").split(",");
    var targetDiv = [];
    
    for (var i=0; i<targetName.length; i++) {
	targetDiv[i] = if_doc.getElementById(targetName[i]);
	if (targetDiv[i] == null) {
	    targetDiv[i] = createEntity(targetName[i]);
	    //console.log("Created target: ", targetName);
	    insertEntity(top, targetDiv[i]);
	}
    }
    
    // find source divs or create, if none exists
    var sourceId = ev.dataTransfer.getData("text").split(",");
    var sourceName = [];
    for (var i=0; i<sourceId.length; i++) {
	var sourceDiv = document.getElementById(sourceId[i]);
	var names = sourceDiv.getAttribute("alt").split(",");
	for (var j=0; j<names.length; j++) {
	    sourceName.push(names[j]);
	}

	// deselect the source span, if selected
	var sourceSpan = document.getElementById(sourceId[i]);
	sourceSpan.className = sourceSpan.className.replace("selected ", "");
    }
    for (var i=0; i<sourceName.length; i++) {
	
	for (var j=0; j<targetName.length; j++) {
	    if (targetName[j] == sourceName[i]) {
		continue;
	    }
	    var sourceDiv = createEntity(sourceName[i]);
	    //console.log("Created source: ", sourceName[i]);

	    insertEntity(targetDiv[j], sourceDiv);
	    //console.log("Linked source to target: ", targetName[j]);
	}
	
	// remove source div from top-level, if exists
	for (var j=0; j<top.children; j++) {
	    var id = top.children[i].id;
	    if (id.localeCompare(sourceName[i]) == 0) {
		top.removeChild(ontology.children[i]);
		break;
	    }
	}
    }
}

function selectSpan(span) {
    if (span.className.indexOf("selected ") < 0) {
	span.className = "selected " + span.className;
    }
    else {
	span.className = span.className.replace("selected ", "");
    }
}

function enableDraggableSpans() {
    // iterate all spans and make drag and drop targets
    var span = document.getElementsByTagName("span");
    
    for (var i=0; i <span.length; i++) {
	if (span[i].className.indexOf("coded_i") > -1) {
	    span[i].setAttribute("id", "s" + i);
	    toggleDraggableSpan(span[i]);
	}
    }
}
