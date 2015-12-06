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
	    list.push(spans[i].id + ":" + spans[i].innerHTML);
	}
    }
    
    // if no selected spans, drag the target span by default
    if (list.length == 0) {
	list.push(ev.target.id + ":" + ev.target.innerHTML);
    }
    //console.log("Dragging: ", list);
    ev.dataTransfer.setData("text", list.join());
}

function dropSpan(ev) {
    ev.preventDefault();
    
    // find target div, create if none exists
    var iframe = window.parent.document.getElementById("ontology_frame");
    var if_doc = iframe.contentDocument || iframe.contentWindow.document;

    var top = if_doc.getElementById("e0");
    var targetName = ev.target.getAttribute("alt").split(",");
    var targetDiv = [];

    for (var i=0; i<targetName.length; i++) {
	var div = getEntitiesByName(targetName[i]);

	// if target does not exist, create and add to top
	if (div.length == 0) {
	    div = [createNewEntity(targetName[i])];
	    //console.log("Created target: ", div[0].id + " " + targetName[i]);
	    insertEntity(top, div[0]);
	}
	else {
	    //console.log("Found target: ", div + " " + targetName[i]);
	}
	targetDiv = targetDiv.concat(div);
    }
    
    // find source divs or create, if none exists
    var source = ev.dataTransfer.getData("text").split(",");
    var sourceName = [];
    for (var i=0; i<source.length; i++) {
	var id_name = source[i].split(":");
	var sourceSpan = document.getElementById(id_name[0]);
	var names = sourceSpan.getAttribute("alt").split(",");
	
	for (var j=0; j<names.length; j++) {
	    sourceName.push(names[j]);
	}

	// deselect the source span, if selected
	sourceSpan.className = sourceSpan.className.replace("selected ", "");
    }
    for (var i=0; i<sourceName.length; i++) {
	for (var j=0; j<targetDiv.length; j++) {
	    var targetName = targetDiv[j].children[1].innerHTML;
	    if (targetName.localeCompare(sourceName[i]) == 0) {
		continue;
	    }
	    var sourceDiv = createNewEntity(sourceName[i]);
	    //console.log("Created source: ", sourceName[i]);

	    insertEntity(targetDiv[j], sourceDiv);
	    //console.log("Linked source to target: ", targetName);
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

