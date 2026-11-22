
#define CARB_EXPORTS

#include <carb/PluginUtils.h>

#include <omni/ext/IExt.h>
#include <pmatx/player/core/IPlayer.h>


const struct carb::PluginImplDesc pluginImplDesc = { "pmatx.player.core.plugin", "Pmatx Player", "Tony",
                                                     carb::PluginHotReload::eEnabled, "dev" };

namespace pmatx::player::core
{

class PmatxPlayerCoreExt : public omni::ext::IExt
{
public:
    void onStartup(const char* extId) override
    {
    }

    void onShutdown() override
    {
    }
};
} // pmatx::player::core

CARB_PLUGIN_IMPL(pluginImplDesc, pmatx::player::core::PmatxPlayerCoreExt);

void fillInterface(pmatx::player::core::PmatxPlayerCoreExt& iface)
{
}
