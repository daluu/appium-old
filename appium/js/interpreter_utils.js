/**
 * interpreter_utils.js
 *   utility methods the get loaded for use in the command line
 *   interpreter.
 *   PLEASE be sure to code this file so that any line can be
 *   wrapped up to the previous. This file is loaded via
 *   "".join(file.read().splitlines())
 *   so line comments "//" should not be used
 */

/**
 * dir - basically like python's dir method
 *  returns a list of attributes on an object
 */
function dir(obj) {
  var attributes = [];
  for (var attr in obj) {
    attributes.push(attr.toString());
  }
  attributes.sort();
  return attributes.join(", ");
}


/* gets printed by the start of interpreter */
"\nUtility methods available to you:\n\n" +
"dir - function that displays the list of attributes on an object\n" +
"    - usage: dir(target)";
