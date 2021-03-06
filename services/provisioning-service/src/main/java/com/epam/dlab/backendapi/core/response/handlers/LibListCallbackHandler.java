/*
 * Copyright (c) 2017, EPAM SYSTEMS INC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.epam.dlab.backendapi.core.response.handlers;

import com.epam.dlab.UserInstanceStatus;
import com.epam.dlab.backendapi.core.commands.DockerAction;
import com.epam.dlab.dto.exploratory.LibListStatusDTO;
import com.epam.dlab.exceptions.DlabException;
import com.epam.dlab.rest.client.RESTService;
import com.epam.dlab.rest.contracts.ApiCallbacks;
import com.fasterxml.jackson.databind.JsonNode;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Handler of docker response for the request the list of libraries.
 */
public class LibListCallbackHandler extends ResourceCallbackHandler<LibListStatusDTO> {

    /**
     * Name of node in response "file".
     */
    private static final String FILE = "file";

    /**
     * The name of docker image.
     */
    private final String imageName;

    /**
     * Instantiate handler for process of docker response for list of libraries.
     *
     * @param selfService REST pointer for Self Service.
     * @param action      docker action.
     * @param uuid        request UID.
     * @param user        the name of user.
     * @param imageName   the name of docker image.
     */
    public LibListCallbackHandler(RESTService selfService, DockerAction action, String uuid, String user, String imageName) {
        super(selfService, user, uuid, action);
        this.imageName = imageName;
    }

    @Override
    protected String getCallbackURI() {
        return ApiCallbacks.UPDATE_LIBS_URI;
    }

    @Override
    protected LibListStatusDTO parseOutResponse(JsonNode resultNode, LibListStatusDTO status) throws DlabException {
        if (UserInstanceStatus.FAILED == UserInstanceStatus.of(status.getStatus())) {
            return status;
        }
        if (resultNode == null) {
            throw new DlabException("Can't handle response result node is null");
        }

        JsonNode resultFileNode = resultNode.get(FILE);
        if (resultFileNode == null) {
            throw new DlabException("Can't handle response without property " + FILE);
        }

        Path path = Paths.get(resultFileNode.asText()).toAbsolutePath();
        if (path.toFile().exists()) {
            try {
                status.withLibs(new String(Files.readAllBytes(path)));
                Files.delete(path);
                return status;
            } catch (IOException e) {
                throw new DlabException("Can't read file " + path + " : " + e.getLocalizedMessage(), e);
            }
        } else {
            throw new DlabException("Can't handle response. The file " + path + " does not exist");
        }
    }

    @Override
    protected LibListStatusDTO getBaseStatusDTO(UserInstanceStatus status) {
        return super.getBaseStatusDTO(status)
                .withImageName(imageName);
    }
}
