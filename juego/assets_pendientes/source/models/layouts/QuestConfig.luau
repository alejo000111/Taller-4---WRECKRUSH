local QuestConfig = {}

QuestConfig.List = {
	{
		Id = "Destroy25",
		Text = "DESTROY %s OBJECTS",
		Type = "Destroy",
		Order = 1,
		Target = 25,
		Rewards = { Cash = 1500, Scrap = 150 },
		Repeat = { TargetScale = 3, RewardScale = 2 },
		Icon = "QuestDestroy",
	},
	{
		Id = "Destroy100",
		Text = "DESTROY %s OBJECTS",
		Type = "Destroy",
		Order = 2,
		Target = 100,
		Rewards = { Cash = 6000, ChaosCores = 1 },
		Repeat = { TargetScale = 3, RewardScale = 2 },
		Icon = "QuestDestroy",
	},
	{
		Id = "Damage10K",
		Text = "DEAL %s DAMAGE",
		Type = "Damage",
		Order = 3,
		Target = 10000,
		ScaleTargetWithProgress = true,
		Rewards = { Cash = 2500, Boost = { Id = "Damage2x", Seconds = 300 } },
		Repeat = { TargetScale = 5, RewardScale = 2 },
		Icon = "QuestDamage",
	},
	{
		Id = "Earn50K",
		Text = "EARN %s CASH",
		Type = "EarnCash",
		Order = 4,
		Target = 50000,
		ScaleTargetWithProgress = true,
		Rewards = { Scrap = 1500, ChaosCores = 1 },
		Repeat = { TargetScale = 5, RewardScale = 2 },
		Icon = "QuestCash",
	},
	{
		Id = "UseTools",
		Text = "USE %s DIFFERENT TOOLS",
		Type = "UseTools",
		Order = 5,
		Target = 3,
		Rewards = { Cash = 20000, ChaosCores = 2 },
		Icon = "QuestTools",
	},
	{
		Id = "ChaosEvent",
		Text = "COMPLETE %s CHAOS EVENT",
		Type = "ChaosEvent",
		Order = 6,
		Target = 1,
		Rewards = { ChaosCores = 3, Boost = { Id = "Cash2x", Seconds = 600 } },
		Repeat = { TargetScale = 1, TargetAdd = 1, RewardScale = 1 },
		Icon = "QuestChaos",
	},
}


-- New contracts use the existing QuestProgress map; IDs of existing quests stay unchanged.
local contracts = {
 { Id="FirstWrecks", Text="BREAK %s OBJECTS", Type="Destroy", Order=1, Target=5, Rewards={Cash=150,Scrap=25}, Icon="QuestDestroy", Description="Start with barrels and wooden crates.", Zone="ScrapYard" },
 { Id="WoodCleanup", Text="BREAK %s WOOD OBJECTS", Type="DestroyMaterial", Material="Wood", Order=2, Target=12, Rewards={Cash=400,Scrap=50}, Icon="QuestDestroy", Description="Look for wooden crates in Scrap Yard." },
 { Id="MetalCleanup", Text="BREAK %s METAL OBJECTS", Type="DestroyMaterial", Material="Metal", Order=3, Target=20, Rewards={Cash=650,Scrap=80}, Icon="QuestDestroy", Description="Barrels, road signs and vehicles count." },
 { Id="RubberCleanup", Text="BREAK %s RUBBER OBJECTS", Type="DestroyMaterial", Material="Rubber", Order=4, Target=10, Rewards={Cash=350,Scrap=50}, Icon="QuestDestroy", Description="Find tire stacks in Scrap Yard." },
 { Id="ScrapCircuit", Text="WRECK %s IN SCRAP YARD", Type="DestroyZone", Zone="ScrapYard", Order=5, Target=25, Rewards={Cash=750,Scrap=100}, Icon="ZoneScrapYard", Description="Clear your starter zone; shared wrecks count." },
 { Id="GlassCleanup", Text="BREAK %s GLASS OBJECTS", Type="DestroyMaterial", Material="Glass", Zone="Downtown", Order=6, Target=10, Rewards={Cash=1200,Scrap=150}, Icon="ZoneDowntown", Description="Find shop windows after unlocking Downtown." },
 { Id="DowntownCircuit", Text="WRECK %s IN DOWNTOWN", Type="DestroyZone", Zone="Downtown", Order=7, Target=20, Rewards={Cash=1800,Scrap=200}, Icon="ZoneDowntown", Description="Unlock Downtown, then demolish its street objects." },
 { Id="IndustrialCircuit", Text="WRECK %s IN INDUSTRIAL", Type="DestroyZone", Zone="Industrial", Order=8, Target=15, Rewards={Cash=5000,Scrap=500}, Icon="ZoneIndustrial", Description="Destroy pipes, tanks and machinery." },
 { Id="MilitaryCircuit", Text="WRECK %s IN MILITARY", Type="DestroyZone", Zone="Military", Order=9, Target=10, Rewards={Cash=15000,Scrap=1000}, Icon="ZoneMilitary", Description="Unlock the base and tackle armored targets." },
 { Id="FutureCircuit", Text="WRECK %s IN FUTURE DISTRICT", Type="DestroyZone", Zone="FutureDistrict", Order=10, Target=8, Rewards={Cash=25000,Scrap=1500}, Icon="ZoneFuture", Description="Demolish drones and futuristic vehicles." },
 { Id="CoreCircuit", Text="WRECK %s IN CHAOS CORE", Type="DestroyZone", Zone="ChaosCore", Order=11, Target=5, Rewards={Cash=50000,ChaosCores=1}, Icon="ZoneChaosCore", Description="Test your best tool against endgame targets." },
 { Id="EventHunter", Text="WRECK %s EVENT OBJECTS", Type="DestroyEvent", Order=12, Target=3, Rewards={Cash=1000,ChaosCores=1}, Icon="QuestChaos", Description="Join an active event; contribute damage to its targets." },
}
table.insert(contracts,{Id="HuntInitiation",Text="EARN %s TARGET HUNT MEDAL",Type="FinishHunt",Order=13,Target=1,Rewards={Cash=300,Scrap=40},Icon="QuestDestroy",Description="Open PLAY and earn Bronze or better in Target Hunt."})
table.insert(contracts,{Id="RelayInitiation",Text="EARN %s TOOL RELAY MEDAL",Type="FinishRelay",Order=14,Target=1,Rewards={Cash=400,Boost={Id="Damage2x",Seconds=120}},Icon="QuestTools",Description="Put two tools in the hotbar. Hit each marked target with the named tool."})
table.insert(contracts,{Id="MarkedCleanup",Text="CLEAR %s MARKED TARGETS",Type="HuntTargets",Order=15,Target=12,Rewards={Cash=1000,Scrap=150},Icon="QuestDestroy",Description="Target Hunt and Tool Relay both count. Your contract progress is saved."})
table.insert(contracts,{Id="SalvageInitiation",Text="EARN %s SALVAGE RUSH MEDAL",Type="FinishSalvage",Order=16,Target=1,Rewards={Cash=350,Scrap=50},Icon="Scrap",Description="Open PLAY. Collect at least three personal drops before the timer ends."})
table.insert(contracts,{Id="SalvageRecovery",Text="RECOVER %s SALVAGE DROPS",Type="SalvagePickups",Order=17,Target=15,Rewards={Cash=1000,Scrap=150},Icon="Scrap",Description="Walk to orange drops in Salvage Rush. Progress carries across runs."})
table.insert(contracts,{Id="SalvageSpecialist",Text="RECOVER %s SALVAGE DROPS",Type="SalvagePickups",Order=18,Target=40,Rewards={Cash=2000,Scrap=300},Icon="Scrap",Description="Keep recovering personal drops; claim this one-time reward after forty pickups."})
for _, quest in ipairs(contracts) do
 quest.Category = "Contracts"
 quest.FixedRewards = true
 table.insert(QuestConfig.List, quest)
end


-- Albums and exploration reuse the same saved quest map.
local Shared=game:GetService("ReplicatedStorage").Shared
local Objects=require(Shared.Config.DestructibleConfig)
local Zones=require(Shared.Config.ZoneConfig)
local Caches=require(Shared.Config.CacheConfig)
local albumCash={1200,3000,8000,20000,35000,60000}
for index,zone in ipairs(Zones.List)do
 local ids={}
 local count=0
 for _,object in ipairs(Objects.List)do
  if object.Zone==zone.Id and not object.TierZone then ids[object.Id]=true count+=1 end
 end
 table.insert(QuestConfig.List,{
  Id="Album"..zone.Id,Text="DISCOVER %s OBJECT TYPES",Type="CollectTypes",
  Zone=zone.Id,ObjectIds=ids,Target=count,Order=index,Category="Collections",
  FixedRewards=true,Rewards={Cash=albumCash[index],Scrap=100*index},
  Icon=zone.Icon,Description="Break each listed type at least once. Album progress is saved.",
 })
end
for trailIndex,trail in ipairs(Caches.Trails)do
 local cacheIds={}local count=0
 for _,cache in ipairs(Caches.List)do
  if cache.QuestId==trail.QuestId then cacheIds[cache.Id]=true count+=1 end
 end
 table.insert(QuestConfig.List,{
  Id=trail.QuestId,Text="FIND %s SALVAGE CACHES",Type="FindCache",ObjectIds=cacheIds,
  Target=count,Order=6+trailIndex,Category="Collections",FixedRewards=true,
  Rewards=trail.Rewards,Icon="Scrap",Description=trail.Description,
 })
end

-- Short job chains: each stage starts after the previous reward is claimed.
QuestConfig.Chapters = {
 {Id="YardRecovery",Name="YARD RECOVERY",Zone="ScrapYard",Material="Wood",Cash=120,Scrap=20,
  Brief="Recover a working yard: clear wood, catalogue scrap, then tackle the heavier wrecks."},
 {Id="CityRenewal",Name="CITY RENEWAL",Zone="Downtown",Material="Glass",Cash=300,Scrap=35,
  Brief="Open the streets: remove glass, survey the district, then demolish bulky obstacles."},
 {Id="FactoryReset",Name="FACTORY RESET",Zone="Industrial",Material="Metal",Cash=800,Scrap=60,
  Brief="Restart the factory: clear metal, identify machinery, then remove heavy equipment."},
 {Id="BaseRecovery",Name="BASE RECOVERY",Zone="Military",Material="Wood",Cash=1500,Scrap=80,FinalCores=1,
  Brief="Restore the perimeter: recover ammo crates, survey the base, then clear armored wrecks."},
 {Id="FutureReboot",Name="FUTURE REBOOT",Zone="FutureDistrict",Material="Tech",Cash=3000,Scrap=100,FinalCores=2,
  Brief="Reboot the district: dismantle tech, catalogue machines, then take down its heavy units."},
 {Id="CoreContainment",Name="CORE CONTAINMENT",Zone="ChaosCore",Material="Crystal",Cash=6000,Scrap=120,FinalCores=3,
  Brief="Contain the core: clear crystals, identify alien machinery, then finish the final cleanup."},
}
for chapterIndex,chapter in ipairs(QuestConfig.Chapters) do
 local objects={}
 for _,object in ipairs(Objects.List) do
  if object.Zone==chapter.Zone and not object.TierZone then objects[object.Id]=true end
 end
 local stages={
  {Type="DestroyMaterial",Target=4,Text="CLEAR %s "..string.upper(chapter.Material).." OBJECTS",Description="Clear the work area. Only wrecks in this chapter's zone count."},
  {Type="CollectTypes",Target=3,Text="SURVEY %s OBJECT TYPES",Description="Break three different object types in this district. Repeats do not count."},
  {Type="DestroyHeavy",Target=2,Text="REMOVE %s HEAVY TARGETS",Description="Medium, Large and Huge targets count. Share a wreck with another player if it is tough."},
  {Type="DestroyZone",Target=10,Text="FINISH %s DISTRICT WRECKS",Description="Finish the cleanup. Claim this stage to complete the chapter."},
 }
 for step,stage in ipairs(stages)do
  stage.Id=chapter.Id..step
  stage.Category="Campaign"
  stage.Chapter=chapter.Id stage.Step=step stage.Order=chapterIndex*10+step
  stage.Zone=chapter.Zone stage.Material=chapter.Material stage.ObjectIds=objects
  stage.Prerequisite=step>1 and (chapter.Id..(step-1))or nil
  stage.FixedRewards=true stage.Rewards={Cash=chapter.Cash*step,Scrap=chapter.Scrap*step}
  if step==4 and chapter.FinalCores then stage.Rewards.ChaosCores=chapter.FinalCores end
  stage.Icon=Zones.ById[chapter.Zone].Icon
  table.insert(QuestConfig.List,stage)
 end
end

function QuestConfig.IsStageUnlocked(quest,data)
 if not quest or not data then return false end
 if quest.Prerequisite then
  local previous=data.QuestProgress and data.QuestProgress[quest.Prerequisite]
  if not previous or previous.Completed~=true then return false end
 end
 return true
end
function QuestConfig.IsAvailable(quest,data)
 return QuestConfig.IsStageUnlocked(quest,data)and
  (not quest.Zone or quest.Zone=="ScrapYard"or (data.Zones and data.Zones[quest.Zone]==true))
end

QuestConfig.ById = {}
for _, quest in ipairs(QuestConfig.List) do
	QuestConfig.ById[quest.Id] = quest
end

return QuestConfig
