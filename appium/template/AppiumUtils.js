// Misc utils

UIAElementNil.prototype.type = function() {
    return "UIAElementNil";
}

UIAElement.prototype.type = function() {
    var type = this.toString();
    return type.substring(8, type.length - 1);
}

UIAElement.prototype.hasChildren = function() {
    var type = this.type();
    // NOTE: UIALink/UIAImage/UIAElement can have children
    return !(type === "UIAStaticText" || type === "UIATextField"
            || type === "UIASecureTextField" || type === "UIAButton"
            || type === "UIASwitch" || type === "UIAElementNil");
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

UIAElement.prototype.matchesTagNameAndText = function(tagName, text) {
    if (!this.matchesTagName(tagName))
        return false;
    var name = this.name();
    if (name)
        name = name.trim();
    if (name === text)
        return true;
    var value = this.value();
    if (value)
        value = String(value).trim();
    return value === text;
}

// Finding elements

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

// if multiple elements match it will return the first one that is visible
// or the last one if none is visible
UIAElement.prototype.findElement = function(tagName, text) {
    var foundElement;
    var foundVisible = false;
    var findElement = function(element, tagName, text) {
        var children = element.elements();
        var numChildren = children.length;
        for ( var i = 0; i < numChildren; i++) {
            var child = children[i];
            if (child.matchesTagNameAndText(tagName, text)) {
                foundElement = child;
                foundVisible = child.isVisible();
                if (foundVisible)
                    return;
            }
            if (child.hasChildren()) { // big optimization
                findElement(child, tagName, text);
                if (foundVisible)
                    return;
            }
        }
    }
    findElement(this, tagName, text)
    return foundElement;
}

UIAElement.prototype.findElementAndSetKey = function(tagName, text, key) {
    var foundElement = this.findElement(tagName, text);
    if (foundElement)
        elements[key] = foundElement;
    return foundElement;
}

// getPageSource

function tabSpacing(depth) {
    switch (depth) {
    case 0:
        return "";
    case 1:
        return "  ";
    case 2:
        return "    ";
    case 3:
        return "      ";
    case 4:
        return "        ";
    case 5:
        return "          ";
    }
    var space = "";
    for ( var i = 0; i < depth; i++)
        space += "  ";
    return space;
}

UIAElement.prototype.getPageSource = function() {
    var source = "";
    var appendPageSource = function(element, depth) {
        var children = element.elements();
        var numChildren = children.length;
        for ( var i = 0; i < numChildren; i++) {
            var child = children[i];
            appendElementSource(child, depth);
            if (child.hasChildren()) // big optimization
                appendPageSource(child, depth + 1);
        }
    }
    var appendElementSource = function(element, depth) {
        source += tabSpacing(depth) + element.type() + ':'
        var label = element.label();
        var name = element.name();
        var value = element.value();
        if (label)
            source += ' "' + label + '"';
        if (name)
            source += ' NAME:"' + name + '"';
        if (value)
            source += ' VALUE:"' + value + '"';
        var r = element.rect();
        source += ' {{' + Math.round(r.origin.x) + ',' + Math.round(r.origin.y)
                + '},{' + Math.round(r.size.width) + ','
                + Math.round(r.size.height) + '}}';
        // show element state
        source += ' [enabled=' + element.isEnabled() + ',valid='
                + element.isValid() + ',visible=' + element.isVisible() + ']';
        source += '\n'
    }
    var target = UIATarget.localTarget();
    try {
        target.pushTimeout(0);
        appendPageSource(this, 0)
    } finally {
        target.popTimeout();
    }
    return source;
}

// screen orientation

function getScreenOrientation() {
    var orientation = UIATarget.localTarget().deviceOrientation();
    switch (orientation) {
    case UIA_DEVICE_ORIENTATION_UNKNOWN:
        return "UNKNOWN";
    case UIA_DEVICE_ORIENTATION_PORTRAIT:
        return "PORTRAIT";
    case UIA_DEVICE_ORIENTATION_PORTRAIT_UPSIDEDOWN:
        return "PORTRAIT";
    case UIA_DEVICE_ORIENTATION_LANDSCAPELEFT:
        return "LANDSCAPE";
    case UIA_DEVICE_ORIENTATION_LANDSCAPERIGHT:
        return "LANDSCAPE";
    case UIA_DEVICE_ORIENTATION_FACEUP:
        return "UNKNOWN";
    case UIA_DEVICE_ORIENTATION_FACEDOWN:
        return "UNKNOWN";
    }
    throw new Error("unsupported orientation: " + orientation);
}

function setScreenOrientation(orientation) {
    var target = UIATarget.localTarget();
    if (orientation === "LANDSCAPE")
        target.setDeviceOrientation(UIA_DEVICE_ORIENTATION_LANDSCAPELEFT);
    else if (orientation === "PORTRAIT")
        target.setDeviceOrientation(UIA_DEVICE_ORIENTATION_PORTRAIT);
    else
        throw new Error("unsupported orientation: " + orientation);
    return getScreenOrientation();
}

// getText

UIAElement.prototype.getText = function() {
    // TODO: tune as more cases are found
    var text;
    var type = this.type();
    if (type === "UIATextField" || type === "UIASecureTextField"
            || type === "UIATextView") {
        // value takes precedence for text fields
        text = this.value();
        if (!text)
            text = this.name();
    } else {
        // name takes preference for others
        // i.e. <h1>title</h1> becomes: name="title", value="1"
        text = this.name();
        if (!text)
            text = this.value();
    }
    return text;
}

// timeouts

function setImplicitWait(seconds) {
    UIATarget.localTarget().setTimeout(seconds);
}

// Keyboard

sendKeysToActiveElement = function(keys) {
    if (hasSpecialKeys(keys)) {
        sendKeysToActiveElementSpecial(keys);
    } else {
        var keyboard = UIATarget.localTarget().frontMostApp().keyboard();
        keyboard.typeString(keys);
    }
}

hasSpecialKeys = function(keys) {
    var numChars = keys.length;
    for ( var i = 0; i < numChars; i++)
        if (isSpecialKey(keys.charAt(i)))
            return true;
    return false;
}

sendKeysToActiveElementSpecial = function(keys) {
    var keyboard = UIATarget.localTarget().frontMostApp().keyboard();
    var numChars = keys.length;
    for ( var i = 0; i < numChars; i++)
        typeKey(keyboard, keys.charAt(i));
}

// handles some of the special keys in org.openqa.selenium.Keys

isSpecialKey = function(k) {
    if (k === '\uE003') // DELETE
        return true;
    else if (k === '\uE006' || k === '\uE007') // RETURN ENTER
        return true;
    return false;
}

typeKey = function(keyboard, k) {
    if (k === '\uE003') // DELETE
        keyboard.keys()["Delete"].tap();
    else if (k === '\uE006' || k === '\uE007') // RETURN ENTER
        keyboard.buttons()["Go"].tap();
    else
        keyboard.typeString(String(k)); // regular key
}

// location/size

UIAElement.prototype.getElementLocation = function() {
    var origin = this.rect().origin;
    return '{"x":' + origin.x + ',"y":' + origin.y + '}';
}

UIAElement.prototype.getElementSize = function() {
    var size = this.rect().size;
    return '{"width":' + size.width + ',"height":' + size.height + '}';
}

// touch

// does a flick in the middle of the screen of size 1/4 of screen
// using the direction corresponding to xSpeed/ySpeed
touchFlickFromSpeed = function(xSpeed, ySpeed) {
    // get x, y of vector that provides the direction given by xSpeed/ySpeed and
    // has length .25
    var mult = Math.sqrt((0.25 * 0.25) / (xSpeed * xSpeed + ySpeed * ySpeed));
    var x = mult * xSpeed;
    var y = mult * ySpeed;

    // translate to flick in the middle of the screen
    var options = {
        startOffset : {
            x : 0.5 - x / 2,
            y : 0.5 - y / 2
        },
        endOffset : {
            x : 0.5 + x / 2,
            y : 0.5 + y / 2
        }
    };

    var mainWindow = UIATarget.localTarget().frontMostApp().mainWindow();
    mainWindow.flickInsideWithOptions(options);
}
