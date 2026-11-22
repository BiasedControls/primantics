// Standard health logic for most objects

#include "IHealth.h"

#include <cstdint>
#include <unordered_map>


namespace pmatx::player::core
{
class HealthController : IHealth
{
public:
    HealthController(const uint16_t maxHealth = 100);
    void decrementHealth(const uint16_t amount) override;
    void incrementHealth(const uint16_t amount) override;
    uint16_t getHealthPoints() const override;
    float getHealthPct() const override;

    uint64_t addHealthChangedCallback(HealthChangeCallback) override;
    void removeHealthChangedCallback(uint64_t id) override;

private:
    uint16_t m_health{ 0 };
    uint16_t m_maxHealth{ 100 };
    uint64_t m_nextCallbackId{ 1 };
    std::unordered_map<uint64_t, HealthChangeCallback> m_onHealthChange;

    void _callHealthChanged();
};
}
