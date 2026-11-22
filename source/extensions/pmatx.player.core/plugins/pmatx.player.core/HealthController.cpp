#include <carb/logging/LoggingUtils.h>

#include <pmatx/player/core/HealthController.h>

#include <cstdint>
#include <exception>
#include <stdexcept>


namespace pmatx::player::core
{
HealthController::HealthController(const uint16_t maxHealth) : m_maxHealth(maxHealth)
{
}

uint16_t HealthController::getHealthPoints() const
{
    return m_health;
}

float HealthController::getHealthPct() const
{
    if (m_maxHealth == 0)
    {
        return 0.0f;
    }

    return static_cast<float>((m_health / m_maxHealth) * 100); // NOLINT
}

void HealthController::decrementHealth(const uint16_t amount)
{
    if (amount == 0)
    {
        return;
    }

    int final = m_health - amount;
    if (final <= 0)
    {
        m_health = 0;
        _callHealthChanged();
        return;
    }

    m_health = final;
    _callHealthChanged();
}

void HealthController::incrementHealth(const uint16_t amount)
{
    if (amount == 0)
    {
        return;
    }

    int final = m_health + amount;

    if (final > m_health)
    {
        if (m_health == m_maxHealth)
        {
            return;
        }

        m_health = m_maxHealth;
    }

    m_health = final;
    _callHealthChanged();
}

uint64_t HealthController::addHealthChangedCallback(HealthChangeCallback callback)
{
    if (m_nextCallbackId == 0)
    {
        throw std::overflow_error("Healh callback limit has been reached, all ids used");
    }

    uint64_t id = m_nextCallbackId;
    m_onHealthChange[id] = callback;
    m_nextCallbackId++;
    return id;
}

void HealthController::removeHealthChangedCallback(uint64_t id)
{
    m_onHealthChange.erase(id);
}

void HealthController::_callHealthChanged()
{
    auto info = HealthInfo{ this->getHealthPct(), m_health, m_maxHealth };
    std::vector<uint64_t> invalid;

    for (const auto& cb : m_onHealthChange)
    {
        try
        {
            cb.second(info);
        }
        catch (const std::exception)
        {
            CARB_LOG_ERROR("Callback raised error on health change, removing callback");
            invalid.push_back(cb.first);
        }
    }

    for (const auto& id : invalid)
    {
        m_onHealthChange.erase(id);
    }
}
}
