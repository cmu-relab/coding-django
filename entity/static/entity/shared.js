
/* Entity Library Functions, Travis Breaux, 6 NOV 2015 */
var entityCounter = 1;

function createNewEntity(name) {
    var id = "e" + entityCounter;
    return createEntity(id, name);
}

function createEntity(id, name, rel) {
    rel = typeof rel != 'undefined' ? rel : "rel_s";
    
    // create the entity div
    var div = document.createElement("div");
    div.id = id;
    div.className = "entity";

    // increase the entity counter
    entityCounter++;
    
    // create the branch icon
    var branch = document.createElement("div");
    branch.setAttribute("class", "branch " + rel);
    div.appendChild(branch);
    
    // label the div with the entity name
    var label = document.createElement("div");
    label.setAttribute("ondragstart", "dragOnto(event)");
    label.setAttribute("ondrop", "dropOnto(event)");
    label.setAttribute("ondragover", "allowDropOnto(event)");
    label.setAttribute("draggable", "true");
    label.setAttribute("class", "label");
    label.setAttribute("onclick", "selectEntity(event, this)");
    label.appendChild(document.createTextNode(name));
    div.appendChild(label);
    return div;
}

function insertEntity(parentDiv, childDiv) {
    var childName = childDiv.children[1].innerHTML;
    
    // find the insertion point, insert and return the entity
    for (var i=0; i<parentDiv.children.length; i++) {
	if (parentDiv.children[i].className != "entity") {
	    continue;
	}
	
        var siblingName = parentDiv.children[i].children[1].innerHTML;
        // if the entity exists, merge offspring, return existing entity
        if (siblingName.localeCompare(childName) == 0) {
	    
	    var existing = parentDiv.children[i];
	    for (var j=0; j<childDiv.children.length; j++) {
		if (childDiv.children[j].className == "entity") {
		    insertEntity(existing, childDiv.children[j]);
		}
	    }
            return existing;
        }
        
        // else, insert the entity and return it
        else if (siblingName.localeCompare(childName) > 0) {
            parentDiv.insertBefore(childDiv, parentDiv.children[i]);
            return parentDiv.children[i];
        }
    }
    
    // else the entity is inserted as the last element
    parentDiv.appendChild(childDiv);
    return parentDiv.children[parentDiv.children.length - 1];
}

function toggleSelectableDiv(div, index) {
    if (div.id != null && div.id.startsWith("text")) {
	if (div.style.cursor == "default") {
	    div.removeAttribute("onkeypress");
	    div.removeAttribute("tabindex");
	    div.removeAttribute("style");
	}
	else {
	    div.setAttribute("onkeypress", "select_text(event, this)");
	    div.setAttribute("tabindex", index);
	    div.style.cursor = "default";
	}
    }
}

function getEntitiesByName(name) {
    var iframe = window.parent.document.getElementById("ontology_frame");
    var if_doc = iframe.contentDocument || iframe.contentWindow.document;

    var div = if_doc.getElementsByTagName("div");
    var entities = [];
    for (var i=0; i<div.length; i++) {
	if (div[i].className == "entity") {
	    if (div[i].children[1].innerHTML.localeCompare(name) == 0) {
		entities.push(div[i]);
	    }
	}
    }
    return entities;
}

function toggleDraggableSpan(span) {
    if (span.className.indexOf("coded_i") < 0) {
	return;
    }
    else if (span.hasAttribute("draggable")) {
	span.removeAttribute("ondragstart");
	span.removeAttribute("ondrop");
	span.removeAttribute("ondragover");
	span.removeAttribute("draggable");
	span.removeAttribute("onclick");
    }
    else {
	span.setAttribute("ondragstart", "dragSpan(event)");
	span.setAttribute("ondrop", "dropSpan(event)");
	span.setAttribute("ondragover", "allowDropSpan(event)");
	span.setAttribute("draggable", "true");
	span.setAttribute("onclick", "selectSpan(this)");
    }
}
