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

package com.epam.dlab.backendapi.dao;

import com.epam.dlab.UserInstanceStatus;
import com.epam.dlab.backendapi.util.DateRemoverUtil;
import com.epam.dlab.dto.StatusEnvBaseDTO;
import com.epam.dlab.dto.UserInstanceDTO;
import com.epam.dlab.dto.exploratory.ExploratoryStatusDTO;
import com.epam.dlab.exceptions.DlabException;
import com.google.inject.Singleton;
import com.mongodb.client.FindIterable;
import com.mongodb.client.result.UpdateResult;
import lombok.extern.slf4j.Slf4j;
import org.bson.Document;
import org.bson.conversions.Bson;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import static com.mongodb.client.model.Filters.and;
import static com.mongodb.client.model.Filters.eq;
import static com.mongodb.client.model.Projections.*;
import static com.mongodb.client.model.Updates.set;
import static org.apache.commons.lang3.StringUtils.EMPTY;

/**
 * DAO for user exploratory.
 */
@Slf4j
@Singleton
public class ExploratoryDAO extends BaseDAO {
    public static final String EXPLORATORY_ID = "exploratory_id";
    public static final String COMPUTATIONAL_RESOURCES = "computational_resources";
    static final String EXPLORATORY_NAME = "exploratory_name";
    static final String UPTIME = "up_time";
    private static final String COMPUTATIONAL_NAME = "computational_name";
    private static final String EXPLORATORY_URL = "exploratory_url";
    private static final String EXPLORATORY_URL_DESC = "description";
    private static final String EXPLORATORY_URL_URL = "url";
    private static final String EXPLORATORY_USER = "exploratory_user";
    private static final String EXPLORATORY_PASSWORD = "exploratory_pass";
    private static final String EXPLORATORY_PRIVATE_IP = "private_ip";

    public ExploratoryDAO() {
        log.info("{} is initialized", getClass().getSimpleName());
    }

    static Bson exploratoryCondition(String user, String exploratoryName) {
        return and(eq(USER, user), eq(EXPLORATORY_NAME, exploratoryName));
    }

    static Bson runningExploratoryAndComputationalCondition(String user, String exploratoryName, String computationalName) {
        return and(eq(USER, user), and(eq(EXPLORATORY_NAME, exploratoryName),
                eq(STATUS, "running"),
                eq(COMPUTATIONAL_RESOURCES + "." + COMPUTATIONAL_NAME, computationalName),
                eq(COMPUTATIONAL_RESOURCES + "." + STATUS, "running")));
    }

    /**
     * Finds and returns the list of user resources.
     *
     * @param user name
     * @return
     */
    public Iterable<Document> findExploratory(String user) {
        return find(USER_INSTANCES, eq(USER, user),
                fields(exclude(ExploratoryLibDAO.EXPLORATORY_LIBS,
                        ExploratoryLibDAO.COMPUTATIONAL_LIBS)));
    }

    /**
     * Finds and returns the unique id for exploratory.
     *
     * @param user            user name.
     * @param exploratoryName the name of exploratory.
     * @throws DlabException
     */
    public String fetchExploratoryId(String user, String exploratoryName) throws DlabException {
        return findOne(USER_INSTANCES,
                exploratoryCondition(user, exploratoryName),
                fields(include(EXPLORATORY_ID), excludeId()))
                .orElse(new Document())
                .getOrDefault(EXPLORATORY_ID, EMPTY).toString();
    }

    /**
     * Finds and returns the status of exploratory.
     *
     * @param user            user name.
     * @param exploratoryName the name of exploratory.
     * @throws DlabException
     */
    public UserInstanceStatus fetchExploratoryStatus(String user, String exploratoryName) throws DlabException {
        return UserInstanceStatus.of(
                findOne(USER_INSTANCES,
                        exploratoryCondition(user, exploratoryName),
                        fields(include(STATUS), excludeId()))
                        .orElse(new Document())
                        .getOrDefault(STATUS, EMPTY).toString());
    }

    /**
     * Finds and returns the info of all user's notebooks.
     *
     * @param user user name.
     * @throws DlabException
     */
    public List<UserInstanceDTO> fetchExploratoryFields(String user) throws DlabException {
        FindIterable<Document> docs = getCollection(USER_INSTANCES)
                .find(eq(USER, user))
                .projection(fields(exclude(COMPUTATIONAL_RESOURCES)));
        List<UserInstanceDTO> instances = new ArrayList<>();
        for (Document d : docs) {
            instances.add(convertFromDocument(d, UserInstanceDTO.class));
        }
        return instances;
    }

    /**
     * Finds and returns the info of exploratory.
     *
     * @param user            user name.
     * @param exploratoryName the name of exploratory.
     */
    public UserInstanceDTO fetchExploratoryFields(String user, String exploratoryName) {
        Optional<UserInstanceDTO> opt = findOne(USER_INSTANCES,
                exploratoryCondition(user, exploratoryName),
                fields(exclude(COMPUTATIONAL_RESOURCES)),
                UserInstanceDTO.class);

        if (opt.isPresent()) {
            return opt.get();
        }
        throw new DlabException("Exploratory instance for user " + user + " with name " + exploratoryName + " not found.");
    }

    /**
     * Finds and returns the info of exploratory.
     *
     * @param user              user name.
     * @param exploratoryName   name of exploratory.
     * @param computationalName name of cluster
     */
    public UserInstanceDTO fetchExploratoryFields(String user, String exploratoryName, String computationalName) {
        Optional<UserInstanceDTO> opt = findOne(USER_INSTANCES,
                runningExploratoryAndComputationalCondition(user, exploratoryName, computationalName),
                UserInstanceDTO.class);

        if (opt.isPresent()) {
            return opt.get();
        }
        throw new DlabException(String.format("Running notebook %s with running cluster %s not found for user %s",
                exploratoryName, computationalName, user));
    }

    /**
     * Inserts the info about notebook into Mongo database.
     *
     * @param dto the info about notebook
     * @throws DlabException
     */
    public void insertExploratory(UserInstanceDTO dto) throws DlabException {
        insertOne(USER_INSTANCES, dto);
    }

    /**
     * Updates the status of exploratory in Mongo database.
     *
     * @param dto object of exploratory status info.
     * @return The result of an update operation.
     * @throws DlabException
     */
    public UpdateResult updateExploratoryStatus(StatusEnvBaseDTO<?> dto) throws DlabException {
        return updateOne(USER_INSTANCES,
                exploratoryCondition(dto.getUser(), dto.getExploratoryName()),
                set(STATUS, dto.getStatus()));
    }

    /**
     * Updates the info of exploratory in Mongo database.
     *
     * @param dto object of exploratory status info.
     * @return The result of an update operation.
     * @throws DlabException
     */
    @SuppressWarnings("serial")
    public UpdateResult updateExploratoryFields(ExploratoryStatusDTO dto) throws DlabException {
        Document values = new Document(STATUS, dto.getStatus()).append(UPTIME, dto.getUptime());
        if (dto.getInstanceId() != null) {
            values.append(INSTANCE_ID, dto.getInstanceId());
        }
        if (dto.getErrorMessage() != null) {
            values.append(ERROR_MESSAGE, DateRemoverUtil.removeDateFormErrorMessage(dto.getErrorMessage()));
        }
        if (dto.getExploratoryId() != null) {
            values.append(EXPLORATORY_ID, dto.getExploratoryId());
        }

        if (dto.getExploratoryUrl() != null) {
            values.append(EXPLORATORY_URL, dto.getExploratoryUrl().stream()
                    .map(url -> {
                                LinkedHashMap<String, String> map = new LinkedHashMap<>();
                                map.put(EXPLORATORY_URL_DESC, url.getDescription());
                                map.put(EXPLORATORY_URL_URL, url.getUrl());
                                return map;
                            }
                    ).collect(Collectors.toList()));
        } else if (dto.getPrivateIp() != null) {
            UserInstanceDTO inst = fetchExploratoryFields(dto.getUser(), dto.getExploratoryName());
            if (!inst.getPrivateIp().equals(dto.getPrivateIp())) { // IP was changed
                if (inst.getExploratoryUrl() != null) {
                    values.append(EXPLORATORY_URL, inst.getExploratoryUrl().stream()
                            .map(url -> {
                                        LinkedHashMap<String, String> map = new LinkedHashMap<>();
                                        map.put(EXPLORATORY_URL_DESC, url.getDescription());
                                        map.put(EXPLORATORY_URL_URL, url.getUrl().replace(inst.getPrivateIp(), dto.getPrivateIp()));
                                        return map;
                                    }
                            ).collect(Collectors.toList()));
                }
            }
        }

        if (dto.getPrivateIp() != null) {
            values.append(EXPLORATORY_PRIVATE_IP, dto.getPrivateIp());
        }
        if (dto.getExploratoryUser() != null) {
            values.append(EXPLORATORY_USER, dto.getExploratoryUser());
        }
        if (dto.getExploratoryPassword() != null) {
            values.append(EXPLORATORY_PASSWORD, dto.getExploratoryPassword());
        }
        return updateOne(USER_INSTANCES,
                exploratoryCondition(dto.getUser(), dto.getExploratoryName()),
                new Document(SET, values));
    }
}