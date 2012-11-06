UIAElementNil.prototype.type = function() {
    return "UIAElementNil";
}

UIAElement.prototype.type = function() {
    var type = this.toString();
    return type.substring(8, type.length - 1);
}

UIAElement.prototype.hasChildren = function() {
    var type = this.type();
    // NOTE: UIALink can have UIAStaticText child
    return !(type === "UIAImage" || type === "UIAStaticText"
	    || type === "UIATextField" || type === "UIASecureTextField"
	    || type === "UIAButton" || type === "UIASwitch"
	    || type === "UIAElementNil" || type == "UIAElement");
}

UIAElement.prototype.matchesTagName = function(tagName) {
    var type = this.type();
    // ELEMENT, LINK, BUTTON, TEXT_FIELD, SECURE_TEXT_FIELD, TEXT
    if (tagName === "element")
	return true;
    if (tagName === "link")
	return type === "UIALink";
    if (tagName === "button")
	return type === "UIAButton";
    if (tagName === "textField")
	return type === "UIATextField";
    if (tagName === "secureTextField")
	return type === "UIASecureTextField";
    if (tagName === "staticText")
	return type === "UIAStaticText";
    throw new Error("add support for: " + tagName);
}

UIAElement.prototype.findElements = function(tagName) {
    var elements = new Array();
    var findElements = function(element, tagName) {
	var children = element.elements();
	var numChildren = children.length;
	for ( var i = 0; i < numChildren; i++) {
	    var child = children[i];
	    if (child.matchesTagName(tagName))
		elements.push(child);
	    if (child.hasChildren()) // big optimization
		findElements(child, tagName);
	}
    }
    findElements(this, tagName)
    return elements;
}