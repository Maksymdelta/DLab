/***************************************************************************

Copyright (c) 2016, EPAM SYSTEMS INC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

****************************************************************************/

package com.epam.dlab.exception;

/** Exception for the error of initialization.
 */
public class InitializationException extends GenericException {

	private static final long serialVersionUID = -666390278139508248L;

	/** Constructs a new exception.
	 * @param message error message.
	 */
	public InitializationException(String message) {
		super(message);
	}

	/** Constructs a new exception.
	 * @param cause the cause.
	 */
	public InitializationException(Throwable cause) {
		super(cause);
	}

	/** Constructs a new exception.
	 * @param message error message.
	 * @param cause the cause.
	 */
	public InitializationException(String message, Throwable cause) {
		super(message, cause);
	}
}
