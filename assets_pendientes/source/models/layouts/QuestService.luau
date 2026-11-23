local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Shared = ReplicatedStorage.Shared
local QuestConfig = require(Shared.Config.QuestConfig)
local Formulas = require(Shared.Modules.Formulas)
local Format = require(Shared.Modules.Format)
local Signal = require(Shared.Modules.Signal)
local TableUtil = require(Shared.Modules.TableUtil)
local Validate = require(ServerScriptService.Modules.Validate)
local Notifier = require(ServerScriptService.Modules.Notifier)

local FLUSH_INTERVAL = 0.5
local IGNORED_CASH_SOURCES = { Purchase = true, Quest = true, Daily = true, Challenge = true }

local QuestService = { Priority = 50 }
QuestService.QuestClaimed = Signal.new()

local dirty = {}

local function ensure(data)
	for _, quest in ipairs(QuestConfig.List) do
		local progress = data.QuestProgress[quest.Id]
		if type(progress) ~= "table" then
			progress = {}
			data.QuestProgress[quest.Id] = progress
		end
		progress.Tier = math.max(0, math.floor(tonumber(progress.Tier) or 0))
		progress.Progress = math.max(0, tonumber(progress.Progress) or 0)
		if type(progress.Target) ~= "number" or progress.Target <= 0 then
			progress.Target = Formulas.QuestTarget(quest, progress.Tier, data)
		end
		progress.Completed = progress.Completed == true
		progress.Notified = progress.Notified == true
		if (quest.Type == "UseTools" or quest.Type == "CollectTypes" or quest.Type == "FindCache") and type(progress.Used) ~= "table" then
			progress.Used = {}
		end
	end
	for questId in pairs(data.QuestProgress) do
		if not QuestConfig.ById[questId] then
			data.QuestProgress[questId] = nil
		end
	end
end

function QuestService:Init(services)
	self.Services = services
	self.Data = services.DataService

	self.Data:OnProfileLoaded(function(player, data)
		ensure(data)
		self.Data:Replicate(player, "QuestProgress")
	end)

	local destruction = services.DestructionService
	destruction.Wrecked:Connect(function(entry, credits)
		for _, credit in ipairs(credits) do
			if credit.Counted then
				self:Advance(credit.Player, "Destroy", 1, nil, entry.Zone)
				self:Advance(credit.Player, "CollectTypes", 0, entry.TypeId, entry.Zone)
				self:Advance(credit.Player, "DestroyMaterial", 1, entry.Def.MaterialType, entry.Zone)
				self:Advance(credit.Player, "DestroyZone", 1, entry.Zone, entry.Zone)
				if entry.SizeClass=="Medium" or entry.SizeClass=="Large" or entry.SizeClass=="Huge" then self:Advance(credit.Player,"DestroyHeavy",1,nil,entry.Zone) end
				if entry.IsEvent then self:Advance(credit.Player, "DestroyEvent", 1) end
			end
		end
	end)
	destruction.Damaged:Connect(function(player, _, amount, toolId)
		self:Advance(player, "Damage", amount)
		self:Advance(player, "UseTools", 0, toolId)
	end)
	services.EconomyService.CashEarned:Connect(function(player, amount, source)
		if not IGNORED_CASH_SOURCES[source] then
			self:Advance(player, "EarnCash", amount)
		end
	end)
 services.RunService.TargetCleared:Connect(function(player)
  self:Advance(player,"HuntTargets",1)
 end)
 services.RunService.SalvageCollected:Connect(function(player,amount)
  self:Advance(player,"SalvagePickups",amount)
 end)
 services.RunService.ChallengeFinished:Connect(function(player,modeId)
  if modeId=="TargetHunt"then self:Advance(player,"FinishHunt",1)
  elseif modeId=="ToolRelay"then self:Advance(player,"FinishRelay",1)
  elseif modeId=="SalvageRush"then self:Advance(player,"FinishSalvage",1)end
 end)
	if services.EventService then
		services.EventService.ChaosCompleted:Connect(function(participants)
			for _, player in ipairs(participants) do
				self:Advance(player, "ChaosEvent", 1)
			end
		end)
	end
end

function QuestService:Start()
	self.Services.AntiExploitService:Connect("ClaimQuest", { Rate = 3, Burst = 6 }, function(player, questId)
		if Validate.String(questId, 32) then
			self:Claim(player, questId)
		end
	end)

	Players.PlayerRemoving:Connect(function(player)
		dirty[player] = nil
	end)

	task.spawn(function()
		while true do
			task.wait(FLUSH_INTERVAL)
			for player in pairs(dirty) do
				dirty[player] = nil
				self.Data:Replicate(player, "QuestProgress")
			end
		end
	end)
end

function QuestService:Advance(player, questType, amount, toolId, zoneId)
	local data = self.Data:GetData(player)
	if not data then
		return
	end
	for _, quest in ipairs(QuestConfig.List) do
		local matches = quest.Type == questType
			and QuestConfig.IsAvailable(quest,data)
			and (not quest.Zone or quest.Zone==zoneId)
			and (questType ~= "DestroyMaterial" or quest.Material == toolId)
			and (questType ~= "DestroyZone" or quest.Zone == toolId)
			and ((questType ~= "CollectTypes" and questType ~= "FindCache") or (quest.ObjectIds and quest.ObjectIds[toolId] == true))
		local progress = matches and data.QuestProgress[quest.Id]
		if progress and not progress.Completed and progress.Progress < progress.Target then
			if questType == "UseTools" or questType == "CollectTypes" or questType == "FindCache" then
				if toolId and not progress.Used[toolId] then
					progress.Used[toolId] = true
					progress.Progress = math.min(TableUtil.Count(progress.Used), progress.Target)
					dirty[player] = true
				end
			else
				progress.Progress = math.min(progress.Progress + amount, progress.Target)
				dirty[player] = true
			end
			if progress.Progress >= progress.Target and not progress.Notified then
				progress.Notified = true
				Notifier.Send(player, {
					Kind = "Quest",
					Text = "QUEST COMPLETE!",
					Subtext = string.format(quest.Text, Format.Commas(progress.Target)),
					Icon = quest.Icon,
				})
			end
		end
	end
end

function QuestService:Claim(player, questId)
	local quest = QuestConfig.ById[questId]
	local data = self.Data:GetData(player)
	local progress = quest and data and data.QuestProgress[questId]
	if not progress or not QuestConfig.IsStageUnlocked(quest,data) or progress.Completed or progress.Progress < progress.Target then
		return
	end
	local rewards = quest.FixedRewards and quest.Rewards or Formulas.QuestRewards(quest, progress.Tier or 0, data)
	if quest.Repeat then
		progress.Tier += 1
		progress.Progress = 0
		progress.Notified = false
		progress.Target = Formulas.QuestTarget(quest, progress.Tier, data)
		if quest.Type == "UseTools" then
			progress.Used = {}
		end
	else
		progress.Completed = true
	end
	self.Data:Replicate(player, "QuestProgress")
	self.Services.EconomyService:GrantRewards(player, rewards, "Quest", "QUEST REWARD")
	self.QuestClaimed:Fire(player, questId)
end

return QuestService
