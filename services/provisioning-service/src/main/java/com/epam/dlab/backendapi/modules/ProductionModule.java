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

package com.epam.dlab.backendapi.modules;

import com.epam.dlab.backendapi.ProvisioningServiceApplicationConfiguration;
import com.epam.dlab.backendapi.core.DockerWarmuper;
import com.epam.dlab.backendapi.core.MetadataHolder;
import com.epam.dlab.backendapi.core.commands.CommandExecutor;
import com.epam.dlab.backendapi.core.commands.ICommandExecutor;
import com.epam.dlab.constants.ServiceConsts;
import com.epam.dlab.rest.client.RESTService;
import com.google.inject.name.Names;
import io.dropwizard.setup.Environment;

import com.epam.dlab.ModuleBase;

/**
 * Production class for an application configuration of SelfService.
 */
public class ProductionModule extends ModuleBase<ProvisioningServiceApplicationConfiguration> {

    /**
     * Instantiates an application configuration of SelfService for production environment.
     *
     * @param configuration application configuration of SelfService.
     * @param environment   environment of SelfService.
     */
    public ProductionModule(ProvisioningServiceApplicationConfiguration configuration, Environment environment) {
        super(configuration, environment);
    }

    @Override
    protected void configure() {
        bind(ProvisioningServiceApplicationConfiguration.class).toInstance(configuration);

        bind(RESTService.class).annotatedWith(Names.named(ServiceConsts.SECURITY_SERVICE_NAME))
                .toInstance(configuration.getSecurityFactory()
                        .build(environment, ServiceConsts.SECURITY_SERVICE_NAME, ServiceConsts.PROVISIONING_USER_AGENT));

        bind(RESTService.class).toInstance(configuration.getSelfFactory().build(environment, ServiceConsts.SELF_SERVICE_NAME));
        bind(MetadataHolder.class).to(DockerWarmuper.class);
        bind(ICommandExecutor.class).to(CommandExecutor.class).asEagerSingleton();
    }
}
