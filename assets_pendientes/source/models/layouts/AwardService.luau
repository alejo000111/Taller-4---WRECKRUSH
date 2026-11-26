local BadgeService = game:GetService("BadgeService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Shared = ReplicatedStorage.Shared
local BadgeConfig = require(Shared.Config.BadgeConfig)
local Formulas = require(Shared.Modules.Formulas)
local Notifier = require(ServerScriptService.Modules.Notifier)

local AwardService = { Priority = 55 }

local checking = {}

local function statValue(data, stat)
	if stat == "ZonesUnlocked" then
		return Formulas.ZonesUnlocked(data)
	end
	return tonumber(data[stat]) or 0
end

function AwardService:Init(services)
	self.Services = services
	self.Data = services.DataService

	local function check(player)
		self:Check(player)
	end
	self.Data:OnProfileLoaded(check)
	if services.DestructionService then
		services.DestructionService.Wrecked:Connect(function(_, credits)
			for _, credit in ipairs(credits) do
				if credit.Counted then
					check(credit.Player)
				end
			end
		end)
	end
	if services.RebirthService then
		services.RebirthService.Reborn:Connect(check)
	end
	if services.ZoneService then
		services.ZoneService.ZoneUnlocked:Connect(check)
	end
	if services.EventService and services.EventService.ChaosCompleted then
		services.EventService.ChaosCompleted:Connect(function(participants)
			for _, player in ipairs(participants) do
				check(player)
			end
		end)
	end
end

function AwardService:Check(player)
	local data = self.Data:GetData(player)
	if not data or checking[player] then
		return
	end
	checking[player] = true
	for _, badge in ipairs(BadgeConfig.List) do
		if badge.Id > 0 and not data.Badges[badge.Key] and statValue(data, badge.Condition.Stat) >= badge.Condition.Value then
			local hasOk, alreadyOwned = pcall(BadgeService.UserHasBadgeAsync, BadgeService, player.UserId, badge.Id)
			if hasOk and alreadyOwned then
				data.Badges[badge.Key] = true
			else
				local ok, awarded = pcall(BadgeService.AwardBadge, BadgeService, player.UserId, badge.Id)
				if ok and awarded then
					data.Badges[badge.Key] = true
					Notifier.Send(player, { Kind = "Badge", Text = "BADGE UNLOCKED", Subtext = badge.Name, Icon = badge.Icon })
				end
			end
		end
	end
	checking[player] = nil
end

return AwardService
