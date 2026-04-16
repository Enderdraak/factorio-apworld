local free_samples = require("script/free_samples").interface

local TRAP_TABLE = {
["Attack Trap"] = function ()
    game.surfaces["nauvis"].build_enemy_base(game.forces["player"].get_spawn_position(game.get_surface(1)), 25)
end,
["Evolution Trap"] = function ()
    local new_factor = game.forces["enemy"].get_evolution_factor("nauvis") +
        (TRAP_EVO_FACTOR * (1 - game.forces["enemy"].get_evolution_factor("nauvis")))
    game.forces["enemy"].set_evolution_factor(new_factor, "nauvis")
    game.print({"", "New evolution factor:", new_factor})
end,
["Teleport Trap"] = function()
    for _, player in ipairs(game.forces["player"].players) do
        if player.character then
            attempt_teleport_player(player, 1)
        end
    end
end,
["Grenade Trap"] = function ()
    fire_entity_at_players("grenade", 0.1)
end,
["Cluster Grenade Trap"] = function ()
    fire_entity_at_players("cluster-grenade", 0.1)
end,
["Artillery Trap"] = function ()
    fire_entity_at_players("artillery-projectile", 1)
end,
["Atomic Rocket Trap"] = function ()
    fire_entity_at_players("atomic-rocket", 0.1)
end,
["Atomic Cliff Remover Trap"] = function ()
    local cliffs = game.surfaces["nauvis"].find_entities_filtered{type = "cliff"}

    if #cliffs > 0 then
        fire_entity_at_entities("atomic-rocket", {cliffs[math.random(#cliffs)]}, 0.1)
    end
end,
["Inventory Spill Trap"] = function ()
    for _, player in ipairs(game.forces["player"].players) do
        spill_character_inventory(player.character)
    end
end,
}

local receive_item = function(item_name, source)
    local force = game.forces["player"]

    local technology = force.technologies[item_name]
    if technology ~= nil then
        if technology.researched then
            return false
        end

        game.print({"", "Received [technology=" .. technology.name .. "] from ", source})
        game.play_sound({path="utility/research_completed"})

        technology.researched = true

        free_samples.send_for_technology(force, technology.name)

        return true
    end

    if string_ends_with(item_name, " recipe") then
        local recipe = force.recipes[item_name:sub(0, -8)]
        if recipe ~= null then
            if recipe.enabled then
                return false
            end

            game.print({"", "Received [recipe=" .. recipe.name .. "] from ", source})
            game.play_sound({path="utility/research_completed"})

            recipe.enabled = true

            free_samples.send_for_recipe(force, recipe.name)

            return true
        end
    end

    if TRAP_TABLE[item_name] ~= nil then
        game.print({"", "Received ", item_name, " from ", source})
        TRAP_TABLE[item_name]()

        return true
    end

    game.print("Unknown Item " .. item_name)
end

local on_init = function()
    storage.receive_index = {}
end

local get_technology_command = function(call)
    local tech
    local force = game.forces["player"]
    if call.parameter == nil then
        game.print("ap-get-technology is only to be used by the Archipelago Factorio Client")
        return
    end
    chunks = split(call.parameter, "\t")
    local item_name = chunks[1]
    local index = chunks[2]
    local source = chunks[3] or "Archipelago"

    if index == nil then
        game.print("ap-get-technology is only to be used by the Archipelago Factorio Client")
        return
    end

    if index == -1 then -- for coop sync and restoring from an older savegame
        tech = force.technologies[item_name]
        if tech.researched ~= true then
            game.print({"", "Received [technology=" .. tech.name .. "] as it is already checked."})
            game.play_sound({path="utility/research_completed"})
            tech.researched = true
        end
        return
    end

    if storage.receive_index[index] == item_name then
        return
    end

    if PROGRESSIVE_ITEMS[item_name] ~= nil then
        for _, item_name in ipairs(PROGRESSIVE_ITEMS[item_name]) do
            received = receive_item(item_name, source)

            if recived ~= false then
                break
            end
        end
    else
        received = receive_item(item_name, source)
    end

    if received then
        storage.receive_index[index] = item_name
    end
end

return {
    on_init = on_init,
    add_commands = function()
        commands.add_command("ap-get-technology", "Grant a technology, used by the Archipelago Client.", get_technology_command)
    end,
}
