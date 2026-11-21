// Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//

#define CARB_EXPORTS

#include <carb/PluginUtils.h>

#include <omni/ext/IExt.h>

#include <pmatx/player/core/IPmatxPlayerCoreInterface.h>

#include <unordered_map>

const struct carb::PluginImplDesc pluginImplDesc = { "pmatx.player.core.plugin",
                                                     "An example C++ extension.", "NVIDIA",
                                                     carb::PluginHotReload::eEnabled, "dev" };

namespace pmatx::player::core
{

class ExampleBoundImplementation : public IPmatxPlayerCoreInterface
{
public:
    void registerPmatxPlayerCoreObject(carb::ObjectPtr<IPmatxPlayerCoreObjectInterface>& object) override
    {
        if (object)
        {
            m_registeredObjectsById[object->getId()] = object;
        }
    }

    void deregisterPmatxPlayerCoreObject(carb::ObjectPtr<IPmatxPlayerCoreObjectInterface>& object) override
    {
        if (object)
        {
            const auto& it = m_registeredObjectsById.find(object->getId());
            if (it != m_registeredObjectsById.end())
            {
                m_registeredObjectsById.erase(it);
            }
        }
    }

    carb::ObjectPtr<IPmatxPlayerCoreObjectInterface> findPmatxPlayerCoreObject(const char* id) const override
    {
        const auto& it = m_registeredObjectsById.find(id);
        if (it != m_registeredObjectsById.end())
        {
            return it->second;
        }

        return carb::ObjectPtr<IPmatxPlayerCoreObjectInterface>();
    }

private:
    std::unordered_map<std::string, carb::ObjectPtr<IPmatxPlayerCoreObjectInterface>> m_registeredObjectsById;
};

}

CARB_PLUGIN_IMPL(pluginImplDesc, pmatx::player::core::ExampleBoundImplementation)

void fillInterface(pmatx::player::core::ExampleBoundImplementation& iface)
{
}
