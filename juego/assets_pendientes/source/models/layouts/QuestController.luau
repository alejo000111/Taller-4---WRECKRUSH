local ReplicatedStorage = game:GetService("ReplicatedStorage")
local EngineRunService = game:GetService("RunService")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local ThemeConfig = require(Shared.Config.ThemeConfig)
local QuestConfig = require(Shared.Config.QuestConfig)
local GameConfig = require(Shared.Config.GameConfig)
local Formulas = require(Shared.Modules.Formulas)
local Format = require(Shared.Modules.Format)
local Net = require(Shared.Modules.Net)
local Components = script.Parent.Parent:WaitForChild("Components")
local UIKit = require(Components.UIKit)
local Widgets = require(Components.Widgets)

local Colors = ThemeConfig.Colors
local Fonts = ThemeConfig.Fonts

local QuestController = { Priority = 42 }

local window = nil
local category = "Contracts"
local focusQuest
local tabs = {}
local refreshVersion = 0

local function rewardText(rewards)
	local parts = {}
	if rewards.Cash then
		table.insert(parts, Format.Number(rewards.Cash) .. " CASH")
	end
	if rewards.Scrap then
		table.insert(parts, Format.Number(rewards.Scrap) .. " SCRAP")
	end
	if rewards.ChaosCores then
		table.insert(parts, rewards.ChaosCores .. " CORES")
	end
	if rewards.Boost then
		local boost = GameConfig.Boosts[rewards.Boost.Id]
		table.insert(parts, (boost and boost.Name or "BOOST") .. " " .. Format.Time(rewards.Boost.Seconds))
	end
	return table.concat(parts, "  +  ")
end

function QuestController:Init(controllers)
	self.Controllers = controllers
end

function QuestController:Start()
	local controllers = self.Controllers
	window = Widgets.Window("QuestUI", { Title = "QUESTS & CONTRACTS", Accent = Colors.Cyan, Tabs = true })
	Widgets.List(window.Content, 10)
	for index, name in ipairs({"Campaign", "Contracts", "Milestones"}) do
		tabs[name] = Widgets.Tab(window.Tabs, {Name=name, Text=string.upper(name), Width=145, Order=index, OnClick=function()
			category=name focusQuest=nil
			self:Refresh()
		end})
	end
	Widgets.Tab(window.Tabs, {Name="Collections", Text="COLLECTIONS", Width=145, Order=4, OnClick=function()
		controllers.PanelController:Open("Collections")
	end})
	for _,tab in ipairs(window.Tabs:GetChildren())do
  if tab:IsA("GuiButton")then tab.Size=UDim2.new(.25,-6,1,0)end
 end
 controllers.PanelController:Register("Quests", window.Gui, {
		OnOpen = function()
			self:Refresh()
		end,
	})
	controllers.DataController:Observe("QuestProgress", function()
		if controllers.PanelController:IsOpen("Quests") then
			self:Refresh()
		end
	end)
end

function QuestController:ViewQuest(questId)
 local quest = questId and QuestConfig.ById[questId]
 if quest and quest.Category=="Collections"then
  self.Controllers.PanelController:Open("Collections",quest.Type=="FindCache"and "Caches"or quest.Zone)
  return
 end
 focusQuest=questId
 category = quest and quest.Category or "Milestones"
 self.Controllers.PanelController:Open("Quests")
end

function QuestController:Refresh()
 refreshVersion+=1
 local version=refreshVersion
	local data = self.Controllers.DataController:GetAll()
	if not data then
		return
	end
	Widgets.Clear(window.Content)
 if category=="Campaign"then
  local intro=Widgets.Card(window.Content,{Name="CampaignIntro",Size=UDim2.new(1,0,0,58),Order=-10})
  Widgets.Label(intro,{Text="DISTRICT JOBS · "..#QuestConfig.Chapters.." CHAPTERS / "..(#QuestConfig.Chapters*4).." STAGES\nClaim each stage to unlock the next. Chapters can be played separately.",Position=UDim2.fromOffset(12,6),Size=UDim2.new(1,-24,1,-12),MaxSize=16,Color=Colors.Cyan})
 end
	for name, tab in pairs(tabs) do Widgets.SetVariant(tab, name == category and "Primary" or "Secondary") end
	local camera = workspace.CurrentCamera
	local compact = camera and camera.ViewportSize.Y < 600
	for _, quest in ipairs(QuestConfig.List) do
		if (quest.Category or "Milestones") ~= category then continue end
		local progress = data.QuestProgress[quest.Id] or { Tier = 0, Progress = 0, Target = quest.Target }
		local target = progress.Target or quest.Target
		local zoneLocked = quest.Zone and quest.Zone~="ScrapYard"and not data.Zones[quest.Zone]
  local previous=quest.Prerequisite and data.QuestProgress[quest.Prerequisite]
  local stageLocked=quest.Prerequisite and (not previous or not previous.Completed)
  local locked=not QuestConfig.IsAvailable(quest,data)
		local ready = not stageLocked and not progress.Completed and (progress.Progress or 0) >= target
		if category=="Campaign"and quest.Step==1 then
   local chapter
   for _,candidate in ipairs(QuestConfig.Chapters)do if candidate.Id==quest.Chapter then chapter=candidate break end end
   local chapterCard=Widgets.Card(window.Content,{Name=quest.Chapter,Size=UDim2.new(1,0,0,64),Order=quest.Order-1,Accent=Colors.Cyan})
   Widgets.Label(chapterCard,{Text=chapter.Name,Position=UDim2.fromOffset(12,4),Size=UDim2.new(1,-24,0,23),MaxSize=20,Font=Fonts.Display,Color=Colors.Cyan})
   Widgets.Label(chapterCard,{Text=chapter.Brief,Position=UDim2.fromOffset(12,29),Size=UDim2.new(1,-24,0,30),MaxSize=13,Color=Colors.Muted})
  end
  local card = Widgets.Card(window.Content, { Name = quest.Id, Size = UDim2.new(1, 0, 0, 130), Order = category=="Campaign"and quest.Order or ((progress.Completed and 100 or ready and 0 or 10) + quest.Order), Accent = ready and Colors.Yellow or Colors.Cyan })
		if ready then
			card.Outline.Color = Colors.Yellow
		end
		Widgets.Icon(card, quest.Icon, { Size = UDim2.fromOffset(compact and 38 or 58, compact and 38 or 58), Position = UDim2.new(0, compact and 12 or 18, 0.5, 0), AnchorPoint = Vector2.new(0, 0.5), FallbackColor = Colors.Cyan })
		local info = UIKit.Create("Frame", { Name = "Info", BackgroundTransparency = 1, Position = UDim2.fromOffset(compact and 64 or 90, 10), Size = UDim2.new(0.72, compact and -70 or -96, 1, -20), Parent = card })
		Widgets.Label(info, { Name = "QuestText", Text = (quest.Step and ("STEP "..quest.Step.."/4 · ")or "")..string.format(quest.Text, Format.Commas(target)), Font = Fonts.Display, Size = UDim2.new(1, 0, 0, 26), MaxSize = 22 })
		local bar = Widgets.Progress(info, { Name = "Bar", Size = UDim2.new(1, 0, 0, 16), Position = UDim2.fromOffset(0, 32), Color = ready and Colors.Yellow or Colors.Cyan, Value = (progress.Progress or 0) / math.max(target, 1) })
		Widgets.Label(bar, { Name = "Count", Text = Format.Number(math.min(progress.Progress or 0, target)) .. " / " .. Format.Number(target), Font = Fonts.Number, Size = UDim2.fromScale(1, 1), AlignX = Enum.TextXAlignment.Center, MaxSize = 12, Stroke = 1, ZIndex = 3 })
		local rewards = quest.FixedRewards and quest.Rewards or Formulas.QuestRewards(quest, progress.Tier or 0, data)
		Widgets.Label(info, { Name = "Rewards", Text = "REWARD: " .. rewardText(rewards), Font = Fonts.Number, Size = UDim2.new(1, 0, 0, 18), Position = UDim2.fromOffset(0, 56), MaxSize = 14, Color = Colors.Yellow })
		Widgets.Label(info, {Name="Description", Text=zoneLocked and "Unlock this zone to start"or stageLocked and ("Claim step "..(quest.Step-1).." to unlock this job.")or quest.Description or "Keep playing to reach this milestone.", Position=UDim2.fromOffset(0, 79), Size=UDim2.new(1, 0, 0, 30), MaxSize=13, Color=Colors.Muted})
		local action = UIKit.Create("Frame", { Name = "Action", BackgroundTransparency = 1, AnchorPoint = Vector2.new(1, 0.5), Position = UDim2.new(1, -12, 0.5, 0), Size = UDim2.new(0.25, 0, 0, 46), Parent = card })
		if progress.Completed then
			Widgets.Button(action, { Name = "Done", Text = "DONE", Variant = "Disabled", Size = UDim2.fromScale(1, 1) })
		else
			local claim = Widgets.Button(action, {
				Name = "Claim",
				Text = ready and "CLAIM"or zoneLocked and "GO TO ZONE"or stageLocked and "PREVIOUS STEP"or "TRACK TASK",
				Variant = ready and "Primary" or "Secondary",
				Size = UDim2.fromScale(1, 1),
				OnClick = function()
					if ready then
						Net.Remote("ClaimQuest"):FireServer(quest.Id)
					elseif zoneLocked then
						self.Controllers.PanelController:Open("Travel")
					elseif stageLocked then
						self:ViewQuest(quest.Prerequisite)
					else
						self.Controllers.ActivityController:SelectQuest(quest.Id)
						if quest.Zone then self.Controllers.NavigationController:SetZone(quest.Zone)end
						self.Controllers.PanelController:Close("Quests")
					end
				end,
			})
			if ready then
				UIKit.Pop(claim, 1.15)
			end
		end
	end
 task.defer(function()
  EngineRunService.RenderStepped:Wait()
  if version~=refreshVersion or not self.Controllers.PanelController:IsOpen("Quests")then return end
  local def=focusQuest and QuestConfig.ById[focusQuest]
  local card=def and window.Content:FindFirstChild(def.Step==1 and def.Chapter or focusQuest)
  if not card then return end
  -- List offsets remain stable while the opening animation scales the window.
  local children={}
  for _,child in ipairs(window.Content:GetChildren())do
   if child:IsA("GuiObject")and child.Visible then table.insert(children,child)end
  end
  table.sort(children,function(x,y)return x.LayoutOrder<y.LayoutOrder end)
  local y=0
  local padding=window.Content:FindFirstChildOfClass("UIPadding")
  if padding then y=padding.PaddingTop.Offset end
  local layout=window.Content:FindFirstChildOfClass("UIListLayout")
  local gap=layout and layout.Padding.Offset or 0
  for _,child in ipairs(children)do
   if child==card then break end
   y+=child.Size.Y.Offset+gap
  end
  window.Content.CanvasPosition=Vector2.new(0,math.max(0,y-6))
 end)
end

return QuestController
