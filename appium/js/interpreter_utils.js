 /**
 *	Copyright 2012 Appium Committers
 *
 *	Licensed to the Apache Software Foundation (ASF) under one
 *	or more contributor license agreements.  See the NOTICE file
 *	distributed with this work for additional information
 *	regarding copyright ownership.  The ASF licenses this file
 *	to you under the Apache License, Version 2.0 (the
 *	"License"); you may not use this file except in compliance
 *	with the License.  You may obtain a copy of the License at
 *
 *	http://www.apache.org/licenses/LICENSE-2.0
 *
 *	Unless required by applicable law or agreed to in writing,
 *	software distributed under the License is distributed on an
 *	"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 *	KIND, either express or implied.  See the License for the
 *	specific language governing permissions and limitations
 *	under the License.
 */

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
