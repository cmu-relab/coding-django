
/* Entity Library Functions, Travis Breaux, 6 NOV 2015 */

function createEntity(name) {
    // create the entity div
    var div = document.createElement("div");
    div.id = name;
    div.className = "entity";
    
    // create the branch icon
    var branch = document.createElement("div");
    branch.setAttribute("class", "branch");
    div.appendChild(branch);
    
    // label the div with the entity name
    var label = document.createElement("div");
    label.setAttribute("ondragstart", "dragOnto(event)");
    label.setAttribute("ondrop", "dropOnto(event)");
    label.setAttribute("ondragover", "allowDropOnto(event)");
    label.setAttribute("draggable", "true");
    label.setAttribute("class", "label");
    label.setAttribute("onclick", "selectEntity(this)");
    label.appendChild(document.createTextNode(name));
    div.appendChild(label);
    return div;
}

function insertEntity(parentDiv, childDiv) {
    // find the insertion point, insert and return the entity
    var i;
    for (i=0; i<parentDiv.children.length; i++) {
        
        // if the entity exists, return it without inserting duplicate
        if (parentDiv.children[i].id.localeCompare(childDiv.id) == 0) {
            return parentDiv.children[i];
        }
        
        // else, insert the entity and return it
        else if (parentDiv.children[i].id.localeCompare(childDiv.id) > 0) {
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
