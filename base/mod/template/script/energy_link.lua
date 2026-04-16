local count_energy_bridges = function()
    local count = 0
    for i, bridge in pairs(storage.energy_link_bridges) do
        if validate_energy_link_bridge(i, bridge) then
            count = count + 1 + (bridge.quality.level * 0.3)
        end
    end
    return count
end

local get_energy_increment = function(bridge)
    return ENERGY_INCREMENT + (ENERGY_INCREMENT * 0.3 * bridge.quality.level)
end

local on_check_energy_link = function(event)
    --- assuming 1 MJ increment and 5MJ battery:
    --- first 2 MJ request fill, last 2 MJ push energy, middle 1 MJ does nothing
    if event.tick % 60 == 30 then
        local force = "player"
        local bridges = storage.energy_link_bridges
        local bridgecount = count_energy_bridges()
        storage.forcedata[force].energy_bridges = bridgecount
        if storage.forcedata[force].energy == nil then
            storage.forcedata[force].energy = 0
        end
        if storage.forcedata[force].energy < ENERGY_INCREMENT * bridgecount * 5 then
            for i, bridge in pairs(bridges) do
                if validate_energy_link_bridge(i, bridge) then
                    energy_increment = get_energy_increment(bridge)
                    if bridge.energy > energy_increment*3 then
                        storage.forcedata[force].energy = storage.forcedata[force].energy + (energy_increment * ENERGY_LINK_EFFICIENCY)
                        bridge.energy = bridge.energy - energy_increment
                    end
                end
            end
        end
        for i, bridge in pairs(bridges) do
            if validate_energy_link_bridge(i, bridge) then
                energy_increment = get_energy_increment(bridge)
                if storage.forcedata[force].energy < energy_increment and bridge.quality.level == 0 then
                    break
                end
                if bridge.energy < energy_increment*2 and storage.forcedata[force].energy > energy_increment then
                    storage.forcedata[force].energy = storage.forcedata[force].energy - energy_increment
                    bridge.energy = bridge.energy + energy_increment
                end
            end
        end
    end
end

local validate_energy_link_bridge = function(unit_number, entity)
    if not entity then
        if storage.energy_link_bridges[unit_number] == nil then return false end
        storage.energy_link_bridges[unit_number] = nil
        return false
    end
    if not entity.valid then
        if storage.energy_link_bridges[unit_number] == nil then return false end
        storage.energy_link_bridges[unit_number] = nil
        return false
    end
    return true
end

local on_energy_bridge_constructed = function(entity)
    if entity and entity.valid then
        if string_starts_with(entity.prototype.name, "ap-energy-bridge") then
            storage.energy_link_bridges[entity.unit_number] = entity
        end
    end
end

local on_energy_bridge_removed = function(entity)
    if string_starts_with(entity.prototype.name, "ap-energy-bridge") then
        if storage.energy_link_bridges[entity.unit_number] == nil then return end
        storage.energy_link_bridges[entity.unit_number] = nil
    end
end

return {
    events = {
        [defines.events.on_tick] = on_check_energy_link,
        [defines.events.on_built_entity] = function(event) on_energy_bridge_constructed(event.entity) end,
        [defines.events.on_robot_built_entity] = function(event) on_energy_bridge_constructed(event.entity) end,
        [defines.events.on_entity_cloned] = function(event) on_energy_bridge_constructed(event.destination) end,
        [defines.events.script_raised_revive] = function(event) on_energy_bridge_constructed(event.entity) end,
        [defines.events.script_raised_built] = function(event) on_energy_bridge_constructed(event.entity) end,
        [defines.events.on_entity_died] = function(event) on_energy_bridge_removed(event.entity) end,
        [defines.events.on_player_mined_entity] = function(event) on_energy_bridge_removed(event.entity) end,
        [defines.events.on_robot_mined_entity] = function(event) on_energy_bridge_removed(event.entity) end,
    },
}
